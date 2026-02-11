from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class Node:
    id: str
    type: str
    source: str
    parents: List[str] = field(default_factory=list)
    outputs: List[dict] = field(default_factory=list)

@dataclass
class Flowbook:
    metadata: dict
    nodes: Dict[str, Node]
    root: str
