# xor_neat.py
import math
from main import main
from pyqtest import display_network

class XORTrainer(main):

    def __init__(self, population_size: int = 150) -> None:
        super().__init__(input_size=3, output_size=1, count=population_size)


    def get_fitness(self) -> None:
        self.reset_scores()
        for x1 in (0, 1):
            for x2 in (0, 1):
                inputs = [1, x2, x1]
                outputs = self.run_agents(inputs)
                expected = x1 ^ x2
                for agent, out in zip(self.agents, outputs):
                    z = out[0]
                    pred = round(self.sigmoid(z))
                    if pred == expected:
                        agent.score += 1
        self.rank_fitness()

def print_xor_outputs(network) -> None:
    """Prints actual XOR outputs of the given network."""
    print("\nNetwork XOR Evaluation:")
    for x1 in (0, 1):
        for x2 in (0, 1):
            inputs = [1, x1, x2]
            output = network.process_network(inputs)
            output = network.get_output()[0]
            result = 1 / (1 + math.exp(-output))  # sigmoid
            print(f"  {x1} XOR {x2} → {result:.4f} (rounded: {round(result)})")
    print()

if __name__ == "__main__":
    trainer = XORTrainer(population_size=150)
    generation = 0

    SURVIVAL_RATE = 0.7
    i = 0
    while True:
        generation += 1
        trainer.get_fitness()

        scores = [agent.score for agent in trainer.agents]
        best = max(scores)
        avg = sum(scores) / len(scores)

        print(f"Generation {generation}")
        print(f"  Best: {best}, Avg: {avg:.2f} | "
              f"Agents: {len(trainer.agents)}, "
              f"Nodes in champion: {len(trainer.agents[0].nodes)} | {(trainer.agents[0].grace)}")

        if best >= 4:
            print("🎉 Solution found! Displaying best network and XOR outputs...")
            trainer.rank_fitness()
            best_net = trainer.agents[0]
            print_xor_outputs(best_net)
            display_network(
                best_net,
                width=800,
                height=600,
                x=100,
                y=100
            )
            break
        i += 1

        trainer.new_generation(SURVIVAL_RATE)
