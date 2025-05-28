import pygame
import sys
import random
import math
from typing import List
from pyqtest import display_network
from main import main  # your NEAT population manager
from network import Network  # ensure this import matches your Network class path
from pyqtest import display_network

#DISCLAIMER: THE GAME WAS VIBE CODED USING CAHTGPT I DID NOT MAKE MOST OF IT, SOME TWEAKS ARE MINE AND CONNECTING IT TO XOR IS MY WORK
#basically the game logic and visual arent mine, everything else is
# --- Flappy Bird Constants ---
WIN_WIDTH = 500
WIN_HEIGHT = 800
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
PIPE_WIDTH_RANGE = (100, 300)
PIPE_GAP_RANGE = (80, 120)
PIPE_VEL = 5
BASE_HEIGHT = 100
BASE_VEL = 5
FPS = 90

class Bird:
    def __init__(self, x: int, y: int, network: Network):
        self.x = x
        self.y = y
        self.vel = 0
        self.tick_count = 0
        self.height = y
        self.network = network
        self.network.alive = True

    def jump(self):
        self.vel = -10
        self.tick_count = 0
        self.height = self.y

    def update(self):
        self.tick_count += 1
        displacement = self.vel + 0.5 * 3 * self.tick_count
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y += displacement

    def draw(self, win):
        if self.network.alive:
            pygame.draw.rect(win, (255, 255, 0), (self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT))
        else:
            center = (int(self.x + BIRD_WIDTH // 2), int(self.y + BIRD_HEIGHT // 2))
            pygame.draw.circle(win, (255, 0, 0), center, 3)


class Pipe:
    def __init__(self, x: int):
        self.x = x
        pipe_gap = random.randint(PIPE_GAP_RANGE[0], PIPE_GAP_RANGE[1])
        self.height = random.randrange(50, WIN_HEIGHT - pipe_gap - BASE_HEIGHT - 50)
        self.top = self.height
        self.bottom = self.height + pipe_gap
        self.passed = False
        self.pipe_width = random.randint(PIPE_WIDTH_RANGE[0], PIPE_WIDTH_RANGE[1])

    def update(self):
        self.x -= PIPE_VEL

    def collide(self, bird: Bird) -> bool:
        
        bird_rect = pygame.Rect(bird.x, bird.y, BIRD_WIDTH, BIRD_HEIGHT)
        top_rect = pygame.Rect(self.x, 0, self.pipe_width, self.top)
        bottom_rect = pygame.Rect(self.x, self.bottom, self.pipe_width, WIN_HEIGHT - self.bottom)
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

    def off_screen(self) -> bool:
        return self.x + self.pipe_width < 0

    def draw(self, win):
        pygame.draw.rect(win, (0, 255, 0), (self.x, 0, self.pipe_width, self.top))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.bottom, self.pipe_width, WIN_HEIGHT - self.bottom))

class Base:
    def __init__(self):
        self.y = WIN_HEIGHT - BASE_HEIGHT
        self.x1 = 0
        self.x2 = WIN_WIDTH

    def update(self):
        self.x1 -= BASE_VEL
        self.x2 -= BASE_VEL
        if self.x1 + WIN_WIDTH < 0:
            self.x1 = self.x2 + WIN_WIDTH
        if self.x2 + WIN_WIDTH < 0:
            self.x2 = self.x1 + WIN_WIDTH

    def draw(self, win):
        pygame.draw.rect(win, (150, 75, 0), (self.x1, self.y, WIN_WIDTH, BASE_HEIGHT))
        pygame.draw.rect(win, (150, 75, 0), (self.x2, self.y, WIN_WIDTH, BASE_HEIGHT))

class Game:
    """
    One Flappy-Bird episode for a list of NEAT networks.
    If render=False it runs head-less (much faster).
    A single display surface is reused across generations to avoid
    repeatedly creating/destroying the window.
    """

    # ───────── static / shared ─────────
    _pygame_inited = False
    _window        = None
    _clock         = None

    def __init__(self, networks: List[Network], render: bool = True):
        # -------- global pygame context (create once) --------
        if not Game._pygame_inited:
            pygame.init()
            Game._pygame_inited = True

        if Game._window is None:
            Game._window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
            pygame.display.set_caption("Flappy Bird NEAT")
            Game._clock  = pygame.time.Clock()

        self.win   = Game._window
        self.clock = Game._clock
        self.render = render

        # -------- episode state --------
        self.networks = networks
        self.birds  = [Bird(100, WIN_HEIGHT // 2, net) for net in networks]
        self.base   = Base()
        self.pipes  = [Pipe(WIN_WIDTH)]
        self.frame  = 0

        # reset fitness
        for b in self.birds:
            b.network.score = 0

    # ──────────────────────────────────────────────────────────
    # helpers
    def _sigmoid(self, x: float) -> float:
        return 1 / (1 + math.exp(-x))

    def _draw(self) -> None:
        """draw current frame (only if render=True)"""
        self.win.fill((135, 206, 235))
        for pipe in self.pipes:
            pipe.draw(self.win)
        self.base.draw(self.win)
        for bird in self.birds:
            bird.draw(self.win)
        pygame.display.update()

    # ──────────────────────────────────────────────────────────
    def run(self) -> List[int]:
        MAX_FRAMES          = FPS * 100          # ≈ 100 seconds
        COMPLEXITY_PENALTY  = 0.0001             # fitness -= penalty * (#edges + #nodes)

        while any(b.network.alive for b in self.birds):
            # -- timing --
            if self.render:
                self.clock.tick(FPS)            # limit to visible FPS
            else:
                self.clock.tick(0)              # run flat-out
            self.frame += 1

            # -- hard timeout --
            if self.frame >= MAX_FRAMES:
                for b in self.birds:
                    b.network.alive = False
                break

            # -- event handling (only if window is visible) --
            if self.render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                        # grab the current best (highest score) network
                        best_net = max(self.networks, key=lambda n: n.score)
                        # this will block until you close the Qt window
                        display_network(best_net,
                                        width=1200, height=700,
                                        x=400,  y=150)
                        # when you close it, the game loop simply continues


            # -- spawn pipe every 90 frames (~1.5 s at 60 FPS) --
            if self.frame % 90 == 0:
                self.pipes.append(Pipe(WIN_WIDTH))

            # -- update pipes & scoring --
            rem, add_score = [], False
            for pipe in self.pipes:
                pipe.update()
                for bird in self.birds:
                    if bird.network.alive and pipe.collide(bird):
                        bird.network.alive = False
                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        add_score = True
                if pipe.off_screen():
                    rem.append(pipe)

            if add_score:
                for bird in self.birds:
                    if bird.network.alive:
                        bird.network.score += 1

            for r in rem:
                self.pipes.remove(r)

            # -- update each bird still alive --
            for bird in self.birds:
                if not bird.network.alive:
                    continue

                bird.update()

                # next upcoming pipe
                next_pipe = next((p for p in self.pipes
                                  if p.x + p.pipe_width > bird.x), None)

                if next_pipe:
                    inputs = [
                        bird.y / WIN_HEIGHT,
                        (bird.y - next_pipe.height) / WIN_HEIGHT,
                        (next_pipe.bottom - bird.y) / WIN_HEIGHT,
                        next_pipe.x / WIN_WIDTH
                    ]   
                    bird.network.process_network(inputs)

                    z = bird.network.get_output()[0]
                    action = round(self._sigmoid(z))
                    if action == 1:
                        bird.jump()

                # death on ground / ceiling
                if bird.y + BIRD_HEIGHT >= WIN_HEIGHT - BASE_HEIGHT or bird.y <= 0:
                    bird.network.alive = False

            # -- move base & draw (optional) --
            self.base.update()
            if self.render:
                self._draw()

        # -- complexity penalty to discourage bloat --
        if self.frame > 600:
            for net in self.networks:
                net.score -= COMPLEXITY_PENALTY * (len(net.nodes) + len(net.nerves))

        # return scores in same order as input list
        return [net.score for net in self.networks]

        

# --- Main Execution: NEAT Loop ---

if __name__ == "__main__":
    population = main(input_size=4, output_size=1, count=500)
    generation = 0


    while True:
        generation += 1
        print(f"Generation {generation}")
        scores = Game(population.agents).run()

        # assign scores
        for net, score in zip(population.agents, scores):
            net.score = score

        # sort and report
        population.rank_fitness()
        best, avg = max(scores), sum(scores) / len(scores)
        print(f"  Best: {best}, Avg: {avg:.2f}", 
              f"Agents: {len(population.agents)}, Nodes: {len(population.agents[0].nodes)}")


        # evolve
        population.new_generation(0.1)
