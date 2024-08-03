# Runner Module
# Consolidated functionality

import os
import uuid
from typing import Optional, Union
from pathlib import Path

from llexem.ast_md.node import Node, NodeType, OperationType
from llexem.utils import parse_file
from llexem.utils import read_file, change_working_directory, get_content_without_header
from llexem.ast_md.ast import AST, get_ast_part_by_id, perform_ast_operation, get_ast_part_by_path
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError, UnknownOperationError
from llexem.config import Config
from llexem.render.render_ast import render_ast_to_markdown
from llexem.operations.import_op import process_import
from llexem.operations.llm_op import process_llm
from llexem.operations.goto_op import process_goto
from llexem.operations.shell_op import process_shell
from llexem.operations.return_op import process_return
from llexem.git import *


def run(filename: str, param_node: Optional[Union[Node, AST]] = None) -> AST:
    abs_path = os.path.abspath(filename)
    file_dir = os.path.dirname(abs_path)
    local_file_name = os.path.basename(abs_path)
    repo_path = '.' #file_dir
    

    # Initialize goto_count within the run function
    goto_count = {}
    
    # Change to the directory of the file and perform operations
    with change_working_directory(file_dir):

        init_git_repo(".")
        branch_name = create_session_branch(".", "Testing-git-operations")

        ast = parse_file(local_file_name)

        if param_node:
            if isinstance(param_node, AST):
                # Prepend the parameter AST to the beginning of the main AST
                ast.prepend_node_with_ast(ast.first().key, param_node)
                print(f"Inserted parameter AST with nodes: {[node.key for node in param_node.parser.nodes.values()]}")
            else:
                # Create a decorator node as it was done previously
                decorated_param_node = Node(
                    type=NodeType.HEADING,
                    name="Input parameters block",
                    level=1,
                    content=f"# This is an input parameter you've received. {{id=InputParameters}} \n{get_content_without_header(param_node)}",
                    id="InputParameters",
                    key=str(uuid.uuid4())[:8]  # Generate a new key for this node
                )
                
                # Create a new AST with just the parameter node
                param_ast = AST("")
                param_ast.parser.nodes = {decorated_param_node.key: decorated_param_node}
                param_ast.parser.head = decorated_param_node
                param_ast.parser.tail = decorated_param_node
                
                # Prepend the parameter node to the beginning of the main AST
                ast.prepend_node_with_ast(ast.first().key, param_ast)
                
                print(f"Inserted parameter node: {decorated_param_node.key} with content: {decorated_param_node.content}")
        else:
            print("No parameter node provided")

        current_node = ast.first()

        while current_node:
            print(f"Processing node: {current_node.key} with content: {current_node.content.strip()}")

            if current_node.type == NodeType.OPERATION:
                parser = OperationParser(current_node.content.strip())
                op = parser.parse()
                
                operation_name = op.operation
                if operation_name == "@import":
                    current_node = process_import(ast, current_node)
                elif operation_name == "@run":
                    current_node = process_run(ast, current_node)
                elif operation_name == "@llm":
                    current_node = process_llm(ast, current_node)
                elif operation_name == "@goto":
                    current_node = process_goto(ast, current_node, goto_count)
                elif operation_name == "@shell":
                    current_node = process_shell(ast, current_node)
                elif operation_name == "@return":
                    return_result = process_return(ast, current_node)
                    if return_result:
                        output_file = Path(local_file_name).with_suffix('.ctx')
                        render_ast_to_markdown(ast, output_file)

                        commit_changes(repo_path, "@return operation", "empty-parent.file", op.operation)

                        print(f"[RETURN END] AST rendered to Markdown file: {output_file}")
                        return return_result  # Return the resulting node instead of an empty AST                
                else:
                    raise UnknownOperationError(f"Unknown operation: {operation_name}")
            else:
                current_node = current_node.next

        output_file = Path(local_file_name).with_suffix('.ctx')
        render_ast_to_markdown(ast, output_file)

        commit_changes(repo_path, f"Execution done of: {output_file}", "empty-parent.file", None)


        print(f"[RUN END] AST rendered to Markdown file: {output_file}")
        return ast
    
def process_run(ast: AST, current_node: Node) -> Optional[Node]:
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()

    # Combine file path and filename
    source_path = os.path.join(op.src.file_path, op.src.filename)
    if not source_path:
        raise ValueError(f"Source path not found in the @run operation: {current_node.content}")

    # Handle different parameter types
    if op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LITERAL:
        param_node = Node(
            type=NodeType.HEADING,
            name="Input parameters block",
            level=1,
            content=f"# This is an input parameter you've received. {{id=InputParameters}} \n{op.parameter.value}"
        )
    elif op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LINK:
        # Handle block path or ID
        try:
            param_ast = get_ast_part_by_path(ast, op.parameter.value.block_full_path, op.parameter.value.nested_flag)
            ''' 
            if param_ast.parser.nodes:
                param_node = next(iter(param_ast.parser.nodes.values()))
            else:
                param_node = None
            '''  

            
            param_node = param_ast 
            
        except BlockNotFoundError:
            print(f"Warning: Block with path '{op.parameter.value.block_full_path}' not found. Running without parameters.")
            param_node = None
    else:
        param_node = None

    run_result = run(source_path, param_node)  # This is an AST

    # Determine the operation type
    operation_type = OperationType(op.operand) if op.operand else Config.DEFAULT_OPERATION

    if op.target.block_id:
        target_ast = get_ast_part_by_id(ast, op.target.block_id, op.target.nested_flag)
        if not target_ast.parser.nodes:
            raise BlockNotFoundError(f"process_run: Target block with id '{op.target.block_id}' not found.")
        
        # Perform the operation directly on the ASTs
        # TODO: !!! as for now i ve setted src nest flag to true, because we should be agnostic to recieved structure
        perform_ast_operation(run_result, run_result.first().key, True, 
                              ast, op.target.block_id, op.target.nested_flag, operation_type, False)
    else:
        # note, that here we call with blockpath equal to key.
        # TODO: !its bad, we should split params in perform_ast_operation to handle various inputs as params
        perform_ast_operation(run_result, run_result.first().key, True,
                              ast, current_node.key, False, operation_type, False)

    return current_node.next