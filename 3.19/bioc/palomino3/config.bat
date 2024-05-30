@rem ======================
@rem Settings for palomino3
@rem ======================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=palomino3
set BBS_USER=biocbuild
set BBS_WORK_TOPDIR=F:\biocbuild\bbs-3.19-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R

@rem palomino3 has 32 logical CPUs.
set BBS_NB_CPU=22
set BBS_BUILD_NB_CPU=18
set BBS_CHECK_NB_CPU=20
set BBS_EXTRA_CHECK_OPTIONS=--no-vignettes

@rem Central build node is bbscentral1 on Jetstream2.
set BBS_CENTRAL_RHOST=bbscentral1
set BBS_RSH_CMD=ssh -F /cygdrive/f/biocbuild/.ssh/config
set BBS_CENTRAL_ROOT_URL=http://149.165.171.124
set BBS_PRODUCT_TRANSMISSION_MODE=asynchronous

@rem Source tarballs produced during STAGE3 won't be propagated
@rem so we don't need to push them to the central builder.
set DONT_PUSH_SRCPKGS=1



@rem Shared settings (by all Windows nodes).

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
