### Repo where to find the no-vignettes target packages
target_repo <- Sys.getenv('BBS_CENTRAL_BASEURL')

### Repos where to look for the dependencies of the target packages
source("http://bioconductor.org/biocLite.R")
dep_repos <- biocinstallRepos()[-3L] # remove the data/experiment repo

removeLockDirs <- function(lib.loc=NULL)
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

updateInstalledPkgs <- function()
{
    ## No update for the data-experiment builds
    #removeLockDirs()
    #update.packages(repos=dep_repos, ask=FALSE)
    #if (getOption("pkgType") == "source")
    #    return()
    ### For these situations where there is no binary or the binary version
    ### lags behind the source version
    #update.packages(repos=dep_repos, ask=FALSE, type="source")
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and from our "extra" repository won't get installed by installPkgDeps()
### below (because installPkgDeps installs from source)
preinstallPkgs <- function()
{
    ## No preinstall for the data-experiment builds
    #pkgs <- c("XML", "RGtk2", "cairoDevice", "RMySQL", "RCurl", "SSOAP", "fields")
    #removeLockDirs()
    #install.packages(pkgs, repos=dep_repos, dependencies=TRUE)
}

installPkgDeps <- function(pkgs)
{
    removeLockDirs()
    install.packages(pkgs, repos=c(target_repo, dep_repos), dependencies=TRUE, type='source')
}

