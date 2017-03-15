#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

print_usage()
{
	cat <<-EOD
	Usage:
	  $0 DIR-PATH-RELATIVE-TO-DOCROOT 
	EOD
	exit 1
}

if [ "$1" == "" ] || [ "$3" != "" ]; then
    print_usage
fi

SRC_DOCUMENTROOT="$HOME/bioconductor.org"
PKGS_DIR="$SRC_DOCUMENTROOT/$1"

R="$HOME/bin/R-2.7"

R_SCRIPT="library('tools')"
R_SCRIPT="$R_SCRIPT; write_PACKAGES('$PKGS_DIR', verbose=TRUE,
rds_compress='xz')"

echo "$R_SCRIPT" | $R --slave

