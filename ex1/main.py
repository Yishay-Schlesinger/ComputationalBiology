import random
from argparse import ArgumentParser
import pygame as pyg

# initializes

# get user input
parser = ArgumentParser()
parser.add_argument('-N', type=int, help='Number of creatures', default=10000)
parser.add_argument('-R', type=float, help='Percent of fast creatures', default=0.2)
parser.add_argument('-D', type=float, help='Percent of initial infected', default=0.01)
parser.add_argument('-X', type=int, help='Number of generations in which a creature stays infected', default=10)
parser.add_argument('-PA', type=float, help='Probability of infection when infected creatures <T', default=0.9)
parser.add_argument('-PB', type=float, help='Probability of infection when infected creatures >T', default=0.1)
parser.add_argument('-T', type=float, help='The threshold value for changing P (PA <-> PB)', default=0.2)
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
    def __init__(self, location, status, speed):
        self.status = status
        self.speed = speed
        self.location = location
        self.location.next_gen_checkin(self)
        self.location.next_gen_update()
        self.next_gen_location = None
        self.gen_for_healing = 0

    def next_gen_move(self, location, status):
        self.status = status
        self.next_gen_location = location.next_gen_checkin()

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
        return (0, 0, 0) if self.contain is None else stat_color_map[self.contain.status]


class World:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.board_rows = board_size[0]
        self.board_cols = board_size[1]
        self.board = [[Location(i, j) for j in range(len(self.board_rows))] for i in range(len(self.board_cols))]
        self.creatures = self.initialize_creatures()
        self.locations_to_update = set([])

    def initialize_creatures(self):
        creatures = []

        # set random list for the fast cells
        fast_num = int(N * R)
        fast_lst = [10 for fast in range(fast_num)] + [1 for slow in range(N - fast_num)]
        random.shuffle(fast_lst)

        # set random list for the infected cells
        infected_num = int(N * D)
        infected_lst = ["infected" for inf in range(infected_num)] + ["healthy" for heal in range(N - infected_num)]
        random.shuffle(infected_lst)

        # set random indexes for the creatures
        rows_idx_lst = [i for i in range(self.board_size[0])]
        random.shuffle(rows_idx_lst)
        cols_idx_lst = [j for j in range(self.board_size[1])]
        random.shuffle(cols_idx_lst)


        # create the creatures
        for creature_args in zip(rows_idx_lst[:N], cols_idx_lst[:N], infected_lst, fast_lst):
            c = Creature(self.get_location(creature_args[0], creature_args[1]), creature_args[2], creature_args[3])
            creatures.append(c)

        return creatures

    def get_location(self, i, j):
        return self.board[i][j]

    def next_gen(self):
        random.shuffle(self.creatures)
        for c in self.creatures:
            self.creature_next_gen(c)
        self.update_all_locations()

    def update_all_locations(self):
        for loc in self.locations_to_update:
            loc.next_gen_update()

    def creature_next_gen(self, creature):
        if creature.next_gen_location is not None:
            vert_mon_opt, horz_mov_opt = self.movement_options(creature)
            while True:
                creature_row_idx = creature.location.row_idx
                creature_col_idx = creature.location.col_idx
                for step in range(creature.speed):
                    vert_mov = random.choice(vert_mon_opt)
                    horz_mov = random.choice(horz_mov_opt)
                    creature_row_idx += vert_mov
                    creature_col_idx += horz_mov
                    next_loc = self.get_location(creature_row_idx, creature_col_idx)
                if next_loc.contain.next_gen_loc is None:
                    self.creature_next_gen(next_loc.contain)
                if next_loc.next_gen_contain is None:
                    creature.next_gen_move(next_loc, self.creature_next_status(creature, horz_mov_opt, vert_mon_opt))
                    self.locations_to_update.add(creature.location)
                    self.locations_to_update.add(creature.next_gen_location)
                    return

    def creature_next_status(self, creature, horz_mov_opt, vert_mon_opt):
        {"healthy": (255, 255, 255),
         "infected": (255, 0, 0),
         "recovered": (0, 255, 0)}
        if creature.status == "recovered":
            return "recovered"
        if creature.status == "infected":
            creature.gen_for_healing -= 1
            if creature.gen_for_healing == 0:
                return "infected"
            else:
                return "recovered"

        infected_around = 0
        if


    def movement_options(self, creature):
        # vertical movement options
        vertical_movement_options = [-1, 0, 1]
        if creature.location.row_idx == 0:
            vertical_movement_options.remove(-1)
        elif creature.location.row_idx == self.board_rows - 1:
            vertical_movement_options.remove(1)

        # horizontal movement options
        horizontal_movement_options = [-1, 0, 1]
        if creature.location.col_idx == 0:
            horizontal_movement_options.remove(-1)
        elif creature.location.col_idx == self.board_cols - 1:
            horizontal_movement_options.remove(1)

        # return
        return vertical_movement_options, horizontal_movement_options

