#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

print_help()
{
	cat <<-EOD
	This script MUST be run by the 'biocadmin' user.

	It does the following:

	  Extract all DESCRIPTION files from all src packages under ~/PACKAGES/1.9.
	  The extracted DESCRIPTION files are placed under ~/PACKAGES/1.9/DESCRIPTIONS.

	To test this script before to really run it, restart with:
	  $0 test

	Questions/help: hpages@fhcrc.org (ext. 5791)
	Last modified: 2006-07-19

	EOD
	agreed=
	while [ -z "$agreed" ]; do
	    echo "Is that OK? [yes or no] "
	    read reply leftover
	    case $reply in
	        "yes" | [yYoOsS])
	            agreed=1
	            ;;
	        "no" | [nN])
	            exit 1
	            ;;
	    esac
	done
}

cd ~/PACKAGES/1.9/

if [ "$1" != "test" ]; then
	print_help
	rm -rf DESCRIPTIONS
	mkdir DESCRIPTIONS
	TARCMD="x"
else
	mkdir -p DESCRIPTIONS
	TARCMD="t"
fi

cd DESCRIPTIONS
find .. -path '../*/src/contrib/*' -name '*.tar.gz' -exec tar z${TARCMD}vf {} '*/DESCRIPTION' \;

