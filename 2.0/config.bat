@rem ===================================================================
@rem Settings shared by all the Windows nodes involved in the 2.0 builds
@rem ===================================================================


@rem Node local settings
call ..\nodes\%BBS_NODE%\local-settings.bat

set BBS_BIOC_VERSION=2.0

set BBS_BIOC_VERSIONED_REPO_PATH=%BBS_BIOC_VERSION%/%BBS_MODE%

set BBS_R_CMD=%BBS_R_HOME%\bin\R.exe

set TMP=%BBS_WORK_TOPDIR%\tmp
set TMPDIR=%BBS_WORK_TOPDIR%\tmpdir

set BBS_STAGE2_R_SCRIPT=%BBS_HOME%/%BBS_BIOC_VERSIONED_REPO_PATH%/STAGE2.R

set BBS_CENTRAL_RHOST=lamb1
set BBS_CENTRAL_RUSER=biocbuild
set BBS_CENTRAL_RDIR=/home/biocbuild/public_html/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%
set BBS_CENTRAL_BASEURL=http://lamb1/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%

