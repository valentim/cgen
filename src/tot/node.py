from ai.prompt import Prompt
from typing import Optional, List


class Node:
    def __init__(self, parent: Optional["Node"], prompt: Prompt):
        self.parent: Optional["Node"] = parent
        self.prompt: Prompt = prompt
        self.code: Optional[str] = None
        self.errors: List[str] = []
        self.children: List["Node"] = []

    def add_child(self, child_node: "Node"):
        self.children.append(child_node)

    def depth(self):
        depth = 0
        current = self
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth
