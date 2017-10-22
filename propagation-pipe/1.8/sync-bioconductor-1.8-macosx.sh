#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

REPOS_TOPDIRS="bioc data/annotation data/experiment omegahat lindsey monograph"

print_help()
{
	cat <<-EOD
	This script MUST be run by the 'biocadmin' user.
	
	It does the following:

	  Sync Mac binary packages located under the following subdirs of ~/PACKAGES/1.8:
	    $REPOS_TOPDIRS
	  with those found on www.rosuda.org (Simon's machine).

	To test this script before to really run it, restart with:
	  $0 test
    
	Questions/help: hpages@fhcrc.org (ext. 5791)
	Last modified: 2006-08-07
	
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

for repos_topdir in $REPOS_TOPDIRS; do
    macdir="1.8/$repos_topdir/bin/macosx"
    echo ""
    echo "===================================================================="
    echo "=== Syncing local $macdir with www.rosuda.org (Simon's machine)"
    echo "==="
    cd ~/PACKAGES/$macdir
    rsync $DRYRUN --delete -rtlv "rsync://www.rosuda.org:8081/bioc-repos/$macdir/" .
done

if [ "$1" != "test" ]; then
	cat <<-EOD
	Now you must run:
	
	  cd ~/bin
	  ./prepareRepos-1.8-bioc.sh && ./pushRepos-1.8-bioc.sh
	  ./prepareRepos-1.8-data-annotation.sh && ./pushRepos-1.8-data-annotation.sh
	  ./prepareRepos-1.8-data-experiment.sh && ./pushRepos-1.8-data-experiment.sh
	  ./prepareRepos-1.8-omegahat.sh && ./pushRepos-1.8-omegahat.sh
	  ./prepareRepos-1.8-lindsey.sh && ./pushRepos-1.8-lindsey.sh
	  ./prepareRepos-1.8-monograph.sh && ./pushRepos-1.8-monograph.sh

	in order to propagate the new Mac binary packages to cobra.
	EOD
fi

