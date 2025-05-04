from typing import List


class Node():
    """
    Types:
        0 - Input
        1 - Internal
        2 - Output
    """
    type: int
    value: float
    depth: int

    
    def __init__(self, type: int = 1) -> None:
        self.value = 1
        self.type = type
        if type == 0:
            self.depth = 0
        else:
            self.depth = -1
