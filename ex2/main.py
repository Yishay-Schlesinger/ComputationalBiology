# Liav Trabelsy - 315870345
# Yishay Schlesinger -208438119

import numpy as np
import random
from statistics import mean


def printing(solutions, fitness_scores, matrix_size, greater_sign_index):
    lines = []
    # add ' ' and lines to make it look better
    for row in solutions[fitness_scores.index(max(fitness_scores))]:
        line1 = list(row)
        [line1.insert(i, ' ') for i in range(1, matrix_size * 2, 2)]
        line1 = [str(line1[i]) for i in range(matrix_size * 2)]
        line2 = [' ' for space in range(matrix_size * 2)]
        lines.append(line1)
        lines.append(line2)
    # add the greater sign where it is needed
    for greater in greater_sign_index:
        if greater[0] == greater[2]:
            if greater[1] < greater[3]:
                lines[greater[0] * 2][greater[3] * 2 - 1] = ">"
            if greater[1] > greater[3]:
                lines[greater[0] * 2][greater[1] * 2 - 1] = "<"
        if greater[1] == greater[3]:
            if greater[0] < greater[2]:
                lines[greater[2] * 2 - 1][greater[1] * 2] = "v"
            if greater[0] > greater[2]:
                lines[greater[0] * 2 - 1][greater[1] * 2] = "^"
    # print the board
    [print("".join(l)) for l in lines]


if __name__ == '__main__':
    # get file_path from user
    file_path = input("Write the path for the input file: ")
    # get input
    with open(file_path) as input_file:
        inp = input_file.readlines()
    # set input in constant
    matrix_size = int(inp[0][0])
    num_of_given_digits = int(inp[1][:-1])
    # set given_digits dict, key - indexes(i,j) , value - value...
    given_digits_index_dict = {}
    for l_given_digits in inp[2:2 + num_of_given_digits]:
        given_digits_index_dict[(int(l_given_digits[0]) - 1, int(l_given_digits[2]) - 1)] = int(l_given_digits[4])
    # set list for greater sign
    num_of_greater_sign = int(inp[2 + num_of_given_digits][:-1])
    greater_sign_index = []
    for l_greater_sign in inp[3 + num_of_given_digits:3 + num_of_given_digits + num_of_greater_sign]:
        greater_sign_index.append(
            [int(l_greater_sign[0]) - 1, int(l_greater_sign[2]) - 1, int(l_greater_sign[4]) - 1,
             int(l_greater_sign[6]) - 1])

    # set constants
    population_size = 100
    # restriction from the instruction
    max_optimizations = matrix_size
    # set
    mutation_num = matrix_size * 2
    # for each index without duplication error you get 1 point , so in the best case you get 'matrix_size^2' points,
    # moreover for each correct greater sign you get 1 point, so in the best case you get 'num_of_greater_sign' points,
    # combine the above and get 'best score'= the score that we want to get and then we will know we finished
    best_score = matrix_size * matrix_size + num_of_greater_sign

    # I give each algorithm 20 opportunities to solve the problem (each opportunity up to 2000 generation),
    # if the algorithm is not solved, return information on the loop with the best max score value
    for algo in ["Regular", "Lemark", "Darvin"]:
    #for algo in ["Darvin"]:
        # information for results analysis
        info_gen_num = []
        info_mean = []
        info_max = []

        # I give each algorithm 20 opportunities to solve the problem
        for trying in range(20):

            # set the solutions for the first generation
            solutions = []
            # I give each algorithm 20 opportunities to solve the problem
            for p in range(population_size):
                # Use random permutation for each row
                current_sol = np.array(
                    [np.random.permutation(list(range(1, matrix_size + 1))) for i in range(matrix_size)])
                solutions.append(current_sol)
            solutions = np.array(solutions)

            # restriction to have specific given numbers in a specific indexes
            for sol in solutions:
                for given_digit in given_digits_index_dict.keys():
                    # get the current index of the given value
                    given_digit_loc = list(sol[given_digit[0]]).index(given_digits_index_dict[given_digit])
                    # swap with the value in the given_digit place
                    sol[given_digit[0], given_digit[1]], sol[given_digit[0], given_digit_loc] = \
                        sol[given_digit[0], given_digit_loc], sol[given_digit[0], given_digit[1]]

            #printing(solutions, [0 for i in range(population_size)], matrix_size, greater_sign_index)

            # start generation
            gen_num = 0
            # is the algo finished
            finish = False

            # tmp list for the loop info
            tmp_info_gen_num = []
            tmp_info_mean = []
            tmp_info_max = []

            # run till -
            while gen_num <= 2000:
                # in the darvin algo we dont want that the optimization will effect so create copy for later
                if algo == "Darvin":
                    solutions_copy = np.array([np.array(solutions[i]) for i in range(len(solutions))])
                if algo != "Regular":
                    # optimization - on the > (greater sign) :
                    # take for the optimization only greater signs in the rows and only if its index
                    # is not the same as given_digit
                    grater_sign_for_optimization = [greater for greater in greater_sign_index
                                                    if (greater[0] == greater[2]) and (greater[0], greater[1]) not in
                                                    given_digits_index_dict and (greater[2], greater[3]) not in
                                                    given_digits_index_dict]
                    for sol in solutions:
                        # shuffel for randomness
                        random.shuffle(grater_sign_for_optimization)
                        # maximum 'matrix_size' number of optimizations
                        for k in range(min(len(grater_sign_for_optimization), max_optimizations)):
                            greater_idx = grater_sign_for_optimization[k]
                            # if > is not right -> swap
                            if sol[greater_idx[0], greater_idx[1]] <= sol[greater_idx[2], greater_idx[3]]:
                                sol[greater_idx[0], greater_idx[1]], sol[greater_idx[2], greater_idx[3]] \
                                    = sol[greater_idx[2], greater_idx[3]], sol[greater_idx[0], greater_idx[1]]

                # calculate the fitness score
                fitness_scores = []
                # for each solution
                for s in range(len(solutions)):
                    sol_fitness_score = 0
                    # get for each index 1 point if there is not duplicate
                    for j in range(matrix_size):
                        sol_fitness_score += len(np.unique(solutions[s][:, j]))
                    # get for each greater sign 1 point if it is correct
                    for greater_idx in greater_sign_index:
                        if solutions[s][greater_idx[0]][greater_idx[1]] > solutions[s][greater_idx[2]][greater_idx[3]]:
                            sol_fitness_score += 1
                    # add the score to the list
                    fitness_scores.append(sol_fitness_score)

                # printing(solutions, [0 for i in range(population_size)], matrix_size, greater_sign_index)

                # print information
                # add information to the list
                tmp_info_gen_num.append(gen_num)
                tmp_info_max.append(max(fitness_scores))
                tmp_info_mean.append(mean(fitness_scores))

                # check if finished
                if best_score in fitness_scores:
                    print("FINISHED", algo)
                    # print the matrix
                    print("THE MATRIX:")
                    printing(solutions, fitness_scores, matrix_size, greater_sign_index)
                    # set new info and sign to finish this algorithm
                    finish = True
                    info_max = tmp_info_max
                    info_gen_num = tmp_info_gen_num
                    info_mean = tmp_info_mean
                    break

                # the channels of the numpy matrix to take for the next generation
                # the choice is affected by the scores (high_score -> high probability , and vice versa)
                # make min-max normalization for the probability for each score
                max_score = max(fitness_scores)
                min_score = min(fitness_scores)
                # the probability
                prob = [(fitness_scores[c] - min_score) / (max_score - min_score) for c in range(len(fitness_scores))]
                # take 90 solution to the next generation, chosen by the above probability
                next_gen_channels = random.choices(list(range(population_size)), weights=prob,
                                                   k=int(population_size * 0.9))
                # take the best solution with the best score and put it 10 times in the next generation
                next_gen_channels = next_gen_channels + \
                                    [fitness_scores.index(max(fitness_scores)) for v in
                                     range(int(population_size * 0.1))]
                # set the next generation
                # in the darvin algo we dont want that the optimization will effect so set the solutions to the copy
                # that I created before
                if algo == "Darvin":
                    solutions = solutions_copy
                next_gen = [np.array(solutions[i]) for i in next_gen_channels]

                # indexes for mutations and crossover by probability
                crossover_prob = np.random.choice([0, 1], population_size, p=[0.6, 0.4])
                mutations_prob = np.random.choice([0, 1], population_size, p=[0.6, 0.4])

                # for each new solution
                for i in range(population_size):
                    # do crossover if needed
                    if crossover_prob[i]:
                        # chose another parent for crossover
                        other_happy_parent_idx = random.randint(0, population_size - 1)
                        # chose row for crossover
                        crossover_row = random.randint(1, matrix_size - 2)
                        # do swap in the chosen row
                        next_gen[i][crossover_row:], next_gen[other_happy_parent_idx][crossover_row:] = \
                            next_gen[other_happy_parent_idx][crossover_row:], next_gen[i][crossover_row:]

                    # do mutations if needed
                    if mutations_prob[i]:
                        for m in range(mutation_num):
                            # get random row and column indexes for the mutation
                            # the mutation is a swap between the 2 randomly chosen location
                            row_mut = random.randint(0, matrix_size - 1)
                            col_mut1 = random.randint(0, matrix_size - 1)
                            col_mut2 = random.randint(0, matrix_size - 1)
                            # make sure that the first location is not on given_digit
                            while (row_mut, col_mut1) in given_digits_index_dict:
                                col_mut1 = random.randint(0, matrix_size - 1)
                            # make sure that the second location is not on given_digit
                            while (row_mut, col_mut2) in given_digits_index_dict:
                                col_mut2 = random.randint(0, matrix_size - 1)
                            # swap -> mutation
                            next_gen[i][row_mut, col_mut1], next_gen[i][row_mut, col_mut2] = \
                                next_gen[i][row_mut, col_mut2], next_gen[i][row_mut, col_mut1]

                # printing(solutions, [0 for i in range(population_size)], matrix_size, greater_sign_index)

                # set the new_generation to solutions
                solutions = np.array(next_gen)
                # for next generation
                gen_num += 1

                # update info if needed
                if gen_num == 2000:
                    if len(info_max) > 0:
                        if max(info_max) < max(tmp_info_max):
                            info_max = tmp_info_max
                            info_gen_num = tmp_info_gen_num
                            info_mean = tmp_info_mean
            if finish:
                break

        # LIAV DO NOT DELETE NOTHING ABOVE
        # WRITE HERE THE CODE FOR THE GRAPHS
        # YES IT IS REALLY UGLY I DONT CARE
        # NOTICE: 'info_gen_num for' x - axis , 'info_mean' y - axis / 'info_max' - y axis
        # NOTICE: this code (here the comment with you future code) is going to run 3 times for each algorithm
        #         you can check the current algorithm with 'algo'
        # TO DELETE LINE 121?
