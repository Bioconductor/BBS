target_contriburl <- 'file:///home/biocbuild/cran-pkgs'

updateInstalledPkgs <- function()
{
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    update.packages(contriburl=target_contriburl, ask=FALSE)
    if (getOption("pkgType") == "source")
        return()
    ## For these situations where there is no binary or the binary version
    ## lags behind the source version
    update.packages(repos=dep_repos, ask=FALSE, type="source")
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and Omegahat won't get installed by installPkgDeps() below (because
### installPkgDeps installs from source)
preinstallPkgs <- function()
{
    pkgs <- c("XML", "RGtk2", "cairoDevice", "RMySQL")
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    install.packages(pkgs, contriburl=target_contriburl, dependencies=TRUE)
}

installPkgDeps <- function(pkgs)
{
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    install.packages(pkgs, contriburl=target_contriburl, dependencies=TRUE, type='source')
}

