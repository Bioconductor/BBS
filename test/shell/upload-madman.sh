#!/bin/bash
#
# BioC_builder - STAGE1
# ---------------------
#
# Input:
#  - A working copy of the BioC madman dir.
# Output:
#  - A tarball of the BioC madman dir available at
#      http://gopher5/compbio/dailyBuild/$bioc_version_string/latest/madman.tgz
#    so that the STAGE 2 and STAGE 3 scripts can download it.
#
# This script performs the following tasks:
#   1. Update a working copy of the BioC madman dir.
#   2. Use "svn export" to produce a temporary copy of the updated BioC
#      madman dir.  This temporary dir is not a working copy anymore
#      (no .svn subdirs in it).
#   3. Put this temporary BioC madman dir in a tarball madman.tgz.
#   4. Create dir (backup existing one if any)
#        http://gopher5/compbio/dailyBuild/$bioc_version_string/latest/
#      and move madman.tgz under it.

set -e # Exit immediately if a simple command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

if [ "$1" == "" ]; then
	echo "Usage: $0 <bioc_version_string>"
	exit 1
fi
bioc_version_string="$1"

# Working dir (absolute path)
wdir="/loc/biocbuild/$bioc_version_string/src"

# Madman working copy dir (path relative to working dir)
madman_wc_dir="madman-wc"

# Madman dir (not working copy, path relative to working dir)
madman_dir="madman"

# Name of the tarball file to produce
madman_tarball="madman.tgz"

# FIX ME: Currently, /home/compbio/www-gopher5/ is an NFS mounted directory.
# Having it local might be a better situation.
dest_dir="/home/compbio/www-gopher5/dailyBuild/$bioc_version_string/latest"

# ----------------------------------------------------------------------------

roll_backups()
{
        if [ "$1" == "" ]; then
                echo "$0: Usage: roll_backups basename nb_backups"
                return 1
        fi
        basename="$1"
        if [ "$2" == "" ]; then
                nb_backups=0
        else
                nb_backups=$2
        fi
        for (( i=$nb_backups ; i>=0 ; i=i-1 )); do
                if (( $i>0 )); then
                        backup="$basename.$i"
                else
                        backup="$basename"
                fi
                if [ ! -e "$backup" ]; then
                        continue;
                fi
                if (( $i==$nb_backups )); then
                        rm -rf "$backup"
                        continue
                fi
                let j=$i+1
                #echo "mv $backup $basename.$j"
                mv "$backup" "$basename.$j"
        done
        return 0
}

# Update working copy
cd "$wdir"
svn up "$madman_wc_dir"

# Export working copy
rm -rf "$madman_dir"
svn export "$madman_wc_dir" "$madman_dir"
tar zcf "$madman_tarball" "$madman_dir"

# Move to dest_dir
roll_backups "$dest_dir" 7
mkdir "$dest_dir"
mv "$madman_tarball" "$dest_dir"
