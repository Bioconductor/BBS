@rem ===================
@rem Settings for tokay2
@rem ===================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=tokay2
set BBS_USER=biocbuild
set BBS_RSAKEY=C:\Users\biocbuild\.BBS\id_rsa
set BBS_WORK_TOPDIR=C:\Users\biocbuild\bbs-3.7-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=30

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

rem graphviz settings
set GRAPHVIZ_INSTALL_DIR_I386=c:/graphviz/i386
set GRAPHVIZ_INSTALL_MAJOR_I386=2
set GRAPHVIZ_INSTALL_MINOR_I386=20
set GRAPHVIZ_INSTALL_SUBMINOR_I386=3

set GRAPHVIZ_INSTALL_DIR_X64=c:/graphviz/x64
set GRAPHVIZ_INSTALL_MAJOR_X64=2
set GRAPHVIZ_INSTALL_MINOR_X64=25
set GRAPHVIZ_INSTALL_SUBMINOR_X64=20090912.0445



@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
