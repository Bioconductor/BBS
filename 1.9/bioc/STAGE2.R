### Repo where to find the no-vignettes target packages
target_repo <- 'http://lamb1/BBS/1.9/bioc'

### Repos where to look for the dependencies of the target packages
dep_repos <- c('http://bioconductor.org/packages/1.9/data/annotation',
               'http://bioconductor.org/packages/1.9/data/experiment',
               'http://bioconductor.org/packages/1.9/omegahat',
               'http://cran.fhcrc.org')


updateInstalledPkgs <- function()
{
    update.packages(repos=dep_repos, ask=FALSE)
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and Omegahat won't get installed by installPkgDeps() below (because
### installPkgDeps installs from source)
preinstallPkgs <- function()
{
    pkgs <- c("XML", "RGtk2", "RCurl", "SSOAP", "RGtk")
    install.packages(pkgs, repos=dep_repos, dependencies=TRUE)
}

installPkgDeps <- function(pkgs)
{
    lock_dir <- file.path(.libPaths()[1], "00LOCK")
    unlink(lock_dir, recursive=TRUE)
    install.packages(pkgs, repos=c(target_repo, dep_repos), dependencies=TRUE, type='source')
}

