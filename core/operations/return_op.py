from typing import Optional
from core.ast_md.ast import AST, get_ast_part_by_path
from core.ast_md.node import Node, NodeType
from core.errors import BlockNotFoundError

def process_return(ast: AST, current_node: Node) -> Optional[AST]:
    """Process @return operation with updated schema"""
    params = current_node.params
    if not params:
        raise ValueError("No parameters found for @return operation.")

    # Get prompt and block parameters
    prompt = params.get('prompt')
    block_params = params.get('block', {})
    block_uri = block_params.get('block_uri', '')
    nested_flag = block_params.get('nested_flag', False)
    use_header = params.get('use-header')

    # Validate parameters
    if prompt and block_uri:
        raise ValueError("Cannot specify both 'prompt' and 'block' parameters")
    if not prompt and not block_uri:
        raise ValueError("Either 'prompt' or 'block' parameter must be specified")

    # Handle prompt-based return
    if prompt:
        header = ""
        if use_header is not None:
            if use_header.lower() != "none":
                header = f"{use_header}\n"
        else:
            header = "# Return block\n"
        return_ast = AST(f"{header}{prompt}\n")
        return return_ast

    # Handle block-based return
    try:
        return_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
        if not return_ast.parser.nodes:
            raise ValueError(f"Block with path '{block_uri}' is empty.")

        # Only modify header if use-header is specified for block return
        if use_header:
            header_node = Node(
                type=NodeType.HEADING,
                name=use_header.lstrip('#').strip(),
                level=use_header.count('#'),
                content=use_header,
                id=None,  # Let AST generate ID
                key=None  # Let AST generate key
            )
            
            # Update nodes with new header
            updated_nodes = {header_node.key: header_node}
            updated_nodes.update(return_ast.parser.nodes)
            return_ast.parser.nodes = updated_nodes
            return_ast.parser.head = header_node

        return return_ast

    except BlockNotFoundError:
        raise ValueError(f"Block with path '{block_uri}' not found.")
