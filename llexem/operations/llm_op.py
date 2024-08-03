# LLM Operation
# - process_llm

from typing import Optional

from llexem.ast_md.node import Node, OperationType
from llexem.llm.llm_client import llm_call
from llexem.llm.prepare_llm_prompt import prepare_llm_prompt
from llexem.ast_md.ast import AST, perform_ast_operation
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError
from llexem.config import Config

def process_llm(ast: AST, current_node: Node) -> Optional[Node]:
    # Parse the operation
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()

    # Prepare the LLM prompt
    # TODO: need to add here an option not to extract only previous nodes 
    # but to get nodes content using node adress considering hierarchy
    # TODO: it would be cool to add here (maybe) an option to pass a .ctx file for example, to perform analysis of the problem
    # this would be helpful for creation of agent-investegator over execution results
    prompt_text = prepare_llm_prompt(ast, current_node)

    # Call the LLM
    resp = llm_call(prompt_text)
    print(f'[!!! DEBUG, LLM Response]:{resp}')

    if op.parameter.new_block_header is not None:
        header = op.parameter.new_block_header
    else:
        header = "# AI response block::"

    response_ast = AST(f"{header}\n{resp}\n")

    # Determine the operation type
    operation_type = OperationType(op.operand) if op.operand else Config.DEFAULT_OPERATION

    # Determine the target node
    target_node = current_node
    if op.target.block_id:
        target_node = ast.get_node(id=op.target.block_id) or current_node

    # Perform the AST operation
    perform_ast_operation(
        src_ast=response_ast,
        src_path="",  # We're using the entire response AST
        src_hierarchy=False,
        dest_ast=ast,
        dest_path=target_node.key,
        dest_hierarchy=op.target.nested_flag,
        operation=operation_type
    )

    # Return pointer to the next node
    return current_node.next