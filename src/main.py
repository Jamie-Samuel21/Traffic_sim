import numpy as np


def initialize_cars(n, L, S, d, ST):  # n is no. of cars, L is length of motorway, S is avg. speed and d is std. dev of speed.
                                    # ST is stopping distance ie min of LJ potential ish


    lanes = np.empty((3, 1), dtype=object)

    for i in range(3):
        cars = np.zeros((n, 4))

        # Randomly initialize the positions between 0 and L
        cars[:, 0] = np.linspace(0, L, n, endpoint=False)

        # Initialize the speeds with a Gaussian distribution around S
        cars[:, 1] = np.random.normal(S, S * d, n)

        cars[:, 2] = np.random.normal(ST, ST * d, n)
        cars[:, 3] = 0
        lanes[i,0] = cars

    return lanes

#print(initialize_cars(3, 100, 5, 0.3, 2))

def Flj(p, ST1, Elj):  # change R for average of first and second radius.
    F = -4 * Elj * (-12 * ST1 ** 12 * p ** (-13) + 6 * ST1 ** 6 * p ** (-7))
    return (F)

def forceLJ(cars1, cars2, L):
    dx = cars1[:, 0:1].T - cars2[:, 0:1]

    dx[:, :] = np.where(dx[:, :] < -0.8 * L, dx[:, :] + L, dx[:, :])
    dx[:, :] = np.where(dx[:, :] > 0.8 * L, dx[:, :] - L, dx[:, :])

    D = dx

    D[D == 0] = np.inf
    D[D > 0] = np.inf
    force_mag = Flj(D, cars1[:, 2], 1)

    return np.sum(force_mag, axis=0)


def closecars(D, ST):
    mask = (D >= -ST) & (D < 0)

    columns_within_range = np.any(mask, axis=0)

    column_indices = np.where(columns_within_range)[0]

    return column_indices

def noclosecars(D, ST):
    mask = (D >= -ST) & (D <= ST)

    # Find the columns that have all False values in the mask
    columns_no_values_in_range = np.all(~mask, axis=0)

    # Get the indices of those columns
    column_indices = np.where(columns_no_values_in_range)[0]

    return(column_indices)

def cars_out(lanes):
    cars = np.empty((1, 3))
    for i in range(3):
        cars = np.vstack((cars, lanes[i, 0]))

    return(cars[1:])


def evolve(lanes, a, L):
    velocties = np.array([0])
    for i in range(3):
        cars = lanes[i,0]
        force = forceLJ(cars, cars, L)
        cars[:, 3] += force
        cars[:, 3] += cars[:,1]
        velocties = np.hstack((velocties, cars[:, 3]))

    speeds = np.abs(velocties)
    vmax = np.max(speeds[1:])
    print('vmax = ' + str(vmax))
    dt = a / vmax
    print('dt = :' + str(dt))

    for i in range(3):
        cars = lanes[i, 0]
        cars[:, 0] += cars[:, 3] * dt
        cars[:, 3] = 0
        cars[:, 0] = np.where(cars[:, 0] > L, cars[:, 0] - L, cars[:, 0])

    for i in range(2):
        cars = lanes[i, 0]
        dx = cars[:, 0:1].T - cars[:, 0:1]
        dx[:, :] = np.where(dx[:, :] < -0.8 * L, dx[:, :] + L, dx[:, :])
        dx[:, :] = np.where(dx[:, :] > 0.8 * L, dx[:, :] - L, dx[:, :])

        overtake = closecars(dx, 3)

        if len(overtake) > 0:
            noneligable = []

            for j in overtake:
                xpos = lanes[i,0][j,0]
                take = True
                for car in lanes[i+1,0]:
                    if abs(xpos - car[0]) < 3:
                        take = False

                if take == False:
                    noneligable.append(j)

            eligible = [i for i in overtake if i not in noneligable]

            overtakingcars = cars[eligible, :]
            lanes[i,0] = np.delete(cars, eligible, axis = 0)
            lanes[i+1, 0] = np.append(lanes[i + 1, 0], overtakingcars, axis = 0)


    for i in range(1,3):
        carsouter = lanes[i, 0]
        carsinner = lanes[i -1, 0]
        dx = carsouter[:, 0:1].T - carsinner[:, 0:1]
        dx[:, :] = np.where(dx[:, :] < -0.8 * L, dx[:, :] + L, dx[:, :])
        dx[:, :] = np.where(dx[:, :] > 0.8 * L, dx[:, :] - L, dx[:, :])

        undertake = noclosecars(dx, 3)

        if len(undertake) > 0:

            undertakingcars = carsouter[undertake, :]
            lanes[i,0] = np.delete(carsouter, undertake, axis = 0)
            lanes[i - 1, 0] = np.append(lanes[i - 1, 0], undertakingcars, axis = 0)

    return lanes



