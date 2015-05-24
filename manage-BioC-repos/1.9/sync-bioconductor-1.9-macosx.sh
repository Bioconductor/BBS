#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

REPOS_TOPDIRS="bioc data/annotation data/experiment omegahat monograph"
SRC_HOST="r.rsync.urbanek.info"

print_help()
{
	cat <<-EOD
	This script MUST be run by the 'biocadmin' user.
	
	It does the following:

	  Sync Mac binary packages located under the following subdirs of ~/PACKAGES/1.9:
	    $REPOS_TOPDIRS
	  with those found on $SRC_HOST (Simon's machine).

	To test this script (dry-run) before to really run it, restart with:
	  $0 test
    
	Questions/help: hpages@fhcrc.org (ext. 5791)
	Last modified: 2007-01-25
	
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
    macdir="1.9/$repos_topdir/bin/macosx"
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
	  ./prepareRepos-1.9-bioc.sh && ./pushRepos-1.9-bioc.sh
	  ./prepareRepos-1.9-data-annotation.sh && ./pushRepos-1.9-data-annotation.sh
	  ./prepareRepos-1.9-data-experiment.sh && ./pushRepos-1.9-data-experiment.sh
	  ./prepareRepos-1.9-omegahat.sh && ./pushRepos-1.9-omegahat.sh
	  ./prepareRepos-1.9-monograph.sh && ./pushRepos-1.9-monograph.sh

	in order to propagate the new Mac binary packages to cobra.
	EOD
fi

