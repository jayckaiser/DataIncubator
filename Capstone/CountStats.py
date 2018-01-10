"""
CountStats.py

(C) 2018 by Jay Kaiser <jayckaiser.github.io>
Created Jan 5, 2018
Updated Jan 5, 2018

Given a CSVed Reddit file, count up the unique number of users and their number of comments in that subreddit,
as well as the total comments for each subreddit.

"""

import dill as pickle
import os
from collections import defaultdict


def main():
    stats_folder = "D:/reddit/stats/"
    CSV_folder = "D:/reddit/CSV/"

    #files_to_do = os.listdir(CSV_folder)
    files_to_do = ["RC_2012-{}.csv".format(str(i).zfill(2)) for i in range(3, 4)]

    for file in files_to_do:
        previous_output = find_file_stats(file, CSV_folder)
        pickle_stats(file, stats_folder, previous_output)


def find_file_stats(file, directory):
    """
    Returns Pandas DataFrames and counts of the aforementioned stats above, ignoring deleted comments.

    :param file: string representing the path to the file whose stats are to be found
    :return:
    """

    print("\rStarted processing {}.".format(file), end='')

    subreddits = {}

    with open(os.path.join(directory, file), 'r') as FILE:
        for count, line in enumerate(FILE):
            if count == 0:
                continue

            line = line.split('\t', 4)

            # subreddit   created_utc   body   author   score
            subreddit = line[0]
            body = line[2]
            author = line[3]
            score = line[4]

            # Weird data case that must be accounted for.
            if score == "None\n":
                score = 0
            else:
                score = int(score)

            # Deleted comments should be ignored.
            if body == "b'[deleted]'":
                continue

            if subreddit not in subreddits:
                # make a new entry for that subreddit, initialized to zero
                subreddits[subreddit] = {
                    "unique_users": set(),  # the unique users who post per subreddit
                    "total_score": 0,  # total score per subreddit (to be avg by num of comments)
                    "total_number_of_comments": 0,  # num of comments per subreddit
                    "total_comments_length": 0  # total length of all comments per subreddit (to be avged later)
                }

            subreddits[subreddit]['unique_users'].add(author)
            subreddits[subreddit]['total_score'] += score
            subreddits[subreddit]['total_number_of_comments'] += 1
            subreddits[subreddit]['total_comments_length'] += len(body) - 3  # accounting for the b'' characters of the string

            if count % 1000000 == 0:
                print("\r{}: Processed {:,} so far.".format(file, count), end='')

    return subreddits


def pickle_stats(file, path, previous_output):

    file = file[:file.index(".csv")]
    with open(os.path.join(path, file + ".pkl"), 'wb') as handle:
        pickle.dump(previous_output, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('\rPickled {}.'.format(file))


if __name__ == "__main__":
    main()
