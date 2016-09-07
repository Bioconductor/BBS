#! /usr/bin/env python

import time
import sys

log_file = open('loggon_biocbuild_at_startup.log', 'a')

log_file.write('starting do_nothing_forever script at %s ...\n' % time.asctime())
log_file.flush()

while True:
    time.sleep(60.0)

