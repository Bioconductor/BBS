#!/bin/bash

set -e  # exit immediately if a simple command returns a non-zero status

cd "$HOME/propagation/3.15"

. ./config.sh

BBS_OUTGOING_DIR="/home/biocbuild/public_html/BBS/$BIOC_VERSION/workflows/OUTGOING"
R_EXPR="source('/home/biocbuild/BBS/utils/list.old.pkgs.R')"
PROPAGATION_R_EXPR="source('/home/biocbuild/BBS/utils/copyPropagatableFiles.R')"
PROPAGATION_DB_FILE="$BBS_OUTGOING_DIR/../PROPAGATION_STATUS_DB.txt"

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/workflows"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/$R_VERSION"
MAC_CONTRIB="$REPOS_ROOT/bin/macosx/contrib/$R_VERSION"

update_repo()
{
	working_dir="$1"
	outgoing_subdir="$BBS_OUTGOING_DIR/$2"
	fileext="$3"
	cd "$working_dir"
	if [ "$?" != "0" ]; then
		exit 1
	fi
	$Rscript -e "$PROPAGATION_R_EXPR; try(copyPropagatableFiles('$outgoing_subdir', '$fileext', '$PROPAGATION_DB_FILE', '$REPOS_ROOT'))"
	$Rscript -e "$R_EXPR; oldpkgs <- list.old.pkgs(suffix='.$fileext'); removed <- file.remove(oldpkgs); names(removed) <- oldpkgs; removed"
}

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------------------------------------------"

echo ""
echo "Updating $BIOC_VERSION/workflows repo with source packages..."
update_repo "$SRC_CONTRIB" "source" "tar.gz"

echo ""

echo "DONE."
exit 0
