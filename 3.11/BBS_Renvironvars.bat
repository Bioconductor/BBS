@rem ====================================================================
@rem Environment variables used by the Bioconductor Build System to
@rem control the behavior of R during 'R CMD BUILD' and/or 'R CMD check'
@rem ====================================================================

@rem set _R_CHECK_TIMINGS_=0
set _R_CHECK_EXECUTABLES_=false
set _R_CHECK_EXECUTABLES_EXCLUSIONS_=false
set _R_CHECK_LENGTH_1_CONDITION_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
set _R_CHECK_LENGTH_1_LOGIC2_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
set _R_CHECK_S3_METHODS_NOT_REGISTERED_=true
@rem set _R_S3_METHOD_LOOKUP_BASEENV_AFTER_GLOBALENV_=true
@rem set _R_CLASS_MATRIX_ARRAY_=true

