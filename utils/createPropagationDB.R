# This file contains a function createPropagationList() which
# will produce a file containing entries like

# BiocGenerics#source#propagate: YES
# RGalaxy#source#propagate: YES
# mypkg#source#propagate: version 99.99.99 of dependency Foo is not available; found version 0.13.4 for type source

# There is a companion file test_createPropagationDB.R containing
# unit tests.


if (!require(BiocInstaller))
{
    source("http://bioconductor.org/biocLite.R")
}
library(tools)

## GLOBAL VARIABLES

t <- tempdir()
rvers <- paste(getRversion()$major,
    getRversion()$minor,
    sep=".")
biocvers <- BiocInstaller::biocVersion()


# Takes as input the value of an Imports, Depends,
# or LinkingTo field and returns a named character
# vector of Bioconductor dependencies, where the names
# are version specifiers or blank.
cleanupDependency <- function(input)
{
    if (is.null(input)) return(character(0))
    output <- gsub("\\s", "", input)
    raw_nms <- output
    nms <- strsplit(raw_nms, ",")[[1]]
    namevec <- vector(mode = "character", length(nms))
    output <- gsub("\\([^)]*\\)", "", output)
    res <- strsplit(output, ",")[[1]]
    for (i in 1:length(nms))
    {
        if(grepl(">=", nms[i], fixed=TRUE))
        {
            tmp <- gsub(".*>=", "", nms[i])
            tmp <- gsub(")", "", tmp, fixed=TRUE)
            namevec[i] <- tmp
        } else {
            namevec[i] = ''
        }
    }
    names(res) <- namevec
    res <- res[which(res != "R")]
    res
}

# Helper function for tiebreaker()
best <- function(a, b)
{
    try({pa <- package_version(a)}, silent=TRUE)
    try({pb <- package_version(b)}, silent=TRUE)
    if (!exists("pa") && !exists("pb")) return("")
    if (exists('pa') && !exists("pb")) return(a)
    if (!exists("pa") && exists("pb")) return(b)
    as.character(max(pa, pb))
}

# Given two package version specifiers, which is
# for a more recent version.
tiebreaker <- function(vec)
{
    hsh <- new.env(parent = emptyenv())
    for (i in 1:length(vec))
    {
        nm <- names(vec)[i]
        vl <- vec[i]
        if (vl %in% ls(hsh))
        {
            hv <- get(vl, envir=hsh)
            assign(vl, best(hv, nm), envir=hsh)
        } else {
            assign(vl, nm, envir=hsh)
        }
    }
    tmp <- unlist(as.list(hsh))
    vec <- names(tmp)
    names(vec) <- tmp
    vec
}

# Get the Depends/Imports/LinkingTo (Bioconductor) dependencies
# for a given package.
getdeps <- function(pkg, src)
{
    fields <- c("Depends", "Imports", "LinkingTo")
    if (missing(src))
    {
        x <- subset(fullrepo.df, Package == pkg)
        names <- colnames(x)
        if (dim(x)[1] == 0)
            x <- subset(bioc.apdf, Package==pkg)
    } else {
        x <- src
        names <- names(x)
    }
    res <- c()
    for (field in fields)
    {
        if(field %in% names &&  length(x[field]))#!is.na(x[field]))
            res <- c(res, cleanupDependency(unname(x[field])[[1]]))
    }
    if(length(res))
        res <- tiebreaker(res)
    res <- res[res %in% getBiocPkgs()]
    if (!length(res))
        return(NULL)
    res
}

# Get the list of Bioconductor packages
getBiocPkgs <- function()
{
    p <- subset(fullrepo.df, select="Package")
    v <- as.vector(p)[[1]]
    unique(c(v, bioc.ap))
}


# Determine whether a given package can be propagated.
makeDecision <- function(pkg)
{
    if (!pkg %in% dir.pkgs)
    {
        assign(pkg, "RemoveMe", envir=e)
        return()
    }
    tf <- file.path(tempdir(), "mytempfile")
    if (pkg %in% ls(e))
        return() # don't need to do anything
    deps <- getdeps(pkg)
    if (is.null(deps))
    {
        assign(pkg, TRUE, envir=e)
        ap <<- addPkgToPartialRepos(pkg, deps, type)
        cat(pkg, "\n", file=tf, append=TRUE)
    } else {
        repos <- c(partialrepo.url, biocrepo.url)
        ap <- available.packages(contrib.url(repos, type), type=type)
        for (i in 1:length(deps))
        {
            vreq <- names(deps)[i]
            dep <- deps[i]
            # browser()
            row <- ap[dep,]
            if(!length(row))
            {
                assign(pkg, paste("NO: dependency", dep, "not available for type",
                    type), envir=e)
                return()
            }
            if(exists("ver"))
                rm(ver)
            try({ver <- package_version(vreq)}, silent=TRUE)
            if (!exists("ver"))
                ver <- package_version("0.0.0")
            available.version <- package_version(row['Version'])
            if (available.version >= ver)
            {
                # good.
            } else {
                assign(pkg, paste("NO: version", vreq, "of dependency", dep,
                    "is not available; found version", available.version,
                    "for type", type), envir=e)
                return()
            }
        }
    }
    # if we made it here we must be good.
    # so now we should be able to add 'pkg' to partialrepos
    ap <<- addPkgToPartialRepos(pkg, deps, type)


    # this should go away or get modified:
    cat(pkg, "\n", file=tf, append=TRUE)
    assign(pkg, TRUE, envir=e)
}

# Just governs whether pkg should be added to the list of
# packages we are processing that are somehow different
# (newer or changed) than what is already online.
# This is NOT where the final decision is made
# about whether a package should be propagated;
# that's in makeDecision().
shouldPackageBeAdded <- function(pkg)
{
    # compare pkg entry in fullrepos and biocrepos
    # if pkg is not in biocrepos, return TRUE
    # if fullrepos version is higher, return TRUE, otherwise FALSE
    if (!pkg %in% rownames(bioc.apdb))
        return(TRUE)
    pkgInfoInBioc <- bioc.apdb[pkg,]
    pkgInfoInFullrepo <- fullrepo.apdb[fullrepo.apdb[,"Package"] == pkg,]
    # biocDeps <- getdeps(pkg, pkgInfoInBioc)
    # if (!is.null(biocDeps))
    #     biocDeps <- sort(biocDeps)
    # fullrepoDeps <- getdeps(pkg, pkgInfoInFullrepo)
    # if (!is.null(fullrepoDeps))
    #     fullrepoDeps <- sort(fullrepoDeps)
    versionInBioc <- package_version(pkgInfoInBioc['Version'])
    versionInFullrepo <- package_version(pkgInfoInFullrepo['Version'])
    if (versionInFullrepo > versionInBioc)
        return(TRUE)
    FALSE
    # we could check somewhere if the version has been
    # *decremented*, but we're not doing that yet.
    # if (length(biocDeps) == length(fullrepoDeps) &&
    #   all(biocDeps == fullrepoDeps)
    #   && all(names(biocDeps) == names(fullrepoDeps)))
    # {
    #     return(FALSE)
    # }
    # TRUE
}


# If we have determined that 'pkg' can be propagated, then we
# add it to a partial repository we are building. Our main
# algorithm checks each package against the union of what is
# onine already (available via biocLite()) and what is
# in this partial repository.
addPkgToPartialRepos <- function(pkg, deps, type)
{
    if(shouldPackageBeAdded(pkg))
    {
        # print(paste("adding to partial repos:", pkg))
        src.url <- paste0("file://", file.path(t, "fullrepo"))
        src.db <- available.packages(contrib.url(src.url, type), type)
        stuffToCopy <- src.db[pkg,]
        stuffToCopy['Repository'] <- sub("fullrepo", "partialrepo",
            stuffToCopy['Repository'])
        dest.url <- paste0("file://",
            file.path(t, "partialrepo"))
        dest.db <- available.packages(contrib.url(dest.url, type), type)
        if (!pkg %in% dest.db[, "Package"])
        # if (!pkg %in% rownames(dest.db))
        {
            print(paste("adding to partial repos:", pkg))
            dest.db <- rbind(dest.db, stuffToCopy)
            dest <- file.path(t, "partialrepo", contribpath)
            write.dcf(dest.db, file.path(dest, "PACKAGES"))
            if(file.exists(file.path(dest, "PACKAGES.gz")))
                file.remove(file.path(dest, "PACKAGES.gz"))
        }
        dest.db
    } else {
        # print(paste("not adding", pkg))
    }
}

# Create PACKAGES file for temporary repos
makePackagesFile <- function(outgoingDir, type, contribpath)
{
    t <- tempdir()
    fullrepo <- file.path(t, "fullrepo")
    dest <- file.path(fullrepo, contribpath)
    if (file.exists(dest))
        unlink(dest, recursive=TRUE)
    dir.create(dest, recursive=TRUE)
    # FIXME - remove the IF here:
    # if (!file.exists(file.path(outgoingDir, "PACKAGES"))) # hack
    # {
        message("Running write_PACKAGES()...")
        t2 <- type
        if (type %in% c("mac.binary.mavericks", "mac.binary.el-capitan"))
            t2 <- "mac.binary"
        write_PACKAGES(outgoingDir, type=t2)
    # }
    file.copy(file.path(outgoingDir, "PACKAGES"),
        dest, overwrite=TRUE)
    # unlink(file.path(outgoingDir, c("PACKAGES", "PACKAGES.gz")))
    unlink(file.path(outgoingDir, "PACKAGES.gz"))
    read.dcf(file.path(dest, "PACKAGES"))
}


# The recursive function that is called to determine
# the order of packages to process. We start with packages
# that have no (Bioconductor) dependencies and then proceed to
# packages that have only the packages we've already processed
# as dependencies, and so on.
recur <- function(pkg)
{
    deps <- getdeps(pkg)
    if (is.null(deps))
    {
        makeDecision(pkg)
    } else {
        for (dep in deps)
        {
            if (!dep %in% ls(e))
            {
                recur(dep)
            }
        }
        if (all(deps %in% ls(e)))
        {
            makeDecision(pkg)
        }
    }
}


# The main entry point to this file.
# outgoingDirPath is a directory that normally contains under it
# source, win.binary, mac.binary, mac.binary.mavericks, and
# mac.binary.el-capitan directories.
# biocrepo should be either "bioc" (for software packages) or
# "data/experiment" for experiment data packages. internalRepos is
# consulted to see what needs to be propagated (i.e. nothing if package
# there has the same version.)
createPropagationList <- function(outgoingDirPath, propagationDbFilePath,
    biocrepo=c("bioc", "data/experiment", "workflows"), internalRepos)
{
    if(missing(internalRepos))
        stop({"Must specify internalRepos!"})
    if(missing(biocrepo))
        stop("Must specify biocrepo!")
    repo.name <- switch(biocrepo,
                        "bioc" = "BioCsoft",
                        "data/experiment" = "BioCexp",
                        "workflows" = "BioCworkflow")
    bioc.apdb <<- available.packages(
    contrib.url(biocinstallRepos()[repo.name]), type="source")
    bioc.apdf <<- as.data.frame(bioc.apdb, stringsAsFactors=FALSE)
    bioc.ap <<- rownames(bioc.apdb)

    # vv Not robust to new package types! vv
    pkgDirs <- c("source", "win.binary", "mac.binary",
        "mac.binary.mavericks", "mac.binary.el-capitan")
    if (biocrepo!="bioc")
        pkgDirs <- "source"
    descFields <- c("Package", "Version", "Depends", "Imports", "LinkingTo",
        "License", "MD5sum", "NeedsCompilation")
    outgoingDirs <- file.path(outgoingDirPath, pkgDirs)

    # remove me later:
    tf <- file.path(tempdir(), "mytempfile")
    if(file.exists(tf))
        file.remove(tf)


    t <- tempdir()
    partialrepo <<- file.path(t, "partialrepo")
    partialrepo.url <<- paste0("file://", partialrepo)
    contribdirs <- sprintf(
        c("src/contrib",
          "bin/windows/contrib/%s",
          "bin/macosx/contrib/%s",
          "bin/macosx/mavericks/contrib/%s",
          "bin/macosx/el-capitan/contrib/%s"), rvers)
    contribs <- file.path(partialrepo, contribdirs)
    pkgtypes <- c("source", "win.binary", "mac.binary",
        "mac.binary.mavericks", "mac.binary.el-capitan")
    names(contribs) <- outgoingDirs
    if (file.exists(partialrepo))
        unlink(partialrepo, recursive=TRUE)
    dir.create(partialrepo, recursive=TRUE)
    for (contrib in contribs)
        dir.create(contrib, recursive=TRUE)
    overall <<- new.env(parent=emptyenv())

    for (i in 1:length(outgoingDirs))
    {
        outgoingDir <<- outgoingDirs[i]
        if (!file.exists(outgoingDir))
        {
            message(paste(outgoingDir, "does not exist, skipping..."))
            next
        }



        contribpath <<- contribdirs[i]
        type <<- pkgtypes[i]

        fullrepo.apdb <<- makePackagesFile(outgoingDir, type, contribpath)
        fullrepo.df <<- as.data.frame(fullrepo.apdb, stringsAsFactors=FALSE)
        online.contrib <- file.path(t, "biocrepo",
            contribpath)
        if(file.exists(online.contrib))
            unlink(online.contrib, recursive=TRUE)
        dir.create(online.contrib, recursive=TRUE)
        pkgIndex <- file.path(online.contrib, "PACKAGES")
        if(file.exists(pkgIndex))
            unlink(pkgIndex)
        tryCatch(download.file(paste0("http://bioconductor.org/packages/",
                     biocvers, "/", biocrepo, "/src/contrib/PACKAGES"),
                 destfile=pkgIndex), error = function (e) warning(e))
        biocrepo.url <<- paste0("file://", file.path(t, "biocrepo"))
        files <- dir(outgoingDir,
            pattern="\\.tar\\.gz$|\\.tgz$|\\.zip$")
        dir.pkgs <<- unlist(lapply(files,
            function(x)strsplit(x, "_", fixed=TRUE)[[1]][1]))
        e <<- new.env(parent=emptyenv())
        contrib <- contribs[outgoingDir]
        pkgsfile <- file.path(contrib, "PACKAGES")
        if (file.exists(pkgsfile))
            file.remove(pkgsfile)
        file.create(pkgsfile)
        for (pkg in dir.pkgs) recur(pkg)
        assign(type, e, envir=overall)
    }
    nms <- c()
    o <- as.list(overall)
    for (i in names(o))
    {
        o[[i]] <- as.list(o[[i]])
        nms <- append(nms, names(o[[i]]))
    }
    out <- file(propagationDbFilePath, "w")
    nms <- sort(unique(nms))
    for (pkg in nms)
    {
        for(type in names(o))
        {
            status <- o[[type]][[pkg]]
            if(!length(status)) next

            if (status == "RemoveMe")
            {
                next
            } else {
                if (!grepl("^NO", status))
                    status <- doesReposNeedPkg(pkg, type, outgoingDirPath, internalRepos)
            }
            str <- sprintf("%s#%s#propagate: %s", pkg, type, status)
            cat(str, file=out, sep="\n")
        }
    }
    close(out)
}

getPkgVer <- function(pkg)
{
    pkg <- sub("\\.tar\\.gz$|\\.tgz$|\\.zip$", "", pkg)
    package_version(strsplit(pkg, "_")[[1]][2])
}

doesReposNeedPkg <- function(pkg, type, outgoingDirPath, internalRepos)
{
    internalRepos <- sub("data-experiment", "data/experiment",
        internalRepos, fixed=TRUE)
    contribdirs <- sprintf(
        c("src/contrib",
          "bin/windows/contrib/%s",
          "bin/macosx/contrib/%s",
          "bin/macosx/mavericks/contrib/%s",
          "bin/macosx/el-capitan/contrib/%s"), rvers)
    pkgtypes <- c("source", "win.binary", "mac.binary",
        "mac.binary.mavericks", "mac.binary.el-capitan")
    ind <- which(pkgtypes==type)
    fileToCopy <- dir(file.path(outgoingDirPath, type),
        pattern=paste0("^", pkg, "_"))
    destFile <- dir(file.path(internalRepos, contribdirs[ind]),
        pattern=paste0("^", pkg, "_"))
    if(!length(destFile))
    {
        return("YES, package does not exist in internal repository.")
    }
    if (fileToCopy == destFile)
    {
        return("UNNEEDED, same version exists in internal repository")
    }
    if (getPkgVer(fileToCopy) > getPkgVer(destFile))
    {
        return("YES, new version is higher than in internal repository")
    } else {
        return("NO, built version is LOWER than in internal repository!!!")
    }

}

## This function is called by the updateReposPkgs-*.sh scripts,
## running as biocadmin. Instead of just a straight cp --no-clobber --verbose,
## we consult the propagation DB to determine what can be copied,
## and then copy it (without overwriting existing files.) As before, we
## display what has been copied, but we also display what has
## NOT propagated.
copyPropagatableFiles <- function(srcDir, fileExt, propagationDb, destDir=".")
{
    stopifnot(file.exists(propagationDb))
    contribpaths <- c(
        'source'="src/contrib",
        'win.binary'=paste0("bin/windows/contrib/", rvers),
        'mac.binary'=paste0("bin/macosx/contrib/", rvers),
        'mac.binary.mavericks'=paste0("bin/macosx/mavericks/contrib/", rvers),
        'mac.binary.el-capitan'=paste0("bin/macosx/el-capitan/contrib/", rvers))
    db <- read.dcf(propagationDb)
    segs <- strsplit(srcDir, "/")[[1]]
    srcType <- segs[length(segs)]
    srcFiles <- dir(srcDir, pattern=glob2rx(paste0("*.", fileExt)))
    res <- unlist(lapply(srcFiles, function(x){
        pkg <- strsplit(x, "_")[[1]][1]
        key <- sprintf("%s#%s#propagate", pkg, srcType)
        if (key %in% colnames(db) &&  grepl("^YES", db[, key]))
            TRUE
        else
            FALSE
    }))
    propagatable <- srcFiles[res]

    destinations <- c()
    for (file in propagatable)
    {
        # simulate cp --verbose output
        fullDestDir <- file.path(destDir, contribpaths[srcType])
        if(!file.exists(file.path(fullDestDir, file)))
            cat(sprintf("‘%s‘ -> ‘%s‘\n", file.path(srcDir, file),
                file.path(fullDestDir, file)))
        # Currently ignoring the result of the copy operation.
        result <- file.copy(file.path(srcDir, file), fullDestDir,
            overwrite=FALSE)
    }

    invisible(NULL)
}
