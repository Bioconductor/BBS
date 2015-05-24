### Repo where to find the no-vignettes target packages
target_repo <- Sys.getenv('BBS_CENTRAL_BASEURL')

## as long as BiocInstaller doesn't have any dependencies, we can install
## it using just the above repo. This will ensure we do not accidentally
## install the wrong version, which will then pull packages from the wrong
## set of repositories.

if (suppressWarnings(!require(BiocInstaller)))
{
    install.packages("BiocInstaller", repos=target_repo, type="source")
    require("BiocInstaller")
}

### Repos where to look for the dependencies of the target packages
### Remove the software repo
all_repos <- biocinstallRepos()
dep_repos <- all_repos[-match("BioCsoft", names(all_repos))]

repos <- c(target_repo, dep_repos)


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
    removeLockDirs()
    update.packages(repos=dep_repos, ask=FALSE)
    if (getOption("pkgType") == "source")
        return()
    ## For these situations where there is no binary or the binary version
    ## lags behind the source version
    update.packages(repos=dep_repos, ask=FALSE, type="source")
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
    available <- 
        suppressWarnings(available.packages(contriburl=contrib.url(repos, type)))
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


install.packages.both <- function(pkgs, repos, type, INSTALL_opts)
{
    if (type == "source") {
        install.packages(pkgs, repos=repos, type=type,
            INSTALL_opts=INSTALL_opts)
    } else {
        suppressWarnings(install.packages(pkgs, repos=repos, type=type,
            INSTALL_opts=INSTALL_opts))
    }
}

install.packages2 <- function(pkgs, repos=getOption("repos"),
                              type=getOption("pkgType"),
                              multiArch=FALSE)
{
    message("")
    message("INSTALLING THE REQUESTED PACKAGES AND THEIR DEPENDENCIES (IF ANY)")
    message("")
    removeLockDirs()
    
    
    ## Now that the --merge-multiarch flag is enabled on Mac, 
    ## we make multiarch TRUE regardless of how we were called.
    ## TODO - make the change in the Python build code instead,
    ## by having it call installMultiArchPkgDeps() instead
    ## of installPkgDeps() for Mac software builds. We want to 
    ## wait though until the --merge-multiarch feature is available
    ## in both release and devel R (which it will be after R-2.15
    ## is released).
    if (Sys.info()["sysname"] == "Darwin") multiArch = TRUE

    INSTALL_opts = ""
    if (multiArch)
        INSTALL_opts="--merge-multiarch"
    
    if(grepl("^x86_64-apple-darwin", R.Version()$platform))
        INSTALL_opts="--no-test-load --no-multiarch"
        
    install.packages.both(pkgs, repos=repos, type=type,
        INSTALL_opts=INSTALL_opts)
    
    more_pkgs <- getSuggestedPackagesToInstall(pkgs, repos=repos, type=type)
    if (length(more_pkgs) == 0L)
        return(invisible(NULL))
    message("")
    message("INSTALLING THE PACKAGES SUGGESTED BY THE REQUESTED PACKAGES")
    message("")
    removeLockDirs()
    for (pkg in more_pkgs) {
        install.packages.both(pkg, repos=repos, type=type,
            INSTALL_opts=INSTALL_opts)
    }
}

### Used for bootstrapping on Windows and Mac OS X where a few packages from
### CRAN and from our "extra" repository won't get installed by installPkgDeps()
### below (because installPkgDeps installs from source)
preinstallPkgs <- function()
{
    pkgs <- c("ada", "Cairo", "cairoDevice",
              "fields", "gtkDevice", "igraph", "igraph0", "mclust", "ncdf",
              "Rcpp", "RcppClassic", "RCurl", "rggobi", "rgl", "RGtk2",
              "rJava", "RJSONIO", "Rlibstree", "RMySQL", "RODBC",
              "SSOAP", "tcltk2", "tkrplot", "XML", "XMLRPC")
    
    ## on windows multiarch systems we build Rgraphviz from source
    if (STAGE2_mode != "multiarch")
        pkgs <- c(pkgs, "Rgraphviz")

    install.packages2(pkgs, repos=dep_repos)
}

installPkgDeps <- function(pkgs)
{
    install.packages2(pkgs, repos=c(target_repo, dep_repos), type="source")
}

installMultiArchPkgDeps <- function(pkgs)
{
    install.packages2(pkgs, repos=c(target_repo, dep_repos),
        multiArch=TRUE, type="source")
}


