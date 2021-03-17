### =========================================================================
### R function used during STAGE2 to install supporting packages that are not
### target packages
### -------------------------------------------------------------------------


### Same as in build_pkg_dep_graph.R
.get_non_target_repos <- function()
{
    non_target_repos <- readLines(Sys.getenv('BBS_NON_TARGET_REPOS_FILE'))
    gsub("BBS_BIOC_VERSION", Sys.getenv('BBS_BIOC_VERSION'),
         non_target_repos, fixed=TRUE)
}

.NON_TARGET_REPOS <- .get_non_target_repos()

.get_INSTALL_opts <- function(multiArch=FALSE)
{
    if (multiArch)
        return("--merge-multiarch")
    if (grepl("^x86_64-apple-darwin", R.Version()$platform))
        return("--no-multiarch --no-test-load")
    return("")
}

installNonTargetPkg <- function(pkg, multiArch=FALSE)
{
    ## On Windows and Mac we always try to install the binary first (even
    ## when the source version is later). Only if it fails, we will try to
    ## install the source.
    if (getOption("pkgType") != "source") {
        ## Set 'type' to '.Platform$pkgType' to prevent install.packages()
        ## from setting it to 'getOption("pkgType")' (which is "both" by
        ## default on Windows and Mac).
        install.packages(pkg, repos=.NON_TARGET_REPOS,
                              dependencies=FALSE,
                              type=.Platform$pkgType)
        if (pkg %in% rownames(installed.packages()))
            return(invisible(NULL))
        message("")
        message("------------------------------------------------------------")
        message("Installation of binary failed! ",
                "Now trying to install the source ...")
        message("------------------------------------------------------------")
        message("")
    }
    ## Try to install the source.
    install.packages(pkg, repos=.NON_TARGET_REPOS,
                          dependencies=FALSE,
                          type="source",
                          INSTALL_opts=.get_INSTALL_opts(multiArch))
}

.remove_00LOCK_dirs <- function(lib.loc=NULL)
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

updateNonTargetPkgs <- function(multiArch=FALSE)
{
    .remove_00LOCK_dirs()
    ## Try to update using the binary packages.
    if (getOption("pkgType") != "source") {
        message("")
        message("------------------------------------------------------------")
        message("Trying to update using the binary packages ...")
        message("------------------------------------------------------------")
        message("")
        ## See installNonTargetPkg() above for why we use
        ## 'type=.Platform$pkgType'.
        update.packages(repos=.NON_TARGET_REPOS,
                        type=.Platform$pkgType,
                        ask=FALSE)
        ## For these situations where there is no binary or the binary
        ## version of some packages lags behind the source version.
        message("")
        message("------------------------------------------------------------")
        message("Now trying to update again using the source packages ...")
        message("------------------------------------------------------------")
        message("")
    }
    ## Try to update using the source packages.
    update.packages(repos=.NON_TARGET_REPOS,
                    type="source",
                    INSTALL_opts=.get_INSTALL_opts(multiArch),
                    ask=FALSE)
}

