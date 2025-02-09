# Node
# - Node
# - NodeType
# - OperationType

import hashlib
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


    
class NodeType(Enum):
    HEADING = "heading"
    OPERATION = "operation"

class OperationType(Enum):
    REPLACE = "replace"
    PREPEND = "prepend"
    APPEND = "append"

@dataclass
class Node:
    type: NodeType
    name: str
    level: int
    params: Optional[Dict[str, Any]] = None  # Proper type annotation
    content: str = ""
    id: Optional[str] = None
    indent: int = 0
    source_path: Optional[str] = None
    source_block_id: Optional[str] = None
    target_path: Optional[str] = None
    target_block_id: Optional[str] = None
    key: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    prev: Optional['Node'] = None
    next: Optional['Node'] = None
    enabled: bool = True  # Persistent flag for run-once logic


    @property
    def hash(self) -> str:
        return hashlib.md5(self.content.encode()).hexdigest()[:8]