from network import Network
from typing import Tuple, List, Dict
import math
import copy

"""
Potential  features:
    Activation function????
    Adjust the % of agents that surive
"""

class main():
    agents: List[Network]


    def __init__(self, input_size: int = 1, output_size: int = 1, count: int = 10) -> None:
        self.agents = []
        for _ in range(count):
            self.agents.append(Network(input_size, output_size))
    

    def reset_scores(self):
        for agent in self.agents:
            agent.score = 0
        

    def run_agents(self, input: List[int]) -> List[List[float]]:
        output = []
        for network in self.agents:
            network.process_network(input)
            output.append(network.get_output())
        return output


    def rank_fitness(self):
        # helper callable
        def get_network_score(network: Network) -> int:
            return network.score
        
        self.agents = sorted(self.agents, key=get_network_score, reverse=True)
    

    def new_generation(self, surival_rate: float) -> None:
        # save surival_rate% of allagents and mutate that 10% to fill the 90% of slots
        # mutate each agent 9 times and add it
        spots = len(self.agents)
        self.rank_fitness()

        num_survivors = max(1, math.ceil(spots * surival_rate))
        good_agents = self.agents[:num_survivors]
        self.agents = good_agents[:]

        num_to_generate = spots - len(self.agents)
        multiplier = math.ceil(num_to_generate / len(good_agents))

        for agent in good_agents:
            for _ in range(multiplier):
                agent_copy = copy.deepcopy(agent)
                agent_copy.mutate_network()
                self.agents.append(agent_copy)

    
    def get_fitness(self):
        """
        Unimplemented Method
        """
        pass
    




if __name__ == "__main__":
    pass