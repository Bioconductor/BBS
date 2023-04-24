#!/bin/sh

set -e  # Exit immediately if a simple command exits with a non-zero status

export LC_COLLATE="C" # to sort the result of local pathname expansion as on cobra

LOCAL_REPO_ROOT="$HOME/PACKAGES/3.18/data/experiment"
REMOTE_REPO_ROOT="/extra/www/bioc/packages/3.18/data/experiment"
PKG_FILEPATHS="src/contrib/*.tar.gz bin/windows/contrib/4.3/*.zip bin/macosx/contrib/4.3/*.tgz"
CONTRIB_DIR=" \/.*\/"

LOCAL_MD5SUMS="$LOCAL_REPO_ROOT/md5sums.local.txt"
REMOTE_MD5SUMS="$LOCAL_REPO_ROOT/md5sums.cobra.txt"
MD5SUMS_DIFF="$LOCAL_REPO_ROOT/md5sums.diff"

rm -f $LOCAL_MD5SUMS $REMOTE_MD5SUMS $MD5SUMS_DIFF

for filepath in $PKG_FILEPATHS; do
	md5sum $LOCAL_REPO_ROOT/$filepath | sed -r "s/$CONTRIB_DIR/ /" >>$LOCAL_MD5SUMS
	ssh webadmin@cobra md5sum $REMOTE_REPO_ROOT/$filepath | sed -r "s/$CONTRIB_DIR/ /" >>$REMOTE_MD5SUMS
done

diff $LOCAL_MD5SUMS $REMOTE_MD5SUMS >$MD5SUMS_DIFF
mail "hpages.on.github@gmail.com" -s "Result of $0 on $HOSTNAME" <$MD5SUMS_DIFF

