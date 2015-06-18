## NOTE: The appropriate config file should be sourced prior
## to running this, so that environment variables are set correctly.
## ALSO, be sure X11 (Xvfb) is running.

if(!requireNamespace("BiocInstaller", quietly=TRUE))
    stop("BiocInstaller not installed!")

if(!requireNamespace("devtools", quietly=TRUE))
    biocLite("devtools")

if (!requireNamespace("covr", quietly=TRUE))
    devtools::install_github("jimhester/covr")

if (!requireNamespace("BiocParallel", quietly=TRUE))
    biocLite("BiocParallel")

if (!requireNamespace("BatchJobs", quietly=TRUE))
    biocLite("BatchJobs")

if (!requireNamespace("httr", quietly=TRUE))
    biocLite("httr")

#if (!file.exists("/tmp/cclogdir"))
#    unlink("/tmp/cclogdir", recursive=TRUE)

#dir.create("/tmp/cclogdir")
if(file.exists("/tmp/intermediate-coverage"))
    unlink("/tmp/intermediate-coverage", recursive=TRUE)
dir.create("/tmp/intermediate-coverage")

library(covr)
library(BiocParallel)
library(httr)
library(futile.logger)
library(BiocInstaller)


# Assume that we are running in the meat directory


getPkgListFromManifest <- function()
{
    manifestFile <- sprintf("bioc_%s.manifest",
        as.character(BiocInstaller::biocVersion()))
    lines <- readLines(manifestFile)
    lines <- lines[grepl("^Package:", lines)]
    lines <- sub("^Package: ", "", lines)
    lines <- gsub("\\s", "", lines)
    lines
}


pkgsWithTestDirectories <- function(invert=FALSE)
{
    pkgs_in_manifest <- getPkgListFromManifest()
    idx <- unlist(lapply(pkgs_in_manifest, function(x)
        file.exists(file.path(x, "tests"))))
    if (invert)
    {
        pkgs_in_manifest[!idx]
    } else {
        pkgs_in_manifest[idx]
    }
}

get_svn_rev <- function(pkg){
  file <- path.expand(paste0("../svninfo/svn-info-", pkg, ".txt"))
  dcf <- read.dcf(file)
  ret <- dcf[,"Last Changed Rev"]
  names(ret) <- pkg
  ret
}

if (!exists("svninfo"))
    svninfo <- unlist(lapply(getPkgListFromManifest(), get_svn_rev))


# Call me like this:
# lapply(covs, upload_coverage, svninfo=svninfo, bioc_version="devel") 
upload_coverage <- function(cov, svninfo, bioc_version="devel")
{
    pkg <- attr(cov, "package")$package
    print(pkg)
    ## this could throw an error if there is no such repo:
    oldwd <- setwd(paste0("/fh/fast/morgan_m/git_repos/", pkg))
    on.exit(setwd(oldwd))
    branches <- dir(".git/refs/heads")
    relbranch <- sprintf("release-%s", biocVersion())
    if (relbranch %in% branches)
        branch <- relbranch
    else
        branch <- "master"
    git_commit_id <- system2("git",  sprintf(
        "svn find-rev r%s %s", svninfo[[pkg]], branch), stdout=TRUE)
    token <- Sys.getenv("CODECOV_TOKEN")
    url <- sprintf("https://codecov.io/github/Bioconductor-mirror/%s?access_token=%s", pkg, token)
    content <- content(GET(url))
    upload_token <- content$upload_token
    codecov(coverage=cov, token=upload_token, commit=git_commit_id,
        branch=branch)
}

getCoverage <- function(package)
{
    if(!file.exists(file.path(package, "tests")))
        return(NULL)
    # remove this soon:
    if (package %in% c("BrowserViz", "BrowserVizDemo", "RCyjs"))
        return (NULL)
    print(sprintf("Processing %s...", package))
    flog.info(sprintf("Processing %s...", package))
    ret <- tryCatch({cov <- package_coverage(package)}, error=function(e) e)
    save(ret, file=sprintf("/tmp/intermediate-coverage/%s.rda", package))
    if ("coverage" %in% class(ret))
    {
        rcpt <- upload_coverage(ret, svninfo)
        print(sprintf("Uploaded coverage for %s, status was %s.",
            package, rcpt$meta$status))
    }
    ret 
}

packages <- getPkgListFromManifest()


names(packages) <- packages


param <- MulticoreParam(5)#, log=TRUE)

res <- bplapply(packages, getCoverage, BPPARAM=param)
save(res, file="/tmp/res.rda")

 