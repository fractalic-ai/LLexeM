# Import Operation
# - process_import

import os
from typing import Optional
from llexem.config import Config
from llexem.utils import parse_file
from llexem.ast_md.node import NodeType, Node, OperationType
from llexem.utils import read_file
from llexem.ast_md.ast import AST, get_ast_part_by_path, perform_ast_operation
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError

def process_import(ast: AST, current_node: Node) -> Optional[Node]:
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()

    # 1. & 2. Explicitly use source from op
    full_source_path = os.path.join(op.src.file_path, op.src.filename)
    
    # 3. Read file to src_ast
    src_ast = parse_file(full_source_path)
    
    # 4. If source block path is present, get ast part from src_ast
    if op.src.block_full_path:
        source_ast = get_ast_part_by_path(src_ast, op.src.block_full_path, op.src.nested_flag)
    else:
        source_ast = src_ast

    # 5. Perform call to ast_perform_operation, get the returned pointer
    operation_type = OperationType(op.operand) if op.operand else Config.DEFAULT_OPERATION
    target_node = current_node
    if op.target.block_id:
        target_node = ast.get_node(id=op.target.block_id) or current_node

    perform_ast_operation(
        src_ast=source_ast,
        src_path="",  # We've already extracted the correct part of the source AST
        src_hierarchy=False,
        dest_ast=ast,
        dest_path=target_node.key,
        dest_hierarchy=op.target.nested_flag,
        operation=operation_type
    )

    # 6. Return pointer to the next node
    return current_node.next