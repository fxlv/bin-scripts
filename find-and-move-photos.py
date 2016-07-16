#!/usr/bin/env python
import argparse
import sys
import re
import glob
import os
import datetime

DESTINATION_FOLDER = "{}/OneDrive/photos".format(os.environ['HOME'])
DEBUG = True


def usage():
    pass


def yesno(q=None):
    response = None
    while response != "y" or response != "n":
        response = raw_input("{} (y/n):".format(q)).strip().strip()
        if len(response) == 1:
            if response == "y":
                return True
            elif response == "n":
                return False


def die(msg=None):
    if msg:
        print "ERROR: {}".format(msg)
    sys.exit(1)


def is_valid_date(date):
    date_regex = "[0-9]{4}\-[0-9]{2}\-[0-9]{2}"
    if re.match(date_regex, date):
        return True
    else:
        return False


def main():
    desc = """
    Find photos and organize them into directories by date.
    """

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("date", help="Date (yyy-mm-dd)")
    args = parser.parse_args()

    date = args.date
    if not is_valid_date(date):
        die("Invalid date")

    date = datetime.datetime.strptime(date, "%Y-%m-%d")

    photos = find_photos(date)
    print "{} photos found".format(len(photos))
    if len(photos) == 0:
        print "No photos matching the criteria found."
        sys.exit(0)
    dest = "{destination_folder}/{year}/{month:02}/{date}".format(
        destination_folder=DESTINATION_FOLDER,
        year=date.year,
        month=date.month,
        date="{}-{:02}-{:02}".format(date.year, date.month, date.day))
    print "Destination folder will be: {}".format(dest)
    # check that destination directory exists or createit if it does not
    if not os.path.exists(dest):
        os.makedirs(dest)
    to_be_renamed = []
    for photo in photos:
        src_file = "{cwd}/{photo}".format(cwd=os.getcwd(), photo=photo)
        dst_file = "{dest}/{photo}".format(dest=dest, photo=photo)
        print "{} => {}".format(src_file, dst_file)
        to_be_renamed.append((src_file, dst_file))
    if yesno("Shall we continue?"):
        print "Continuing"
        for photo in to_be_renamed:
            src_file, dst_file = photo
            os.rename(src_file, dst_file)
        print "All done."
    else:
        print "Aborting"


def find_photos(date=None):
    """
    Find all files that match the wildcard and make sure they are files.
    Then filter them by date and return a list.
    """
    wildcard = "*.jpg"
    photos_list = []
    for file_name in glob.glob(wildcard):
        if os.path.isfile(file_name):
            # now, check if creation date is a match
            creation_date = os.path.getmtime(file_name)
            creation_date = datetime.datetime.fromtimestamp(creation_date)
            # since date will always be midnight, then we only care about
            # files that are created on or after midnight
            if creation_date >= date:
                delta = creation_date - date
                if delta.days == 0:
                    if DEBUG:
                        print "{} > {} ".format(creation_date, date),
                        print delta,
                        print " found {}".format(file_name)
                    photos_list.append(file_name)
    return photos_list


if __name__ == "__main__":
    main()
