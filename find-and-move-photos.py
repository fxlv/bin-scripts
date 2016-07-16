#!/usr/bin/env python
import argparse
import sys
import re
import glob
import os
import datetime

DESTINATION_FOLDER = "{}/OneDrive/photos".format(os.environ['HOME'])
DEBUG = True

# TODO: usage message
# TODO: better way of finding photos, no need to do deltas, can just use date.month and date.day to compare


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


def is_valid_date_month(date):
    date_regex_month = "[0-9]{4}\-[0-9]{2}"
    if re.match(date_regex_month, date):
        return True
    else:
        return False


def is_valid_date_day(date):
    date_regex_day = "[0-9]{4}\-[0-9]{2}\-[0-9]{2}"
    if re.match(date_regex_day, date):
        return True
    else:
        return False


def is_valid_date(date):
    if is_valid_date_day(date) or is_valid_date_month(date):
        return True
    else:
        return False


def main():
    desc = """
    Find photos and organize them into directories by date.
    """

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("date", help="Date (yyyy-mm-dd or yyyy-mm)")
    args = parser.parse_args()

    find_month = False
    date = args.date
    if not is_valid_date(date):
        die("Invalid date")

    if is_valid_date_day(date):
        date_format = "%Y-%m-%d"
    elif is_valid_date_month(date):
        date_format = "%Y-%m"
        find_month = True # will search for photos from whole month

    date = datetime.datetime.strptime(date, date_format)

    photos = find_photos(date, find_month)
    print "{} photos found".format(len(photos))
    if len(photos) == 0:
        print "No photos matching the criteria found."
        sys.exit(0)

    to_be_renamed = []
    for photo in photos:
        # since there can be photos from different days, 
        # destination needs to be set for each photo individually
        mdate = get_mdate(photo)
        dest = "{destination_folder}/{year}/{month:02}/{date}".format(
            destination_folder=DESTINATION_FOLDER,
            year=mdate.year,
            month=mdate.month,
            date="{}-{:02}-{:02}".format(mdate.year, mdate.month, mdate.day))
        print "Destination folder will be: {}".format(dest)

        # check that destination directory exists or createit if it does not
        if not os.path.exists(dest):
            os.makedirs(dest)

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

def get_mdate(file_name):
    mdate = os.path.getmtime(file_name)
    mdate = datetime.datetime.fromtimestamp(mdate)
    return mdate

def find_photos(date, find_month):
    """
    Find all files that match the wildcard and make sure they are files.
    Then filter them by date and return a list.
    """
    wildcard = "*.jpg"
    photos_list = []
    for file_name in glob.glob(wildcard):
        if os.path.isfile(file_name):
            # now, check if creation date is a match
            creation_date = get_mdate(file_name)
            # since date will always be midnight, then we only care about
            # files that are created on or after midnight
            if creation_date >= date:
                delta = creation_date - date
                if find_month:
                    # find photos from whole month
                    if creation_date.year == date.year:
                        if creation_date.month == date.month:
                            if DEBUG:
                                print "{} > {} ".format(creation_date, date),
                                print delta,
                                print " found {}".format(file_name)
                            photos_list.append(file_name)
                else:
                    # find photos from one day
                    if delta.days == 0:
                        if DEBUG:
                            print "{} > {} ".format(creation_date, date),
                            print delta,
                            print " found {}".format(file_name)
                        photos_list.append(file_name)
    return photos_list


if __name__ == "__main__":
    main()
