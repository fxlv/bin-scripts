#!/usr/bin/env python
import argparse
from subprocess import call
import sys
import socket
import time
import datetime


def sleepy_time(seconds=2):
    time.sleep(seconds)
    print datetime.datetime.now(), "Sleeping..."


DEBUG = False

def dprint(msg):
    if DEBUG:
        print "DEBUG: {}".format(msg)

def check_target(target):
    socket.setdefaulttimeout(2)
    s = socket.socket()
    try:
        s.connect((target, 22))
        dprint(s.recv(100))
        s.close()
        dprint("socket closed")
        return True
    except Exception, e:
        if "Name or service not known" in e:
            print "Cannot resolve the hostname, buddy"
            sys.exit(1)
        elif "timed out" in e:
            dprint("Sorry buddy, the server is not responding.")
        else:
            print "Unhandled exception:"
            print e
            sys.exit(1)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target host")
    args = parser.parse_args()

    target = args.target

    print "Connecting to {}".format(target)
    while not check_target(target):
        sleepy_time()
    else:
        print "Host is up, connecting."
        call("ssh {}".format(target), shell=True)


if __name__ == "__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        print
        print "Ctrl-c pressed"
        sys.exit(0)

