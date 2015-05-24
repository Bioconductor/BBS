#!/bin/bash
#
# Typical use:
# ls | extract-pkglist-from-filelist.sh

set -e  # Exit immediately if a simple command exits with a non-zero status

NB_REGEXP="[0-9]+"
VERSION_REGEXP="($NB_REGEXP)(\.|-)($NB_REGEXP)(\.|-)($NB_REGEXP)"
PKGFILE_REGEXP="([^[:space:]]+)_($VERSION_REGEXP)\.tar\.gz"
VALIDLINE_REGEXP="^$PKGFILE_REGEXP[[:space:]]*$"

grep -E "$VALIDLINE_REGEXP" | sed -r "s/$VALIDLINE_REGEXP/\1/"

