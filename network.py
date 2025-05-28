from __future__ import annotations
from typing import List
from node import Node
from nerve import Nerve
import random
import math
import copy

class Network():
    # NOTES:
    #       remember to normalize input values so some inputs arent weighed heavier
    """
    RI's:
    - Input nodes must be at the start of 'nodes' and must not change order
    - Output nodes must be at the end of 'nodes' and must not change order
    """
    nodes: List[Node] 
    nerves: List[Nerve]
    score: int
    grace: int

    def __init__(self, input_size: int = 1, output_size: int = 1) -> None:
        # default network connect all input to output
        # create input and output nodes
        nodes = []
        for _ in range(input_size):
            nodes.append(Node(0))
        for _ in range(output_size):
            nodes.append(Node(2))

        # connect all input to all output nodes (rand  weights)
        nerves = []
        for inp in nodes[0 : input_size]:
            for out in nodes[input_size:]:
                nerves.append(Nerve(inp, out))

        self.nodes = nodes
        self.nerves = nerves
        self.score = 0
        self.set_depth()
        self.grace = 0
    

    # testing initalizer
    def reinit_custom(self, nodes: List[Node], nerves: List[Nerve]) -> None:
        self.nodes = nodes
        self.nerves = nerves


    def relu(self, x: float) -> float:
        return max(0.0, x)
    
    def sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x))


    def process_network(self, in_data: list[int]) -> None:
        self.set_depth()
        # reset all node values and set input node values
        i = 0
        for node in self.nodes:
            # if input set value
            if node.type == 0:
                node.value = in_data[i]
                i += 1
            # else reset to 0
            else:
                node.value = 0
        
        # sort in nerves start depth first and then process each nerve
        self.sort_nerves()
        process_layer = 0
        for nerve in self.nerves:
            while process_layer < nerve.start.depth:
                process_layer += 1
                for node in self.nodes:
                    if node.depth == process_layer:
                        node.value = self.relu(node.value)
            nerve.process_nerve()
    

    def get_output(self) -> List[float]:
        self.sort_nodes_depth()
        output = []
        for node in self.nodes:
            if node.type == 2:
                output.append(node.value)
        return output


    def mutate_network(self) -> int:
        """ Return 0 if mutation adjusted a weight, 
        3 if mutation altered nerves
        6 if mutation altered nodes
        Chances of mutation:
        75% weight mutation (10% of weights get mutated)
        10% new node
        3% remove a node
        8% add a nerve
        4% remove a nerve
        * if mutation is not possible its skipped and no mutation happens
        """
        NERVE_GRACE = 3
        NODE_GRACE = 6
        roll = random.randint(1, 100)
        # weight mutation
        if roll <= 75:
            if self.nerves != []:
                # 10% of weights get mutated
                to_mutate = math.ceil(len(self.nerves)*0.1)
                for i in range(to_mutate):
                    random.choice(self.nerves).mutate_nerve()
            return 0

        # new node
        elif roll <= 85:
            # only add node if possible
            if self.nerves != []:
                # choose a random nerve to split
                old = random.choice(self.nerves)
                new_node = Node()
                self.nodes.append(new_node) # add new node
                # make new nerves 
                first = Nerve(old.start, new_node)
                second = Nerve(new_node, old.end)

                # keep weights so network remains the same 
                first.weight = 1.0         
                second.weight = old.weight  

                # add new and remove old nerves
                self.nerves.append(first)
                self.nerves.append(second)
                self.nerves.remove(old)
                self.sort_nodes_depth()
            return NODE_GRACE

        # remove a node
        elif roll <= 88: 
            # only remove node if possible
            internal_nodes = []
            for node in self.nodes:
                if node.type == 1:
                    internal_nodes.append(node)

            # if possible
            if internal_nodes != []:
                # choose a node
                node_to_remove = random.choice(internal_nodes)
                nerves_to_remove = []
                # find all nerves that touch that node and remove them
                for nerve in self.nerves:
                    if nerve.start == node_to_remove or nerve.end == node_to_remove:
                        nerves_to_remove.append(nerve)
                for nerve in nerves_to_remove:
                    self.nerves.remove(nerve)
                self.nodes.remove(node_to_remove)
                self.sort_nodes_depth()
            return NODE_GRACE
                        
                
        # add a nerve
        elif roll <= 96: 
            # only add node if possible
            # go thru every possible nerve location and get list of all missing nerves
            # (L time complexity)
            missing = []
            for start in self.nodes:
                for end in self.nodes:
                    if start.depth < end.depth:
                        exists = False
                        for nerve in self.nerves:
                            if nerve.start is start and nerve.end is end:
                                exists = True
                                break
                        if not exists:
                            missing.append((start, end))
            # add a random selection from missing nerve list if not empty
            if missing != []:
                new_nerve_spots = random.choice(missing)
                self.nerves.append(Nerve(new_nerve_spots[0], new_nerve_spots[1]))
            return NERVE_GRACE

        # only remove nerve if possible
        else:
            if self.nerves != []:
                self.nerves.remove(random.choice(self.nerves))
            return NERVE_GRACE
        
    
    def sort_nerves(self) -> None:
        """
        Sort based on start node depth
        """
        self.set_depth()
        # helper callable
        def get_nerve_start_depth(nerve: Nerve) -> int:
            return nerve.start.depth
        
        self.nerves = sorted(self.nerves, key=get_nerve_start_depth)


    def sort_nodes_depth(self) -> None:
        self.set_depth()
        # helper callable
        def get_node_depth(node: Node) -> int:
            return node.depth
        
        self.nodes = sorted(self.nodes, key=get_node_depth)

        
    def set_depth(self) -> None:
        curr = self.reset_depths()

        # get all input nodes
        depth = 0
        next = []
        for nerve in self.nerves:
            if nerve.start in curr:
                next.append(nerve.end)

        # set current layers depth and then move to next layer of nodes
        while next:
            for node in curr:
                node.depth = depth
            curr = next[:]
            next = []
            for nerve in self.nerves:
                if nerve.start in curr:
                    next.append(nerve.end)
            depth += 1

        # set final layers depths
        for node in curr:
            node.depth = depth
        curr = next

        # Ensure output nodes are always in the final layer
        max_depth = max(max((node.depth for node in self.nodes if node.depth != -1)), 1)
        for node in self.nodes:
            if node.type == 2:  # Output node
                node.depth = max_depth
        

    def reset_depths(self) -> None:
        # if input then return it, else set to -1 temporarily
        inputs = []
        for node in self.nodes:
            if node.type != 0:
                node.depth = -1
            else:
                inputs.append(node)
        return inputs


# ------------------------------------------------------------
#  HARD-CODED 3-2-1 XOR NETWORK (bias, A, B  →  H1, H2  →  O1)
# ------------------------------------------------------------
# ------------------------------------------------------------------
#  MINIMAL 3-2-1 XOR NETWORK  (feed inputs [1, A, B] → sigmoid out)
# ------------------------------------------------------------------
def build_handcrafted_xor_network() -> Network:
    """
    Returns a Network that rounds perfectly to XOR:
        in = [bias(1), A, B]   out ≈ 0 or 1
    Hidden units:
        H1 = ReLU( +A − B )
        H2 = ReLU( −A + B )
    Output:
        z = 2·H1 + 2·H2 − 1
        y = sigmoid(z)
    """

    # -------- nodes --------
    bias, A, B = Node(0), Node(0), Node(0)   # three inputs
    H1, H2     = Node(), Node()              # hidden (ReLU)
    O1         = Node(2)                     # output (sigmoid)
    nodes      = [bias, A, B, H1, H2, O1]

    # -------- nerves (connections & weights) --------
    nerves = [
        # inputs → hidden
        Nerve(A, H1),  #  +1
        Nerve(B, H1),  #  –1
        Nerve(A, H2),  #  –1
        Nerve(B, H2),  #  +1

        # hidden → output
        Nerve(H1, O1), #  +2
        Nerve(H2, O1), #  +2

        # bias → output
        Nerve(bias, O1)  #  –1
    ]

    # assign the exact weights
    nerves[0].weight = +1   # A  → H1
    nerves[1].weight = -1   # B  → H1
    nerves[2].weight = -1   # A  → H2
    nerves[3].weight = +1   # B  → H2
    nerves[4].weight = +2   # H1 → O1
    nerves[5].weight = +2   # H2 → O1
    nerves[6].weight = -1   # bias → O1

    # -------- package into a Network --------
    net = Network()                       # dummy constructor
    net.reinit_custom(nodes, nerves)      # inject topology
    net.set_depth()
    net.sort_nodes_depth()
    net.sort_nerves()
    return net




if __name__ == "__main__":
    
    n1, n2, n3, n4, n5 = Node(0), Node(), Node(), Node(), Node(2)
    l1 = Nerve(n1, n2)
    l2 = Nerve(n2, n3)
    l3 = Nerve(n3, n5)

    l4 = Nerve(n1, n4)
    l5 = Nerve(n4, n5)

    l6 = Nerve(n4, n3)

    x = -0.5 #test
    l1.weight = x
    l2.weight = x
    l3.weight = x
    l4.weight = x
    l5.weight = x
    l6.weight = x

    net = Network()
    net.reinit_custom([n1, n2, n3, n4, n5], [l1, l2,  l3, l4, l5, l6])
    net.process_network([1, 1, 1, 1, 1, 1])

    net.set_depth()

    
    for node in net.nodes:
        print(node.value)

    print("----------------------")
    net2 = Network(2, 2)
    net2.process_network([1, 1])
    for node in net2.nodes:
        print(node.value)
    # for nerve in net.nerves:
    #     print(nerve.start.value, nerve.end.value)
        
    # print()

    # for node in net.nodes:
    #     print(node.value)

    

    # xor = build_handcrafted_xor_network()
    # for A, B in [(0,0), (0,1), (1,0), (1,1)]:
    #     xor.process_network([1, A, B])                 # [bias, A, B]
    #     out = xor.sigmoid(xor.get_output()[0])         # convert last ReLU → sigmoid
    #     print(f"{A} XOR {B} -> {round(out)}   ({out:.3f})")

