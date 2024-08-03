# Prepare LLM Prompt
# - prepare_llm_prompt

from llexem.ast_md.node import NodeType, Node
from llexem.ast_md.ast import AST, get_ast_part_by_path
from llexem.ast_md.operation_parser import OperationParser
from llexem.errors import BlockNotFoundError

def prepare_llm_prompt(ast: AST, current_node: Node) -> str:
    def heading_contents_before_current(node):
        while node and node != current_node:
            if node.type == NodeType.HEADING:
                yield node.content
            node = node.next

    # Collect previous nodes' content and headings relative to the current one
    content_before_current = "".join(heading_contents_before_current(ast.first()))

    parser = OperationParser(current_node.content.strip())
    op = parser.parse()
    
    if op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LITERAL:
        param_content = op.parameter.value
        prompt_text = content_before_current + "\n" + param_content
    elif op.parameter.param_type == OperationParser.ParamType.PARAM_TYPE_LINK:
        try:
            param_ast = get_ast_part_by_path(ast, op.parameter.value.block_full_path, op.parameter.value.nested_flag)
            param_content = "".join(node.content for node in param_ast.parser.nodes.values())
            prompt_text = param_content
        except BlockNotFoundError:
            raise BlockNotFoundError(f"Block with path '{op.parameter.value.block_full_path}' not found.")
            
    else:
        raise ValueError("ERROR in [prepare_llm_prompt]: Unrecognized parameter type in @llm operation.")

    return prompt_text