from node import Node
from random import uniform


class Nerve():
    weight: float
    start: Node
    end: Node
    
    def __init__(self, start: Node, end: Node) -> None:
        self.start = start
        self.end = end
        self.weight = uniform(-1, 1)


    def process_nerve(self) -> None:
        self.end.value += self.start.value * self.weight
    

    def mutate_nerve(self) -> None:
        # Reinitialization %15
        if uniform(0, 1) <= 0.15:  
            self.weight = uniform(-1, 1)
        # Perturbation     %85
        else:
            self.weight += uniform(-0.5, 0.5)


    
    


