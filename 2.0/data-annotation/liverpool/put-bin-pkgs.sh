#!/bin/bash
#
# put-bin-pkgs.sh
#
# Put the "2.0-data-annotation" binary packages on lamb1.
# The binary packages are taken from
#   E:\biocbld\bbs-2.0-data-annotation\bin-pkgs
#
# Questions/help: hpages@fhcrc.org (ext. 5791)
# Last modified: 2006-08-23

REPOS_LABEL="2.0-data-annotation"
REPOS_DIR="2.0/data/annotation"

SRC_DIR="/cygdrive/e/biocbld/bbs-2.0-data-annotation/bin-pkgs"

DEST_HOST="lamb1"
DEST_USER="biocadmin"
DEST_DIR="PACKAGES/$REPOS_DIR/bin/windows/contrib/2.5"

RSAKEY="/cygdrive/e/biocbld/.BBS/id_rsa"
SSH_CMD="/usr/bin/ssh -qi $RSAKEY -o StrictHostKeyChecking=no"


ask()
{
        agreed=
        while [ -z "$agreed" ]; do
            echo "Is that OK? [yes or no] "
            read reply leftover
            case $reply in
                "yes" | "ok" | [yYoOsS])
                    agreed=1
                    ;;
                "no" | [nN])
                    exit 1
                    ;;
            esac
        done
}


echo ""
echo "This script will put the \"$REPOS_LABEL\" binary packages on $DEST_HOST."
echo ""
echo "After this script has terminated, you must run:"
echo "  prepareRepos-$REPOS_LABEL.sh && pushRepos-$REPOS_LABEL.sh"
echo "from the $DEST_USER account on $DEST_HOST."
echo ""

ask

/usr/bin/rsync -rtv --delete -e "$SSH_CMD" "$SRC_DIR/" "$DEST_USER@$DEST_HOST:$DEST_DIR"

