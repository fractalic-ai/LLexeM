# runner.py

import os
import uuid
from typing import Optional, Tuple, Union
from pathlib import Path

from core.ast_md.ast import AST, get_ast_part_by_id, perform_ast_operation, get_ast_part_by_path
from core.ast_md.node import Node, NodeType, OperationType
from core.errors import BlockNotFoundError, UnknownOperationError
from core.config import Config
from core.utils import parse_file, get_content_without_header
from core.render.render_ast import render_ast_to_markdown
from core.operations.import_op import process_import
from core.operations.llm_op import process_llm
from core.operations.goto_op import process_goto
from core.operations.shell_op import process_shell
from core.operations.return_op import process_return
from core.operations.call_tree import CallTreeNode
from core.git import ensure_git_repo, create_session_branch, commit_changes
from rich import print
from rich.console import Console

def get_relative_path(base_dir: str, file_path: str) -> str:
    """Convert absolute path to relative path based on base directory."""
    try:
        return os.path.relpath(file_path, base_dir)
    except ValueError:
        return file_path

def run(filename: str, param_node: Optional[Union[Node, AST]] = None, create_new_branch: bool = True,
        p_parent_filename=None, p_parent_operation: str = None, p_call_tree_node=None,
        committed_files=None, file_commit_hashes=None, base_dir=None) -> Tuple[AST, CallTreeNode, str, str, str]:
 
    console = Console(force_terminal=True, color_system="auto")
    if committed_files is None:
        committed_files = set()
    if file_commit_hashes is None:
        file_commit_hashes = {}

    abs_path = os.path.abspath(filename)
    file_dir = os.path.dirname(abs_path)
    local_file_name = os.path.basename(abs_path)

    if base_dir is None and create_new_branch:
        base_dir = file_dir

    goto_count = {}
    branch_name = None
    original_cwd = os.getcwd()
    
    try:
        os.chdir(file_dir)

        if create_new_branch:
            ensure_git_repo(base_dir)
            branch_name = create_session_branch(base_dir, "Testing-git-operations")

            console.print(f"[light_green]✓[/light_green] git. new branch created: [cyan]{branch_name}[/cyan]")

        relative_file_path = os.path.relpath(abs_path, base_dir)

        if not os.path.exists(local_file_name):
            raise FileNotFoundError(f"File not found: {local_file_name}")

        if relative_file_path not in committed_files:
            try:
                md_commit_hash = commit_changes(
                    base_dir,
                    "Operation [@run] execution start",
                    [local_file_name],
                    p_parent_filename,
                    p_parent_operation
                )
                committed_files.add(relative_file_path)
                file_commit_hashes[relative_file_path] = md_commit_hash
            except Exception as e:
                print(f"[ERROR runner.py] Error committing file {relative_file_path}: {str(e)}")
                raise

        # RESTORING LOGIC    
        else:
            md_commit_hash = file_commit_hashes[relative_file_path]

        # RESTORING LOGIC  
        # Process the AST
        try:
            ast = parse_file(local_file_name)
        except Exception as e:
            print(f"[ERROR runner.py] Error parsing file {local_file_name}: {str(e)}")
            print(f"[ERROR runner.py] Current directory: {os.getcwd()}")
            print(f"[ERROR runner.py] File exists: {os.path.exists(local_file_name)}")
            print(f"[ERROR runner.py] File contents:")
            try:
                with open(local_file_name, 'r', encoding='utf-8') as f:
                    print(f.read())
            except Exception as read_error:
                print(f"[ERROR runner.py] Could not read file: {str(read_error)}")
            raise

        # RESTORING LOGIC 
        # Initialize call tree node with relative path
        if p_call_tree_node is None:
            call_tree_node = CallTreeNode(
                operation='@run',
                operation_src=None,
                filename=relative_file_path,  # Use relative path
                md_commit_hash=md_commit_hash,
                ctx_commit_hash=None,
                ctx_file=None,
                parent=None
            )
            new_node = call_tree_node
        else:
            new_node = CallTreeNode(
                operation='@run',
                operation_src=p_parent_operation,
                filename=relative_file_path,  # Use relative path
                md_commit_hash=md_commit_hash,
                ctx_commit_hash=None,
                ctx_file=None,
                parent=p_call_tree_node
            )
            p_call_tree_node.add_child(new_node)



        

        if param_node:
            if isinstance(param_node, AST):
                ast.prepend_node_with_ast(ast.first().key, param_node)
            else:
                decorated_param_node = Node(
                    type=NodeType.HEADING,
                    name="Input Parameters",
                    level=1,
                    #content=f"# Input Parameters\n{get_content_without_header(param_node)}",
                    content=f"{param_node.content}",
                    id="InputParameters",
                    key=str(uuid.uuid4())[:8]
                )
                param_ast = AST("")
                param_ast.parser.nodes = {decorated_param_node.key: decorated_param_node}
                param_ast.parser.head = decorated_param_node
                param_ast.parser.tail = decorated_param_node
                ast.prepend_node_with_ast(ast.first().key, param_ast)

        # RESTORING LOGIC
        # moved operation, was before this block
        current_node = ast.first()

        while current_node:
            if current_node.type == NodeType.OPERATION:
                operation_name = f"@{current_node.name}"
                if operation_name == "@import":
                    current_node = process_import(ast, current_node)
                elif operation_name == "@run":
                    current_node, child_node, run_ctx_file, run_ctx_hash = process_run(
                        ast,
                        current_node,
                        local_file_name,
                        current_node.content.strip(),
                        new_node,  # Pass new_node instead of p_call_tree_node
                        committed_files=committed_files,
                        file_commit_hashes=file_commit_hashes,
                        base_dir=base_dir
                    )
                elif operation_name == "@llm":
                    current_node = process_llm(ast, current_node)
                elif operation_name == "@goto":
                    current_node = process_goto(ast, current_node, goto_count)
                elif operation_name == "@shell":
                    current_node = process_shell(ast, current_node)
                elif operation_name == "@return":
                    return_result = process_return(ast, current_node)
                    if return_result:
                        ctx_filename = Path(local_file_name).with_suffix('.ctx')
                        output_file = os.path.join(file_dir, ctx_filename)
                        relative_ctx_path = get_relative_path(base_dir, output_file)
                        
                        render_ast_to_markdown(ast, output_file)

                        #print(f"[DEBUG runner.py] Committing return operation files")
                        ctx_commit_hash = commit_changes(
                            base_dir,
                            "@return operation",
                            [local_file_name, ctx_filename],  # Use local names
                            p_parent_filename,
                            p_parent_operation
                        )
                        console.print(f"[light_green]✓[/light_green] git. context commited: [light_green]{ctx_filename}[/light_green]")

                        new_node.ctx_file = relative_ctx_path
                        new_node.ctx_commit_hash = ctx_commit_hash

                        # RESTORING LOGIC
                        # this operation was commented out
                        return return_result, new_node, relative_ctx_path, ctx_commit_hash, branch_name
                    break  # Exit processing on return
                else:
                    raise UnknownOperationError(f"Unknown operation: {operation_name}")
            else:
                current_node = current_node.next

        ctx_filename = Path(local_file_name).with_suffix('.ctx')
        output_file = os.path.join(file_dir, ctx_filename)
        relative_ctx_path = os.path.relpath(output_file, base_dir)
        
        # Assuming render_ast_to_markdown is a function to render AST to markdown
        render_ast_to_markdown(ast, output_file)

        ctx_commit_hash = commit_changes(
            base_dir,
            "Final processed files",
            [local_file_name, ctx_filename],
            p_parent_filename,
            p_parent_operation
        )
        console.print(f"[light_green]✓[/light_green] git. main context commited: [light_green]{ctx_filename}[/light_green]")

        new_node.ctx_file = relative_ctx_path
        new_node.ctx_commit_hash = ctx_commit_hash

        return ast, new_node, relative_ctx_path, ctx_commit_hash, branch_name

    finally:
        os.chdir(original_cwd)

def process_run(ast: AST, current_node: Node, local_file_name, parent_operation, call_tree_node,
                committed_files=None, file_commit_hashes=None, base_dir=None) -> Optional[Tuple[Node, CallTreeNode, str, str]]:
    params = current_node.params
    if not params:
        raise ValueError("No parameters found for @run operation.")

    # Source file parameters
    src_params = params.get('file', {})
    src_file_path = src_params.get('path', '')
    src_file_name = src_params.get('file', '')

    # Action and operation type
    action = params.get('mode', Config.DEFAULT_OPERATION) 
    operation_type = OperationType(action)

    # Target parameters
    target_params = params.get('to', {})
    target_block_id = target_params.get('block_uri', '')
    target_nested = target_params.get('nested_flag', False)

    # Handle prompt or block parameter
    prompt = params.get('prompt')
    block_params = params.get('block', {})
    block_uri = block_params.get('block_uri', '')
    nested_flag = block_params.get('nested_flag', False)
    use_header = params.get('use-header')

    # Validate prompt and block are not both specified
    # if prompt and block_uri:
    #     raise ValueError("Cannot specify both 'prompt' and 'block' parameters")
    
    # Create an empty input AST that will hold all input blocks
    input_ast = None
    
    # Handle blocks first (can be single block or array)
    if block_params:
        try:
            if block_params.get('is_multi'):
                # Handle array of blocks
                blocks = block_params.get('blocks', [])
                for block_info in blocks:
                    block_uri = block_info.get('block_uri')
                    nested_flag = block_info.get('nested_flag', False)
                    
                    block_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
                    if not block_ast.parser.nodes:
                        raise BlockNotFoundError(f"Block with path '{block_uri}' is empty.")
                        
                    if input_ast:
                        # Stack blocks by appending
                        perform_ast_operation(
                            src_ast=block_ast,
                            src_path='',
                            src_hierarchy=False,
                            dest_ast=input_ast,
                            dest_path=input_ast.parser.tail.key,
                            dest_hierarchy=False,
                            operation=OperationType.APPEND
                        )
                    else:
                        # First block becomes base AST
                        input_ast = block_ast
            else:
                # Handle single block (existing logic)
                block_uri = block_params.get('block_uri')
                nested_flag = block_params.get('nested_flag', False)
                block_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
                if not block_ast.parser.nodes:
                    raise BlockNotFoundError(f"Block with path '{block_uri}' is empty.")
                input_ast = block_ast
                
        except BlockNotFoundError as e:
            raise BlockNotFoundError(f"Error processing blocks: {str(e)}")
    
    # Handle prompt if specified (append to blocks if present)
    if prompt:
        header = ""
        if use_header is not None:
            if use_header.lower() != "none":
                header = f"{use_header}\n"
        else:
            header = "# Input Parameters {id=input-parameters}\n"
            
        parameter_value = f"{header}{prompt}"
        param_node = Node(
            type=NodeType.HEADING,
            name="Input Parameters",
            level=1,
            content=parameter_value,
            id="InputParameters",
            key=str(uuid.uuid4())[:8]
        )
        
        # Create prompt AST
        prompt_ast = AST("")
        prompt_ast.parser.nodes = {param_node.key: param_node}
        prompt_ast.parser.head = param_node
        prompt_ast.parser.tail = param_node
        
        if input_ast:
            # Append prompt to existing blocks
            perform_ast_operation(
                src_ast=prompt_ast,
                src_path='',
                src_hierarchy=False,
                dest_ast=input_ast,
                dest_path=input_ast.parser.tail.key,
                dest_hierarchy=False,
                operation=OperationType.APPEND
            )
        else:
            # No blocks, use prompt as input
            input_ast = prompt_ast

    # Handle file execution
    current_dir = os.path.dirname(os.path.abspath(local_file_name))
    source_path = os.path.abspath(os.path.join(current_dir, src_file_path, src_file_name))

    if not os.path.exists(source_path):
        raise ValueError(f"Source file not found: {source_path}")

    # Create parameter node if we have content
    param_node = None
    if parameter_value:
        param_node = Node(
            type=NodeType.HEADING,
            name="Input Parameters",
            level=1,
            content=parameter_value,
            id="InputParameters",
            key=str(uuid.uuid4())[:8]
        )

    # Execute run
    if input_ast and input_ast.parser.nodes:
        run_result, child_call_tree_node, ctx_file, ctx_file_hash, branch_name = run(
            source_path,
            input_ast,  # Pass the complete input AST
            False,
            local_file_name,
            parent_operation,
            call_tree_node,
            committed_files=committed_files,
            file_commit_hashes=file_commit_hashes,
            base_dir=base_dir
        )
    else:
        run_result, child_call_tree_node, ctx_file, ctx_file_hash, branch_name = run(
            source_path,
            None,
            False,
            local_file_name,
            parent_operation,
            call_tree_node,
            committed_files=committed_files,
            file_commit_hashes=file_commit_hashes,
            base_dir=base_dir
        )

    # Handle results insertion
    if target_block_id:
        perform_ast_operation(
            run_result,
            run_result.first().key,
            True,
            ast,
            target_block_id,
            target_nested,
            operation_type,
            False
        )
    else:
        perform_ast_operation(
            run_result,
            run_result.first().key,
            True,
            ast,
            current_node.key,
            False,
            operation_type,
            False
        )

    return current_node.next, child_call_tree_node, ctx_file, ctx_file_hash