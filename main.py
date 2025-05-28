from network import Network
from typing import Tuple, List, Dict
import math
import copy

"""
Potential  features:
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
    
    #TODO: LOOK OVER
    def new_generation(self, survival_rate: float = 0.3) -> None:
        self.rank_fitness()

        top_agents = round(len(self.agents)*survival_rate)
        survivors = self.agents[:top_agents]
        for agent in self.agents:
            if agent.grace > 0 and not (agent in survivors):
                survivors.append(agent)
            agent.grace -= 1

        filled = len(survivors)
        spots = len(self.agents) - filled
        i = 0
        self.agents = []
        while len(self.agents) < spots:
            agent = survivors[i % filled]
            agent_copy = copy.deepcopy(agent)
            mutation_type = agent_copy.mutate_network()
            agent_copy.grace += mutation_type
            self.agents.append(agent_copy)
            i += 1
        self.agents.extend(survivors)

        self.rank_fitness()
        

    
    def get_fitness(self):
        """
        Unimplemented Method
        """
        pass
    




if __name__ == "__main__":
    pass