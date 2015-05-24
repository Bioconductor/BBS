"""
This script exists to get around the "file changed as we read it" issue with tar.
We still don't know exactly what causes this error, though we know how to induce 
this state. 

Contrary to tar's documentation, it exits with a non-zero exit code (exit code 1)
when it experiences this error. This wrapper simply looks for that exit code and
returns 0 when it is encountered, otherwise it returns tar's exit code.

See the following from "info tar" about tar exit codes:

--BEGIN quote
  Possible exit codes of GNU `tar' are summarized in the following
table:

0
    `Successful termination'.

1
    `Some files differ'.  If tar was invoked with `--compare'
    (`--diff', `-d') command line option, this means that some files
    in the archive differ from their disk counterparts (*note
    compare::).  If tar was given `--create', `--append' or `--update'
    option, this exit code means that some files were changed while
    being archived and so the resulting archive does not contain the
    exact copy of the file set.

2
    `Fatal error'.  This means that some fatal, unrecoverable error
    occurred.
--END quote

So it may be safe to just look for exit code 1 (as this script does) and 
return 0. For extra safety, you could parse the output (probably on stderr)
of the tar command, and only return 0 if the output contains
"file changed as we read it". Just be sure and echo the output to 
stdout/stderr of this script so it is captured in our build logs.

Note that as the script currently stands, stdout/stderr of the tar command
is not redirected anywhere, so it will still show up in build logs.

In order to use this wrapper, the TAR environment variable should be
defined to be something like this:
python d:/biocbld/BBS/utils/tar-wrapper.py --no-same-owner


"""

import sys
import subprocess



sys.argv.pop(0)
args = " ".join(sys.argv)
retcode = subprocess.call("tar %s" % args, shell=True)


if retcode == 1:
    sys.exit(0)
sys.exit(retcode)
