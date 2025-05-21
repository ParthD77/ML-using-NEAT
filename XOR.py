from main import main
from network import Network
from typing import Tuple, List, Dict

class XOR(main):
    agents: List[Network]

    
    def __init__(self):
        super().__init__(2, 1, 10)

    def get_fitness(self):
        self.reset_scores()
        for i in range(2):
            for j in range(2):
                output = self.run_agents([i, j])
                xor_result = i ^ j
                for k in range(len(output)):
                    result = output[k]
                    if xor_result == round(result[0]):
                        self.agents[k].score += 1
        for agent in self.agents:
            print(agent.score)
        print("--------------------")
        self.rank_fitness()
        for network in self.agents:
            network.mutate_network()    


if __name__ == "__main__":
    xor = XOR()
    for i in range(300):
        xor.get_fitness()



