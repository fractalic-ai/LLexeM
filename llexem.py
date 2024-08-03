import os
import sys
import argparse

from llexem.ast_md.parser import print_parsed_structure
from llexem.utils import parse_file
from llexem.config import Config
from llexem.ast_md.ast import AST
from llexem.utils import read_file
from llexem.operations.runner import run
from llexem.errors import BlockNotFoundError, UnknownOperationError

def main():
    parser = argparse.ArgumentParser(description="Process and run operations on a markdown file.")
    parser.add_argument('input_file', type=str, help='Path to the input markdown file.')
    parser.add_argument('--task_file', type=str, help='Path to the task markdown file.')
    parser.add_argument('--api_key', type=str, help='OpenAI API key', default=os.getenv('OPENAI_API_KEY'))
    parser.add_argument('--operation', type=str, help='Default operation to perform', default="append")
    parser.add_argument('--param_input_user_request', type=str, help='Part path for ParamInput-UserRequest', default=None)

    args = parser.parse_args()

    # Ensure the API key is set before making the API call
    if not args.api_key:
        raise ValueError("OpenAI API key must be provided either as an argument or through the OPENAI_API_KEY environment variable.")

    os.environ['OPENAI_API_KEY'] = args.api_key
    Config.DEFAULT_OPERATION = args.operation

    try:


        if args.task_file and args.param_input_user_request:
            temp_ast = parse_file(args.task_file)
            # print_parsed_structure(temp_ast)
            param_node = temp_ast.get_part_by_path(args.param_input_user_request, True)
            result_nodes = run(args.input_file, param_node)
        else:
            result_nodes = run(args.input_file)
    except (BlockNotFoundError, UnknownOperationError, IOError) as e:
        raise RuntimeError(f"Error: {e}")

if __name__ == "__main__":
    main()
