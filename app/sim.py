import doctest
import json
import math
from functools import reduce
from operator import __or__
from random import random

# MODELING & SIMULATION
gravitational_constant = 6.67 * (10 ** -11)
init = {
    'Planet': {'name': "Earth", 'time': 0, 'time_step': 0.02, 'x': 0, 'y': 0, 'vx': -.01, 'vy': 0, 'm': 1000},
    'Satellite': {'name': "Moon", 'time': 0, 'time_step': 0.02, 'x': 0, 'y': 5, 'vx': 0.01, 'vy': -0.01,
                  'm': 1000},
    'Sun': {'name': "Sun", 'time': 0, 'time_step': 0.02, 'x': 10, 'y': 2.5, 'vx': 0, 'vy': 0, 'm': 10000},
}


def propagate(agentId, universe):
    """Propagate agentId from `time` to `time + time_step`."""
    state = universe[agentId]
    name = state['name']
    mass = state['m']
    time, time_step, x, y, vx, vy = state['time'], state['time_step'], state['x'], state['y'], state['vx'], state['vy']

    force_x = 0
    force_y = 0

    # Calculate the sum of the gravitational forces acting on the current body based on other celestial bodies
    # GMm/r^2
    for ID, body in universe.items():
        if ID == agentId: continue
        dx = (body['x'] - x)
        dy = (body['y'] - y)
        distance = math.sqrt(
            dx*dx +
            dy*dy)

        force_magnitude = gravitational_constant * mass * body['m']/distance*distance

        force_x += force_magnitude * dx / distance
        force_y += force_magnitude * dy / distance

    accel_x = force_x / mass
    accel_y = force_y / mass

    x += vx * time_step + 0.5 * accel_x * time_step ** 2
    y += vy * time_step + 0.5 * accel_y * time_step ** 2
    vx += accel_x * time_step
    vy += accel_y * time_step

    return {'name': name, 'time': time + time_step, 'time_step': 1.0, 'x': x, 'y': y, 'vx': vx,
            'vy': vy, 'm': mass}


# DATA STRUCTURE

class QRangeStore:
    """
    A Q-Range KV Store mapping left-inclusive, right-exclusive ranges [low, high) to values.
    Reading from the store returns the collection of values whose ranges contain the query.
    ```
    0  1  2  3  4  5  6  7  8  9
    [A      )[B)            [E)
    [C   )[D   )
           ^       ^        ^  ^
    ```
    >>> store = QRangeStore()
    >>> store[0, 3] = 'Record A'
    >>> store[3, 4] = 'Record B'
    >>> store[0, 2] = 'Record C'
    >>> store[2, 4] = 'Record D'
    >>> store[8, 9] = 'Record E'
    >>> store[2, 0] = 'Record F'
    Traceback (most recent call last):
    IndexError: Invalid Range.
    >>> store[2.1]
    ['Record A', 'Record D']
    >>> store[8]
    ['Record E']
    >>> store[5]
    Traceback (most recent call last):
    IndexError: Not found.
    >>> store[9]
    Traceback (most recent call last):
    IndexError: Not found.
    """

    def __init__(self):
        self.store = []

    def __setitem__(self, rng, value):
        (low, high) = rng
        if not low < high: raise IndexError("Invalid Range.")
        self.store.append((low, high, value))

    def __getitem__(self, key):
        ret = [v for (l, h, v) in self.store if l <= key < h]
        if not ret: raise IndexError("Not found.")
        return ret


# doctest.testmod()


# SIMULATOR

def read(t):
    try:
        data = store[t]
    except IndexError:
        data = []
    return reduce(__or__, data, {})


store = QRangeStore()
store[-999999999, 0] = init
times = {agentId: state['time'] for agentId, state in init.items()}

for _ in range(10000):
    for agentId in init:
        t = times[agentId]
        universe = read(t - 0.001)
        if set(universe) == set(init):
            newState = propagate(agentId, universe)
            store[t, newState['time']] = {agentId: newState}
            times[agentId] = newState['time']

with open('./public/data.json', 'w') as f:
    f.write(json.dumps(store.store, indent=4))
