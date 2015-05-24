@rem ===================================================================
@rem Settings shared by all the Windows nodes involved in the 3.1 builds
@rem ===================================================================


@rem Paths to local commands
@rem -----------------------

call ..\nodes\%BBS_NODE_HOSTNAME%\local-settings.bat

@rem With StrictHostKeyChecking=no, ssh will automatically add new host keys
@rem to the user known hosts files (so it doesn't get stalled waiting for an
@rem answer when not run interactively).
set BBS_SSH_CMD=%BBS_SSH_CMD% -qi %BBS_RSAKEY% -o StrictHostKeyChecking=no
set BBS_RSYNC_CMD=%BBS_RSYNC_CMD% -r --delete --exclude='.svn'
set BBS_RSYNC_RSH_CMD=%BBS_RSYNC_CMD% -e '%BBS_SSH_CMD%'

set BBS_R_CMD=%BBS_R_HOME%\bin\R.exe
set TMP=%BBS_WORK_TOPDIR%\tmp
set TMPDIR=%BBS_WORK_TOPDIR%\tmpdir


@rem Variables specifying the version and mode of the current builds
@rem ---------------------------------------------------------------

set BBS_BIOC_VERSION=3.1
set BBS_BIOC_VERSIONED_REPO_PATH=%BBS_BIOC_VERSION%/%BBS_MODE%
set BBS_STAGE2_R_SCRIPT=%BBS_HOME%/%BBS_BIOC_VERSIONED_REPO_PATH%/STAGE2.R
set BBS_NON_TARGET_REPOS_FILE=%BBS_HOME%/%BBS_BIOC_VERSIONED_REPO_PATH%/non_target_repos.txt

set BBS_CENTRAL_RHOST=zin2
set BBS_CENTRAL_RUSER=biocbuild
set BBS_CENTRAL_RDIR=/home/biocbuild/public_html/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%
set BBS_CENTRAL_BASEURL=http://zin2/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%


@rem 'R CMD check' variables
@rem -----------------------

set _R_CHECK_TIMINGS_=0
set _R_CHECK_EXECUTABLES_=false
set _R_CHECK_EXECUTABLES_EXCLUSIONS_=false

