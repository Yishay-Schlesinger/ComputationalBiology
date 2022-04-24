import pip


# make sure all the needed modules are installed, if not install them
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])


[import_or_install(package_name) for package_name in ['random', 'argparse', 'matplotlib', 'numpy', 'pygame']]

import random
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import pygame

# get user input, or use the default
parser = ArgumentParser()
parser.add_argument('-N', type=int, help='Number of creatures', default=30000)
parser.add_argument('-R', type=float, help='Percent of fast creatures', default=0.2)
parser.add_argument('-D', type=float, help='Percent of initial infected', default=0.05)
parser.add_argument('-X', type=int, help='Number of generations in which a creature stays infected', default=3)
parser.add_argument('-PA', type=float, help='Probability of infection when infected creatures <T', default=0.9)
parser.add_argument('-PB', type=float, help='Probability of infection when infected creatures >T', default=0.1)
parser.add_argument('-T', type=float, help='The threshold value for changing P (PA <-> PB)', default=0.03)
args = parser.parse_args()

# set
N = args.N
R = args.R
D = args.D
X = args.X
PA = args.PA
PB = args.PB
T = args.T

# constant
BOARD_SIZE = [200, 200]

# CHECKING INPUTS
if N > BOARD_SIZE[0] * BOARD_SIZE[1] or N < 0:
    raise Exception(f"N need to be - N > {BOARD_SIZE[0] * BOARD_SIZE[1]} or N < 0")
if X < 0:
    raise Exception(f'X need to be - X > 0')
if R < 0 or R > 1:
    raise Exception(f'R need to be -  1 < R < 0')
if D < 0 or D > 1:
    raise Exception(f'D need to be -  1 < D < 0')
if PA < 0 or PA > 1:
    raise Exception(f'PA need to be -  1 < PA < 0')
if PB < 0 or PB > 1:
    raise Exception(f'PB need to be -  1 < PB < 0')
if T < 0 or T > 1:
    raise Exception(f'T need to be -  1 < T < 0')

"""
Creature class
"""
class Creature:
    def __init__(self, location, status, speed=1):
        # status : healthy , infected, recovered
        self.status = status
        self.speed = speed
        self.location = location
        self.location.next_gen_checkin(self)
        self.location.next_gen_update()
        self.next_gen_location = None
        self.gen_for_healing = X

    # first next generation update
    def next_gen_move(self, location, status):
        self.status = status
        self.next_gen_location = location
        self.next_gen_location.next_gen_checkin(self)

    # final next generation update
    def next_gen_update(self):
        self.location = self.next_gen_location
        self.next_gen_location = None


"""
Location class
"""
class Location:
    def __init__(self, i, j):
        # initialize the color to be white
        self.color = (255, 255, 255)
        # initialize the location content to None
        self.contain = None
        self.next_gen_contain = None
        #  location object's index on the board
        self.row_idx = i
        self.col_idx = j

    # first next generation update
    def next_gen_checkin(self, creature):
        self.next_gen_contain = creature

    # final next generation update
    def next_gen_update(self):
        self.contain = self.next_gen_contain
        self.color = self.get_color_from_status()
        self.next_gen_contain = None

    def get_color_from_status(self):
        # rgb color map for each creature status (the location color which contain the creature)
        stat_color_map = {"healthy": (0, 255, 0),
                          "infected": (255, 0, 0),
                          "recovered": (0, 0, 255)}
        # if the contain is not None return color by the status,if is None the location is empty so return white.
        if self.contain is not None:
            return stat_color_map[self.contain.status]
        else:
            return (255, 255, 255)


"""
World class
everything is under the control of this class (game manager)
"""
class World:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.board_rows = board_size[0]
        self.board_cols = board_size[1]
        # initizlize all the Locations object, on each place on the board
        self.board = [[Location(i, j) for j in range(self.board_cols)] for i in range(self.board_rows)]
        # number of infected
        self.infected_num = int(N * D)
        # initialize creature
        self.creatures = self.initialize_creatures()
        # after first updates of going to next generation, I want to do another update only for the needed locations,
        # without duplications, so initialize set.
        self.locations_to_update = set()
        # initialize P by T and D(=infected percent)
        self.P = PA if D < T else PB

    # initialize creatures on the board
    def initialize_creatures(self):
        creatures = []

        # set random list for the fast cells
        fast_num = int(N * R)
        fast_lst = [10 for fast in range(fast_num)] + [1 for slow in range(N - fast_num)]
        random.shuffle(fast_lst)

        # set random list for the infected cells
        infected_lst = ["infected" for inf in range(self.infected_num)] + ["healthy" for heal in
                                                                           range(N - self.infected_num)]
        # set random indexes for the creatures
        rows_idx_lst = [i for i in range(self.board_rows)]
        cols_idx_lst = [j for j in range(self.board_cols)]
        indexes = set()
        c = 0
        while len(indexes) < N:
            indexes.add((random.choice(rows_idx_lst), random.choice(cols_idx_lst)))

        # create the creatures
        for creatur_args in zip(indexes, infected_lst, fast_lst):
            c = Creature(self.get_location(creatur_args[0][0], creatur_args[0][1]), creatur_args[1], creatur_args[2])
            creatures.append(c)
        # return
        return creatures

    # get the Location object in this indexes on the board
    def get_location(self, i, j):
        return self.board[i][j]

    # go to next generation
    def next_gen(self):
        # for each creature find its next location on the board, and do first update for the creatures and the locations
        for c in self.creatures:
            self.creature_next_loc(c)
        # final update
        self.next_gen_update()

    # final update for all the creature and the relevant Locations
    def next_gen_update(self):
        # final update for all the creature and the relevant Locations
        for c in self.creatures:
            c.next_gen_update()
        self.update_all_locations()
        # initialize the locations_to_update for the next generation
        self.locations_to_update = set()
        # update the P for the next generation
        self.P = PA if (self.infected_num / N) < T else PB

    # final update for all the relevant Location
    def update_all_locations(self):
        for loc in self.locations_to_update:
            loc.next_gen_update()

    # get the next generation location of the creature, avoiding collisions
    def creature_next_loc(self, creature):
        move_options = self.movement_options(creature)
        # get the new status
        next_status = self.creature_next_status(creature, self.movement_options(creature, steps=1))
        # for random choise of the next step
        random.shuffle(move_options)
        # try for each optional movement till the creature find a place to stop
        for movement in move_options:
            # calculate the new indexes
            creature_row_idx = creature.location.row_idx
            creature_col_idx = creature.location.col_idx
            vert_mov = movement[0]
            horz_mov = movement[1]
            creature_row_idx += vert_mov
            creature_col_idx += horz_mov
            # if it is a fast creature there is going to another iteration, so set new mov_opt for next step
            next_loc = self.get_location(creature_row_idx, creature_col_idx)
            # all the options to update and avoid collision -
            # If the next potential Location of the current creature is not empty, check if the creature in this
            # next potential Location is already checked in other location for the next generation,
            # If not try other option
            if next_loc.next_gen_contain is not None:
                continue
            elif next_loc.contain is None:
                return self.creature_next_loc_update(creature, next_loc, next_status)
            elif next_loc.contain == creature:
                return self.creature_next_loc_update(creature, next_loc, next_status)
            elif next_loc.contain.next_gen_location is not None:
                if next_loc.next_gen_contain is None:
                    return self.creature_next_loc_update(creature, next_loc, next_status)

    # help func for first update
    def creature_next_loc_update(self, creature, next_loc, next_status):
        creature.next_gen_move(next_loc, next_status)
        self.locations_to_update.add(creature.location)
        self.locations_to_update.add(creature.next_gen_location)

    # return the status of given creature for the next generation
    def creature_next_status(self, creature, movement_options):
        # if already infected, cant be sick again
        if creature.status == "recovered":
            return "recovered"
        # if infected count the generations from infected and when the creature will recover
        if creature.status == "infected":
            creature.gen_for_healing -= 1
            if creature.gen_for_healing == 0:
                self.infected_num -= 1
                return "recovered"
            else:
                return "infected"

        # if the creature healthy, check its neighbors
        infected_around = 0
        for [y, x] in movement_options:
            neighbor = self.get_location(creature.location.row_idx + y, creature.location.col_idx + x).contain
            if neighbor is not None:
                if neighbor.status == "infected":
                    infected_around += 1
        # if no neighbor is sick
        if infected_around == 0:
            return "healthy"
        # each sick neighbor need to be consider, so usr the probability of staying healthy in power of the sicks number
        elif np.random.binomial(1, pow(1 - self.P, infected_around)) == 0:
            self.infected_num += 1
            return "infected"
        else:
            return "healthy"

    # movement options for the next generation
    def movement_options(self, creature, steps=None):
        row_idx = creature.location.row_idx
        col_idx = creature.location.col_idx
        steps = creature.speed if steps is None else 1
        # vertical movement options
        vertical_movement_options = [-steps, 0, steps]
        if row_idx - steps < 0:
            vertical_movement_options.remove(-steps)
        elif row_idx + steps > self.board_rows - 1:
            vertical_movement_options.remove(steps)
        # horizontal movement options
        horizontal_movement_options = [-steps, 0, steps]
        if col_idx - steps < 0:
            horizontal_movement_options.remove(-steps)
        elif col_idx + steps > self.board_cols - 1:
            horizontal_movement_options.remove(steps)
        # return
        return [[y, x] for y in vertical_movement_options for x in horizontal_movement_options]

# set a new World object
world = World()
generation = 0
X_AXE = [generation]
Y_AXE = [world.infected_num]
# initial pygame
pygame.init()
surface = pygame.display.set_mode((410, 410))
# move generation till there is 0 infected
while world.infected_num != 0:
    world.next_gen()
    generation += 1
    X_AXE.append(generation)
    Y_AXE.append(world.infected_num)
    for i in range(int(200)):
        for j in range(int(200)):
            # Draw creatures on the screen.
            offset = 5
            a = i * 2 + offset
            b = j * 2 + offset
            pygame.draw.rect(surface, world.get_location(i, j).color, (a, b, 2, 2))
    pygame.display.flip()

# Plot lists 'x' and 'y'
plt.plot(X_AXE, Y_AXE)

# Plot axes labels and show the plot
plt.xlabel('X-axis Label')
plt.ylabel('Y_AXE-axis Label')
plt.show()
