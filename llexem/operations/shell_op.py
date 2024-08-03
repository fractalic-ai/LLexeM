# Shell Operation
# - process_shell
#
import locale
import subprocess
from typing import Optional
from llexem.ast_md.node import Node, NodeType, OperationType
from llexem.ast_md.ast import AST, perform_ast_operation
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError
from llexem.config import Config




def prepare_shell_prompt(ast: AST, current_node: Node) -> str:
    def heading_contents_before_current(node):
        while node and node != current_node:
            if node.type == NodeType.HEADING:
                yield node.content
            node = node.next

    content_before_current = "".join(heading_contents_before_current(ast.first()))

    parser = OperationParser(current_node.content.strip())
    op = parser.parse()
    param_content = op.parameter.value if op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LITERAL else ""

    prompt_text = param_content
    return prompt_text

def process_shell(ast: AST, current_node: Node) -> Optional[Node]:
    # Parse the operation
    parser = OperationParser(current_node.content.strip())
    op = parser.parse()

    # Prepare the shell command
    prompt_text = prepare_shell_prompt(ast, current_node)

    # Execute the shell command
    resp = execute_shell_command(prompt_text)

    # Create a new AST from the shell command response using recieved header or using default one

    if op.parameter.new_block_header is not None:
        header = op.parameter.new_block_header
    else:
        header = "# OS Shell Tool response block:"

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



def execute_shell_command(prompt):
    try:
        default_encoding = locale.getpreferredencoding()

        result = subprocess.run(prompt, shell=True, capture_output=True, text=True, encoding=default_encoding)
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        return str(e)

