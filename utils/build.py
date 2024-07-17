#! /usr/bin/env python3

"""
This script works like a cronjob to schedule the build for Apple Silicon
machines where cronjobs run slow due to receiving a "utility" quality of service
(QoS) clamp, which is the lower bound of the QoS. The long-running script should
get an "unspecified" clamp, which is slightly higher than "utility". See
https://github.com/Bioconductor/BBS/issues/387 for details.

Note: This could be run in a screen (or tmux if available) or as a background
processes. Be careful that the `kill` in the corresponding run script doesn't
also kill the process running this script.

Set Up
------

python3 -m venv env
source env/bin/active
pip3 install schedule pytz

Run in Background
-----------------

# Use python in the env path
env/bin/python /Users/biocbuild/BBS/utils/build.py &

Run the Script
--------------

In a screen, run the following commands to create an environment and run the
script. It will produce a log at LOG_PATH.

python3 build.py

Screen Commands
---------------

screen - to start (press enter)
screen -ls
screen -XS <session-id> quit - close a screen
ctrl+a d - to detact
screen -r - to resume a screen
ctrl+a, ctrl+s - new horizontal screen
ctrl+a tab - move to next window
ctrl+a c - activate new window
ctrl+a k - kill a screen


"""


from datetime import date
import logging
from pytz import timezone
from schedule import every, repeat, run_pending
from subprocess import PIPE, run, STDOUT
from time import sleep


HOSTNAME = "kjohnson3"
LOG_PATH = "/Users/biocbuild/bbs-3.20-bioc/log/build.log"

def build(logger):
    logger.debug("START job")
    yyyymmdd = date.today().strftime('%Y%m%d')
    run_path = f"/Users/biocbuild/BBS/3.20/bioc/{HOSTNAME}"
    log_path = f"/Users/biocbuild/bbs-3.20-bioc/log/{HOSTNAME}-{yyyymmdd}-run.log"
    job = ["/bin/bash", "--login", "-c", f"cd {run_path} && ./run.sh >> {log_path} 2>&1"]
    result = run(job, stdout=PIPE, stderr=STDOUT)
    if result.stdout.decode():
        logger.debug(result.stdout.decode())
    logger.debug("END job")
    

if __name__ == "__main__":
    logging.basicConfig(filename = LOG_PATH, format = "%(asctime)s %(message)s",
                        datefmt = "%m/%d/%Y %I:%M:%S %p", level = logging.DEBUG)
    logger = logging.getLogger('schedule')
    logger.debug("Starting build.py")
    every().sunday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    every().monday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    every().tuesday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    every().wednesday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    every().thursday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    every().friday.at("15:00", timezone("US/Eastern")).do(build, logger=logger)
    while True:
        run_pending()
        sleep(1)
    logger.debug("Ending build.py")
