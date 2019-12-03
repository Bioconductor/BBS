#!/bin/bash
# ====================================================================
# Environment variables that control the behavior of R / 'R CMD check'
# ====================================================================
#
# IMPORTANT: Make sure the settings used by the Bioconductor Devel
# Docker image are kept in sync with the settings in this file.
# A PR should be send to https://github.com/Bioconductor/bioconductor_full
# each time this file is modified.
#

#export _R_CHECK_TIMINGS_="0"
export _R_CHECK_EXECUTABLES_=false
export _R_CHECK_EXECUTABLES_EXCLUSIONS_=false
export _R_CHECK_LENGTH_1_CONDITION_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
export _R_CHECK_LENGTH_1_LOGIC2_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
export _R_CHECK_S3_METHODS_NOT_REGISTERED_=true
#export _R_S3_METHOD_LOOKUP_BASEENV_AFTER_GLOBALENV_=true

