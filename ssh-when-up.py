#!/usr/bin/env python
import argparse
from subprocess import call
import sys
import socket
import time
import datetime
from threading import Thread
from Queue import Queue

#
# The target host can be:
# * up and accepting SSH
# * up and refusing SSH
# * down
#


class Sleepy:

    def __init__(self):
        self.sleep_time = 1

    def increment_sleep_time(self):
        self.sleep_time += 1

    def sleep(self):
        time.sleep(self.sleep_time)
        print datetime.datetime.now(), "Sleeping...{}".format(self.sleep_time)
        self.increment_sleep_time()


DEBUG = False

def dprint(msg):
    if DEBUG:
        print "DEBUG: {}".format(msg)

def check_target(target, q):
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
        elif "Connection refused" in e:
            dprint("Connection refused, the host is up but not accepting SSH")
            q.put("refused")
        else:
            print "Unhandled exception:"
            print e
            sys.exit(1)
        return False

def sleep_till_host_responds(target, q):
    while not check_target(target, q):
        time.sleep(0.1)
        dprint("Thread is sleeping")

def main():
    desc = """
    SSH to a server if it is up, 
    if not up, wait till it comes up and SSH
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("target", help="Target host")
    args = parser.parse_args()

    target = args.target
    # use a queue to communicate with the thread
    # if queue size > 0 this means the host is up but is not accepting SSH
    q = Queue()
    sleepy = Sleepy()
    print "Connecting to {}".format(target)

    t = Thread(target=sleep_till_host_responds,args=(target,q))
    t.start()

    dot = "."
    while t.isAlive():
        msg = "{}: ".format(datetime.datetime.now())
        if q.qsize() > 0:
            msg += "The host is not accepting SSH"
        else:
            msg += "Waiting for the host to come up"
        msg += "{}\r".format(dot)
        sys.stdout.write(msg)
        sys.stdout.flush()
        time.sleep(0.1)
        dot += "."
        if len(dot)> 60:
            dot="."
            print 
    else:
        print
        print "Host is up, connecting."
        start_time = datetime.datetime.now()
        call("ssh {}".format(target), shell=True)
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        print "Elapsed time {}".format(elapsed_time)


if __name__ == "__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        print
        print "Ctrl-c pressed"
        sys.exit(0)

