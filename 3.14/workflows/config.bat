@rem =================================================================================
@rem Settings shared by all the Windows nodes involved in the 3.14-workflows subbuilds
@rem =================================================================================


set BBS_SUBBUILDS=workflows


set wd1=%cd%
cd ..
call config.bat
cd %wd1%


@rem What type of meat? Only 3 types are supported:
@rem   1: svn repo (contains pkg dirs)
@rem   2: CRAN-style local repo containing .tar.gz pkgs
@rem   3: git repo containing pkg dirs
set BBS_MEAT0_TYPE=3

@rem Needed only if BBS_MEAT0_TYPE is 3
set BBS_BIOC_MANIFEST_GIT_REPO_URL=https://git.bioconductor.org/admin/manifest
set BBS_BIOC_MANIFEST_GIT_BRANCH=RELEASE_3_14
set BBS_BIOC_MANIFEST_CLONE_PATH=%BBS_WORK_TOPDIR%\manifest

@rem Needed if BBS_MEAT0_TYPE is 1 or 3
set BBS_BIOC_MANIFEST_FILE=workflows.txt

@rem Where is the fresh meat to be stored by prerun (stage1)
set BBS_MEAT0_RHOST=%BBS_CENTRAL_RHOST%
set BBS_MEAT0_RUSER=%BBS_CENTRAL_RUSER%
set BBS_MEAT0_RDIR=/home/biocbuild/bbs-3.14-workflows/MEAT0

@rem Triggers a MEAT0 update at beginning of prerun (stage1)
set BBS_UPDATE_MEAT0=1

@rem Local meat copy
set BBS_MEAT_PATH=%BBS_WORK_TOPDIR%\meat

@rem Where are the gitlog files stored by prerun (stage1)
set BBS_GITLOG_RHOST=%BBS_CENTRAL_RHOST%
set BBS_GITLOG_RUSER=%BBS_CENTRAL_RUSER%
set BBS_GITLOG_RDIR=%BBS_CENTRAL_RDIR%/gitlog

@rem Local gitlog copy
set BBS_GITLOG_PATH=%BBS_WORK_TOPDIR%\gitlog

