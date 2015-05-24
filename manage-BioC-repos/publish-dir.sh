#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

# Change this to mamba or whatever server is hosting the migrated
# bioconductor.org website if cobra fails
RHOST="cobra"

print_usage()
{
	cat <<-EOD
	Usage:
	  $0 DIR-PATH-RELATIVE-TO-DOCROOT [test|yes]
	EOD
	exit 1
}

if [ "$1" == "" ] || [ "$3" != "" ]; then
    print_usage
fi

PUSHME_DIR="$1"

SRC_DOCUMENTROOT="$HOME/bioconductor.org"
DEST_DOCUMENTROOT="webadmin@$RHOST:/extra/www/bioc"

SRC_DIR="$SRC_DOCUMENTROOT/$PUSHME_DIR"
DEST_DIR="$DEST_DOCUMENTROOT/$PUSHME_DIR"

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

ask_me_first()
{
	cat <<-EOD
	This script will resync remote "$PUSHME_DIR" dir on $RHOST
	  $DEST_DIR
	with local "$PUSHME_DIR" dir
	  $SRC_DIR
	To test this script (dry-run) before to really run it, restart with the "test" option.
	To run it without being asked the confirmation below, restart with the "yes" option.
	Questions/help: hpages@fhcrc.org (ext. 5791)
	Last modified: 2006-12-12
	EOD
	continue_or_abort "Is that OK?"
}

DRYRUN=""
case "$2" in
    "")
        ask_me_first
        ;;
    "yes" | [yYoOsS])
        ;;
    "test")
        DRYRUN="--dry-run"
        ;;
    *)
        print_usage
        ;;
esac

chmod +r "$SRC_DIR" -Rc
rsync --exclude="publish-this-dir.sh" --exclude="DONT-COME-HERE-ANYMORE.TXT" \
      $DRYRUN --delete -avC --include='*.exe' -e ssh "$SRC_DIR/" "$DEST_DIR"

