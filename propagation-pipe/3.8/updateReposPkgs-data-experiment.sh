#!/bin/bash

cd "$HOME/propagation-pipe/3.8"

. ./config.sh

BBS_OUTGOING_DIR="/home/biocbuild/public_html/BBS/$BIOC_VERSION/data-experiment/OUTGOING"
R_SCRIPT="source('/home/biocbuild/BBS/utils/list.old.pkgs.R')"
PROPAGATION_R_SCRIPT="source('/home/biocbuild/BBS/utils/createPropagationDB.R')"
PROPAGATION_DB_FILE="$BBS_OUTGOING_DIR/../PROPAGATE_STATUS_DB.txt"

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/data/experiment"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/$R_VERSION"
MAC_ELCAPITAN_CONTRIB="$REPOS_ROOT/bin/macosx/el-capitan/contrib/$R_VERSION"

update_repo()
{
	working_dir="$1"
	outgoing_subdir="$BBS_OUTGOING_DIR/$2"
	fileext="$3"
	cd "$working_dir"
	if [ "$?" != "0" ]; then
		exit 1
	fi
#	cp --no-clobber --verbose "$outgoing_subdir"/*.$fileext .
  echo "$PROPAGATION_R_SCRIPT; copyPropagatableFiles('$outgoing_subdir', '$fileext', '$PROPAGATION_DB_FILE', '$REPOS_ROOT') " | $R --slave
	echo "$R_SCRIPT; oldpkgs <- list.old.pkgs(suffix='.$fileext'); removed <- file.remove(oldpkgs); names(removed) <- oldpkgs; removed" | $R --slave
}

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------------------------------------------"

echo ""
echo "Updating $BIOC_VERSION/data/experiment repo with source packages..."
update_repo "$SRC_CONTRIB" "source" "tar.gz"

#echo ""
#echo "Updating $BIOC_VERSION/data/experiment repo with Windows binary packages..."
#update_repo "$WIN_CONTRIB" "win.binary" "zip"

#echo ""
#echo "Updating $BIOC_VERSION/bioc repo with Mac El Capitan binary packages..."
#update_repo "$MAC_ELCAPITAN_CONTRIB" "mac.binary.el-capitan" "tgz"



MANUALS_DEST="$REPOS_ROOT/manuals"
MANUALS_SRC="$BBS_OUTGOING_DIR/manuals"
echo "Updating $BIOC_VERSION/data/experiment repo with reference manuals..."
for i in `ls $MANUALS_SRC`;
do
    pkg=`echo $i| awk '{split($0,a,".pdf"); print(a[1])}'`
    mkdir -p $MANUALS_DEST/$pkg/man
    cp --update --verbose $MANUALS_SRC/$i $MANUALS_DEST/$pkg/man
done


exit 0
