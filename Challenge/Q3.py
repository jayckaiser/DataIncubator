#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Q3.py

This is the same code submitted to the Data Incubator during the challenge, but extended.

(C) 2017 by Jay Kaiser <jayckaiser.github.io>
Updated Oct 29, 2017

Convert raw Reddit Datastore into CSV data with only useful information;
Iterate through specific subreddits and find politic trends

 """

import json, sys, os
from glob import glob
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt


def main():

    to_work_on_csv_files = [
                 ]
    already_parsed_csvs = ['2014-01',
                           '2014-02',
                           '2014-03',
                           '2015-04',
                           '2015-05',
                           '2015-06',
                           '2016-04',
                           '2016-09',
                           '2016-10',
                           '2016-11',
                           '2016-12',
                           '2017-09',
                           ]

    # these represent the x-coordinates for each of the dates for graphing
    date_values = [1, 2, 3, 16, 17, 18, 28, 33, 34, 35, 36, 45]

    """Complete all stages below to run all parts from scratch."""
    #stageOne(to_work_on_csv_files)
    #stageTwo(already_parsed_csvs)

# these are the fields to take from the JSON lines of Reddit data.
# each year has different ones so this is the smallest subset shared by all three files.
fields = ['subreddit',
          'subreddit_id',
          'created_utc',
          'id',
          'parent_id',
          'body',
          'author',
          'score',
          'link_id',
          'edited',
          'gilded',
          'retrieved_on',
          'distinguished',
          'controversiality',
          ]

# These are politically-charged words and phrases from the 2016 campaign.
# Seeing their change over time could provide useful insights as to when and how political views changed
# throughout the course of the years before and after the election.
political_words = [r'republicans?',
                   r'conservatives?',
                   r'trump',
                   r'make america great again|maga\b',

                   r'democrats?',
                   r'liberals?',
                   r'hillary|clinton|hillary clinton',
                   r'emails?',
                   r'barack|obama|barack obama',
                   r'bernie|sanders|bernie sanders',

                   r'america',
                   r'americans?',

                   r'abortion',
                   r'marijuana',
                   r'legalization',

                   r'immigration',
                   r'foreigners?',
                   r'mexic(o|ans?)',
                   r'(border )?wall',

                   r'gun control',
                   r'guns',
                   r'shooting',

                   r'gay marriage',
                   r'homosexual relations',

                   r'jobs?',
                   r'economy',
                   r'wall street',
                   r'recession',

                   r'(universal )?health (care|insurance)',

                   r'global warming',
                   r'climate change',

                   r'russia',
                   r'hacking',
                   r'spying',

                   r'islam(ic)?',
                   r'radicalis(m|ts?)',
                   r'terroris(m|ts?)',

                   r'racis(m|ts?)',
                   r'black lives matter',

                   r'white supremacists?',
                   r'(neo[- ]?)?nazis?',
                   r'white lives matter',
                   r'confederacy',
                   ]

# These are politically-motivated subreddits (as well as some less-so but still significant).
# It is from here that statistics will be found.
political_subreddits = [
                        'politics',
                        'Ask_Politics',
                        'POLITIC',
                        'SandersForPresident',
                        'hillaryclinton',
                        'The_Donald',
                        'TedCruzForPresident',

                        'democrats',
                        'Republican',
                        'PoliticalHumor',
                        'PoliticalDiscussion',

                        'worldnews',
                        'news',
                        'funny',
                        'AskReddit',
                        ]



### Stage One

def parseDS(datastore_location, output_location):
    """
    Streams in the JSON comment data dump file and outputs it as a CSV file.

    :param datastore_location: string representing the path to the datastore
    :param output_location: string representing the path to the output file
    :return: write a csv file that holds all the information from the JSON file
    """

    with open(datastore_location, 'r') as f:
        with open(output_location, 'w') as o:

            output_string = "\t".join('{}'.format(field) for field in fields)
            o.write(output_string + "\n")

            n = 1
            for line in f:

                if n % 100000 == 0:
                    print("\rFinished {:,}.".format(n), end='')

                post = json.loads(line)
                # print(post)

                post['body'] = post['body'].encode(sys.stdout.encoding, errors='replace')

                output_string = "\t".join('{}'.format(post[field]) for field in fields)
                o.write(output_string + "\n")

                n += 1
    print()


def isolate_subreddit(csv_location, subreddit):
    """
    Given a premade CSV file, isolate and print separately only comments from the given subreddit

    :param csv_location: string representing the path to the csv file made previously
    :param output_location: string representing the path to the output file
    :param subreddit: string representing a particular subreddit to extract
    :return: write a csv file that holds all the information from the given subreddit comments
    """

    individual_subreddit_csvs = csv_location + "_" + subreddit + '.*.csv'

    df = dd.read_csv(csv_location + ".csv", header=0, sep='\t')
    sub_df = df.loc[df['subreddit'] == subreddit]

    sub_df.to_csv(individual_subreddit_csvs)
    filenames = glob(individual_subreddit_csvs)
    with open(csv_location + "_" + subreddit + '.csv', 'w') as out:
        for fn in filenames:
            with open(fn) as f:
                out.write(f.read())
            os.remove(fn)


def stageOne(csv_files):
    """
    Takes all the original datadump files, and converts them into specific subreddit csv_files.

    :param csv_files: the list of month_year csv files that we'll be working with here.
    :return: all subreddits are written into csv files for all months of data
    """

    output_location = "D:/Reddit/{}/{}"
    datastore_location = "D:/Reddit/{}/RC_{}"

    for csv in csv_files:

        print("Rewriting {}.".format(csv))
        parseDS(datastore_location.format(csv, csv), output_location.format(csv, csv + ".csv"))

        for subreddit in political_subreddits:
            isolate_subreddit(output_location.format(csv, csv), subreddit)
            print("\rParsed {} for {}.".format(csv, subreddit), end='')



### Stage Two

def find_occurrence_data(month_year, csvs_location):
    """
    Given an individual subreddit's csv_file, find the frequencies of a list of trending words.

    :param month_year: a string representing which month's data is being parsed
    :param csvs_location: the string that is to be formatted representing the path to this info
    :return: a Pandas DataFrame that holds all the frequency data
    """

    subreddit_counts = pd.DataFrame(0, index=political_words, columns=political_subreddits, dtype=float)

    for subreddit in political_subreddits:

        subreddit_csv_file = csvs_location.format(month_year, month_year) + "_{}.csv".format(subreddit)
        df = pd.read_csv(subreddit_csv_file, header=0)

        subreddit_comments = df['body'].str.lower()
        number_of_comments = subreddit_comments.count()

        for word in political_words:
            word_count = subreddit_comments.str.contains(word, regex=True).sum()
            subreddit_counts.at[word, subreddit] = word_count / number_of_comments

        del subreddit_comments

        print("\rFinished r/{}.".format(subreddit), end='')
    print()

    return subreddit_counts


def stageTwo(csv_files):
    """
    Takes the subreddit csv files and converts them into pickle files of political word frequencies.

    :param csv_files: the list of month_year csv files that we'll be working with here.
    :return: all subreddits' word frequencies are found for all months of data.
    """

    csv_location = "D:/Reddit/{}/{}"

    for month_year in csv_files:
        print("Working on {}.".format(month_year))
        frequencies = find_occurrence_data(month_year, csv_location)
        frequencies.to_pickle(csv_location.format(month_year, month_year + ".pkl"))

if __name__ == "__main__":
    main()