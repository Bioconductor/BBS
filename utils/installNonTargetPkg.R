### =========================================================================
### R function used during STAGE2 to install supporting packages that are not
### target packages
### -------------------------------------------------------------------------


### Same as in make_STAGE2_pkg_deps_list.R
.get_non_target_repos <- function()
{
    non_target_repos <- readLines(Sys.getenv('BBS_NON_TARGET_REPOS_FILE'))
    gsub("BBS_BIOC_VERSION", Sys.getenv('BBS_BIOC_VERSION'),
         non_target_repos, fixed=TRUE)
}

installNonTargetPkg <- function(pkg, multiArch=FALSE)
{
    ## On Windows and Mac we always try to install the binary first (even
    ## when the source version is later). Only if it fails, we try to install
    ## the source.
    if (getOption("pkgType") != "source") {
        ## Set 'type' to '.Platform$pkgType' to prevent install.packages()
        ## from setting it to 'getOption("pkgType")' (which is "both" by
        ## default on Windows and Mac).
        install.packages(pkg, repos=.get_non_target_repos(),
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
    INSTALL_opts <- ""
    if (multiArch)
        INSTALL_opts <- "--merge-multiarch"
    if (grepl("^x86_64-apple-darwin", R.Version()$platform))
        INSTALL_opts <- "--no-multiarch --no-test-load"
    install.packages(pkg, repos=.get_non_target_repos(),
                          dependencies=FALSE,
                          type="source",
                          INSTALL_opts=INSTALL_opts)
}

