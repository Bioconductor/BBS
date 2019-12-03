#!/bin/bash
# ====================================================================
# Environment variables that control the behavior of R / 'R CMD check'
# ====================================================================

#export _R_CHECK_TIMINGS_="0"
export _R_CHECK_EXECUTABLES_=false
export _R_CHECK_EXECUTABLES_EXCLUSIONS_=false
export _R_CHECK_LENGTH_1_CONDITION_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
export _R_CHECK_LENGTH_1_LOGIC2_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
export _R_CHECK_S3_METHODS_NOT_REGISTERED_=true
#export _R_S3_METHOD_LOOKUP_BASEENV_AFTER_GLOBALENV_=true

