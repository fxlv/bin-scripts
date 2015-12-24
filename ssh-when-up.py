#!/usr/bin/env python
import argparse
from subprocess import call
import subprocess
import sys
import socket
import time
import datetime
import os
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


def get_ssh_path():
    for ssh_path in ["/usr/bin/ssh", "/bin/ssh"]:
        if os.path.exists(ssh_path):
            return ssh_path
    return False


def die(msg="Error. Cannot continue."):
    print msg
    sys.exit(1)


def ssh_supports_g():
    # starting with OpenSSH version 6.8
    # there's a nice -G option that can be used to do a sort of a dry run
    # this is useful to determine if a proxy will be used for connecting
    ssh_version = get_ssh_version()
    ssh_version = ssh_version.split("_")
    # SSH version string will look like "OpenSSH_6.9p1"
    # extract the number out of it and check if it's larger than 6.8
    if "OpenSSH" in ssh_version[0]:
        version_number = ssh_version[1]
        if "p" in version_number:
            version_number = version_number.split("p")[0]
            if "." in version_number:
                version_number = float(version_number)
                if version_number >= 6.8:
                    dprint("OpenSSH version {} is supported".format(
                        version_number))
                    return True
    return False


def get_ssh_version():
    cmd = "{} -V".format(get_ssh_path())
    p = subprocess.Popen(cmd.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # Output example:
    # OpenSSH_6.9p1, LibreSSL 2.1.8
    # openssh will output version info to STDERR
    for line in p.stderr:
        if "OpenSSH" in line:
            # split by whitespace and expect first part to contain
            # something like: "OpenSSH_6.9p1"
            openssh_version = line.split()[0]
            return openssh_version
    # if failed to determine SSH version
    return "Unknown"


def proxy_used(target):
    # determine if an SSH proxy command is used to reach this target
    # by running "ssh -G <target>"
    # if a proxy is to be used this will be printed out by SSH
    # this only works starting with
    # OpenSSH > = 6.8 (http://www.openssh.com/txt/release-6.8)
    cmd = "{} -G {}".format(get_ssh_path(), target)
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    for line in p.stdout:
        if "proxycommand" in line:
            return True
    return False


def check_target(target, q):
    """
    Check if the target is up.
    If it is return true
    """
    # target can be hostname or ip
    # optionally it can be prepended by a username followed by an '@'
    # like user@host
    #
    # for such cases we need to test and see
    # if username was provided and remove it from the target
    # as it is not relevant for testing connectivity
    if "@" in target:
        try:
            username, target = target.split("@")
        except:
            die("Cannot parse the target")
    # prepare the socket
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


def sleep_till_host_responds(target, q, stop_q):
    while not check_target(target, q):
        # user has requested abort
        if stop_q.qsize() > 0:
            break
        time.sleep(0.1)
        dprint("Thread is sleeping")

# stop_q is 0 by default but if it is > 0 then the sleeper thread will exit
# this can be used if user aborts the program
# to signal the thread to exit gracefully
stop_q = Queue()


def ssh(target):
    cmd = "{} {}".format(get_ssh_path(), target)
    call(cmd, shell=True)


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

    # determine the full path to ssh binary
    # as it might be aliased and we can't just assume that
    # calling 'ssh' will be the right thing
    ssh_binary = get_ssh_path()
    if not ssh_binary:
        die("ssh command was not found")
    if ssh_supports_g():
        if proxy_used(target):
            print "Proxy is used for this host!"
            ssh(target)
            return
    dprint("OpenSSH version: {}".format(get_ssh_version()))
    print "Connecting to {}".format(target)
    down_time_begin = datetime.datetime.now()

    t = Thread(target=sleep_till_host_responds, args=(target, q, stop_q))
    t.start()
    # use dots to indicete that stuff is happening
    dot = "."
    dot_length = 1
    increment_dot = True
    iteration_counter = 0
    dot_max_length = 20
    progress_container = "[ {} ]"
    cursor = "->"
    while t.isAlive():
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%d.%m.%y %H:%M:%S")
        msg = "{}: ".format(timestamp)
        # if the host refuses connection, we start adding stuff to queue
        # not ideal but this is how we communicate that host is actually up
        if q.qsize() > 0:
            msg += "The host is not accepting SSH"
        else:
            msg += "Waiting for the host to come up"
        msg += " "
        if dot_length < dot_max_length and increment_dot:
            dot_length += 1
        elif dot_length == dot_max_length and increment_dot:
            increment_dot = False
            cursor = "<-"
        elif not increment_dot:
            dot_length = dot_length - 1
            if dot_length == 1:
                increment_dot = True
                cursor = "->"
        right_padding = dot_max_length - dot_length
        progress = "{}{}{}".format(dot * dot_length, cursor,
                                   "." * right_padding)
        msg += progress_container.format(progress)
        msg += "\r"
        # in case this is the first iteration, wait
        # for one second ( 10 x 0.1 ) to give ssh the chance to connect
        if iteration_counter > 10:
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            iteration_counter += 1
        # sleep till next iteration
        time.sleep(0.1)

    else:
        down_time_end = datetime.datetime.now()
        down_time = down_time_end - down_time_begin
        print
        print "Host is up, connecting."
        if down_time.seconds > 1:
            print "Down time was: {}".format(down_time)
        start_time = datetime.datetime.now()
        ssh(target)
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        print "Elapsed time {}".format(elapsed_time)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print
        print "Ctrl-c pressed, stopping the thread, please wait."
        # add something to the queue to signal that it needs to exit
        stop_q.put(1)
        sys.exit(0)
