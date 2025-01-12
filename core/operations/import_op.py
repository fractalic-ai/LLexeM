# import_op.py

import os
from typing import Optional
from core.config import Config
from core.utils import parse_file
from core.ast_md.node import Node, OperationType
from core.ast_md.ast import AST, perform_ast_operation
from core.errors import BlockNotFoundError, FileNotFoundError

def process_import(ast: AST, current_node: Node) -> Optional[Node]:
    # Extract parameters from current_node.params
    src_params = current_node.params.get('file', {})
    src_file_path = src_params.get('path', '')
    src_file_name = src_params.get('file', '')

    block_params = current_node.params.get('block', {})
    source_block_uri = block_params.get('block_uri', '')
    source_nested = block_params.get('nested_flag', False)

    #print(f"[DEBUG] Processing import node {current_node.key} from: {src_file_path}/{src_file_name}")
 

# Validate required parameters
    if not src_params:
        raise ValueError("Source file name is required for @import operation")


    mode = current_node.params.get('mode', Config.DEFAULT_OPERATION)
    operation_type = OperationType(mode)

    to_params = current_node.params.get('to', {})
    target_block_uri = to_params.get('block_uri', '')
    target_nested = to_params.get('nested_flag', False)


    # Get the full source file path
    full_source_path = os.path.join(src_file_path, src_file_name)



    if not os.path.exists(full_source_path):
        raise FileNotFoundError(f"Source file not found: {full_source_path}")

    # Read the source file
    source_ast = parse_file(full_source_path)

    # If source block URI is provided, get the AST part from source_ast
    if source_block_uri:
        try:
            source_ast = source_ast.get_part_by_path(source_block_uri, source_nested)
        except BlockNotFoundError:
            raise BlockNotFoundError(f"Block with URI '{source_block_uri}' not found in source file.")

    # Determine the target node using get_node_by_path
    if target_block_uri:
        try:
            target_node = ast.get_node_by_path(target_block_uri)
        except BlockNotFoundError:
            raise BlockNotFoundError(f"Target block with URI '{target_block_uri}' not found.")
    else:
        target_node = current_node

    # Perform the AST operation
    perform_ast_operation(
        src_ast=source_ast,
        src_path='',  # We're using the entire source_ast
        src_hierarchy=source_nested,
        dest_ast=ast,
        dest_path=target_node.key,
        dest_hierarchy=target_nested,
        operation=operation_type
    )

    # Return pointer to the next node
    return current_node.next