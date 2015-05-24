#!/bin/bash
#
# put-bin-pkgs.sh
#
# Put the "2.9-data-annotation" binary packages on wilson2.
# The binary packages are taken from
#   D:\biocbld\bbs-2.9-data-annotation\bin-pkgs
#
# Questions/help: hpages@fhcrc.org (ext. 5791)
# Last modified: 2011-07-27

REPOS_LABEL="2.9-data-annotation"
REPOS_DIR="2.9/data/annotation"

SRC_DIR="/cygdrive/d/biocbld/bbs-2.9-data-annotation/bin-pkgs"

DEST_HOST="wilson2"
DEST_USER="biocadmin"
DEST_DIR="PACKAGES/$REPOS_DIR/bin/windows/contrib/2.14"

RSAKEY="/cygdrive/d/biocbld/.BBS/id_rsa"
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
echo "  cd ~/manage-BioC-repos/2.9"
echo "  ./prepareRepos-data-annotation.sh && ./pushRepos-data-annotation.sh"
echo "from the $DEST_USER account on $DEST_HOST."
echo ""

ask

/usr/bin/rsync -rtv --delete -e "$SSH_CMD" "$SRC_DIR/" "$DEST_USER@$DEST_HOST:$DEST_DIR"

