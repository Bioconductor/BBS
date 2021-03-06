.removeLockDirs <- function(lib.loc=NULL)
{
    if (is.null(lib.loc))
        lib.loc <- .libPaths()[1L]
    lock_dirs <- list.files(lib.loc, pattern="^00LOCK", full.names=TRUE)
    if (length(lock_dirs) != 0L) {
        message("deleting LOCK dirs:\n  ", paste(lock_dirs, collapse="\n  "))
        if (unlink(lock_dirs, recursive=TRUE) != 0L)
            warning("failed to remove LOCK dirs")
    }
    return(invisible(NULL))
}

### Same as in BBS/utils/build_pkg_dep_graph.R and in
### BBS/utils/installNonTargetPkg.R
.get_non_target_repos <- function()
{
    non_target_repos <- readLines(Sys.getenv('BBS_NON_TARGET_REPOS_FILE'))
    gsub("BBS_BIOC_VERSION", Sys.getenv('BBS_BIOC_VERSION'),
         non_target_repos, fixed=TRUE)
}

updateNonTargetPkgs <- function()
{
    .removeLockDirs()
    non_target_repos <- .get_non_target_repos()
    update.packages(repos=non_target_repos, ask=FALSE)
    if (getOption("pkgType") == "source")
        return()

    ## For these situations where there is no binary or the binary version
    ## lags behind the source version
    cat("\n")
    cat("--- now trying again to update from source packages ---\n")
    cat("\n")
    update.packages(repos=non_target_repos, ask=FALSE, type="source")
}

