# Render AST
# - render_ast_to_markdown

import os
from llexem.ast_md.ast import AST

def render_ast_to_markdown(ast: AST, output_file: str = "out.md") -> None:
    with open(output_file, 'w') as f:
        current = ast.first()
        while current:
            indent = ' ' * (current.indent + current.level * 2)
            f.write(''.join(f"{indent}{line}\n" for line in current.content.splitlines()))
            current = current.next

