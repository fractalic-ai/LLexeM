# AST
# - AST
# - nodes_to_ast
# - perform_ast_operation
# - get_ast_part_by_path
# - get_ast_part_by_id
# - get_ast_part_by_id_or_key
# - _get_ast_part

import copy
from typing import Dict, Optional
from core.ast_md.parser import Parser, get_head, get_tail
from core.ast_md.node import Node, NodeType, OperationType
from core.errors import BlockNotFoundError

class AST:
    def __init__(self, content: str):
        self.parser = Parser()
        self.parser.parse(content)

    def first(self) -> Optional[Node]:
        return self.parser.head

    def last(self) -> Optional[Node]:
        return self.parser.tail

    def get_node(self, **kwargs) -> Optional[Node]:
        #print(f"Debug: get_node called with kwargs: {kwargs}")
        for node in self.parser.nodes.values():
            if all(getattr(node, key) == value for key, value in kwargs.items()):
                #print(f"Debug: Found matching node: key={node.key}, id={node.id}, content={node.content[:50]}...")
                return node
        #print("Debug: No matching node found")
        return None

    # new function for new parser
    def get_node_by_path(self, block_id_or_key_path: str) -> Optional[Node]:
        #print(f"Debug: get_node_by_path called with path: {block_id_or_key_path}")

        if block_id_or_key_path is None:
            raise ValueError("block_id_or_key_path cannot be None")

        block_ids_or_keys = block_id_or_key_path.split('/')
        current_node = self.get_node(id=block_ids_or_keys[0]) or self.parser.nodes.get(block_ids_or_keys[0])

        if not current_node:
            raise BlockNotFoundError(f"get_node_by_path: Block with id or key '{block_ids_or_keys[0]}' not found.")

        for part in block_ids_or_keys[1:]:
            found = False
            next_level = current_node.level + 1
            temp_node = current_node.next

            while temp_node:
                if (temp_node.id == part or temp_node.key == part) and temp_node.level == next_level:
                    current_node = temp_node
                    found = True
                    break
                temp_node = temp_node.next

            if not found:
                raise BlockNotFoundError(f"get_node_by_path: Block with id or key '{part}' not found at the expected level.")

        return current_node
    
    def replace_node(self, target_key: str, new_node: Node):
        self.parser.replace_node(target_key, new_node)

    def replace_node_with_ast(self, target_key: str, new_ast: 'AST'):
        self.parser.replace_node_with_ast(target_key, new_ast.parser.nodes)

    def prepend_node_with_ast(self, target_key: str, new_ast: 'AST'):
        self.parser.prepend_node_with_ast(target_key, new_ast.parser.nodes)

    def append_node_with_ast(self, target_key: str, new_ast: 'AST'):
        self.parser.append_node_with_ast(target_key, new_ast.parser.nodes)

    def get_part_by_path(self, block_id_path: str, use_hierarchy: bool) -> Dict[str, Node]:
        return get_ast_part_by_path(self, block_id_path, use_hierarchy)
    
def nodes_to_ast(nodes: Dict[str, Node]) -> AST:
    new_ast = AST("")
    new_ast.parser.nodes = nodes
    new_ast.parser.head = next(iter(nodes.values())) if nodes else None
    new_ast.parser.tail = list(nodes.values())[-1] if nodes else None
    return new_ast

def perform_ast_operation(src_ast: AST, src_path: str, src_hierarchy: bool, 
                          dest_ast: AST, dest_path: str, dest_hierarchy: bool, 
                          operation: OperationType, process_src: bool = True) -> None:
    def print_operation_debug():
        print(f"""[EXCEPTION] > perform_ast_operation:
        - src_ast: {src_ast}
        - src_path: {src_path}
        - src_hierarchy: {src_hierarchy}  
        - dest_ast: {dest_ast}
        - dest_path: {dest_path}
        - dest_hierarchy: {dest_hierarchy}
        - operation: {operation}
        - process_src: {process_src}""")
    # Ensure operation is of type OperationType
    if isinstance(operation, str):
        try:
            # Try to convert string directly to OperationType
            operation = OperationType(operation)
        except ValueError:
            try:
                # If direct conversion fails, try matching by value
                operation = next(op for op in OperationType if op.value == operation)
            except StopIteration:
                # If no matching operation is found, raise an error
                print_operation_debug()
                raise ValueError(f"Unknown operation type: {operation}")

    # Extract source nodes
    if src_path and process_src:
        # If src_path is provided, get the specific part of the AST
        source_ast = get_ast_part_by_path(src_ast, src_path, src_hierarchy)
    else:
        # If no src_path, use the entire src_ast
        source_ast = src_ast

    # Validate that the source AST is not empty
    if process_src:
        if  not source_ast.parser.nodes:
            print_operation_debug()
            raise ValueError(f"Source AST is empty for path: {src_path}")

    # Extract destination nodes
    if '/' in dest_path:
        # If dest_path contains '/', it's definitely a path
        dest_node_ast = get_ast_part_by_path(dest_ast, dest_path, dest_hierarchy)
    else:
        # If no '/', it could be either a single node name (ID) or a key
        # First, try to find the node by ID
        dest_node = dest_ast.get_node(id=dest_path)
        
        if not dest_node:
            # If not found by ID, then try to find by key
            dest_node = dest_ast.parser.nodes.get(dest_path)
        
        if not dest_node:
            # If neither ID nor key matched, raise an error
            print_operation_debug()
            raise BlockNotFoundError(f"Node with id or key '{dest_path}' not found.")
        
        # Create a single-node AST for consistency with path-based lookup
        dest_node_ast = AST("")
        dest_node_ast.parser.nodes = {dest_node.key: dest_node}
        dest_node_ast.parser.head = dest_node_ast.parser.tail = dest_node

    # Validate that the destination AST is not empty
    if not dest_node_ast.parser.nodes:
        print_operation_debug()
        raise BlockNotFoundError(f"No destination nodes found for path: {dest_path}")

    # Perform the requested operation
    if operation == OperationType.REPLACE:
        if dest_hierarchy:
            # Hierarchical replace: Replace entire subtree
            # Identify the nodes before and after the replaced subtree
            preceding_node = dest_node_ast.parser.head.prev
            following_node = dest_node_ast.parser.tail.next

            # Remove old nodes from the destination AST
            for key in dest_node_ast.parser.nodes:
                del dest_ast.parser.nodes[key]

            # Insert new nodes from source AST into destination AST
            dest_ast.parser.nodes.update(source_ast.parser.nodes)

            # Update links to maintain the AST structure
            if preceding_node:
                # Connect preceding node to the start of the new subtree
                preceding_node.next = source_ast.parser.head
                source_ast.parser.head.prev = preceding_node
            else:
                # If no preceding node, update the AST head
                dest_ast.parser.head = source_ast.parser.head

            if following_node:
                # Connect the end of the new subtree to the following node
                following_node.prev = source_ast.parser.tail
                source_ast.parser.tail.next = following_node
            else:
                # If no following node, update the AST tail
                dest_ast.parser.tail = source_ast.parser.tail

        else:
            # Non-hierarchical replace: Replace single node
            if not dest_node_ast.parser.tail:
                print_operation_debug()
                raise BlockNotFoundError(f"Destination AST is empty for path: {dest_path}")
            # Use existing method to replace the node with the entire source AST
            dest_ast.replace_node_with_ast(dest_node_ast.parser.tail.key, source_ast)

    elif operation == OperationType.PREPEND:
        # Prepend: Insert source AST before the destination node
        if not dest_node_ast.parser.head:
            print_operation_debug()
            raise BlockNotFoundError(f"Destination AST is empty for path: {dest_path}")
        # Use existing method to prepend the entire source AST to the destination node
        dest_ast.prepend_node_with_ast(dest_node_ast.parser.head.key, source_ast)

    elif operation == OperationType.APPEND:
        # Append: Insert source AST after the destination node
        if not dest_node_ast.parser.tail:
            print_operation_debug()
            raise BlockNotFoundError(f"Destination AST is empty for path: {dest_path}")
        # Use existing method to append the entire source AST to the destination node
        dest_ast.append_node_with_ast(dest_node_ast.parser.tail.key, source_ast)
    
    else:
        # If the operation is not recognized, raise an error
        print_operation_debug()
        raise ValueError(f"Unknown operation type: {operation}")

    # Ensure the integrity of the doubly-linked list structure
    current = dest_ast.parser.head
    while current and current.next:
        # Ensure each node's 'next' points to a node that points back to it
        current.next.prev = current
        current = current.next

    # Validate the resulting AST
    if not dest_ast.parser.head or not dest_ast.parser.tail or len(dest_ast.parser.nodes) == 0:
        # Ensure the AST has a head, tail, and is not empty
        print_operation_debug()
        raise ValueError("Resulting AST is invalid: missing head, tail, or empty")

    # Output debug information
    #print(f"perform_ast_operation completed. Operation: {operation}, Destination path: {dest_path}")

def _get_ast_part(ast: AST, starting_node: Node, use_hierarchy: bool) -> AST:
    new_ast = AST("")
    result_nodes = {}
    current_node = starting_node
    base_level = starting_node.level

    while current_node:
        # Skip operation blocks
        if current_node.type == NodeType.OPERATION:
            current_node = current_node.next
            continue

        if current_node == starting_node:
            result_nodes[current_node.key] = copy.deepcopy(current_node)
        elif use_hierarchy and current_node.level > base_level:
            result_nodes[current_node.key] = copy.deepcopy(current_node)
        else:
            break

        current_node = current_node.next

    new_ast.parser.nodes = result_nodes
    new_ast.parser.head = get_head(result_nodes)
    new_ast.parser.tail = get_tail(result_nodes)

    # Rebuild links
    prev_node = None
    for node in result_nodes.values():
        node.prev = prev_node
        node.next = None
        if prev_node:
            prev_node.next = node
        prev_node = node

    if new_ast.parser.head:
        new_ast.parser.head.prev = None

    return new_ast

def get_ast_part_by_id(ast: AST, block_id: str, use_hierarchy: bool = False) -> AST:

    # print(f"Debug: get_ast_part_by_id called with id: {block_id}")

    starting_node = ast.get_node(id=block_id)
    if not starting_node:
        raise BlockNotFoundError(f"get_ast_part_by_id: Block with id '{block_id}' not found.")
    return _get_ast_part(ast, starting_node, use_hierarchy)

def get_ast_part_by_id_or_key(ast: AST, block_id_or_key: str, use_hierarchy: bool = False) -> AST:

    # print(f"Debug: get_ast_part_by_id_or_key called with id or key: {block_id_or_key}")

    starting_node = ast.get_node(id=block_id_or_key)
    if not starting_node:
        starting_node = ast.parser.nodes.get(block_id_or_key)
    if not starting_node:
        raise BlockNotFoundError(f"get_ast_part_by_id_or_key: Block with id or key '{block_id_or_key}' not found.")
    return _get_ast_part(ast, starting_node, use_hierarchy)

def get_ast_part_by_path(ast: AST, block_id_or_key_path: str, use_hierarchy: bool = False) -> AST:

    # print(f"Debug: get_ast_part_by_path called with path: {block_id_or_key_path}")

    if block_id_or_key_path is None:
        raise ValueError("block_id_or_key_path cannot be None")
    
    block_ids_or_keys = block_id_or_key_path.split('/')
    current_node = None
    
    # First, try to find by ID
    current_node = ast.get_node(id=block_ids_or_keys[0])
    
    # If not found by ID, try to find by key
    if not current_node:
        current_node = ast.parser.nodes.get(block_ids_or_keys[0])
    
    if not current_node:
        #print(f"debug before raise of block_ids_or_keys:{block_ids_or_keys}")
        raise BlockNotFoundError(f"get_ast_part_by_path: Block with id or key '{block_ids_or_keys[0]}' not found.")
    
    for i in range(1, len(block_ids_or_keys)):
        found = False
        next_block_id_or_key = block_ids_or_keys[i]
        next_level = current_node.level + 1

        temp_node = current_node.next
        while temp_node:
            if (temp_node.id == next_block_id_or_key or temp_node.key == next_block_id_or_key) and temp_node.level == next_level:
                current_node = temp_node
                found = True
                break
            temp_node = temp_node.next

        if not found:
            raise BlockNotFoundError(f"get_ast_part_by_path: Block with id or key '{next_block_id_or_key}' not found at the expected level.")

    # Return the AST part starting from the final current_node
    return _get_ast_part(ast, current_node, use_hierarchy)


