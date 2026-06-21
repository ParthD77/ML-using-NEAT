from typing import Any

from population import Population


class Template(Population):
    """Small starting point for another neuroevolution experiment."""

    def __init__(
        self,
        input_size: int,
        output_size: int,
        population_size: int,
    ) -> None:
        super().__init__(input_size, output_size, population_size)

    def additional_activation_func(self, value: float) -> Any:
        """Add another output activation here if the problem needs one."""
        return value

    def get_fitness(self) -> None:
        """
        Reset scores, run each agent on the problem, assign fitness, and call
        rank_fitness(). See XOR.py and flappybird.py for complete examples.
        """
        raise NotImplementedError("Add a fitness function for this experiment.")


if __name__ == "__main__":
    trainer = Template(input_size=3, output_size=1, population_size=150)
    print(
        "Template population created. Implement Template.get_fitness() "
        "before starting training."
    )
