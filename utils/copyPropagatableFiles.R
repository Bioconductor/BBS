### =========================================================================
### Used by the updateReposPkgs-*.sh scripts to propagate packages
### -------------------------------------------------------------------------
### Author: Dan Tenenbaum, May/June 2015


### getRversion() returns R version in X.Y.Z format (e.g. 4.1.0), but we
### want X.Y (e.g. 4.1).
.get_R_version_as_X.Y <- function()
    paste(getRversion()$major, getRversion()$minor, sep=".")

## This function is called by the updateReposPkgs-*.sh scripts,
## running as biocpush. Instead of just a straight cp --no-clobber --verbose,
## we consult the propagation DB to determine what can be copied,
## and then copy it (without overwriting existing files.) As before, we
## display what has been copied, but we also display what has
## NOT propagated.
copyPropagatableFiles <- function(srcDir, fileExt, propagationDb, destDir=".")
{
    stopifnot(file.exists(propagationDb))
    rvers <- .get_R_version_as_X.Y()
    contribpaths <- c(
        'source'="src/contrib",
        'win.binary'=paste0("bin/windows/contrib/", rvers),
        'mac.binary'=paste0("bin/macosx/contrib/", rvers),
        'mac.binary.mavericks'=paste0("bin/macosx/mavericks/contrib/", rvers),
        'mac.binary.el-capitan'=paste0("bin/macosx/el-capitan/contrib/", rvers))
    db <- read.dcf(propagationDb)
    segs <- strsplit(srcDir, "/")[[1]]
    srcType <- segs[length(segs)]
    srcFiles <- dir(srcDir, pattern=glob2rx(paste0("*.", fileExt)))
    res <- unlist(lapply(srcFiles, function(x){
        pkg <- strsplit(x, "_")[[1]][1]
        key <- sprintf("%s#%s#propagate", pkg, srcType)
        if (key %in% colnames(db) &&  grepl("^YES", db[, key]))
            TRUE
        else
            FALSE
    }))
    propagatable <- srcFiles[res]

    destinations <- c()
    for (file in propagatable)
    {
        # simulate cp --verbose output
        fullDestDir <- file.path(destDir, contribpaths[srcType])
        if (!file.exists(file.path(fullDestDir, file)))
            cat(sprintf("‘%s‘ -> ‘%s‘\n", file.path(srcDir, file),
                file.path(fullDestDir, file)))
        # Currently ignoring the result of the copy operation.
        result <- file.copy(file.path(srcDir, file), fullDestDir,
            overwrite=FALSE)
    }

    invisible(NULL)
}

