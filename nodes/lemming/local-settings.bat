@rem ==========================
@rem Local settings for lemming
@rem ==========================

set BBS_HOME=D:\biocbld\BBS

set BBS_PYTHON_CMD=C:\usr\Python24\python.exe

set BBS_TAR_CMD=C:\usr\RTools\bin\tar.exe

@rem With StrictHostKeyChecking=no, ssh will automatically add new host keys
@rem to the user known hosts files (so it doesn't get stalled waiting for an
@rem answer when not run interactively).
set BBS_RSAKEY=D:\biocbld\.BBS\id_rsa
set BBS_SSH_CMD=C:\usr\cygwin\bin\ssh.exe -qi %BBS_RSAKEY% -o StrictHostKeyChecking=no
set BBS_RSYNC_CMD=C:\usr\cygwin\bin\rsync.exe -r --delete --exclude='.svn'
set BBS_RSYNC_RSH_CMD=%BBS_RSYNC_CMD% -e '%BBS_SSH_CMD%'

@rem Needed only on the "prelim repo builder" node
@rem i.e. the node performing stage1
@rem set BBS_SVN_CMD=
