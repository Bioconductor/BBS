@rem ============================================================================
@rem Settings shared by all the Windows nodes involved in the 2.0-biocLite builds
@rem ============================================================================


set BBS_MODE=biocLite
set BBS_R_CMD_TIMEOUT=600.0

@rem What type of meat? Only 2 types are supported:
@rem   1: svn repo (contains pkg dirs)
@rem   2: CRAN-style local repo containing .tar.gz pkgs
set BBS_MEAT0_TYPE=1

@rem Where is it?
set BBS_MEAT0_RHOST=lamb1
set BBS_MEAT0_RUSER=biocbuild
set BBS_MEAT0_RDIR=/home/biocbuild/bbs-2.0-biocLite/MEAT0

@rem Triggers a MEAT0 update at beginning of prerun (stage1)
set BBS_UPDATE_MEAT0=1

@rem Local meat copy
set BBS_MEAT_PATH=%BBS_WORK_TOPDIR%\meat


set wd1=%cd%
cd ..
call config.bat
cd %wd1%


set BBS_BIOC_MANIFEST_FILE=%BBS_HOME%\2.0\biocLite\biocLite_2.0.manifest

