# Operation Parser
# - OperationParser
# - ParsedLink
# - Parameter
# - OperationComponents

from enum import Enum
import re
from dataclasses import dataclass
from typing import Optional, Union

from llexem.config import Config

from llexem.ast_md.node import OperationType


class OperationParser:
    class ParamType(Enum):
        PARAM_TYPE_LITERAL = "PARAM_TYPE_LITERAL"
        PARAM_TYPE_LINK = "PARAM_TYPE_LINK"

    @dataclass
    class ParsedLink:
        file_path: str
        filename: str
        block_id: str
        block_full_path: str
        nested_flag: bool

    @dataclass
    class Parameter:
        param_type: 'OperationParser.ParamType'
        value: Union[str, 'OperationParser.ParsedLink']
        new_block_header: Optional[str] = None

    @dataclass
    class OperationComponents:
        operation: str
        src: 'OperationParser.ParsedLink'
        parameter: 'OperationParser.Parameter'
        operand: OperationType 
        target: 'OperationParser.ParsedLink'


    def __init__(self, operation_string: str):
        self.operation_string = operation_string

    def string_to_operation_type(self, operand_str: Union[str, list]) -> OperationType:
        if isinstance(operand_str, list):
            # If operand_str is an empty list, use the default operation
            if not operand_str:
                return OperationType(Config.DEFAULT_OPERATION)
            # If it's a non-empty list, use the first element
            # TODO: !! I thoink this code should be removed
            operand_str = operand_str[0]
        
        if operand_str == "=>":
            return OperationType.REPLACE
        elif operand_str == "+>":
            return OperationType.APPEND
        elif operand_str == ".>":
            return OperationType.PREPEND
        else:
            return OperationType(operand_str)
          
    def parse(self) -> OperationComponents:
        left, central, right = self.parse_step1(self.operation_string)
        operation, source_path, parameter_str = self.parse_step2(left)
        src_link = self.decompose_link(source_path)
        parameter = self.parse_parameter(parameter_str)
        target_link = self.parse_block_link(right.strip())
        
        # Convert central to OperationType, use default if not specified
        operand = self.string_to_operation_type(central if central else Config.DEFAULT_OPERATION)
        
        return self.OperationComponents(operation, src_link, parameter, operand, target_link)

    def parse_step1(self, string: str):
        central = re.findall(r'\.>|=>|\+>', string)
        if central:
            central = central[0]
            left, right = re.split(re.escape(central), string, maxsplit=1)
        else:
            left = string
            right = ""
            central = ""  # Use an empty string instead of an empty list
        return left, central, right

    def parse_step2(self, left: str):
        match = re.match(r'(@\S+)\s+', left)
        if match:
            operation = match.group(1)
            rest = left[match.end():]
        else:
            operation = ""
            rest = left

        param_match = re.search(r'\(([^)]*)\)', rest)
        if param_match:
            parameter = param_match.group(1)
            source_path = rest[:param_match.start()].strip()
        else:
            parameter = ""
            source_path = rest.strip()
        
        return operation, source_path, parameter

    def decompose_link(self, link: str) -> ParsedLink:
        filename_match = re.search(r'(/?[^/]*[^/.]\.[^/.][^/]*/?)', link)
        if filename_match:
            filename = filename_match.group(1).strip('/')
            file_path = link[:filename_match.start()].rstrip('/')
            block_path = link[filename_match.end():].lstrip('/')
        else:
            filename = ""
            file_path = ""
            block_path = link

        nested_flag = block_path.endswith('/*')
        block_full_path = block_path.rstrip('/*')
        
        block_id_parts = block_full_path.split('/')
        block_id = block_id_parts[-1] if block_id_parts else ""

        return self.ParsedLink(file_path, filename, block_id, block_full_path, nested_flag)


    def parse_block_link(self, block_path: str) -> ParsedLink:
        block_id = block_path.rstrip('/*').split('/')[-1] if block_path else ""
        nested_flag, block_full_path = self.check_blockpath(block_path)
        
        return self.ParsedLink(file_path='', filename='', block_id=block_id, block_full_path=block_full_path, nested_flag=nested_flag)

    def check_blockpath(self, blockpath: str):
        if blockpath.endswith('/*'):
            nest_flag = True
            cleaned_blockpath = blockpath[:-2]
        else:
            nest_flag = False
            cleaned_blockpath = blockpath
        return nest_flag, cleaned_blockpath



    def parse_parameter(self, parameter: str) -> Parameter:
        new_block_header = None
        
        # Regex to find a comma not inside single or double quotes
        match = re.search(r',(?=(?:[^\'"]|\'[^\']*\'|"[^"]*")*$)', parameter)
        
        if match:
            comma_index = match.start()
            parameter_part = parameter[:comma_index].strip()
            new_block_header = parameter[comma_index + 1:].strip()
        else:
            parameter_part = parameter.strip()
        
        # Process the parameter part with the original logic
        if (parameter_part.startswith('"') and parameter_part.endswith('"')) or (parameter_part.startswith("'") and parameter_part.endswith("'")):
            literal_value = parameter_part[1:-1]
            return self.Parameter(self.ParamType.PARAM_TYPE_LITERAL, literal_value, new_block_header)
        else:
            parsed_link = self.decompose_link(parameter_part)
            return self.Parameter(self.ParamType.PARAM_TYPE_LINK, parsed_link, new_block_header)
