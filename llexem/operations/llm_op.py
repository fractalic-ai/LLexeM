# LLM Operation
# - process_llm

from typing import Optional
from pathlib import Path
import time

from llexem.ast_md.node import Node, OperationType, NodeType
from llexem.ast_md.ast import AST, get_ast_part_by_path, perform_ast_operation
from llexem.errors import BlockNotFoundError
from llexem.config import Config
from llexem.llm.llm_client import LLMClient  # Import the LLMClient class
from rich.console import Console
from rich.spinner import Spinner
from rich import print
from rich.status import Status

# Assuming LLM_PROVIDER and API_KEY are globally set in llexem.py
# You can initialize LLMClient here if it's a singleton


def process_llm(ast: AST, current_node: Node) -> Optional[Node]:
    """Process @llm operation with updated schema support"""
    console = Console(force_terminal=True)

    def get_previous_headings(node: Node) -> str:
        context = []
        current = ast.first()
        while current and current != node:
            if current.type == NodeType.HEADING:
                context.append(current.content)
            current = current.next
        return "\n\n".join(context)

    # Get parameters
    params = current_node.params or {}
    prompt = params.get('prompt')
    block_params = params.get('block', {})

    # Validate at least one of prompt/block is provided
    if not prompt and not block_params:
        raise ValueError("@llm operation requires either 'prompt' or 'block' parameter")

    # Get target parameters 
    to_params = params.get('to', {})
    target_block_uri = to_params.get('block_uri') if to_params else None
    target_nested = to_params.get('nested_flag', False) if to_params else False

    # Build prompt parts based on parameters
    prompt_parts = []

    # Handle blocks first - can be single block or array
    if block_params:
        if block_params.get('is_multi'):
            # Handle array of blocks
            blocks = block_params.get('blocks', [])
            for block_info in blocks:
                try:
                    block_uri = block_info.get('block_uri')
                    nested_flag = block_info.get('nested_flag', False)
                    block_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
                    if block_ast.parser.nodes:
                        block_content = "\n\n".join(node.content for node in block_ast.parser.nodes.values())
                        prompt_parts.append(block_content)
                except BlockNotFoundError:
                    raise ValueError(f"Block with URI '{block_uri}' not found")
        else:
            # Handle single block
            try:
                block_uri = block_params.get('block_uri')
                nested_flag = block_params.get('nested_flag', False)
                block_ast = get_ast_part_by_path(ast, block_uri, nested_flag)
                if block_ast.parser.nodes:
                    block_content = "\n\n".join(node.content for node in block_ast.parser.nodes.values())
                    prompt_parts.append(block_content)
            except BlockNotFoundError:
                raise ValueError(f"Block with URI '{block_uri}' not found")

    # Add context if only prompt is provided (no blocks)
    elif prompt:
        context = get_previous_headings(current_node)
        if context:
            prompt_parts.append(context)

    # Add prompt if specified (always last)
    if prompt:
        prompt_parts.append(prompt)

    # Combine all parts with proper spacing
    prompt_text = "\n\n".join(part.strip() for part in prompt_parts if part.strip())

    # Call LLM
    llm_client = LLMClient(provider=Config.LLM_PROVIDER, api_key=Config.API_KEY)
    
    start_time = time.time()
    try:
        with console.status("[cyan] @llm[/cyan] processing...", spinner="dots") as status:
            response = llm_client.llm_call(prompt_text, params)
        
        duration = time.time() - start_time
        mins, secs = divmod(int(duration), 60)
        duration_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        console.print(f"[light_green]✓[/light_green][cyan] @llm[/cyan] completed ({duration_str})")
        
    except Exception as e:
        console.print(f"[bold red]✗ Failed: {str(e)}[/bold red]")
        raise

    # Get save-to-file parameter
    save_to_file = params.get('save-to-file')

    # Save raw response to file if save_to_file is specified
    if save_to_file:
        file_path = Path(save_to_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(response)

    # Handle header
    header = ""
    use_header = params.get('use-header')
    if use_header is not None:
        if use_header.lower() != "none":
            header = f"{use_header}\n"
    else:
        header = "# LLM Response block\n"

    response_ast = AST(f"{header}{response}\n")

    # Handle target block insertion
    operation_type = OperationType(params.get('mode', Config.DEFAULT_OPERATION))

    if target_block_uri:
        try:
            target_node = ast.get_node_by_path(target_block_uri)
            target_key = target_node.key
        except BlockNotFoundError:
            raise ValueError(f"Target block '{target_block_uri}' not found")
    else:
        target_key = current_node.key

    perform_ast_operation(
        src_ast=response_ast,
        src_path="",
        src_hierarchy=False,
        dest_ast=ast,
        dest_path=target_key,
        dest_hierarchy=target_nested,
        operation=operation_type
    )

    return current_node.next