import pygame
import numpy as np
from main import initialize_cars, evolve

# Simulation Parameters
n = 10
L = 100

def main():
    # Screen dimensions
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)

    # Car dimensions
    CAR_RADIUS = 10

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Simulation")

    # Define motorways and lanes
    NUM_MOTORWAYS = 4
    MOTORWAY_HEIGHT = SCREEN_HEIGHT // NUM_MOTORWAYS

    lane_y_positions = [
        [(MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 4),
        (MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 2),
        (MOTORWAY_HEIGHT * i + 3 * MOTORWAY_HEIGHT // 4)]
        for i in range(NUM_MOTORWAYS)
    ]

    print(lane_y_positions)

    # Main loop
    running = True
    clock = pygame.time.Clock()

    lanes = initialize_cars(n, L, 5, 0.2, 2)
    print(lanes)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(BLACK)

        # Draw the lanes
        for motorway in lane_y_positions:
            for y in motorway:
                pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y), 2)

        lanes = evolve(lanes, 0.05, 100)
        for i in range(3):
            cars = lanes[i,0]
            for car in cars:
                part = np.floor(car[0]*4/L)
                if part > 3 or part < 0:
                    print(part)
                x = (car[0] - part*L/4) * SCREEN_WIDTH * 4/L
                y = lane_y_positions[int(part)][int(i)]
                pygame.draw.circle(screen, RED, (x,y), radius=CAR_RADIUS)

        # Update the display
        pygame.display.flip()
        clock.tick(60)
        pygame.display.set_caption("Traffic Simulation - {} FPS".format(int(clock.get_fps())))

    pygame.quit()

if __name__ == "__main__":
    main()