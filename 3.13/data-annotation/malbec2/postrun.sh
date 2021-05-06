#!/bin/bash

echo ""
echo "======================================================================="
this_script=$(basename "$0")
echo "<<< Now starting $this_script at $(date) >>>"
echo "-------------------"

# Adapted from : http://stackoverflow.com/a/246128/320399
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "${script_dir}"/config.sh

cd "$BBS_CENTRAL_RDIR"

# Remove target repo (no-vignettes source packages). It's no longer
# needed so we can make room before we generate the HTML report below
# and before we propagate packages (this will be done later by the
# updateReposPkgs-data-annotation.sh script that we run from the biocadmin
# account). Can help significantly if the machine has limited disk capacity.
rm -rf src

# Fix perms
chmod -R +r .
find products-in -type d -exec chmod 755 {} \;

set -e # Exit immediately if a simple command exits with a non-zero status.

# Generate STATUS_DB.txt file
$BBS_PYTHON_CMD $BBS_HOME/BBS-make-STATUS_DB.py

if [ -n "$BBS_OUTGOING_MAP" ]; then
    # Create and populate OUTGOING dir
    $BBS_PYTHON_CMD $BBS_HOME/BBS-make-OUTGOING.py
    # Generate PROPAGATE_STATUS_DB.txt
    OUTGOING_DIR=$BBS_CENTRAL_RDIR/OUTGOING
    PROPAGATE_STATUS_DB=$BBS_CENTRAL_RDIR/PROPAGATE_STATUS_DB.txt
    INTERNAL_REPOS=/home/biocadmin/PACKAGES/$BBS_BIOC_VERSIONED_REPO_PATH/
    $BBS_RSCRIPT_CMD --vanilla -e "source('$BBS_HOME/utils/createPropagationDB.R');createPropagationList('$OUTGOING_DIR', '$PROPAGATE_STATUS_DB', 'data/annotation', '$INTERNAL_REPOS')"
fi

# Generate the HTML report
$BBS_PYTHON_CMD $BBS_HOME/BBS-report.py no-alphabet-dispatch
REPORT_DIRNAME=$(dirname "$BBS_REPORT_PATH")
REPORT_BASENAME=$(basename "$BBS_REPORT_PATH")
cd "$REPORT_DIRNAME"
$BBS_TAR_CMD zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"

# Publish it (no more --delete here, too dangerous!)
$BBS_RSYNC_CMD -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_PUBLISHED_REPORT_DEST_DIR/"
