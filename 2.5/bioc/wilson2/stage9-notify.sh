#!/bin/bash

. ./config.sh

# By default (without the do-it arg), BBS-notify.py does not send the
# notification emails to the maintainers but write them to the std output
# (use for debugging). Another way to test is to replace do-it by a valid
# email address:
#
#   $BBS_HOME/BBS-notify.py hpages@fhcrc.org
#
# then all outgoing emails are redirected to it.

$BBS_HOME/BBS-notify.py do-it

