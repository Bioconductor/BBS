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
    type <- getOption("pkgType")
    if (type != "source")
        type <- "both"

    INSTALL_opts <- ""
    if (multiArch)
        INSTALL_opts <- "--merge-multiarch"
    if(grepl("^x86_64-apple-darwin", R.Version()$platform))
        INSTALL_opts <- "--no-multiarch --no-test-load"

    install.packages(pkg, repos=.get_non_target_repos(), dependencies=FALSE,
                          type=type, INSTALL_opts=INSTALL_opts)
}

