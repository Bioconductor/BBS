#!/usr/bin/env python

# A script to kill R processes that have been running
# for longer than a given time.

import psutil
import datetime
import os
from datetime import date, timedelta

now = datetime.datetime.now()

username = "biocbuild"

number_of_hours = 4

for p in psutil.process_iter():
    if p.username() == username and p.name() == "R":
        if "compute_coverage" in p.cmdline():
            continue
        pstart = datetime.datetime.fromtimestamp(p.create_time())
        then = now-timedelta(hours=number_of_hours)
        if pstart < then:
            print("process %s has been running for more than %s hours!" %
                (p.pid, number_of_hours))
            try:
                print("name: %s, cmdline: %s, started: %s, cwd: %s" % 
                (p.name(), p.cmdline(), pstart.strftime("%Y-%m-%d %H:%M:%S"), 
                p.cwd()))
            except (psutil.AccessDenied):
                print("Could not print out info for this process (access denied)")
            print("killing process at %s ..." % now)
            if psutil.pid_exists(p.pid):
                os.kill(p.pid, 9)
            print("\n")
