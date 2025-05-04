from typing import List
from node import Node
from nerve import Nerve


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
        self.set_depth()
    

    # testing initalizer
    def reinit_custom(self, nodes: List[Node], nerves: List[Nerve]) -> None:
        self.nodes = nodes
        self.nerves = nerves


    def process_network(self, in_data: list[int]) -> list[int]:
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
        for nerve in self.nerves:
            nerve.process_nerve()


    def sort_nerves(self) -> None:
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
        

    def reset_depths(self) -> None:
        # if input then return it, else set to -1 temporarily
        inputs = []
        for node in self.nodes:
            if node.type != 0:
                node.depth = -1
            else:
                inputs.append(node)
        return inputs
    





if __name__ == "__main__":
    n1, n2, n3, n4, n5 = Node(0), Node(), Node(), Node(), Node(2)
    l1 = Nerve(n1, n2)
    l2 = Nerve(n2, n3)
    l3 = Nerve(n3, n5)

    l4 = Nerve(n1, n4)
    l5 = Nerve(n4, n5)

    l6 = Nerve(n4, n3)

    net = Network()
    net.reinit_custom([n1, n2, n3, n4, n5], [l1, l2,  l3, l4, l5, l6])
    net.process_network([1, 1, 1, 1, 1, 1])

    net.set_depth()

    
    for node in net.nodes:
        print(node.value)


    net2 = Network(2, 2)
    net2.process_network([1, 1])
    for node in net2.nodes:
        print(node.value)
    # for nerve in net.nerves:
    #     print(nerve.start.value, nerve.end.value)
        
    # print()

    # for node in net.nodes:
    #     print(node.value)

