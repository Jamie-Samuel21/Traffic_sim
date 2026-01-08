import numpy as np
from dataclasses import dataclass

# =========================
# Parameter class
# =========================

@dataclass
class SimParams:
    n: int = 100                                                # Number of cars
    L: float = 100.0                                            # Length of road
    R: float = 1.0                                              # Radius of cars (Unit)
    C: float = 2.0                                              # Over / Under take length

    a: float = 0.05                                             # Time step length (Unphysical)
    v_rand: float = 10.0                                        # Random velocities fluctuations
    v_avg: float = 20.0                                         # Average speed
    D: float = 1.0                                              # Rate of velocity fluctuations


    Elj: float = 1.0                                            # Energy scale (Unit)
    drag: float = 1.0                                           # drag coefficent (Unit)
    overtake_dt: float = 0.2                                    # Overtake timestep (Unphysical)

    @property
    def dist(self):
        return 2 * self.R


# =========================
# Initialisation
# =========================

def create_cars(n, L):                                          # Creates the cars and lanes
    positions = np.random.uniform(0, L, size=n)                 # Inital postitions of cars
    angles = np.random.uniform(0, 2 * np.pi, size=n)            # Inital velocity flucation angle
    lane = np.arange(n) % 3
    force = np.zeros_like(lane, dtype=float)

    cars = np.column_stack((positions, angles, force))          # creates cars arrays
    cars[:, 2] = 0.0

    lanes = [                                                   # puts cars into lanes
        cars[lane == i][cars[lane == i][:, 0].argsort()]
        for i in range(3)
    ]
    return lanes


# =========================
# Forces
# =========================

def Fs(dx, dist, Elj):                                          # linear Force to push cars appart
    if 0 < dx < dist:
        return Elj * (dx - dist)
    if -dist < dx < 0:
        return Elj * (dx + dist)
    return 0.0


def Fc(dx, D, Elj):                                             # coulomb repulsive force
    return -Elj * 0.1 / (dx - D) ** 2

def Flj(dx, D, Elj):                                            # Lenard Jones force
    F = 4 * Elj * (-12 * D ** 12 * dx ** (-13) + 6 * D ** 6 * dx ** (-7))
    return (F)


# =========================
# Separation phase
# =========================

def seperate(lanes, params, t):                                 # pushes apart randomly place cars
    velocities = []

    for i in range(3):                                          # loops though cars
        cars = lanes[i]
        n = len(cars)

        for j, car in enumerate(cars):                          # calcuates forces on neighbouring cars
            dx1 = (cars[(j - 1) % n][0] - car[0] + params.L / 2) % params.L - params.L / 2
            dx2 = (cars[(j + 1) % n][0] - car[0] + params.L / 2) % params.L - params.L / 2

            force = Fs(dx1, params.dist, params.Elj) + Fs(dx2, params.dist, params.Elj)
            cars[j, 2] = force / params.drag                    # appends veclocity to cars

        velocities.extend(cars[:, 2])                           # puts all vecocities in a big list

    vmax = max(np.max(np.abs(velocities)), 1e-3)                # calculates vmax
    dt = min(params.a / vmax, 0.3)                              # calculates dt

    vrms = np.sqrt(np.mean(np.array(velocities) ** 2))          # calculates vrms

    for i in range(3):                                          # loops though lanes, updates positions then resets veclocties
        cars = lanes[i]
        cars[:, 0] += cars[:, 2] * dt                          
        cars[:, 2] = 0.0
        cars[:, 0] %= params.L                                  # Perodic BC

    return lanes, t + dt, vrms


# =========================
# Lane changing
# =========================

def overtake(lanes, params):                                    # does overtakes
    for i in range(2):                                          # loops over inner two lanes
        cars = lanes[i]
        cars_above = lanes[i + 1]
        overtake_idx = []

        for j, car in enumerate(cars):                          # loops though cars in a lane, checks if close to car infrount, if not skisps to next car
            dx = (cars[(j + 1) % len(cars)][0] - car[0]) % params.L
            if abs(dx) > params.C:
                continue

            if np.cos(cars[(j + 1) % len(cars)][1]) - np.cos(car[1]) > 0:   # checks is going faster than car infrount
                continue

            for other in cars_above:                            # Loops though cars in one lane outer, checks no car is too close
                dx2 = (other[0] - car[0] + params.L / 2) % params.L - params.L / 2
                if abs(dx2) < params.C:
                    break
            else:
                overtake_idx.append(j)

        if overtake_idx:                                        # If passes all tests preforms the overtake
            movers = cars[overtake_idx]
            lanes[i] = np.delete(cars, overtake_idx, axis=0)
            lanes[i + 1] = np.vstack((lanes[i + 1], movers))
            lanes[i + 1] = lanes[i + 1][lanes[i + 1][:, 0].argsort()]

    return lanes


def undertake(lanes, params):                                   # Preformes undertakes
    for i in range(1, 3):                                       # Loops through outer two lanes
        cars = lanes[i]
        cars_below = lanes[i - 1]
        undertake_idx = []

        for j, car in enumerate(cars):                          # Loops though cars, checks if any close cars in inner lane
            for other in cars_below:
                dx = (other[0] - car[0] + params.L / 2) % params.L - params.L / 2
                if abs(dx) < params.C:
                    break
            else:
                undertake_idx.append(j)

        if undertake_idx:                                       # preforms undertake
            movers = cars[undertake_idx]
            lanes[i] = np.delete(cars, undertake_idx, axis=0)
            lanes[i - 1] = np.vstack((lanes[i - 1], movers))
            lanes[i - 1] = lanes[i - 1][lanes[i - 1][:, 0].argsort()]

    return lanes


# =========================
# Evolution
# =========================

def evolve(lanes, params, t, counter):                          # Updates simulation
    velocities = []

    for i in range(3):                                          # Loops through lanes
        cars = lanes[i]
        n = len(cars)

        for j, car in enumerate(cars):                          # Loops through cars
            dx = (cars[(j + 1) % n][0] - car[0]) % params.L
            force = Fc(dx, 2 * params.R, params.Elj)            # calculates force from car infrount
                                                                # calculates veclocites
            cars[j, 2] = max(force / params.drag  + params.v_rand * np.cos(car[1]) + params.v_avg, 0)

        velocities.extend(cars[:, 2])                           # makes big list of velocities

    vmax = max(np.max(np.abs(velocities)), 1e-3)                # calcualtes vmax
    dt = min(params.a / vmax, 0.1)                              # calcualtes dt
    vrms = np.sqrt(np.mean(np.array(velocities) ** 2))          # calcualtes vrms

    for i in range(3):                                          # loops though lanes and updates position and angle
        cars = lanes[i]
        cars[:, 0] += cars[:, 2] * dt
        cars[:, 1] += np.sqrt(2 * params.D * dt) * np.random.randn(len(cars))
        cars[:, 0] %= params.L

    t += dt                                                     # increases t

    if t > counter:                                             # does overtakes if every overtake_dt
        lanes = overtake(lanes, params)
        lanes = undertake(lanes, params)
        counter += params.overtake_dt

    return lanes, t, vrms, counter

