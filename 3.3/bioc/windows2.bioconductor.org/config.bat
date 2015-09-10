@rem =====================
@rem Settings for windows2.bioconductor.org
@rem =====================


set BBS_DEBUG=0

set BBS_NODE_HOSTNAME=windows2.bioconductor.org
set BBS_USER=biocbuild
set BBS_RSAKEY=c:\biocbld\.BBS\id_rsa
set BBS_WORK_TOPDIR=c:\biocbld\bbs-3.3-bioc
set BBS_R_HOME=%BBS_WORK_TOPDIR%\R
set BBS_NB_CPU=9

set BBS_STAGE2_MODE=multiarch
set BBS_STAGE4_MODE=multiarch
set BBS_STAGE5_MODE=multiarch

set RCYTOSCAPE_PORT_OVERRIDE=4023
set RCYTOSCAPE_HOST_OVERRIDE=taipan

set RCYTOSCAPE3_PORT_OVERRIDE=4024
set RCYTOSCAPE3_HOST_OVERRIDE=taipan

set RCYTOSCAPE_PORT_OVERRIDE_64=3064
set RCYTOSCAPE_HOST_OVERRIDE_64=taipan

set RCYTOSCAPE3_PORT_OVERRIDE_64=3065
set RCYTOSCAPE3_HOST_OVERRIDE_64=taipan


set GENE_E_URL=http://taipan:9998

rem graphviz settings
set GRAPHVIZ_INSTALL_DIR_I386=c:/graphviz/i386
set GRAPHVIZ_INSTALL_MAJOR_I386=2
set GRAPHVIZ_INSTALL_MINOR_I386=20
set GRAPHVIZ_INSTALL_SUBMINOR_I386=3

set GRAPHVIZ_INSTALL_DIR_X64=c:/graphviz/x64
set GRAPHVIZ_INSTALL_MAJOR_X64=2
set GRAPHVIZ_INSTALL_MINOR_X64=25
set GRAPHVIZ_INSTALL_SUBMINOR_X64=20090912.0445

set USERDNSDOMAIN=bioconductor.org




@rem Shared settings (by all Windows nodes)

set wd0=%cd%
cd ..
call config.bat
cd %wd0%
