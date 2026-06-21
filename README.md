# ML Using NEAT

This project is a small custom NEAT-inspired neuroevolution experiment. It
builds and mutates its own neural networks instead of using TensorFlow,
PyTorch, or another machine learning library.

The two main examples are:

- XOR, where networks evolve until one predicts all four XOR cases.
- Flappy Bird, where a population of birds learns when to jump.

This is a student project, so the implementation is intentionally fairly
small and readable instead of trying to include every feature from the full
NEAT paper.

## How it works

`Network` stores nodes and weighted connections. Mutations can change
connection weights, add or remove a connection, or add or remove a hidden
node. `Population` ranks the networks, keeps the best survivors, and fills the
next generation with mutated copies.

The project is NEAT-inspired, but it does not currently include every standard
NEAT feature such as species grouping, crossover, or innovation numbers.

### XOR

Each network receives three inputs: a bias value, input A, and input B. It has
one output. A network gets one fitness point for each XOR case it predicts
correctly. Training stops when a network scores 4 out of 4.

### Flappy Bird

Each bird owns one network. The network receives:

1. The bird's vertical position.
2. Distance from the bird to the top of the next pipe gap.
3. Distance from the bird to the bottom of the next pipe gap.
4. Horizontal distance to the next pipe.

There is one output. After a sigmoid activation, a value above `0.5` makes the
bird jump. Fitness comes from staying alive, passing pipes, and keeping the
network reasonably small.

The opening screen lets you change population size, survival rate, mutation
chance, pipe gap, visible FPS, and episode length. Training results are also
written to `training_log.csv`.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

PyQt6 is only needed for the separate large network visualizer. To run the
training without it, install just Pygame:

```bash
pip install pygame
```

## Run Flappy Bird

```bash
python flappybird.py
```

Controls:

- `Enter` or the Start Training button starts from the setup screen.
- `P` pauses or resumes training.
- `Esc` returns to the setup screen.
- `S` opens the champion in the PyQt6 visualizer, if PyQt6 is installed.

The panel on the right shows generation stats and a smaller live drawing of
the best-performing network.

## Run XOR

```bash
python XOR.py
```

When a solution is found, its four outputs are printed. If PyQt6 is installed,
the winning network is also displayed in a separate window.

## Main files

- `network.py` - network processing and structural mutations.
- `node.py` and `nerve.py` - basic network parts.
- `population.py` - population ranking and generation creation.
- `flappybird.py` - Pygame simulation and training interface.
- `XOR.py` - XOR training example.
- `pyqtest.py` - optional PyQt6 network visualizer.
- `template.py` - starting point for another experiment.

## Tests

```bash
python -m unittest
```
