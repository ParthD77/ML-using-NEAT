# test_network.py
import pytest
from network import Network
from node import Node
from nerve import Nerve

def make_linear_chain(weights):
    """
    Build a simple 3‐layer chain: input → hidden → output
    with the given two weights.
    """
    n_in = Node(0)
    n_hidden = Node()       # type 1 internal
    n_out = Node(2)
    l1 = Nerve(n_in, n_hidden)
    l2 = Nerve(n_hidden, n_out)
    l1.weight, l2.weight = weights
    net = Network()
    net.reinit_custom([n_in, n_hidden, n_out], [l1, l2])
    return net, n_in, n_hidden, n_out

def test_single_connection_identity():
    # one input → one output, weight = 1.0 → output should equal input
    in_n = Node(0)
    out_n = Node(2)
    conn = Nerve(in_n, out_n)
    conn.weight = 1.0

    net = Network()
    net.reinit_custom([in_n, out_n], [conn])

    for val in [0, 1, 5, -3]:
        net.process_network([val])
        assert net.get_output() == [val]

def test_weight_multiplier():
    # one input → one output, weight = 2.5
    in_n = Node(0)
    out_n = Node(2)
    conn = Nerve(in_n, out_n)
    conn.weight = 2.5

    net = Network()
    net.reinit_custom([in_n, out_n], [conn])
    net.process_network([4])
    assert net.get_output() == [10.0]

def test_linear_chain_forward_and_relu():
    # input→hidden→output with positive weights
    net, n_in, n_h, n_out = make_linear_chain([2.0, 3.0])
    net.process_network([2])
    # hidden = 2 * 2 = 4 → ReLU(4) = 4
    # output = 4 * 3 = 12
    assert net.get_output() == [12.0]

def test_negative_weights_relu_zeroes_hidden():
    # input→hidden→output with negative weights → hidden gets negative, ReLU zeroes it
    net, n_in, n_h, n_out = make_linear_chain([-2.0, -3.0])
    net.process_network([2])
    # hidden = 2 * -2 = -4 → ReLU(-4) = 0
    # output = 0 * -3 = 0
    assert net.get_output() == [0.0]

def test_multi_input_sum_weights():
    # two inputs → one output, weight1=1, weight2=1 → output = sum(inputs)
    n1, n2 = Node(0), Node(0)
    out_n = Node(2)
    c1 = Nerve(n1, out_n); c1.weight = 1.0
    c2 = Nerve(n2, out_n); c2.weight = 1.0

    net = Network()
    net.reinit_custom([n1, n2, out_n], [c1, c2])
    net.process_network([3, 4])
    assert net.get_output() == [7.0]

@pytest.mark.parametrize("inputs, weights, expected", [
    ([5], [1.0, 1.0], 5.0),
    ([1], [3.0, 0.5], 1.5),
    ([0], [2.0, 2.0], 0.0),
])
def test_chain_various_weights(inputs, weights, expected):
    # parameterized linear chains
    net, n_in, n_h, n_out = make_linear_chain(weights)
    net.process_network(inputs)
    assert pytest.approx(net.get_output()[0]) == expected

def test_depth_assignment_linear():
    # check that depths are 0,1,2 in a 3‐layer chain
    net, n_in, n_h, n_out = make_linear_chain([1.0,1.0])
    net.set_depth()
    assert n_in.depth == 0
    assert n_h.depth == 1
    assert n_out.depth == 2

def test_process_resets_values_between_runs():
    # same network, two runs: ensure no residual accumulation
    in_n = Node(0)
    out_n = Node(2)
    conn = Nerve(in_n, out_n)
    conn.weight = 1.0

    net = Network()
    net.reinit_custom([in_n, out_n], [conn])

    net.process_network([1])
    assert net.get_output() == [1.0]

    net.process_network([2])
    assert net.get_output() == [2.0]

def test_branching_network():
    # input → two hidden nodes → output; both branches weight=1
    inp = Node(0)
    h1, h2 = Node(), Node()
    out = Node(2)

    e1 = Nerve(inp, h1); e1.weight = 1.0
    e2 = Nerve(inp, h2); e2.weight = 2.0
    e3 = Nerve(h1, out); e3.weight = 1.0
    e4 = Nerve(h2, out); e4.weight = 1.0

    net = Network()
    net.reinit_custom([inp, h1, h2, out], [e1, e2, e3, e4])
    # input=3 → h1=3, h2=6 → ReLU keeps both
    # out = 3*1 + 6*1 = 9
    net.process_network([3])
    assert net.get_output() == [9.0]
