# Return Operation
# - process_return

from typing import Optional

from llexem.ast_md.parser import print_ast_as_doubly_linked_list, print_parsed_structure
from llexem.ast_md.node import Node
from llexem.ast_md.ast import AST, get_ast_part_by_path
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError

def process_return(ast: AST, current_node: Node) -> Optional[AST]:
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()
    print(f"Debug: Parsed operation: {op}")
    print(f"Debug: op.src.block_full_path: {op.src.block_full_path}")
    print(f"Debug: op.src.block_id: {op.src.block_id}")

    if op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LITERAL:
        # Handle string literal return
        literal_content = op.parameter.value
        return_ast = AST(f"# Return content\n{literal_content}\n")
        return return_ast

    if op.src.block_full_path: # it should works no matter if path or single block is specified
        # Handle block path return (including nested blocks)
        try:
            return_ast = get_ast_part_by_path(ast, op.src.block_full_path, op.src.nested_flag)
            if return_ast.parser.nodes:
                return return_ast
            else:
                print(f"Block with path '{op.src.block_full_path}' is empty.")
                return None
        except BlockNotFoundError:
            print("AST structure before raising BlockNotFoundError:")
            print_ast_as_doubly_linked_list(ast)
            print_parsed_structure(ast)
            raise BlockNotFoundError(f"Block with path '{op.src.block_full_path}' not found.")
    return None