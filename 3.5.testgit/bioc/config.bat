@rem ========================================================================
@rem Settings shared by all the Windows nodes involved in the 3.5.testgit-bioc builds
@rem ========================================================================


set BBS_MODE=bioc

@rem What type of meat? Only 3 types are supported:
@rem   1: svn repo (contains pkg dirs)
@rem   2: CRAN-style local repo containing .tar.gz pkgs
@rem   3: git repo containing pkg dirs
set BBS_MEAT0_TYPE=3

@rem Needed only if BBS_MEAT0_TYPE is 3
set BBS_BIOC_MANIFEST_GIT_REPO_URL=https://git.bioconductor.org/admin/manifest
set BBS_BIOC_MANIFEST_GIT_BRANCH=RELEASE_3_5

@rem Needed if BBS_MEAT0_TYPE is 1 or 3
set BBS_BIOC_MANIFEST_FILE=software.txt

@rem Where is the fresh meat to be stored by prerun (stage1)
set BBS_MEAT0_RHOST=malbec2
set BBS_MEAT0_RUSER=biocbuild
set BBS_MEAT0_RDIR=/home/biocbuild/bbs-3.5.testgit-bioc/MEAT0

@rem Triggers a MEAT0 update at beginning of prerun (stage1)
set BBS_UPDATE_MEAT0=1

@rem Local meat copy
set BBS_MEAT_PATH=%BBS_WORK_TOPDIR%\meat


set wd1=%cd%
cd ..
call config.bat
cd %wd1%
