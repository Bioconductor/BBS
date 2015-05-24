### Repo where to find the no-vignettes target packages
target_repo <- Sys.getenv('BBS_CENTRAL_BASEURL')

### Repos where to look for the dependencies of the target packages
source("http://bioconductor.org/biocLite.R")
### Remove the data/experiment repo
all_repos <- biocinstallRepos()
dep_repos <- all_repos[-match("BioCexp", names(all_repos))]

### Dan: we need to make the necessary changes to the updateInstalledPkgs(),
### preinstallPkgs() and installPkgDeps() functions below so that they
### update/install for multiple archs or not depending on the value of
### STAGE2_mode (can be "" or "multiarch").
STAGE2_mode <- Sys.getenv('BBS_STAGE2_MODE')

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

### Unfortunately, when used with 'dependencies=TRUE', install.packages() will
### *recursively* install the suggested packages, which does not make sense
### (for example it leads to the installation of hundreds of unneeded packages
### when installing the annotate package).
### install.packages2() only installs the packages which are directly suggested
### by the packages specified in 'pkgs', plus of course the packages that those
### directly suggested packages depend on or import.
getSuggestedPackagesToInstall <- function(pkgs, repos=getOption("repos"),
                                          type=getOption("pkgType"))
{
    ## Code based on utils:::getDependencies(). The key difference here is
    ## that we don't use a repeat{} loop to "grow" the 'deps' vector.
    p0 <- unique(pkgs)
    available <- available.packages(contriburl=contrib.url(repos, type))
    is_avail <- p0 %in% row.names(available)
    p0 <- p0[is_avail]
    deps <- available[p0, "Suggests"]
    deps <- deps[!is.na(deps)]
    installed <- installed.packages(fields=c("Package", "Version"))
    res <- utils:::.clean_up_dependencies2(deps, installed, available)
    not_avail <- unique(res[[2L]])
    if (length(not_avail)) {
        warning(sprintf(ngettext(length(not_avail),
                                 "suggested package %s is not available",
                                 "suggested packages %s are not available"),
                        paste(sQuote(not_avail), collapse=", ")),
                domain=NA, call.=FALSE, immediate.=TRUE)
        flush.console()
    }
    deps <- unique(res[[1L]])
    deps[!(deps %in% c("R", pkgs))]
}

install.packages2 <- function(pkgs, repos=getOption("repos"),
                              type=getOption("pkgType"))
{
    message("")
    message("INSTALLING THE REQUESTED PACKAGES AND THEIR DEPENDENCIES (IF ANY)")
    message("")
    removeLockDirs()
    install.packages(pkgs, repos=repos, type=type,
        INSTALL_opts="--no-multiarch")
    more_pkgs <- getSuggestedPackagesToInstall(pkgs, repos=repos, type=type)
    if (length(more_pkgs) == 0L)
        return(invisible(NULL))
    message("")
    message("INSTALLING THE PACKAGES SUGGESTED BY THE REQUESTED PACKAGES")
    message("")
    removeLockDirs()
    install.packages(more_pkgs, repos=repos, type=type,
        INSTALL_opts="--no-multiarch")
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and from our "extra" repository won't get installed by installPkgDeps()
### below (because installPkgDeps installs from source)
preinstallPkgs <- function()
{
    ## No preinstall for the data-experiment builds
    #pkgs <- c("XML", "RGtk2", "cairoDevice", "RMySQL", "RCurl", "SSOAP", "fields")
    #install.packages2(pkgs, repos=dep_repos)
}

installPkgDeps <- function(pkgs)
{
    install.packages2(pkgs, repos=c(target_repo, dep_repos), type='source')
}

installMultiArchPkgDeps <- function(pkgs)
{
    installPkgDeps(pkgs)
}

