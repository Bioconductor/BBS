#!/usr/bin/env bash

# TODO: Once the build system is better understood, we should uncomment the exit at the
#   end of this function and 'fail fast' with confidence.  However, for now, it'll be
#   safer to print output that indicates something seems like an error as a notice that it
#   should be ispected.  Something that seems like an error may actualy be an expected
#   state, which we won't want to break by detecting a false positive.

# Adapted from http://stackoverflow.com/a/185900/320399
bashErrorHandler() {
  echo "EEE - Start of bashErrHandler" >&2
  if [ "$#" -ne 4 ]; then
    echo "Detected incorrect number of arguments.  Output may be incorrect." >&2
  fi

  # Declare all local variables
  local parent_script parent_lineno errloc message code email_subject

  # Error location
  parent_script="${1:-UNKNOWN}"
  parent_lineno="${2:-UNKNOWN}"
  errloc="$parent_script:$parent_lineno"
  # Optionally provide an error message
  message="${3:-Unknown Error}"
  # Error code is -1 by default
  code="${4:-1}" 
  
  err_msg="Error on or near '${errloc}'; ${message}; exiting with status ${code}" >&2
  
  # Print the message to STDERR  
  echo "$err_msg" >&2
  email_subject="BBS error encountered by '$(whoami)'"
  # Send the message to an email recipient
  echo "$err_msg" | mail -s "$email_subject" brian@bioconductor.org

  echo "EEE - End of bashErrHandler" >&2
  # TODO: See note at start of function
  # exit "${code}"
}
