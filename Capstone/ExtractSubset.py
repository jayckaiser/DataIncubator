"""
ExtractSubset.py

(C) 2018 by Jay Kaiser <jayckaiser.github.io>
Created January 10, 2018
Updated Jan 10, 2018

Given a CSVed Reddit file and a list of subs to extract from, rewrite the CSVs to include only comments from those subs.

"""

import os
import pickle
import re

def main():
    csv_directory = "/media/jayckaiser/My Passport/reddit/CSV/"
    topN_directory = "/media/jayckaiser/My Passport/reddit/top_subs/"
    topN_subset_directory = "/media/jayckaiser/My Passport/reddit/top_subs_CSV/"

    csvs_to_parse = sorted([f for f in os.listdir(csv_directory)
                            if f >= 'RC_2014-03.csv'  # due to crashing, include this line as necessary
                            # if f == 'RC_2012-03.csv'
                           ])
    # csvs_to_parse = ['RC_2013-01.csv']  # test-case

    for csv_file in csvs_to_parse:
        raw_filename = csv_file[:-4]  # remove the filetype

        defaults, topN = extractTopSubs(topN_directory, raw_filename + '.pkl')
        rewrite_csv(csv_directory, topN_subset_directory, csv_file, subreddits=topN)


def extractTopSubs(directory, file):
    """
    Given the directory where the pickled lists of top 100 subs to search can be found, return the subs for that file.

    :param directory:
    :param file:
    :return:
    """

    file = os.path.join(directory, file)

    defaults, topN = pickle.load(open(file, 'rb'))

    print('Extracted top subreddits for {}.'.format(file), end='\r')
    return defaults, topN


def rewrite_csv(csv_directory, new_directory, file, subreddits):

    original_csv = os.path.join(csv_directory, file)
    new_csv = os.path.join(new_directory, file)

    with open(original_csv, 'r', encoding='utf_8') as FULL, open(new_csv, 'w', encoding='utf_8') as SUBSET:

        print('Extracting and rewriting subsets of {}.'.format(file), end='\r')

        for index, line in enumerate(FULL):
            if index == 0:
                SUBSET.write(line)
                continue

            split_line = line.split('\t', 4)

            # subreddit   created_utc   body   author   score
            subreddit = split_line[0]

            if subreddit in subreddits:

                body = split_line[2]

                if body == "b'[deleted]'":
                    continue

                # remove the byte-string marks
                body = body[2:-1]

                # replace URLs with URL
                url_regex = re.compile(r'''https?://  # header
                                           (?:
                                           [a-zA-Z]|
                                           [0-9]|
                                           [$-_@.&+]|
                                           [!*(),]|
                                           (?:%[0-9a-fA-F]{2})
                                           )+''',
                                       re.X)
                body = re.sub(url_regex, r'URL', body)

                created_utc = split_line[1]
                author = split_line[3]
                score = split_line[4]

                # there are weird things happening here
                if score == "None\n":
                    score = 0

                SUBSET.write( '\t'.join([subreddit, created_utc, body, author, score]) + '\n' )

            if index % 1_000_000 == 0:
                print('Finished {:,}.'.format(index), end='\r', flush=True)

    print('Finished {}.'.format(file))


if __name__ == '__main__':
    main()