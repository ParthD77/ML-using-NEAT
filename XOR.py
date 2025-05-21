from main import main
from network import Network
from typing import Tuple, List, Dict
from pyqtest import display_network
import math

class XOR(main):
    agents: List[Network]

    
    def __init__(self):
        super().__init__(3, 1, 20)

    def sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x))

    def get_fitness(self):
        self.reset_scores()
        for i in range(2):
            for j in range(2):
                output = self.run_agents([1, i, j])
                xor_result = i ^ j
                for k in range(len(output)):
                    result = output[k]
                    result = self.sigmoid(result[0])
                    if xor_result == round(result):
                        self.agents[k].score += 1
        for agent in self.agents:
            print(agent.score, len(self.agents))
        print("--------------------")
        self.rank_fitness()
      


if __name__ == "__main__":
    xor = XOR()
    for i in range(1000):
        xor.get_fitness()
        xor.new_generation(0.5) 

    display_network(xor.agents[13])
    display_network(xor.agents[0])
    print(len(xor.agents[0].nodes), len(xor.agents[13].nodes))





