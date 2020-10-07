#!/bin/bash

set -e # Exit immediately if a simple command exits with a non-zero status.

WORKING_DIR="/home/biocbuild/src"

# Input
CRAN_RSOURCE_TOPDIR="R-alpha"
CRAN_TARBALL="R-latest.tar.gz"
CRAN_TARBALL_URL="http://cran.r-project.org/src/base-prerelease/$CRAN_TARBALL"
LOCAL_WIN32EXT_TOPDIR="/home/biocbuild/src/R-win32-external"

# Output
HOSTNAME=`hostname`
LOCAL_TARBALL_DIR="/home/biocbuild/public_html/BBS"
LOCAL_TARBALL_URL="http://$HOSTNAME/BBS/"


# ------ It is very unlikely that you need to touch anything below this ------

R_TCL_ZIPFILE="R_Tcl_8-5-8.zip"
JPEGSRC_TARBALL="jpegsrc.v8c.tar.gz"
LIBPNG_TARBALL="libpng-1.2.40.tar.gz"
LIBTIFF_TARBALL="tiff-3.8.2.tar.gz"

NB_REGEXP="0|[1-9][0-9]*"
VERSION_REGEXP="^($NB_REGEXP)\.($NB_REGEXP)\.($NB_REGEXP)[[:space:]].*"

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

print_help()
{
	cat <<-EOD
	This script must be run by the 'biocbuild' user.
	
	Download the latest $CRAN_RSOURCE_TOPDIR snapshot (source tarball) from
	CRAN and repackage it as a "Windows-and-Unix ready" source tarball
	(by adding $R_TCL_ZIPFILE, $JPEGSRC_TARBALL, $LIBPNG_TARBALL and
	$LIBTIFF_TARBALL to it).
	
	Questions/help: hpages.on.github@gmail.com
	Last modified: 2009-10-09
	
	EOD
	continue_or_abort "Is that OK?"
}

print_help

# cd to working directory
cd "$WORKING_DIR"

if [ -f "$CRAN_TARBALL" ]; then
    echo "Found local $CRAN_TARBALL in $WORKING_DIR/:"
    ls -l "$CRAN_TARBALL"
    continue_or_abort "Remove it?"
    rm "$CRAN_TARBALL"
fi

if [ -d "$CRAN_RSOURCE_TOPDIR" ]; then
    echo "Found a $CRAN_RSOURCE_TOPDIR/ directory under $WORKING_DIR/:"
    ls -ld "$CRAN_RSOURCE_TOPDIR"
    continue_or_abort "Remove it?"
    rm -rf "$CRAN_RSOURCE_TOPDIR"
fi

# Download the latest snapshot from CRAN
/usr/bin/wget "$CRAN_TARBALL_URL"

# Extract it
/bin/tar zxf "$CRAN_TARBALL"
/bin/rm "$CRAN_TARBALL"

# Add R_Tcl/ to the source
cd "$CRAN_RSOURCE_TOPDIR"
/usr/bin/unzip "$LOCAL_WIN32EXT_TOPDIR/$R_TCL_ZIPFILE"
chmod 755 Tcl -R

# Add jpegsrc.v8a/, libpng/ and libtiff/ to the source
cd src/gnuwin32/bitmap
/bin/tar zxf "$LOCAL_WIN32EXT_TOPDIR/$JPEGSRC_TARBALL"
/bin/tar zxf "$LOCAL_WIN32EXT_TOPDIR/$LIBPNG_TARBALL"
/bin/tar zxf "$LOCAL_WIN32EXT_TOPDIR/$LIBTIFF_TARBALL"
/bin/mv libpng-1.2.40 libpng
/bin/mv tiff-3.8.2/libtiff .
/bin/rm -rf tiff-3.8.2

# Get R version and revision
cd ../../..
version_string=`cat VERSION | sed -r "s/$VERSION_REGEXP/\1.\2/"`
revision_string=`head -n 1 SVN-REVISION | sed -r "s/Revision: //g"`
LOCAL_RSOURCE_TOPDIR="R-$version_string.r$revision_string"

# Rename R source top dir
cd ..
if [ -d "$LOCAL_RSOURCE_TOPDIR" ]; then
    echo "Directory $LOCAL_RSOURCE_TOPDIR/ already exists under $WORKING_DIR/"
    echo "This probably means that latest R-devel snapshot has not changed on"
    echo "CRAN since last time you (or someone else) has run this script."
    echo "If you choose to continue, it will be replaced by newly created "
    echo "$CRAN_RSOURCE_TOPDIR/ directory. It's probably safe to do so..." 
    continue_or_abort "Continue?"
    rm -rf "$LOCAL_RSOURCE_TOPDIR"
fi
/bin/mv -i "$CRAN_RSOURCE_TOPDIR" "$LOCAL_RSOURCE_TOPDIR"

# Create the "Windows-and-Unix ready" tarball
LOCAL_TARBALL="$LOCAL_RSOURCE_TOPDIR.tgz"
/bin/tar zcf "$LOCAL_TARBALL" "$LOCAL_RSOURCE_TOPDIR"

# Publish it internally
/bin/mv -i "$LOCAL_TARBALL" "$LOCAL_TARBALL_DIR/"

echo "DONE."
echo ""
echo "A new \"Windows-and-Unix ready\" tarball $LOCAL_TARBALL is available at $LOCAL_TARBALL_URL"
echo "A new source tree $LOCAL_RSOURCE_TOPDIR/ is available under $WORKING_DIR/"
