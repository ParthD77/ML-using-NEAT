import math

from population import Population


class XORTrainer(Population):
    def __init__(self, population_size: int = 150) -> None:
        super().__init__(input_size=3, output_size=1, count=population_size)

    def get_fitness(self) -> None:
        self.reset_scores()
        for x1 in (0, 1):
            for x2 in (0, 1):
                inputs = [1, x1, x2]
                outputs = self.run_agents(inputs)
                expected = x1 ^ x2
                for agent, output in zip(self.agents, outputs):
                    prediction = round(self.sigmoid(output[0]))
                    if prediction == expected:
                        agent.score += 1
        self.rank_fitness()


def print_xor_outputs(network) -> None:
    print("\nNetwork XOR Evaluation:")
    for x1 in (0, 1):
        for x2 in (0, 1):
            network.process_network([1, x1, x2])
            output = network.get_output()[0]
            result = 1 / (1 + math.exp(-output))
            print(
                f"  {x1} XOR {x2} -> {result:.4f} "
                f"(rounded: {round(result)})"
            )
    print()


if __name__ == "__main__":
    trainer = XORTrainer(population_size=150)
    generation = 0
    survival_rate = 0.7

    while True:
        generation += 1
        trainer.get_fitness()
        scores = [agent.score for agent in trainer.agents]
        champion = trainer.agents[0]
        best = max(scores)
        average = sum(scores) / len(scores)

        print(
            f"Generation {generation:4d} | "
            f"best {best:.0f} | average {average:.2f} | "
            f"nodes {len(champion.nodes)} | edges {len(champion.nerves)}"
        )

        if best >= 4:
            print("Solution found!")
            print_xor_outputs(champion)
            try:
                from pyqtest import display_network
            except ImportError:
                print("PyQt6 is not installed. Run: pip install PyQt6")
            else:
                display_network(
                    champion,
                    width=800,
                    height=600,
                    x=100,
                    y=100,
                )
            break

        trainer.new_generation(survival_rate)
