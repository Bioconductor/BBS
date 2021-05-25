#!/bin/bash

cd "$HOME/propagation/3.12"

. ./config.sh

BBS_OUTGOING_DIR="/home/biocbuild/public_html/BBS/$BIOC_VERSION/bioc/OUTGOING"
R_EXPR="source('/home/biocbuild/BBS/utils/list.old.pkgs.R')"
PROPAGATION_R_EXPR="source('/home/biocbuild/BBS/utils/copyPropagatableFiles.R')"
PROPAGATION_DB_FILE="$BBS_OUTGOING_DIR/../PROPAGATION_STATUS_DB.txt"

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/bioc"
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
	$Rscript -e "$PROPAGATION_R_EXPR; copyPropagatableFiles('$outgoing_subdir', '$fileext', '$PROPAGATION_DB_FILE', '$REPOS_ROOT')"
	$Rscript -e "$R_EXPR; manage.old.pkgs(suffix='.$fileext', bioc_version='$BIOC_VERSION')"
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
echo "Updating $BIOC_VERSION/bioc repo with Mac (High Sierra) binary packages..."
update_repo "$MAC_CONTRIB" "mac.binary" "tgz"



MANUALS_DEST="$REPOS_ROOT/manuals"
MANUALS_SRC="$BBS_OUTGOING_DIR/manuals"
echo "Updating $BIOC_VERSION/bioc repo with reference manuals..."
for i in `ls $MANUALS_SRC`; do
	pkg=`echo $i| awk '{split($0,a,".pdf"); print(a[1])}'`
	mkdir -p $MANUALS_DEST/$pkg/man
	cp --update --verbose $MANUALS_SRC/$i $MANUALS_DEST/$pkg/man
done

exit 0
