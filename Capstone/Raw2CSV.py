#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Raw2CSV.py

This is the same code submitted to the Data Incubator during the challenge, but extended.

(C) 2017 by Jay Kaiser <jayckaiser.github.io>
Updated Jan 2, 2018

Convert raw Reddit Datastore into CSV data with only useful information, and store on hard drive.
Remove temp files created during this process.

"""

import json, sys, os, bz2, shutil, requests


def main():
    downloadingIsWorking = False
    main_directory = "C:/Users/jayka/Downloads/Reddit/"

    directories = dict(zipped_directory=main_directory + "Zipped/",
                       unzipped_directory=main_directory + "Unzipped/",
                       CSV_directory=main_directory + "CSV/",
                       final_directory="D:/reddit/CSV/")


    years_to_do = [2012]
    months_to_do = range(4, 5)

    if downloadingIsWorking:
        for j in years_to_do:
            for i in months_to_do:
                testfile = "RC_{}-{}".format(j, str(i).zfill(2))
                allAtOnce(testfile, **directories)

    else:
        downloadingFailed(**directories)

# these are the fields to take from the JSON lines of Reddit data.
# each year has different ones so this is the smallest subset shared by all three files.
fields = ['subreddit',
          'created_utc',
          'body',
          'author',
          'score',
          ]


# individual process methods
def downloadJSON(file, directory, url='https://files.pushshift.io/reddit/comments/{}'):
    """
    Downloads the JSON file from pushshift.io.

    :param file: the specific month-day file to be downloaded
    :param directory: the directory to where the file is to be downloaded
    :param url: the url from where the file is downloaded
    :return:
    """
    print("\rBegan downloading {}.".format(file), end="")

    with open(directory + file + ".bz2", 'wb') as path:
        response = requests.get(url.format(file + ".bz2"))
        path.write(response.content)

    print("\rDownloaded {}.".format(file), end="")


def unzipJSON(downloads, new_directory, file):
    """
    Unzips the downloaded JSON file and deletes the compressed version of it.

    :param downloads: string representing the path to the downloads folder
    :param new_directory: string representing the path to the new unzipped directory
    :param file:
    :return:
    """

    print("\rAttempting to unzip {}.".format(file), end="")
    # unzips the file and moves it to the /Reddit folder
    with open(downloads + file + ".bz2", 'rb') as source, open(new_directory + file, 'wb') as dest:
        decompressor = bz2.BZ2Decompressor()
        for data in iter(lambda: source.read(100 * 1024), b''):
            dest.write(decompressor.decompress(data))
        print("\rUnzipped {}.".format(file), end="")

    # deletes the old, compressed file
    os.remove(os.path.join(downloads, file + ".bz2"))
    print("\rRemoved zipped {}.".format(file), end="")


def JSON2CSV(datastore_location, output_location, file):
    """
    Streams in the JSON comment data dump file and outputs it as a CSV file.
    Deletes the JSON file afterward.

    :param datastore_location: string representing the path to the datastore
    :param output_location: string representing the path to the output file
    :param file: the name of the file being moved
    :return: write a csv file that holds all the information from the JSON file
    """
    try:
        with open(os.path.join(datastore_location, file), 'r') as f:
            with open(os.path.join(output_location, file + ".csv"), 'w') as o:

                output_string = "\t".join('{}'.format(field) for field in fields)
                o.write(output_string + "\n")
                print("\rRewriting {}.".format(file), end="")

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

        os.remove(os.path.join(datastore_location, file))
        print('\rFinished {}'.format(file), end="")
    except Exception:
        print("Could not parse {}.".format(file))


def moveToHardDrive(old_directory, new_directory, file):
    """
    Moves the newly parsed CSV file to the hard drive.

    :param old_directory: string representing the old directory where the file is being held
    :param new_directory: string representing the new directory for the file (the hard drive)
    :param file: the name of the file being moved.
    :return:
    """
    shutil.move(old_directory + file + '.csv', new_directory + file + '.csv')
    print("\rMoved {} to the hard drive.".format(file), end="")


# methods for completing the entire process
def allAtOnce(file, zipped_directory, unzipped_directory, CSV_directory, final_directory):
    # download the file from pushshift
    downloadJSON(file, zipped_directory)

    # unzip the file and delete the compressed version
    unzipJSON(zipped_directory, unzipped_directory, file)

    # convert to CSV and delete JSON version
    JSON2CSV(unzipped_directory, CSV_directory, file)

    # move final CSV to hard drive
    moveToHardDrive(CSV_directory, final_directory, file)

    print("\r{} is totally finished!".format(file))


def downloadingFailed(zipped_directory, unzipped_directory, CSV_directory, final_directory):
    """
    The downloading process failed for some reason, so they've been downloaded and put into
    the zipped folder manually.
    """

    for file in os.listdir(zipped_directory):
        file = file[:file.index(".bz2")]

        unzipJSON(zipped_directory, unzipped_directory, file)
        JSON2CSV(unzipped_directory, CSV_directory, file)
        moveToHardDrive(CSV_directory, final_directory, file)
        print("\r{} is totally finished!".format(file))


if __name__ == "__main__":
    main()
