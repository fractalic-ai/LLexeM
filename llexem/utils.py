# Utilities
# - read_file
# - change_working_directory
# - print_ast_nodes
# - get_content_without_header
# - execute_shell_command

import os
import subprocess
import locale
from contextlib import contextmanager

from llexem.ast_md.node import NodeType, Node
from llexem.ast_md.ast import AST

def parse_file(filename: str) -> AST:
    content = read_file(filename)
    return AST(content)

@contextmanager
def change_working_directory(new_path):
    """
    Temporarily change the working directory.
    
    :param new_path: Path to the new working directory
    """
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)

def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Error reading file '{file_path}': {e}")



def print_ast_nodes(ast: AST) -> None:
    current_node = ast.get_first_node()
    if current_node is None:
        print("[Debug: print_ast_nodes] AST is empty.")
        return

    while current_node is not None:
        print(f"Key: {current_node.key}, ID: {current_node.id}, Content: {current_node.content.strip()}")
        current_node = current_node.next

    
def get_content_without_header(node: Node) -> str:
    content_lines = node.content.split('\n')
    if node.type == NodeType.HEADING and content_lines:
        content_lines = content_lines[1:]
    content_without_header = '\n'.join(content_lines)
    return content_without_header.strip()


import toml



def load_settings(settings_file='settings.toml'):
    """Load settings from TOML file with proper error handling."""
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for settings file at: {settings_file}")
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return toml.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Settings file {settings_file} not found. Using defaults.")
        return {}
    except toml.TomlDecodeError as e:
        print(f"[ERROR] Error parsing {settings_file}: {e}")
        return {}