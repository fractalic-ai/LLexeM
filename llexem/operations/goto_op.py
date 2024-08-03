# Goto Operation
# - process_goto

from typing import Optional
from llexem.ast_md.node import NodeType, Node
from llexem.ast_md.ast import AST
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError
from llexem.config import GOTO_LIMIT

def process_goto(ast: AST, current_node: Node, goto_count: dict) -> Optional[Node]:
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()

    # Extract the target block path from the operation
    target_block_path = op.src.block_full_path

    print(f"Debug: Processing @goto operation. Target block path: {target_block_path}")

    if not target_block_path:
        raise ValueError(f"Source block path not found in the @goto operation: {current_node.content}")

    # Iterate through nodes to find the target node by ID or key
    target_node = None
    for node in ast.parser.nodes.values():
        if node.id == target_block_path or node.key == target_block_path:
            target_node = node
            break

    if target_node is None:
        print(f"Error: Block with path '{target_block_path}' not found.")
        raise BlockNotFoundError(f"Error: Block with path '{target_block_path}' not found.")

        # Use the block node's key to track goto count
    target_key = target_node.key
    if target_key in goto_count:
        goto_count[target_key] += 1
    else:
        goto_count[target_key] = 1

    if goto_count[target_key] > GOTO_LIMIT:
        raise RuntimeError(f"@goto operation limit exceeded for block '{target_block_path}'")



    print(f"Debug: Returning target node with key '{target_node.key}' and content: {target_node.content.strip()}")
    return target_node