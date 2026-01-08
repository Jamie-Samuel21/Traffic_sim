import pygame
import numpy as np
from dataclasses import dataclass

@dataclass
class SimParams:
    n: int = 50                                                 # Number of cars
    L: float = 100.0                                            # Length of road
    R: float = 1.0                                              # Radius of cars (Unit)
    C: float = 4.0                                              # Over / Under take length

    a: float = 0.05                                             # Time step length (Unphysical)
    v_rand: float = 10.0                                        # Random velocities fluctuations
    v_avg: float = 20.0                                         # Average speed
    D: float = 0.1                                              # Rate of velocity fluctuations


    Elj: float = 1.0                                            # Energy scale (Unit)
    drag: float = 1.0                                           # drag coefficent (Unit)
    overtake_dt: float = 0.1                                    # Overtake timestep (Unphysical)

    @property
    def dist(self):
        return 2 * self.R


from traffic_model import (
    create_cars,
    seperate,
    evolve
)

class TrafficSimulation:
    def __init__(self):
        pygame.init()

        self.params = SimParams()
        self.lanes = create_cars(self.params.n, self.params.L)

        self.t = 0.0
        self.counter = 0.0
        self.vrms = 10.0
        self.check = True

        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 700
        self.NUM_MOTORWAYS = 4

        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()

        self._setup_lanes()
        self._load_car()

    def _setup_lanes(self):
        MOTORWAY_HEIGHT = self.SCREEN_HEIGHT // self.NUM_MOTORWAYS
        self.LANE_HEIGHT = MOTORWAY_HEIGHT // 4

        self.lane_y_positions = [
            [(MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 4),
             (MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 2),
             (MOTORWAY_HEIGHT * i + 3 * MOTORWAY_HEIGHT // 4)]
            for i in range(self.NUM_MOTORWAYS)
        ]

        self.lane_surface = pygame.Surface(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        for motorway in self.lane_y_positions:
            for y in motorway:
                pygame.draw.rect(
                    self.lane_surface, (60, 60, 60),
                    (0, y - self.LANE_HEIGHT // 2,
                     self.SCREEN_WIDTH, self.LANE_HEIGHT)
                )

    def _load_car(self):
        self.CAR_RADIUS = 16
        self.car_img = pygame.image.load(
            "/home/jamiesamuel/PhD work/Traffic_sim/pointer/car.png"
        )
        self.car_img = pygame.transform.rotate(self.car_img, -90)
        self.car_img = pygame.transform.scale(
            self.car_img, (self.CAR_RADIUS * 3, self.CAR_RADIUS * 2)
        )

    def update(self):
        if self.vrms > 1e-3 and self.check:
            self.lanes, self.t, self.vrms = seperate(
                self.lanes, self.params, self.t
            )
        else:
            self.check = False
            self.lanes, self.t, self.vrms, self.counter = evolve(
                self.lanes, self.params, self.t, self.counter
            )

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.lane_surface, (0, 0))

        for lane_idx in range(3):
            for car in self.lanes[lane_idx]:
                part = int(np.floor(car[0] * 4 / self.params.L))
                x = (car[0] - part * self.params.L / 4) * \
                    self.SCREEN_WIDTH * 4 / self.params.L
                y = self.lane_y_positions[part][lane_idx]

                self.screen.blit(
                    self.car_img,
                    (x - self.CAR_RADIUS, y - self.CAR_RADIUS)
                )

        pygame.display.flip()
        pygame.display.set_caption(f"time = {self.t:.3f}")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()
            self.draw()
            self.clock.tick(100)

        pygame.quit()


if __name__ == "__main__":
    TrafficSimulation().run()
