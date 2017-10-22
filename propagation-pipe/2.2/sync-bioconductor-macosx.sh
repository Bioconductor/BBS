#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

REPOS_TOPDIRS="bioc data/annotation data/experiment extra"
#REPOS_TOPDIRS="bioc data/annotation data/experiment"
#REPOS_TOPDIRS="extra"
SRC_HOST="r.rsync.urbanek.info"

continue_or_abort()
{
	agreed=
	while [ -z "$agreed" ]; do
	    echo "$1 [yes or no]"
	    read reply leftover
	    case $reply in
	        "yes" | [yYoOsS])
	            agreed=1
	            ;;
	        "no" | [nN])
	            echo "ABORTED."
	            exit 1
	            ;;
	    esac
	done
}

print_help()
{
	cat <<-EOD
	This script MUST be run by the 'biocadmin' user.
	
	It does the following:

	  Sync Mac binary packages located under the following subdirs of ~/PACKAGES/2.2:
	    $REPOS_TOPDIRS
	  with those found on $SRC_HOST (Simon's machine).

	To test this script (dry-run) before to really run it, restart with:
	  $0 test
    
	Questions/help: hpages@fhcrc.org (ext. 5791)
	Last modified: 2007-05-22
	
	EOD
        continue_or_abort "Is that OK?"
}

DRYRUN=""
if [ "$1" != "test" ]; then
    print_help
else
    DRYRUN="--dry-run"
fi

echo "###"
echo "### SCRIPT WAS CALLED WITH: $0 $*"
echo "### STARTED WORKING AT: `date`"
echo "###"
echo ""

for repos_topdir in $REPOS_TOPDIRS; do
    macdir="2.2/$repos_topdir/bin/macosx"
    echo ""
    echo "===================================================================="
    echo "=== Syncing local $macdir with $SRC_HOST (Simon's machine)"
    echo "==="
    cd ~/PACKAGES/$macdir
    rsync $DRYRUN --delete -rtlv "rsync://$SRC_HOST:8081/bioc-repos/$macdir/" .
done

echo ""
echo "###"
echo "### ENDED WORKING AT: `date`"
echo "###"
echo ""

if [ "$1" != "test" ]; then
	cat <<-EOD
	Now you must run:
	
	  cd ~/bin
	  ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh
	  ./prepareRepos-data-annotation.sh && ./pushRepos-data-annotation.sh
	  ./prepareRepos-data-experiment.sh && ./pushRepos-data-experiment.sh
	  ./prepareRepos-extra.sh && ./pushRepos-extra.sh

	in order to propagate the new Mac binary packages to cobra.
	EOD
fi

