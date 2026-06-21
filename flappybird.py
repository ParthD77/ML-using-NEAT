import csv
import math
import os
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from network import Network
from population import Population


GAME_WIDTH = 500
PANEL_WIDTH = 320
WIN_WIDTH = GAME_WIDTH + PANEL_WIDTH
WIN_HEIGHT = 800
BIRD_X = 100
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
PIPE_WIDTH_RANGE = (80, 120)
PIPE_VEL = 5
BASE_HEIGHT = 30
BASE_VEL = 5

SKY = (135, 206, 235)
PANEL = (28, 35, 48)
PANEL_BOX = (39, 48, 64)
WHITE = (240, 243, 248)
MUTED = (160, 170, 186)
GREEN = (63, 185, 80)
RED = (220, 75, 75)
BLUE = (74, 144, 226)
YELLOW = (255, 220, 65)


@dataclass
class TrainingSettings:
    population_size: int = 100
    survival_rate: float = 0.20
    mutation_rate: float = 1.0
    pipe_gap: int = 125
    fps: int = 90
    max_seconds: int = 100


@dataclass
class TrainingStats:
    generation: int
    previous_best: float = 0
    previous_average: float = 0


class InputBox:
    def __init__(
        self,
        label: str,
        value: str,
        minimum: float,
        maximum: float,
        is_integer: bool,
        y: int,
    ) -> None:
        self.label = label
        self.text = value
        self.minimum = minimum
        self.maximum = maximum
        self.is_integer = is_integer
        self.rect = pygame.Rect(500, y, 180, 40)
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in "0123456789." and len(self.text) < 8:
                if event.unicode != "." or "." not in self.text:
                    self.text += event.unicode

    def get_value(self) -> float:
        try:
            value = float(self.text)
        except ValueError:
            value = self.minimum
        value = max(self.minimum, min(self.maximum, value))
        return int(round(value)) if self.is_integer else value

    def draw(self, window: pygame.Surface, font: pygame.font.Font) -> None:
        label = font.render(self.label, True, WHITE)
        window.blit(label, (210, self.rect.y + 9))
        color = BLUE if self.active else MUTED
        pygame.draw.rect(window, PANEL_BOX, self.rect, border_radius=5)
        pygame.draw.rect(window, color, self.rect, 2, border_radius=5)
        value = font.render(self.text, True, WHITE)
        window.blit(value, (self.rect.x + 10, self.rect.y + 8))


class SettingsScreen:
    def __init__(self, window: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.window = window
        self.clock = clock
        self.font = pygame.font.SysFont("consolas", 22)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.fields = [
            InputBox("Bird count (10-300)", "100", 10, 300, True, 250),
            InputBox("Survival rate (0.05-0.95)", "0.20", 0.05, 0.95, False, 305),
            InputBox("Mutation chance (0-1)", "1.0", 0, 1, False, 360),
            InputBox("Pipe gap (90-220)", "125", 90, 220, True, 415),
            InputBox("Visible FPS (30-240)", "90", 30, 240, True, 470),
            InputBox("Episode seconds (10-300)", "100", 10, 300, True, 525),
        ]
        self.start_button = pygame.Rect(310, 620, 200, 55)

    def run(self) -> Optional[TrainingSettings]:
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return self._settings()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        return self._settings()
                for field in self.fields:
                    field.handle_event(event)

            self._draw()

    def _settings(self) -> TrainingSettings:
        values = [field.get_value() for field in self.fields]
        return TrainingSettings(
            population_size=int(values[0]),
            survival_rate=float(values[1]),
            mutation_rate=float(values[2]),
            pipe_gap=int(values[3]),
            fps=int(values[4]),
            max_seconds=int(values[5]),
        )

    def _draw(self) -> None:
        self.window.fill(PANEL)
        title = self.title_font.render("Flappy Bird NEAT Lab", True, WHITE)
        subtitle = self.small_font.render(
            "Choose training settings, then watch the population learn.",
            True,
            MUTED,
        )
        self.window.blit(title, (185, 95))
        self.window.blit(subtitle, (180, 150))

        pygame.draw.rect(
            self.window,
            (23, 29, 40),
            (175, 205, 470, 390),
            border_radius=10,
        )
        for field in self.fields:
            field.draw(self.window, self.small_font)

        pygame.draw.rect(self.window, BLUE, self.start_button, border_radius=7)
        start = self.font.render("START TRAINING", True, WHITE)
        self.window.blit(start, start.get_rect(center=self.start_button.center))

        hint = self.small_font.render(
            "Enter starts | Esc quits | values are clamped to safe limits",
            True,
            MUTED,
        )
        self.window.blit(hint, (170, 705))
        pygame.display.flip()


class Bird:
    def __init__(self, network: Network):
        self.x = BIRD_X
        self.y = WIN_HEIGHT // 2
        self.vel = 0
        self.tick_count = 0
        self.network = network
        self.network.alive = True

    def jump(self) -> None:
        self.vel = -10
        self.tick_count = 0

    def update(self) -> None:
        self.tick_count += 1
        displacement = self.vel + 1.5 * self.tick_count
        displacement = min(displacement, 16)
        if displacement < 0:
            displacement -= 2
        self.y += displacement

    def draw(self, window: pygame.Surface) -> None:
        if self.network.alive:
            pygame.draw.rect(
                window,
                YELLOW,
                (self.x, int(self.y), BIRD_WIDTH, BIRD_HEIGHT),
                border_radius=4,
            )


class Pipe:
    def __init__(self, x: int, gap_size: int):
        self.x = x
        self.pipe_width = random.randint(*PIPE_WIDTH_RANGE)
        gap_change = random.randint(-10, 10)
        self.gap_size = max(80, gap_size + gap_change)
        self.height = random.randrange(
            40,
            WIN_HEIGHT - self.gap_size - BASE_HEIGHT - 40,
        )
        self.top = self.height
        self.bottom = self.height + self.gap_size
        self.passed = False

    def update(self) -> None:
        self.x -= PIPE_VEL

    def collide(self, bird: Bird) -> bool:
        bird_rect = pygame.Rect(
            bird.x,
            int(bird.y),
            BIRD_WIDTH,
            BIRD_HEIGHT,
        )
        top_rect = pygame.Rect(self.x, 0, self.pipe_width, self.top)
        bottom_rect = pygame.Rect(
            self.x,
            self.bottom,
            self.pipe_width,
            WIN_HEIGHT - self.bottom,
        )
        return bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect)

    def off_screen(self) -> bool:
        return self.x + self.pipe_width < 0

    def draw(self, window: pygame.Surface) -> None:
        pygame.draw.rect(window, GREEN, (self.x, 0, self.pipe_width, self.top))
        pygame.draw.rect(
            window,
            GREEN,
            (
                self.x,
                self.bottom,
                self.pipe_width,
                WIN_HEIGHT - self.bottom,
            ),
        )


class Base:
    def __init__(self):
        self.y = WIN_HEIGHT - BASE_HEIGHT
        self.x1 = 0
        self.x2 = GAME_WIDTH

    def update(self) -> None:
        self.x1 -= BASE_VEL
        self.x2 -= BASE_VEL
        if self.x1 + GAME_WIDTH < 0:
            self.x1 = self.x2 + GAME_WIDTH
        if self.x2 + GAME_WIDTH < 0:
            self.x2 = self.x1 + GAME_WIDTH

    def draw(self, window: pygame.Surface) -> None:
        pygame.draw.rect(
            window,
            (150, 75, 0),
            (self.x1, self.y, GAME_WIDTH, BASE_HEIGHT),
        )
        pygame.draw.rect(
            window,
            (150, 75, 0),
            (self.x2, self.y, GAME_WIDTH, BASE_HEIGHT),
        )


class Game:
    SURVIVAL_REWARD = 0.1
    PIPE_REWARD = 100.0
    COMPLEXITY_PENALTY = 0.02

    def __init__(
        self,
        window: pygame.Surface,
        clock: pygame.time.Clock,
        networks: List[Network],
        settings: TrainingSettings,
        stats: TrainingStats,
    ) -> None:
        self.window = window
        self.clock = clock
        self.networks = networks
        self.settings = settings
        self.stats = stats
        self.birds = [Bird(network) for network in networks]
        self.base = Base()
        self.pipes = [Pipe(GAME_WIDTH, settings.pipe_gap)]
        self.frame = 0
        self.paused = False
        self.font = pygame.font.SysFont("consolas", 17)
        self.small_font = pygame.font.SysFont("consolas", 13)
        self.heading_font = pygame.font.SysFont("consolas", 21, bold=True)

        for network in self.networks:
            network.score = 0

    def run(self) -> Tuple[List[float], str]:
        max_frames = self.settings.fps * self.settings.max_seconds
        spawn_every = 72

        while any(bird.network.alive for bird in self.birds):
            self.clock.tick(self.settings.fps)
            action = self._handle_events()
            if action != "continue":
                return [network.score for network in self.networks], action
            if self.paused:
                self._draw()
                continue

            self.frame += 1
            if self.frame >= max_frames:
                break
            if self.frame % spawn_every == 0:
                self.pipes.append(Pipe(GAME_WIDTH, self.settings.pipe_gap))

            self._update_birds()
            self._update_pipes()
            self.base.update()
            self._draw()

        for network in self.networks:
            network.alive = False
            network.score -= self.COMPLEXITY_PENALTY * (
                len(network.nodes) + len(network.nerves)
            )
        self._draw()
        return [network.score for network in self.networks], "finished"

    def _handle_events(self) -> str:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "settings"
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_s:
                    try:
                        from pyqtest import display_network
                    except ImportError:
                        print("PyQt6 is not installed. Run: pip install PyQt6")
                    else:
                        best_network = max(
                            self.networks,
                            key=lambda network: network.score,
                        )
                        display_network(best_network)
        return "continue"

    def _update_birds(self) -> None:
        for bird in self.birds:
            if not bird.network.alive:
                continue

            bird.network.score += self.SURVIVAL_REWARD
            bird.update()
            next_pipe = next(
                (
                    pipe
                    for pipe in self.pipes
                    if pipe.x + pipe.pipe_width > bird.x
                ),
                None,
            )

            if next_pipe is not None:
                inputs = [
                    bird.y / WIN_HEIGHT,
                    (bird.y - next_pipe.top) / WIN_HEIGHT,
                    (next_pipe.bottom - bird.y) / WIN_HEIGHT,
                    (next_pipe.x - bird.x) / GAME_WIDTH,
                ]
                bird.network.process_network(inputs)
                output = bird.network.get_output()[0]
                jump_probability = self._sigmoid(output)
                if jump_probability > 0.5:
                    bird.jump()

            if bird.y <= 0 or bird.y + BIRD_HEIGHT >= WIN_HEIGHT - BASE_HEIGHT:
                bird.network.alive = False

    def _update_pipes(self) -> None:
        for pipe in self.pipes:
            pipe.update()

            for bird in self.birds:
                if bird.network.alive and pipe.collide(bird):
                    bird.network.alive = False

            if not pipe.passed and pipe.x + pipe.pipe_width < BIRD_X:
                pipe.passed = True
                for bird in self.birds:
                    if bird.network.alive:
                        bird.network.score += self.PIPE_REWARD

        self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]

    @staticmethod
    def _sigmoid(value: float) -> float:
        # This form avoids overflow for very large network outputs.
        if value >= 0:
            return 1 / (1 + math.exp(-value))
        exp_value = math.exp(value)
        return exp_value / (1 + exp_value)

    def _draw(self) -> None:
        self.window.fill(SKY)
        pygame.draw.rect(self.window, SKY, (0, 0, GAME_WIDTH, WIN_HEIGHT))
        for pipe in self.pipes:
            pipe.draw(self.window)
        self.base.draw(self.window)
        for bird in self.birds:
            bird.draw(self.window)
        self._draw_panel()
        pygame.display.flip()

    def _draw_panel(self) -> None:
        panel_rect = pygame.Rect(GAME_WIDTH, 0, PANEL_WIDTH, WIN_HEIGHT)
        pygame.draw.rect(self.window, PANEL, panel_rect)
        champion = max(self.networks, key=lambda network: network.score)
        alive = sum(network.alive for network in self.networks)

        self.window.blit(
            self.heading_font.render("TRAINING STATS", True, WHITE),
            (GAME_WIDTH + 20, 22),
        )
        lines = [
            f"Generation: {self.stats.generation}",
            f"Alive: {alive}/{len(self.networks)}",
            f"Current best: {champion.score:.1f}",
            f"Last best: {self.stats.previous_best:.1f}",
            f"Last average: {self.stats.previous_average:.1f}",
            f"Champion nodes: {len(champion.nodes)}",
            f"Champion edges: {len(champion.nerves)}",
        ]
        for index, text in enumerate(lines):
            rendered = self.font.render(text, True, WHITE)
            self.window.blit(rendered, (GAME_WIDTH + 20, 66 + index * 27))

        self.window.blit(
            self.heading_font.render("CHAMPION NETWORK", True, WHITE),
            (GAME_WIDTH + 20, 285),
        )
        network_rect = pygame.Rect(GAME_WIDTH + 15, 325, PANEL_WIDTH - 30, 330)
        pygame.draw.rect(self.window, PANEL_BOX, network_rect, border_radius=8)
        self._draw_network(champion, network_rect)

        controls = [
            "S: open PyQt network view",
            "P: pause",
            "Esc: return to settings",
        ]
        for index, text in enumerate(controls):
            rendered = self.small_font.render(text, True, MUTED)
            self.window.blit(rendered, (GAME_WIDTH + 20, 690 + index * 24))

        if self.paused:
            paused = self.heading_font.render("PAUSED", True, YELLOW)
            self.window.blit(paused, (GAME_WIDTH + 115, 760))

    def _draw_network(self, network: Network, rect: pygame.Rect) -> None:
        visible_nodes = [node for node in network.nodes if node.depth >= 0]
        if not visible_nodes:
            return

        layers = {}
        for node in visible_nodes:
            layers.setdefault(node.depth, []).append(node)
        max_depth = max(layers)
        positions = {}

        for depth, nodes in layers.items():
            if max_depth == 0:
                x = rect.centerx
            else:
                x = rect.left + 25 + int(
                    depth / max_depth * (rect.width - 50)
                )
            spacing = rect.height / (len(nodes) + 1)
            for index, node in enumerate(nodes, start=1):
                positions[node] = (x, rect.top + int(spacing * index))

        for nerve in network.nerves:
            if nerve.start not in positions or nerve.end not in positions:
                continue
            color = GREEN if nerve.weight >= 0 else RED
            thickness = max(1, min(4, int(abs(nerve.weight) * 2) + 1))
            pygame.draw.line(
                self.window,
                color,
                positions[nerve.start],
                positions[nerve.end],
                thickness,
            )

        for node, position in positions.items():
            if node.type == 0:
                color = BLUE
                label = "I"
            elif node.type == 2:
                color = YELLOW
                label = "O"
            else:
                color = (170, 110, 220)
                label = "H"
            pygame.draw.circle(self.window, color, position, 11)
            pygame.draw.circle(self.window, WHITE, position, 11, 1)
            text = self.small_font.render(label, True, PANEL)
            self.window.blit(text, text.get_rect(center=position))


def save_training_stats(
    generation: int,
    scores: List[float],
    champion: Network,
    filename: str = "training_log.csv",
) -> None:
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        if not file_exists:
            writer.writerow(
                [
                    "generation",
                    "best_score",
                    "average_score",
                    "champion_nodes",
                    "champion_edges",
                ]
            )
        writer.writerow(
            [
                generation,
                max(scores),
                sum(scores) / len(scores),
                len(champion.nodes),
                len(champion.nerves),
            ]
        )


def run_training(
    window: pygame.Surface,
    clock: pygame.time.Clock,
    settings: TrainingSettings,
) -> str:
    population = Population(
        input_size=4,
        output_size=1,
        count=settings.population_size,
    )
    generation = 0
    previous_best = 0.0
    previous_average = 0.0

    while True:
        generation += 1
        stats = TrainingStats(generation, previous_best, previous_average)
        scores, action = Game(
            window,
            clock,
            population.agents,
            settings,
            stats,
        ).run()
        if action != "finished":
            return action

        population.rank_fitness()
        champion = population.agents[0]
        previous_best = max(scores)
        previous_average = sum(scores) / len(scores)
        print(
            f"Generation {generation:4d} | "
            f"best {previous_best:8.2f} | "
            f"average {previous_average:8.2f} | "
            f"nodes {len(champion.nodes):2d} | "
            f"edges {len(champion.nerves):2d}"
        )
        save_training_stats(generation, scores, champion)
        population.new_generation(
            settings.survival_rate,
            settings.mutation_rate,
        )


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Flappy Bird NEAT Lab")
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        settings = SettingsScreen(window, clock).run()
        if settings is None:
            break
        action = run_training(window, clock, settings)
        if action == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()
