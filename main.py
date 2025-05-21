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
    

    def new_generation(self) -> None:
        # save 10% of allagents and mutate that 10% to fill the 90% of slots
        # mutate each agent 9 times and add it
        spots = len(self.agents)
        good_agents = self.agents[0 : math.ceil(spots*0.1)]
        self.agents = good_agents

        for agent in good_agents:
            for _ in range(9):
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