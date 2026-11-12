#!/bin/bash

. ./config.sh


# Make sure this script is scheduled to run only after the build report has
# been created. This is because the emails that are sent out have links to
# the build report and will not be useful if those links are broken.

# By default (without the do-it arg), BBS-notify.py does not send the
# notification emails to the maintainers but write them to the std output
# (use for debugging). Another way to test is to replace do-it by a valid
# email address:
#
#   $BBS_PYTHON_CMD $BBS_HOME/BBS-notify.py hpages.on.github@gmail.com
#
# then all outgoing emails are redirected to it.

$BBS_PYTHON_CMD $BBS_HOME/BBS-notify.py do-it

