# Run me like this:
# library(RUnit)
# runTestFile("test_createPropagationDB.R")
# ...or from the OS command line with:
# R -e "RUnit::runTestFile('test_createPropagationDB.R')"

if(!require(BiocInstaller))
    source("http://bioconductor.org/biocLite.R")


deps <- c("RUnit", "devtools", "BiocGenerics")

for (dep in deps)
{
    if(!suppressPackageStartupMessages(do.call(require, list(package=dep))))
        biocLite(dep, suppressUpdates=TRUE)
}

source("createPropagationDB.R")

.setUp <- function()
{
    unitTestHome <<- file.path(tempdir(), "unitTestHome")
    if (file.exists(unitTestHome))
        unlink(unitTestHome, recursive=TRUE)
    dir.create(unitTestHome)    
}

.tearDown <- function()
{
    unlink(unitTestHome, recursive=TRUE)
}


.create <- function(path, description=getOption("devtools.desc"))
{
    dir.create(path, recursive=TRUE)
    o<-capture.output(suppressMessages(suppressWarnings(setup(path, description,
        rstudio=FALSE))))
}

.buildsrcpkg <- function(pkg, removeSource=TRUE,
    dir=file.path(unitTestHome, "source"))
{
    oldwd <- getwd()
    on.exit(setwd(oldwd))
    setwd(dir)
    R <- file.path(Sys.getenv("R_HOME"), "bin", "R")
    system2(R, paste0("CMD build ", pkg), stdout=FALSE, stderr=FALSE)
    if(removeSource)
        unlink(pkg, recursive=TRUE)
}


.buildbinpkg <- function(pkg, dir, type=c("mac.binary", "win.binary"))
{
    oldwd <- getwd()
    on.exit({
        if(!is.null(oldwd))
            setwd(oldwd)
    })
    setwd(dir)
    .buildsrcpkg(pkg, dir=dir)
    R <- file.path(Sys.getenv("R_HOME"), "bin", "R")
    tarball <- dir(dir)[1]
    system2(R, paste0("CMD INSTALL --build ", tarball), stdout=FALSE, stderr=FALSE)
    #binpkg <- dir(dir)[2]
    pkgentries <- dir(dir)[grepl(paste0("^", pkg, "_"), dir(dir))]
    binpkg <-  pkgentries[!grepl(tarball, pkgentries, fixed=TRUE)]
    unlink(tarball)
    # FIXME - file will not always say unknown-linux; find out how
    # the name is generated.
    if (grepl("_R_x86_64-unknown-linux-gnu.tar.gz", binpkg))
    {
        newname <- sub("_R_x86_64-unknown-linux-gnu.tar.gz", ".tgz",
            binpkg, fixed=TRUE)
        file.rename(binpkg, newname)
        binpkg <- newname
    }
    if (type == "win.binary")
    {
        untar(binpkg)
        dcf <- read.dcf(file.path(pkg, "DESCRIPTION"))
        dcf[,'Built'] <- sub("unix", "windows", dcf[,'Built'])
        write.dcf(dcf, file.path(pkg, "DESCRIPTION"))
        zipname <- sub(".tgz", ".zip", binpkg)
        z<-capture.output(suppressMessages(suppressWarnings(zip(zipname,
            pkg, zip="zip"))))
        unlink(pkg, recursive=TRUE)
        unlink(binpkg)
    }
}
 
test_impossibleDepDoesNotPropagate0 <- function()
{
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    dir.create(file.path(unitTestHome, "source"))
    dir.create(file.path(unitTestHome, "src", "contrib"), recursive=TRUE)
    .create(file.path(unitTestHome, "source", "mypkg"),
        list(Imports="BiocGenerics (>= 99.99.99)"))
    .buildsrcpkg("mypkg")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(grepl("mypkg#source#propagate: NO: version 99.99.99 of dependency BiocGenerics is not available;", lines))
}

test_pkgCanPropagate0 <- function()
{
    dir.create(file.path(unitTestHome, "source"))
       .create(
        file.path(
         unitTestHome,
            "source", "mypkg"
          ),
          list(
            Imports="BiocGenerics (>= 0.0.0)"
          )
        )
    dir.create(file.path(unitTestHome, "src", "contrib"), recursive=TRUE)
    .buildsrcpkg("mypkg")
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(grepl("mypkg#source#propagate: YES", lines))
}

test_newPkgCanSatisfyVersionDependency <- function()
{
    dir.create(file.path(unitTestHome, "source"))
    dir.create(file.path(unitTestHome, "src", "contrib"), recursive=TRUE)
    ## Note, we're depending on the existence of RGalaxy in bioc
    .create(file.path(unitTestHome, "source", "RGalaxy"),
        list(Imports="BiocGenerics (>= 99.0.0)"))
    .buildsrcpkg("RGalaxy")
    .create(file.path(unitTestHome, "source", "BiocGenerics"),
        list(Version="99.1.1"))
    .buildsrcpkg("BiocGenerics")
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(any(grepl("BiocGenerics#source#propagate: YES", lines)))
    checkTrue(any(grepl("RGalaxy#source#propagate: YES", lines)))
}

test_binPkg0 <- function()
{
    macbindir <- file.path(unitTestHome, "mac.binary")
    dir.create(macbindir)
    dir.create(file.path(unitTestHome, "bin", "macosx", "contrib",
        BiocInstaller:::BIOC_VERSION), recursive=TRUE)
    pkgdir <- file.path(macbindir, "myMacPkg")
    .create(pkgdir)
    .buildbinpkg("myMacPkg", macbindir, "mac.binary")
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(grepl("myMacPkg#mac.binary#propagate: YES", lines))
}


test_impossibleDepDoesNotPropagate_win <- function()
{
    dir.create(file.path(unitTestHome, "bin", "macosx", "mavericks", "contrib",
        BiocInstaller:::BIOC_VERSION), recursive=TRUE)

    dir.create(file.path(unitTestHome, "bin", "windows", "contrib",
        BiocInstaller:::BIOC_VERSION), recursive=TRUE)
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    windir <- file.path(unitTestHome, "win.binary")
    dir.create(windir)
    pkgdir <- file.path(windir, "RGalaxy")
    .create(pkgdir,
        list(Imports="BiocGenerics (>= 99.99.99)"))
    .buildbinpkg("RGalaxy", windir, "win.binary")
    pkgdir <- file.path(windir, "BiocGenerics")
    .create(pkgdir,
        list(Version="100.100.2"))
    .buildbinpkg("BiocGenerics", windir, "win.binary")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(any(grepl("RGalaxy#win.binary#propagate: YES", lines)))
}

test_binPkg_mavericks <- function()
{
    macbindir <- file.path(unitTestHome, "mac.binary.mavericks")
    dir.create(macbindir)
    pkgdir <- file.path(macbindir, "myMacPkg")
    .create(pkgdir)
    .buildbinpkg("myMacPkg", macbindir, "mac.binary.mavericks")
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    result <- createPropagationList(unitTestHome, outfile, "bioc", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(grepl("myMacPkg#mac.binary.mavericks#propagate: YES", lines))
}

test_impossibleDepDoesNotPropagate_dataexp0 <- function()
{
    dir.create(file.path(unitTestHome, "src", "contrib"), recursive=TRUE)
    outfile <- file.path(unitTestHome, "propagationdb.txt")
    dir.create(file.path(unitTestHome, "source"))
    .create(file.path(unitTestHome, "source", "mypkg"),
        list(Imports="ALL (>= 99.99.99)"))
    .buildsrcpkg("mypkg")
    result <- createPropagationList(unitTestHome, outfile, "data/experiment", unitTestHome)
    lines <- readLines(outfile)
    checkTrue(grepl("mypkg#source#propagate: NO: version 99.99.99 of dependency ALL is not available;", lines))
}
