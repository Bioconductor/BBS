### Repo where to find the no-vignettes target packages
target_repo <- Sys.getenv('BBS_CENTRAL_BASEURL')

### Repos where to look for the dependencies of the target packages
source("http://bioconductor.org/biocLite.R")
dep_repos <- biocinstallRepos()[-1] # remove the software repo (bioc)

updateInstalledPkgs <- function()
{
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    update.packages(repos=dep_repos, ask=FALSE)
    if (getOption("pkgType") == "source")
        return()
    ## For these situations where there is no binary or the binary version
    ## lags behind the source version
    update.packages(repos=dep_repos, ask=FALSE, type="source")
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and from our "extra" repository won't get installed by installPkgDeps()
### below (because installPkgDeps installs from source)
preinstallPkgs <- function()
{
    pkgs <- c("XML", "RGtk2", "cairoDevice", "RMySQL", "RCurl", "SSOAP",
              "RGtk", "fields", "gtkDevice", "rgl", "rggobi", "RODBC",
              "rJava", "ada", "ncdf", "Rlibstree", "igraph")
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    install.packages(pkgs, repos=dep_repos, dependencies=TRUE)
}

installPkgDeps <- function(pkgs)
{
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    install.packages(pkgs, repos=c(target_repo, dep_repos), dependencies=TRUE, type='source')
}

