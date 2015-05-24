#!/bin/bash

cd "$HOME/manage-BioC-repos/2.7"

. ./config.sh

BBS_OUTGOING_DIR="/home/biocbuild/public_html/BBS/$BIOC_VERSION/bioc/OUTGOING"
R_SCRIPT="source('/home/biocbuild/BBS/utils/list.old.pkgs.R')"

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/bioc"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/$R_VERSION"
MAC_LEOPARD_CONTRIB="$REPOS_ROOT/bin/macosx/leopard/contrib/$R_VERSION"

update_repo()
{
	working_dir="$1"
	outgoing_subdir="$BBS_OUTGOING_DIR/$2"
	fileext="$3"
	cd "$working_dir"
	if [ "$?" != "0" ]; then
		exit 1
	fi
	cp --no-clobber --verbose "$outgoing_subdir"/*.$fileext .
	echo "$R_SCRIPT; oldpkgs <- list.old.pkgs(suffix='.$fileext'); removed <- file.remove(oldpkgs); names(removed) <- oldpkgs; removed" | $R --slave
}

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------------------------------------------"

echo ""
echo "Updating $BIOC_VERSION/bioc repo with source packages..."
update_repo "$SRC_CONTRIB" "source" "tar.gz"

echo ""
echo "Updating $BIOC_VERSION/bioc repo with Windows binary packages..."
update_repo "$WIN_CONTRIB" "win.binary" "zip"

echo ""
echo "Updating $BIOC_VERSION/bioc repo with Mac Leopard binary packages..."
update_repo "$MAC_LEOPARD_CONTRIB" "mac.binary.leopard" "tgz"

exit 0
