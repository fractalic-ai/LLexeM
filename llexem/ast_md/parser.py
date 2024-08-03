# Parser
# - Parser
# - print_parsed_structure

from ast import AST
import re
from typing import Dict, Optional, Union
from llexem.ast_md.node import Node, NodeType
from llexem.ast_md.operation_parser import OperationParser


class Parser:
    #HEADING_PATTERN = re.compile(r'^(#+)\s+(.+?)(?:\s+\{id=([^}]+)\})?$')
    
    #bad: HEADING_PATTERN = re.compile(r'^(#+)\s+(.+?)\s*\{id=([^}]+)\}\s*$')
    HEADING_PATTERN = re.compile(r'^(#+)\s+(.+?)(?:\s+\{id=([^}\s]+)\}\s*)?$')

    OPERATION_PATTERN = re.compile(r'^@(\S+)\s+(\S+)(?:\s*(=>|\+>|\.>)\s*(\S+))?$')

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None

    def parse(self, text: str) -> Dict[str, Node]:
        lines = text.split('\n')
        base_indent = len(lines[0]) - len(lines[0].lstrip())

        for line in lines:
            self.process_line(line, base_indent)

        return self.nodes

    def process_line(self, line: str, base_indent: int) -> None:
        stripped_line = line.lstrip()
        indent = len(line) - len(stripped_line)
        relative_indent = max(0, indent - base_indent)

        if not stripped_line:
            if self.tail:
                self.tail.content += line + '\n'
            return

        heading_match = self.HEADING_PATTERN.match(stripped_line)
        operation_match = self.OPERATION_PATTERN.match(stripped_line)

        if heading_match:
            self.handle_heading(heading_match, line, relative_indent)
        elif operation_match or stripped_line.startswith('@'):
            self.handle_operation(stripped_line, line, relative_indent)
        else:
            self.handle_content(line)

    def handle_heading(self, match: re.Match, line: str, indent: int) -> None:
        level = len(match.group(1))
        name = match.group(2)
        id = match.group(3)

        new_node = Node(
            type=NodeType.HEADING,
            name=name,
            level=level,
            id=id,
            indent=indent,
            content=line + '\n'
        )
        self.add_node(new_node)

    def handle_operation(self, operation_string: str, line: str, indent: int) -> None:
        parser = OperationParser(operation_string)
        op = parser.parse()

        new_node = Node(
            type=NodeType.OPERATION,
            name=op.operation,
            level=(indent // 4) + 1,
            indent=indent,
            content=line + '\n',
            source_path=op.src.file_path,
            source_block_id=op.src.block_id,
            target_path=op.target.file_path,
            target_block_id=op.target.block_id
        )

        self.add_node(new_node)

    def handle_content(self, line: str) -> None:
        if self.tail:
            self.tail.content += line + '\n'
        else:
            raise ValueError(f"Content without a parent node: {line}")

    def add_node(self, node: Node) -> None:
        self.nodes[node.key] = node
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node

    def get_node_by_id(self, id: str) -> Optional[Node]:
        return next((node for node in self.nodes.values() if node.id == id), None)

    def replace_node(self, target_key: str, new_node: Node):
        target_node = self.nodes.get(target_key)
        if not target_node:
            raise KeyError(f"Node with key '{target_key}' not found.")

        if target_node.prev:
            target_node.prev.next = new_node
            new_node.prev = target_node.prev
        else:
            self.head = new_node

        if target_node.next:
            target_node.next.prev = new_node
            new_node.next = target_node.next
        else:
            self.tail = new_node

        del self.nodes[target_key]
        self.nodes[new_node.key] = new_node

    def replace_node_with_ast(self, target_key: str, new_ast: Dict[str, Node]):
        old_node = self.nodes.get(target_key)
        if not old_node:
            raise KeyError(f"Node with key '{target_key}' not found.")

        new_nodes = list(new_ast.values())
        first_new_node = new_nodes[0]
        last_new_node = new_nodes[-1]

        if old_node.prev:
            old_node.prev.next = first_new_node
            first_new_node.prev = old_node.prev
        else:
            self.head = first_new_node

        if old_node.next:
            old_node.next.prev = last_new_node
            last_new_node.next = old_node.next
        else:
            self.tail = last_new_node

        del self.nodes[target_key]
        self.nodes.update({node.key: node for node in new_nodes})

    def prepend_node_with_ast(self, target_key: str, new_ast: Dict[str, Node]):
        target_node = self.nodes.get(target_key)
        if not target_node:
            raise KeyError(f"Node with key '{target_key}' not found.")

        new_nodes = list(new_ast.values())
        first_new_node = new_nodes[0]
        last_new_node = new_nodes[-1]

        if target_node.prev:
            target_node.prev.next = first_new_node
            first_new_node.prev = target_node.prev
        else:
            self.head = first_new_node

        target_node.prev = last_new_node
        last_new_node.next = target_node

        self.nodes.update({node.key: node for node in new_nodes})

    def append_node_with_ast(self, target_key: str, new_ast: Dict[str, Node]):
        target_node = self.nodes.get(target_key)
        if not target_node:
            raise KeyError(f"Node with key '{target_key}' not found.")

        new_nodes = list(new_ast.values())
        first_new_node = new_nodes[0]
        last_new_node = new_nodes[-1]

        if target_node.next:
            target_node.next.prev = last_new_node
            last_new_node.next = target_node.next
        else:
            self.tail = last_new_node

        target_node.next = first_new_node
        first_new_node.prev = target_node

        self.nodes.update({node.key: node for node in new_nodes})

def get_preceding_node(nodes: Dict[str, Node], head_node: Node) -> Optional[Node]:
    return head_node.prev

def get_following_node(nodes: Dict[str, Node], tail_node: Node) -> Optional[Node]:
    return tail_node.next

def remove_nodes_by_keys(parser: Parser, keys: list[str]) -> None:
    for key in keys:
        del parser.nodes[key]

def connect_nodes(preceding_node: Optional[Node], new_head: Node, new_tail: Node, following_node: Optional[Node]) -> None:
    if preceding_node:
        preceding_node.next = new_head
        new_head.prev = preceding_node
    if following_node:
        new_tail.next = following_node
        following_node.prev = new_tail

def get_head(ast_or_nodes: Union[AST, Dict[str, Node]]) -> Optional[Node]:
    if isinstance(ast_or_nodes, AST):
        return ast_or_nodes.parser.head
    elif isinstance(ast_or_nodes, dict):
        return next(iter(ast_or_nodes.values())) if ast_or_nodes else None
    else:
        raise TypeError("Expected AST or dict of nodes")

def get_tail(ast_or_nodes: Union[AST, Dict[str, Node]]) -> Optional[Node]:
    if isinstance(ast_or_nodes, AST):
        return ast_or_nodes.parser.tail
    elif isinstance(ast_or_nodes, dict):
        return list(ast_or_nodes.values())[-1] if ast_or_nodes else None
    else:
        raise TypeError("Expected AST or dict of nodes")

def print_node(node: Node, level: int) -> None:
    indent = "  " * level
    print(f"{indent}{'='*40} Node {'='*40}")
    print(f"{indent}[{node.hash}] {node.type.value.upper()}: {node.name} (Level: {node.level})")
    print(f"{indent}Key: {node.key}")
    print(f"{indent}ID: {node.id}")
    print(f"{indent}Level: {node.level}")

    if node.type == NodeType.OPERATION:
        print(f"{indent}Source Path: {node.source_path}")
        print(f"{indent}Source Block ID: {node.source_block_id}")
        print(f"{indent}Target Path: {node.target_path}")
        print(f"{indent}Target Block ID: {node.target_block_id}")

    print(f"{indent}Content:")
    for line in node.content.strip().split('\n'):
        print(f"{indent}{line}")

def print_ast_as_doubly_linked_list(ast: AST):
    current = ast.first()
    while current:
        prev_key = current.prev.key if current.prev else "    None"
        next_key = current.next.key if current.next else "None    "
        node_name_preview = current.content.strip()[:50].replace('\n', ' ')
        print(f"[{prev_key}] <- [id:{current.id}]({current.key}) {node_name_preview} -> [{next_key}]")
        current = current.next

def print_parsed_structure(ast: AST) -> None:
    current = ast.first()
    while current:
        print_node(current, 0)
        current = current.next