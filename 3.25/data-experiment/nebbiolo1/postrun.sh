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
# updateReposPkgs-data-experiment.sh script that we run from the biocpush
# account). Can help significantly if the machine has limited disk capacity.
rm -rf src

# Fix perms
find products-in -type d -exec chmod 755 {} \;
chmod -R +r .

set -e # Exit immediately if a simple command exits with a non-zero status.

$BBS_PYTHON_CMD $BBS_HOME/BBS-make-BUILD_STATUS_DB.py

if [ -n "$BBS_OUTGOING_MAP" ]; then
    $BBS_PYTHON_CMD $BBS_HOME/BBS-make-OUTGOING.py
    find OUTGOING -type d -exec chmod 755 {} \;
    $BBS_PYTHON_CMD $BBS_HOME/BBS-make-PROPAGATION_STATUS_DB.py
    chmod -R +r .
fi

# Generate the HTML report
$BBS_PYTHON_CMD $BBS_HOME/BBS-report.py
REPORT_DIRNAME=$(dirname "$BBS_REPORT_PATH")
REPORT_BASENAME=$(basename "$BBS_REPORT_PATH")
cd "$REPORT_DIRNAME"
find . -type d -exec chmod 755 {} \;
chmod -R +r .
$BBS_TAR_CMD zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
chmod -R +r .

# Publish it (no more --delete here, too dangerous!)
$BBS_RSYNC_CMD -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_PUBLISHED_REPORT_DEST_DIR/"
