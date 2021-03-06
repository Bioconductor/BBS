@rem ====================================================================
@rem Settings shared by all the Windows nodes involved in the 3.12 builds
@rem ====================================================================


@rem Paths to local commands
@rem -----------------------

call ..\nodes\%BBS_NODE_HOSTNAME%\local-settings.bat

@rem With StrictHostKeyChecking=no, ssh will automatically add new host keys
@rem to the user known hosts files (so it doesn't get stalled waiting for an
@rem answer when not run interactively).
set BBS_RSH_CMD=%BBS_SSH_CMD% -qi %BBS_RSAKEY% -o StrictHostKeyChecking=no
set BBS_RSYNC_CMD=%BBS_RSYNC_CMD% -r --delete --exclude='.svn' --exclude='.git' --exclude='.github' --exclude='.git_*'
set BBS_RSYNC_RSH_CMD=%BBS_RSYNC_CMD% --rsh '%BBS_RSH_CMD%'

set BBS_R_CMD=%BBS_R_HOME%\bin\R.exe
set BBS_RSCRIPT_CMD=%BBS_R_HOME%\bin\Rscript.exe
set TMP=%BBS_WORK_TOPDIR%\tmp
set TMPDIR=%BBS_WORK_TOPDIR%\tmpdir


@rem Variables specifying the version and mode of the current builds
@rem ---------------------------------------------------------------

set BBS_BIOC_VERSION=3.12
set BBS_BIOC_GIT_BRANCH=RELEASE_3_12
set BBS_BIOC_VERSIONED_REPO_PATH=%BBS_BIOC_VERSION%/%BBS_SUBBUILDS%
set BBS_NON_TARGET_REPOS_FILE=%BBS_HOME%/%BBS_BIOC_VERSIONED_REPO_PATH%/non_target_repos.txt

set BBS_CENTRAL_RUSER=biocbuild
set BBS_CENTRAL_RDIR=/home/biocbuild/public_html/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%
set BBS_CENTRAL_BASEURL=http://%BBS_CENTRAL_RHOST%/BBS/%BBS_BIOC_VERSIONED_REPO_PATH%


@rem Define some environment variables to control the behavior of R
@rem --------------------------------------------------------------

set R_ENVIRON_USER=%BBS_HOME%\%BBS_BIOC_VERSION%\Renviron.bioc

