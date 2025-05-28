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
        self.input_size = input_size
        self.output_size = output_size
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
        # limit hidden nodes network size
        MAX_HIDDEN_SIZE = 2 + self.input_size + self.output_size

      
        self.rank_fitness()

        # find # of agents to save according to surival rate
        top_agents = round(len(self.agents)*survival_rate)
        survivors = self.agents[:top_agents] # since its sorted save them
        # if non-top agent has grace remove them and add them in later
        for agent in self.agents:
            if agent.grace > 0 and not (agent in survivors):
                survivors.append(agent)
            agent.grace -= 1 

        # see how many spots are left to fill with mutated agents
        filled = len(survivors)
        spots = len(self.agents) - filled
        
        i = 0
        self.agents = []
        # fill empty spots with mutated agents
        while len(self.agents) < spots:
            agent = survivors[i % filled]
            agent_copy = copy.deepcopy(agent)
            mutation_type = agent_copy.mutate_network()
            agent_copy.grace += mutation_type # if structural change happens add grace
            self.agents.append(agent_copy)
            i += 1 # to swap between surivors to be mutated
        self.agents.extend(survivors)

        # remove agents who surpass the hidden node size limit
        for i in range(len(self.agents)):
            if len(self.agents[i].nodes) > MAX_HIDDEN_SIZE:
                self.agents[i] = Network(self.input_size, self.output_size)

        self.rank_fitness()
        



    def relu(self, x: float) -> float:
        return max(0.0, x)
    

    def sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x))
    

    def get_fitness(self) -> None:
        """
        Unimplemented Method
        """
        pass
    




if __name__ == "__main__":
    pass