#!/bin/bash
#
# Script for making the Mac OS X binary .tgz from a package installation
# directory.
#
# Author: H. Pages (hpages@fhcrc.org)
# Last modified: 2007-08-11

set -e  # Exit immediately if a simple command exits with a non-zero status

CHOWNROOTADMIN=`dirname "$0"`/chown-rootadmin

if [ ! -f "$CHOWNROOTADMIN" ]; then
	echo "Installation problem: before you can use the $0 script, you must"
	echo "install chown-rootadmin in the same directory as $0 like this:"
	echo "  cd" `dirname "$0"`
	echo "  gcc chown-rootadmin.c -o chown-rootadmin"
	echo "  sudo chown root:admin chown-rootadmin"
	echo "  sudo chmod 4750 chown-rootadmin"
	exit 1
fi

print_usage()
{
	cat <<-EOD
	Usage:
	  $0 <pkg-dirpath>
	EOD
	exit 2
}

if [ "x$1" == "x" ] || [ "x$2" != "x" ]; then
	print_usage
fi

pkg_dirpath="$1"

#pkg_dirname=`echo "$pkg_dirpath" | sed 's/.*\///'`

desc_file="$pkg_dirpath/DESCRIPTION"
DESCFIELD_PARSER="^.*:[[:space:]]*([^[:space:]]+)[[:space:]]*$"
line=`grep -E "^Package:" $desc_file`
pkgname=`echo $line | sed -E "s/$DESCFIELD_PARSER/\1/"`
line=`grep -E "^Version:" $desc_file`
pkgversion=`echo $line | sed -E "s/$DESCFIELD_PARSER/\1/"`
tgz_file="${pkgname}_${pkgversion}.tgz"

chmod -R ug+w "$pkg_dirpath" # Just because Simon does it

$CHOWNROOTADMIN "$pkg_dirpath" # Change the ownerchip to root:admin

tar zcf "$tgz_file" -C "$pkg_dirpath/.." "$pkgname"

