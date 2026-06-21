import copy
import math
import random
from typing import List

from network import Network


class Population:
    """Keeps a group of networks and creates the next generation."""

    def __init__(
        self,
        input_size: int = 1,
        output_size: int = 1,
        count: int = 10,
    ) -> None:
        if count < 1:
            raise ValueError("Population count must be at least 1.")

        self.input_size = input_size
        self.output_size = output_size
        self.agents: List[Network] = [
            Network(input_size, output_size) for _ in range(count)
        ]

    def reset_scores(self) -> None:
        for agent in self.agents:
            agent.score = 0

    def run_agents(self, inputs: List[float]) -> List[List[float]]:
        outputs = []
        for network in self.agents:
            network.process_network(inputs)
            outputs.append(network.get_output())
        return outputs

    def rank_fitness(self) -> None:
        self.agents.sort(key=lambda network: network.score, reverse=True)

    def new_generation(
        self,
        survival_rate: float = 0.3,
        mutation_rate: float = 1.0,
    ) -> None:
        if not self.agents:
            raise ValueError("Cannot evolve an empty population.")

        survival_rate = max(0.0, min(1.0, survival_rate))
        mutation_rate = max(0.0, min(1.0, mutation_rate))
        population_size = len(self.agents)
        max_node_count = 2 + self.input_size + self.output_size

        self.rank_fitness()
        top_agents = max(1, round(population_size * survival_rate))
        survivors = self.agents[:top_agents]

        for agent in self.agents:
            if agent.grace > 0 and agent not in survivors:
                survivors.append(agent)
            agent.grace = max(0, agent.grace - 1)

        # Grace periods can temporarily keep more networks than the requested
        # survival rate, but never more than the original population size.
        survivors = survivors[:population_size]
        children_needed = population_size - len(survivors)
        children = []

        for index in range(children_needed):
            child = copy.deepcopy(survivors[index % len(survivors)])
            if random.random() <= mutation_rate:
                mutation_grace = child.mutate_network()
                child.grace += mutation_grace
            child.score = 0
            children.append(child)

        self.agents = children + survivors

        for index, agent in enumerate(self.agents):
            if len(agent.nodes) > max_node_count:
                self.agents[index] = Network(self.input_size, self.output_size)

        self.rank_fitness()

    @staticmethod
    def relu(x: float) -> float:
        return max(0.0, x)

    @staticmethod
    def sigmoid(x: float) -> float:
        if x >= 0:
            return 1 / (1 + math.exp(-x))
        exp_value = math.exp(x)
        return exp_value / (1 + exp_value)

    def get_fitness(self) -> None:
        """Override this method for a specific training problem."""
        pass
