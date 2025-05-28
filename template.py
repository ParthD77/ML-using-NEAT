import math
from main import main
from pyqtest import display_network
from typing import Any

class Template(main):
    """ Basic template to implement on your own. Has slight features from XOR and flappybird. 
    Depending on if it's a game with continous score or a test like XOR changes will be required.
    Refer to XOR.py and flappybird.py to see more detailed and functional implementations.
    """
     

    def __init__(self, input_size: int, output_size: int, population_size: int) -> None:
        super().__init__(input_size, output_size, population_size)

    #  optional output layer activation function 
    def additional_activation_func(self, x) -> Any:
        """
        Unimplemented Method
        """
        pass
    


    def get_fitness(self) -> None:
        """
        self.reset_scores()
        
        # inputs = [1, x1, x2]                              # get desired inputs and add bias here
        # outputs = self.run_agents(inputs)                 # run agents on inputs
        # expected = x1 ^ x2                                # calculate wanted score OR run game an get score
        # for i in range(len(agents)):                      # set scores
        #    result = outputs[i][0]
        #    activated_result = round(self.sigmoid(z))
        #    if activated_result == expected:
        #            agent.score += 1

        self.rank_fitness()                                 # rerank agents
        """



if __name__ == "__main__":
    POP_SIZE = 150
    SURVIVAL_RATE = 0.7

    trainer = Template(POP_SIZE)
    generation = 0

    i = 0
    while True:
        generation += 1
        trainer.get_fitness()  # calc scores

        scores = [agent.score for agent in trainer.agents]
        best = max(scores)


        if best >= 4:
            print("🎉 Solution found!")
            trainer.rank_fitness()
            best_net = trainer.agents[0]
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
