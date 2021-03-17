### =========================================================================
### Used at the beginning of STAGE2 to generate the pkg_dep_graph.txt file
### -------------------------------------------------------------------------


## If a data/experiment package depends on a software
## package and nothing else is going to trigger
## the installation of that software package,
## (i.e. no other software packages depend on it),
## then you can manually trigger it by putting
## ForceInstall: TRUE
## in the optional .BBSoptions file in the root
## of the software package's directory. The following
## function takes the list of target packages and spits out
## the ones that have this tag, and therefore should
## be installed no matter what.
.getPkgsToForceInstall <- function(pkgs)
{
    meatDir <- Sys.getenv("BBS_MEAT_PATH")

    shouldBeForceInstalled <- function(pkg)
    {
        optionsFile <- file.path(meatDir, pkg, ".BBSoptions")
        if (!file.exists(optionsFile))
            return(FALSE)
        lines <- readLines(optionsFile)
        idx <- grepl("^ForceInstall:", lines)
        if (!any(idx))
            return (FALSE)
        line <- lines[idx]
        value = trimws(toupper(strsplit(line, ":")[[1]][2]))
        return (value == "TRUE")
    }
    idx <- unlist(lapply(pkgs, shouldBeForceInstalled))
    pkgs[idx]
}

### Return a character vector containing the *direct* deps for 'pkg' (can
### be 'character(0)'), or NULL if 'pkg' is an "unknown" package (i.e. not
### available *and* not installed).
.extractDirectPkgDeps <- function(pkg, available_pkgs,
                                  fields=c("Depends", "Imports", "LinkingTo"))
{
    if (pkg %in% rownames(available_pkgs)) {
        deps <- available_pkgs[pkg, fields]
    } else {
        ## Only in that case we look at the installed packages. This allows us
        ## to get the deps for base packages, and, more generally speaking,
        ## to cover the situation where a package is installed but not
        ## available.
        installed_pkgs <- installed.packages()
        if (!(pkg %in% rownames(installed_pkgs)))
            return(NULL)  # 'pkg' is an unknown package
        deps <- installed_pkgs[pkg, fields]
    }
    deps <- deps[!is.na(deps)]
    if (length(deps) == 0L)
        return(character(0))
    deps <- unlist(strsplit(deps, ",", fixed=TRUE), use.names=FALSE)
    deps <- sapply(strsplit(deps, "(", fixed=TRUE), `[[`, 1L)
    deps <- gsub("(^[ \n\t]*|[ \n\t]*$)", "", deps)
    setdiff(unique(deps), "R")
}

### Return all direct deps in a character vector.
.extractAllDirectDeps <- function(pkgs, available_pkgs,
                                  fields=c("Depends", "Imports", "LinkingTo"))
{
    tmp <- lapply(pkgs, .extractDirectPkgDeps, available_pkgs, fields=fields)
    unique(unlist(tmp, use.names=FALSE))
}

### The names on the returned list are the union of 'pkgs' and their direct
### and indirect hard deps (extracted from the Depends, Imports, and LinkingTo
### fields). Each list element is a character vector containing the *direct*
### hard deps for the corresponding package (can be 'character(0)'), or NULL
### for an "unknown" package (i.e. not available *and* not installed)).
### Note that the function uses a simple and efficient algorithm that is
### robust to circular deps (it actually doesn't need to do anything special
### to handle them).
.buildPkgDepsList <- function(pkgs, available_pkgs)
{
    ## Growing a list is not efficient (a copy of the list is triggered each
    ## time elements are added to it), so we use an environment instead.
    buf <- new.env(parent=emptyenv())
    new_keys <- pkgs
    while (length(new_keys)) {
        for (key in new_keys) {
            deps <- .extractDirectPkgDeps(key, available_pkgs)
            assign(key, deps, envir=buf)
        }
        all_deps <- unique(unlist(as.list(buf), use.names=FALSE))
        all_keys <- ls(buf, all.names=TRUE)
        new_keys <- setdiff(all_deps, all_keys)
    }
    as.list(buf)
}

### Write the STAGE2 package list and their deps to a file in a "key: values"
### format with one line per key. For example:
###   pkg1: pkg1a pkg1b
###   pkg2: pkg2a pkg2b pkg2c
###   pkg3:
###   pkg4: pkg4a
### Each line lists the deps for a given package and is called an "entry" (e.g.
### the 2nd line is the entry for pkg2). "Unknown" packages (i.e. not available
### *and* not installed) can appear on the right side of the colon (i.e. in the
### list of deps) but not on its left side, that is, we don't generate an entry
### for them.
### Note that the generated file can be seen as a kind of simplified Makefile.
.build_pkg_dep_graph <- function(target_pkgs_file, repos,
                                 outfile="", short.list=FALSE)
{
    if (is.character(outfile)) {
        if (identical(outfile, "")) {
            outfile <- stdout()
        } else {
            outfile <- file(outfile, "w")
            on.exit(close(outfile))
        }
    }

    ## Load the list of target packages.
    target_pkgs <- readLines(target_pkgs_file)

    ## Fetch the available *source* packages (we use type="source" even on
    ## Windows or Mac).
    contrib_urls <- contrib.url(repos, type="source")
    available_pkgs <- available.packages(contrib_urls)

    ## Build the package deps list.
    if (short.list) {
        fields <- c("Depends", "Imports", "LinkingTo", "Suggests")
        direct_deps <- .extractAllDirectDeps(target_pkgs, available_pkgs,
                                             fields=fields)
        ## Add in the list of packages that should be
        ## force-installed no matter what, as indicated
        ## by the ForceInstall: TRUE tag in
        ## the .BBSoptions file:
        pkgs <- union(.getPkgsToForceInstall(target_pkgs), direct_deps)
    } else {
        suggested_pkgs <- .extractAllDirectDeps(target_pkgs, available_pkgs,
                                                fields="Suggests")
        pkgs <- union(target_pkgs, suggested_pkgs)
    }
    pkg_dep_graph <- .buildPkgDepsList(pkgs, available_pkgs)

    ## Write the package deps list to the output file.
    for (i in seq_along(pkg_dep_graph)) {
        deps <- pkg_dep_graph[[i]]
        if (is.null(deps))
            next
        pkg <- names(pkg_dep_graph)[[i]]
        cat(pkg, ": ", paste0(deps, collapse=" "), "\n", sep="", file=outfile)
    }
}

### Same as in installNonTargetPkg.R
.get_non_target_repos <- function()
{
    non_target_repos <- readLines(Sys.getenv('BBS_NON_TARGET_REPOS_FILE'))
    gsub("BBS_BIOC_VERSION", Sys.getenv('BBS_BIOC_VERSION'),
         non_target_repos, fixed=TRUE)
}

.get_all_repos <- function()
{
    target_repo <- Sys.getenv('BBS_CENTRAL_BASEURL')
    non_target_repos <- .get_non_target_repos()
    c(target_repo, non_target_repos)
}

build_pkg_dep_graph <- function(target_pkgs_file, outfile="", short.list=FALSE)
{
    .build_pkg_dep_graph(target_pkgs_file, .get_all_repos(),
                         outfile=outfile, short.list=short.list)
}

