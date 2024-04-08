#! /usr/bin/env python3

"""
This script works functions as a cronjob to schedule the build for Apple Silicon
machines where cronjobs run slow due to receiving a "utility" quality of service
(QoS) clamp, which is the lower bound of the QoS. The long-running script should
get an "unspecified" clamp, which is slightly higher than "utility". See
https://github.com/Bioconductor/BBS/issues/387 for details.

Screen Commands
---------------

screen - to start (press enter)
ctrl+a d - to detact
screen -r - to resume a screen
screen -ls
ctrl+a, ctrl+S - new horizontal screen
ctrl+a, tab - move to next window
ctrl+a, c - activate new window


Run the Script
--------------

In a screen, run the following commands to create an environment and run the
script. It will produce a log at LOG_PATH.

python3 -m venv env
source env/bin/active
pip3 install schedule pytz
python3 build.py
"""


from datetime import date
import logging
from pytz import timezone
from schedule import every, repeat, run_pending
from subprocess import PIPE, run, STDOUT
from time import sleep


HOSTNAME = "kjohnson3"
LOG_PATH = "/Users/biocbuild/build.log"

def build(logger):
    logger.debug("START job")
    yyyymmdd = date.today().strftime('%Y%m%d')
    run_path = f"/Users/biocbuild/BBS/3.19/bioc-mac-arm64/{HOSTNAME}" 
    log_path = f"/Users/biocbuild/bbs-3.19-bioc-mac-arm64/log/{HOSTNAME}-{yyyymmdd}-run.log"
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
