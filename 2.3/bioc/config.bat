@rem ========================================================================
@rem Settings shared by all the Windows nodes involved in the 2.3-bioc builds
@rem ========================================================================


set BBS_MODE=bioc

set BBS_BIOC_MANIFEST_FILE=bioc_2.3.manifest

@rem What type of meat? Only 2 types are supported:
@rem   1: svn repo (contains pkg dirs)
@rem   2: CRAN-style local repo containing .tar.gz pkgs
set BBS_MEAT0_TYPE=1

@rem Where is it?
set BBS_MEAT0_RHOST=wilson2
set BBS_MEAT0_RUSER=biocbuild
set BBS_MEAT0_RDIR=/home/biocbuild/bbs-2.3-bioc/MEAT0

@rem Triggers a MEAT0 update at beginning of prerun (stage1)
set BBS_UPDATE_MEAT0=1

@rem Local meat copy
set BBS_MEAT_PATH=%BBS_WORK_TOPDIR%\meat


set wd1=%cd%
cd ..
call config.bat
cd %wd1%
