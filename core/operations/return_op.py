from typing import Optional
from core.ast_md.ast import AST, get_ast_part_by_path, perform_ast_operation, OperationType
from core.ast_md.node import Node, NodeType
from core.errors import BlockNotFoundError
from rich.console import Console

def process_return(ast: AST, current_node: Node) -> Optional[AST]:
    """Process @return operation with updated schema"""
    console = Console(force_terminal=True, color_system="auto")
    params = current_node.params
    if not params:
        raise ValueError("No parameters found for @return operation.")

    # Create an empty AST to hold all blocks
    return_ast = None

    # Get prompt and block parameters
    prompt = params.get('prompt')
    block_params = params.get('block', {})
    use_header = params.get('use-header')

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
                        
                    if return_ast:
                        # Stack blocks by appending
                        perform_ast_operation(
                            src_ast=block_ast,
                            src_path='',
                            src_hierarchy=False,
                            dest_ast=return_ast,
                            dest_path=return_ast.parser.tail.key,
                            dest_hierarchy=False,
                            operation=OperationType.APPEND
                        )
                    else:
                        # First block becomes base AST
                        return_ast = block_ast
            else:
                # Handle single block
                block_uri = block_params.get('block_uri')
                nested_flag = block_params.get('nested_flag', False)
                block_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
                if not block_ast.parser.nodes:
                    raise BlockNotFoundError(f"Block with path '{block_uri}' is empty.")
                return_ast = block_ast
                
        except BlockNotFoundError:
            raise BlockNotFoundError(f"Block not found in @return operation")

    # Handle prompt if specified (append to blocks if present)
    if prompt:
        header = ""
        if use_header is not None:
            if use_header.lower() != "none":
                header = f"{use_header}\n"
        else:
            header = "# Return block\n"
            
        # Create prompt AST
        prompt_ast = AST(f"{header}{prompt}\n")
        
        if return_ast:
            # Append prompt to existing blocks
            perform_ast_operation(
                src_ast=prompt_ast,
                src_path='',
                src_hierarchy=False,
                dest_ast=return_ast,
                dest_path=return_ast.parser.tail.key,
                dest_hierarchy=False,
                operation=OperationType.APPEND
            )
        else:
            # No blocks, use prompt as return AST
            return_ast = prompt_ast

    if not return_ast:
        raise ValueError("Either 'prompt' or 'block' parameter must be specified for @return operation")

    console.print("[light_green]→[/light_green] @return ")
    return return_ast
