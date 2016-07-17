#!/usr/bin/env python
#
# Execute simple python commands
#
# you can do this: python -c "import os; print os.uname()"
# but with pycli you can do:
# ./pycli.py "os.uname()"
#
# Just a proof of concept for now.
#

import sys
command = sys.argv[1]

module = command.split(".")[0]
method = command.split(".")[1]
try:
    print "Executing: " + command
    print eval("__import__('{}').{}".format(module, method))
except Exception, e:
    print "FAIL:"
    print e
