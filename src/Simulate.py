# Imports
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
    CAR_RADIUS = 16

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Traffic Simulation")

    # Define motorways and lanes
    NUM_MOTORWAYS = 4
    MOTORWAY_HEIGHT = SCREEN_HEIGHT // NUM_MOTORWAYS
    LANE_HEIGHT = MOTORWAY_HEIGHT // 4

    lane_y_positions = [
        [(MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 4),
        (MOTORWAY_HEIGHT * i + MOTORWAY_HEIGHT // 2),
        (MOTORWAY_HEIGHT * i + 3 * MOTORWAY_HEIGHT // 4)]
        for i in range(NUM_MOTORWAYS)
    ]

    lanes = initialize_cars(n, L, 5, 0.2, 2)
    print(lanes)

    # Load Car Image
    car_img = pygame.image.load("res/car.png")
    car_img = pygame.transform.rotate(car_img, -90)
    car_img = pygame.transform.scale(car_img, (CAR_RADIUS*3, CAR_RADIUS*2))

    # Create Lane Transparent Surface
    lane_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for motorway in lane_y_positions:

        # For Each Lane
        for y in motorway:

            # Draw The Lane Background
            pygame.draw.rect(lane_surface, (70, 70, 70), (0, y - LANE_HEIGHT//2, SCREEN_WIDTH, LANE_HEIGHT))

            # Draw the motorway center line as dashes
            for x in range(0, SCREEN_WIDTH, 20):
                pygame.draw.line(lane_surface, (*WHITE, 120), (x, y), (x + 10, y), 2)
            
            # Draw each lane border
            pygame.draw.line(lane_surface, WHITE, (0, y - LANE_HEIGHT//2), (SCREEN_WIDTH, y - LANE_HEIGHT//2), 2)
            pygame.draw.line(lane_surface, WHITE, (0, y + LANE_HEIGHT//2), (SCREEN_WIDTH, y + LANE_HEIGHT//2), 2)

        # Draw the border across all lanes
        pygame.draw.line(lane_surface, WHITE, (0, motorway[0] - LANE_HEIGHT//2), (SCREEN_WIDTH, motorway[0] - LANE_HEIGHT//2), 8)
        pygame.draw.line(lane_surface, WHITE, (0, motorway[2] + LANE_HEIGHT//2), (SCREEN_WIDTH, motorway[2] + LANE_HEIGHT//2), 8)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(BLACK)

        # Evolve Traffic
        lanes = evolve(lanes, 0.05, 100)

        # Draw The Lanes
        screen.blit(lane_surface, (0, 0))

        # Draw The Cars
        for i in range(3):
            cars = lanes[i, 0]
            for car in cars:
                part = np.floor(car[0]*4/L)
                if part > 3 or part < 0:
                    print(part)
                x = (car[0] - part*L/4) * SCREEN_WIDTH * 4/L
                y = lane_y_positions[int(part)][int(i)]
                # pygame.draw.circle(screen, RED, (x,y), radius=CAR_RADIUS)

                # Draw car as image
                screen.blit(car_img, (x-CAR_RADIUS, y-CAR_RADIUS))

        # Update The Display
        pygame.display.flip()
        clock.tick(60)
        pygame.display.set_caption("Traffic Simulation - {} FPS".format(int(clock.get_fps())))

    pygame.quit()

if __name__ == "__main__":
    main()