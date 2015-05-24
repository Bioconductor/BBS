#!/bin/bash

# ===============
# BioC_builder.sh
# ===============

cd ~/BioC_builder/scripts
. ./functions

echo ""
echo "======================================================================="

if [ "$1" == "" ] || [ "$2" == "" ]; then
	echo "Usage: $0 {STAGE1|STAGE2|STAGE3|STAGE4} <bioc_version_string>"
	exit 1
fi

# Init global variables
stage="$1"
bioc_version_string="$2"
. ./BioC_builder.conf
case "$stage" in
	STAGE1)
		stage_child_wd="$STAGE1_CHILD_WD"
		stage_child_cmd="$STAGE1_CHILD_CMD"
		;;
	STAGE2)
		stage_child_wd="$STAGE2_CHILD_WD"
		stage_child_cmd="$STAGE2_CHILD_CMD"
		;;
	STAGE3)
		stage_child_wd="$STAGE3_CHILD_WD"
		stage_child_cmd="$STAGE3_CHILD_CMD"
		;;
	STAGE4)
		stage_child_wd="$STAGE4_CHILD_WD"
		stage_child_cmd="$STAGE4_CHILD_CMD"
		;;
	*)
		echo "$0: ERROR: Unknown stage '$stage'!"
		exit 1
esac

job_label="$stage for bioc-$bioc_version_string"
lockfile="${LOCKFILE_BASENAME}bioc-${bioc_version_string}"
logfile="${LOGFILE_BASENAME}${stage}-bioc-$bioc_version_string"
stage_topcmd="$0"
stage_topcmd_args="$*"
if [ "$stage_topcmd_args" != "" ]; then
	stage_topcmd="$stage_topcmd $stage_topcmd_args"
fi

# First output
echo ""
date
exit_if_locked "$lockfile"
echo "$job_label started on $HOSTNAME at `date`" > "$lockfile"
echo "Changing to dir $stage_child_wd..."
cd $stage_child_wd
echo "Starting $job_label..."

# Run child
time $stage_child_cmd &>"$logfile"

# Are we successfull?
if [ $? -eq 0 ]; then
	echo "DONE."
	rm -f "$lockfile"
	subject="$job_label: DONE"
	mail "$MAIL_TO" -r "$MAIL_FROM" -s "$subject" -a "$logfile" <<-EOD
	Command
	    $stage_child_cmd
	terminated successfully.
	See attached file for complete output produced by this command.
	EOD
else
	echo "FAILED!"
	subject="$job_label: FAILED!"
	mail "$MAIL_TO" -r "$MAIL_FROM" -s "$subject" -a "$logfile" <<-EOD
	A FATAL ERROR occurred in command
	    $stage_child_cmd
	that prevented it to terminate successfully.
	See attached file for complete output produced by this command.
	--------------------------------------------------------------
	IMPORTANT:  The BioC_builder system  will remain locked  until
	lock file
	    $lockfile
	is manually deleted!
	EOD
fi
