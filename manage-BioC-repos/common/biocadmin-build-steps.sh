#!/usr/bin/env bash

# Declare all local vars
local me grandparent_dir err_msg log_file

# The current script's name
me=$(basename "$0")

# Adapted from : http://stackoverflow.com/a/246128/320399
grandparent_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../.. && pwd )

# Provides the function `bashErrorHandler`
source "${grandparent_dir}"/utils/bashErrorHandler.sh
trap 'bashErrorHandler ${me} ${LINENO}' ERR

if [ "$(whoami)" != "biocadmin" ]; then
  bashErrorHandler "$me" "$LINENO" "This script must be run as user 'biocadmin'.  Can not continue"
fi

if [ -z "$1" ]; then
  bashErrorHandler "$me" "$LINENO" "Version to build is empty.  Can not continue."
else
  local version_to_build=$1
fi

source "$grandparent_dir""${version_to_build}"/config.sh

# The steps executed by 'biocadmin' will not
# succeed without the following :
biocadmin_precondition=true
if ! [ $biocadmin_precondition ]; then
  err_msg="Preconditions for build steps are not met (for biocadmin).  Can not continue."
  bashErrorHandler "$me" "$LINENO" "$err_msg"
fi

log_file=/home/biocadmin/cron.log/"$BBS_BIOC_VERSION"/updateRepos-bioc.log

cd manage-BioC-repos/"$version_to_build" || bashErrorHandler "$me" "$LINENO" "An error occurred attempting to cd to manage-BioC-repos/$version_to_build . Cannot continue"

# Group the following commands and redirect all
# output to the same log.
# TODO: Consider splitting logs to separate files
#	and handling STDOUT / STDERR distinctly
{
  ./updateReposPkgs-bioc.sh
  ./prepareRepos-bioc.sh
  ./pushRepos-bioc.sh
} >> "$log_file" 2>&1
