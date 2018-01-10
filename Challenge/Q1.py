#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Q1

(C) 2017 by Jay Kaiser <jayckaiser.github.io>
Updated Oct 26 by Jay Kaiser

run_experiment actually finds the results for each question, first using find_sequence to find an array
of 100,000 iterations of this process which are then averaged together into their appropriate means,
standard deviations and the conditional probability (given the problem at hand), using find_statistics and
find_conditional_probability_of_sums respectively. This process is repeated until is_true_average is yields False,
at which case all three variables have converged to ten decimal places.

"""

import random
import numpy as np


def main():
    # Results for questions regarding 16 moves.
    # run_experiment(16, 13, 5, 13)

    # Results for questions regarding 512 moves.
    run_experiment(512, 311, 7, 43)


def find_sequence(number_of_moves, number_of_runs):
    """
    Given a number of moves, returns the total random sequence of the knight, across a number of runs.
    This is to account for the randomness inherent in the problem.

    :param number_of_moves:
    :param number_of_runs:
    :return numpy array of size number_of_moves * number_of_runs:

    """

    # Note: While I could have created an algorithm to simulate the knight's movement, because there are only 16
    #       total possibilities, I simply manually plotted each space's allowable next moves.
    #       If a much larger square was given, then the algorithm would have been faster. But here, this is faster.
    next_move_choices = {0: [6, 9],
                         1: [7, 8, 10],
                         2: [4, 9, 11],
                         3: [5, 10],
                         4: [2, 10, 13],
                         5: [3, 11, 12, 14],
                         6: [0, 8, 13, 15],
                         7: [1, 9, 14],
                         8: [1, 6, 14],
                         9: [0, 2, 7, 15],
                         10: [1, 3, 4, 12],
                         11: [2, 5, 13],
                         12: [5, 10],
                         13: [4, 6, 11],
                         14: [5, 7, 8],
                         15: [6, 9]
                         }

    all_moves = []

    for run in range(number_of_runs):

        current_square = 0
        list_of_moves = []

        for i in range(number_of_moves):
            next_move = random.choice(next_move_choices.get(current_square))
            list_of_moves.append(next_move)
            current_square = next_move

        all_moves.append(list_of_moves)

    return np.array(all_moves)


def find_statistics(total_moves_array):
    """
    Returns the cumulative statistics from the numpy array.

    :param total_moves_array:
    :return two ints (mean and standard deviation of dataset):
    """
    mean = np.average(np.average(total_moves_array, axis=1))
    std = np.average(np.std(total_moves_array, axis=1))

    return mean, std


def find_conditional_probability_of_sums(total_moves_array, A, B):
    """
    Finds the probability that the sum is divisible by A given it is divisible by B, across all runs in the total array.

    :param total_moves_array:
    :param A:
    :param B:
    :return float representing the given probability described above:
    """

    all_sums = np.sum(total_moves_array, axis=1)
    givenB = all_sums[all_sums % B == 0]
    AandB = givenB[givenB % A == 0]

    return len(AandB) / len(givenB)


def is_true_average(old_average, new_average, total, runs_per_iteration):
    """
    The averages I'm obtaining aren't precise enough. I'm going to keep running the script until a precision level
    of 10 decimal places is reached, weighting the old averages with the total runs so far and adding the new ones.

    :param old_average:
    :param new_average:
    :param total:
    :param runs_per_iteration:
    :return boolean, declaring whether the two averages did not converge:
    :return the true average, unchanged between iterations to 10 decimal places:
    """
    prior_run_count = total * runs_per_iteration

    cum_average = (old_average * prior_run_count + new_average * runs_per_iteration) / (prior_run_count + runs_per_iteration)
    return (abs(cum_average - old_average) >= 0.0000000001), cum_average


def run_experiment(number_of_turns, modulo, A, B):
    """
    Runs the experiment with the given values as indicated by the Challenge.

    :param number_of_turns:
    :param modulo:
    :param A:
    :param B:
    :return a print-out to console of all statistics:
    """

    iterations = 100000

    # The first 100,000 iterations.
    turns = find_sequence(number_of_turns, iterations)
    total_avg, total_std = find_statistics(turns)
    total_cond_prob = find_conditional_probability_of_sums(turns, A, B)
    print(total_avg, total_std, total_cond_prob, end=" ")

    # run until all three results converge.
    n = 1
    while n < 100:  # this is a failsafe so this literally does not run forever
    # I used n < 10000 for finding the solutions to T=16 n < 100 for T=512.

        turns = find_sequence(number_of_turns, iterations)
        cum_avg, cum_std = find_statistics(turns)
        cum_cond_prob = find_conditional_probability_of_sums(turns, A, B)

        meanRepeat, total_avg = is_true_average(total_avg, cum_avg, n, iterations)
        stdRepeat, total_std = is_true_average(total_std, cum_std, n, iterations)
        condProbRepeat, total_cond_prob = is_true_average(total_cond_prob, cum_cond_prob, n, iterations)
        print(total_avg, total_std, total_cond_prob, end=" ")

        if not meanRepeat and not stdRepeat and not condProbRepeat:
            print("All three results converged after {:,} iterations.".format(n * 100000))
            break

        n += 1

    else:
        print("One or more of the results did not converge after {:,} iterations.".format(n * 100000))

    print("Turns: {}\n".format(number_of_turns),
          "Mean % {}: {:.10f}\n".format(modulo, total_avg % modulo),
          "Std: {:.10f}\n".format(total_std),
          "P(divisible by {}|divisible by {}): {:.10f}\n".format(A, B, total_cond_prob))

if __name__ == "__main__":
    main()
