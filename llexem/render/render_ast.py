# Render AST
# - render_ast_to_markdown

import os
from llexem.ast_md.ast import AST

# it soesnt grab header while using content

def render_ast_to_markdown(ast: AST, output_file: str = "out.ctx") -> None:
    with open(output_file, 'w') as f:
        current = ast.first()
        while current:
            f.write(''.join(f"{line}\n" for line in current.content.splitlines())+"\n")
            current = current.next

