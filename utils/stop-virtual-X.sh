#!/bin/bash
# ============================================================================
# Stop the virtual X server started by start-virtual-X.sh
# ----------------------------------------------------------------------------
#
# See start-virtual-X.sh for important information.
#
# ----------------------------------------------------------------------------

# xvfb_pid is set by start-virtual-X.sh
if [ "$VIRTUALX_OUTPUT_FILE" == "" ]; then
	kill $xvfb_pid
else
	print_msg1()
	{
		echo "--------------------------------------------------------"
		echo "STOPPING the virtual X server"
		echo "-----------------------------"
		date
		echo "xvfb_pid=$xvfb_pid"
	}
	print_msg1 >>"$VIRTUALX_OUTPUT_FILE" 2>&1
	kill $xvfb_pid >>"$VIRTUALX_OUTPUT_FILE" 2>&1
	print_msg2()
	{
		echo "========================================================"
	}
	print_msg2 >>"$VIRTUALX_OUTPUT_FILE" 2>&1
fi

