import random
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import pygame


# initializes

# get user input
parser = ArgumentParser()
parser.add_argument('-N', type=int, help='Number of creatures', default=30000)
parser.add_argument('-R', type=float, help='Percent of fast creatures', default=0.2)
parser.add_argument('-D', type=float, help='Percent of initial infected', default=0.001)
parser.add_argument('-X', type=int, help='Number of generations in which a creature stays infected', default=3)
parser.add_argument('-PA', type=float, help='Probability of infection when infected creatures <T', default=0.8)
parser.add_argument('-PB', type=float, help='Probability of infection when infected creatures >T', default=0.05)
parser.add_argument('-T', type=float, help='The threshold value for changing P (PA <-> PB)', default=0.02)
args = parser.parse_args()

# TODO: CHECKING INPUTS

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


class Creature:
    def __init__(self, location, status, speed=1):
        self.status = status
        self.speed = speed
        self.location = location
        self.location.next_gen_checkin(self)
        self.location.next_gen_update()
        self.next_gen_location = None
        self.gen_for_healing = X

    def next_gen_move(self, location, status):
        self.status = status
        self.next_gen_location = location
        self.next_gen_location.next_gen_checkin(self)

    def next_gen_update(self):
        self.location = self.next_gen_location
        self.next_gen_location = None


class Location:
    def __init__(self, i, j):
        self.color = (0, 0, 0)
        self.contain = None
        self.next_gen_contain = None
        self.row_idx = i
        self.col_idx = j

    def next_gen_checkin(self, creature):
        self.next_gen_contain = creature

    def next_gen_update(self):
        self.contain = self.next_gen_contain
        self.color = self.get_color_from_status()
        self.next_gen_contain = None

    def get_color_from_status(self):
        stat_color_map = {"healthy": (255, 255, 255),
                          "infected": (255, 0, 0),
                          "recovered": (0, 255, 0)}
        if self.contain is None:
            return (0, 0, 0)
        else:
            return stat_color_map[self.contain.status]


class World:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.board_rows = board_size[0]
        self.board_cols = board_size[1]
        self.board = [[Location(i, j) for j in range(self.board_cols)] for i in range(self.board_rows)]
        self.infected_num = int(N * D)
        self.creatures = self.initialize_creatures()
        self.locations_to_update = set([])
        self.P = PA if D < T else PB
        print(self.P)

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
        while len(indexes) < N:
            indexes.add((random.choice(rows_idx_lst), random.choice(cols_idx_lst)))

        # create the creatures
        for creatur_args in zip(indexes, infected_lst, fast_lst):
            c = Creature(self.get_location(creatur_args[0][0], creatur_args[0][1]), creatur_args[1], creatur_args[2])
            creatures.append(c)
        # return
        return creatures

    def get_location(self, i, j):
        return self.board[i][j]

    def next_gen(self):
        # random.shuffle(self.creatures)
        is_creatures_ready_for_next_gen = [False]
        while (not all(is_creatures_ready_for_next_gen)):
            is_creatures_ready_for_next_gen = []
            for c in self.creatures:
                self.creature_next_loc(c)
                is_creatures_ready_for_next_gen.append(c.next_gen_location is not None)
        self.next_gen_update()

    def next_gen_update(self):
        self.update_all_locations()
        self.locations_to_update = set([])
        for c in self.creatures:
            c.next_gen_update()
        self.P = PA if (self.infected_num / N) < T else PB
        print(self.P)

    def update_all_locations(self):
        for loc in self.locations_to_update:
            loc.next_gen_update()

    def creature_next_loc(self, creature):
        if creature.next_gen_location is None:
            creature_row_idx = creature.location.row_idx
            creature_col_idx = creature.location.col_idx
            move_options = self.movement_options(creature)
            next_status = self.creature_next_status(creature, move_options)
            for movement in move_options:
                creature_row_idx = creature.location.row_idx
                creature_col_idx = creature.location.col_idx
                vert_mov = movement[0]
                horz_mov = movement[1]
                creature_row_idx += vert_mov
                creature_col_idx += horz_mov
                # if it is a fast creature there is going to another iteration, so set new mov_opt for next step
                next_loc = self.get_location(creature_row_idx, creature_col_idx)
                if(next_loc.contain is not None) and (next_loc.contain is not creature):
                    if next_loc.contain.next_gen_location is None:
                        continue
                if next_loc.next_gen_contain is None:
                    creature.next_gen_move(next_loc, next_status)
                    self.locations_to_update.add(creature.location)
                    self.locations_to_update.add(creature.next_gen_location)

    def creature_next_status(self, creature, movement_options):
        if creature.status == "recovered":
            return "recovered"
        if creature.status == "infected":
            creature.gen_for_healing -= 1
            if creature.gen_for_healing == 0:
                self.infected_num -= 1
                return "recovered"
            else:
                return "infected"

        infected_around = 0
        for [y, x] in movement_options:
            neighbor = self.get_location(creature.location.row_idx + y, creature.location.col_idx + x).contain
            if neighbor is not None:
                if neighbor.status == "infected":
                    infected_around += 1
        if infected_around == 0:
            return "healthy"
        elif np.random.binomial(1, pow(1 - self.P,infected_around))== 0:
            self.infected_num += 1
            return "infected"
        else:
            return "healthy"

    def movement_options(self, creature):
        row_idx = creature.location.row_idx
        col_idx = creature.location.col_idx
        steps = creature.speed
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


world = World()
generation = 0
X_AXE = [generation]
Y_AXE = [world.infected_num]
pygame.init()
surface = pygame.display.set_mode((410, 410))
while (world.infected_num != 0):
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
            pygame.draw.rect(surface, world.get_location(i, j).get_color_from_status(), (a, b, 2, 2))
    pygame.display.flip()
    print("gen:", generation, "num:", world.infected_num)

# Plot lists 'x' and 'y'
plt.plot(X_AXE, Y_AXE)

# Plot axes labels and show the plot
plt.xlabel('X-axis Label')
plt.ylabel('Y_AXE-axis Label')
plt.show()






