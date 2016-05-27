## NOTE: The appropriate config file should be sourced prior
## to running this, so that environment variables are set correctly.
## ALSO, be sure X11 (Xvfb) is running.

if(!requireNamespace("BiocInstaller", quietly=TRUE))
    stop("BiocInstaller not installed!")

reqs <- c("devtools", "BiocParallel", "BatchJobs", "httr", "jsonLite", "R.utils")
lapply(reqs, function(x){
    if(!requireNamespace(x, quietly=TRUE))
    {
        biocLite(x)
        requireNamespace(x)
    }
})


if (!requireNamespace("covr", quietly=TRUE))
{
    devtools::install_github("jimhester/covr")
    requireNamespace("covr")
}

TIMEOUT <- 2400 # 40 minutes


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

.stopifnot <- function(msg, expr)
{
    if (!expr)
    {
        flog.info(msg)
        print(msg)
        stopifnot(expr)
    }
}

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
  if (file.exists(file)) {
      dcf <- read.dcf(file)
      ret <- dcf[,"Last Changed Rev"]
      names(ret) <- pkg
      ret
  }
}

if (!exists("svninfo")) {
    svninfo <- unlist(Filter(Negate(is.null), lapply(getPkgListFromManifest(), get_svn_rev)))
}


getBranch <- function()
{
    if (BiocInstaller:::IS_USER)
        sprintf("release-%s", biocVersion())
    else
        'master'
}

getGitCommitId <- function(package, svn_rev)
{
    branch <- getBranch()
    url <- sprintf("https://api.github.com/repos/Bioconductor-mirror/%s/commits?sha=%s&access_token=%s",
                   package, branch, Sys.getenv("GITHUB_OAUTH_TOKEN"))
    commits <- content(GET(url))
    interm <- unlist(lapply(commits, function(x){
        grepl(sprintf("%s@", package, svn_rev), x$commit$message)
    }))
    if (!any(interm))
        return(NULL)
    intermMatches <- commits[which(interm)]
    # find the first one that is after svn_rev
    res <- unlist(lapply(intermMatches, function(x){
        regex <- sprintf("%s@([0-9]+) ", package)
        rslt <- regexec(regex, x$commit$message)
        if (rslt[[1]][1] == -1)
            return(-1)
        start <- rslt[[1]][2]
        len <- attr(rslt[[1]], "match.length")[2] -1
        as.integer(substr(x$commit$message, start, start+len))
    }))
    res <- sort(res)
    closestSvnRevision <- res[res >= as.numeric(svn_rev)][1]
    theCommit <- lapply(commits, function(x){
        grepl(sprintf("%s@%s", package, as.character(closestSvnRevision)),
            x$commit$message)
    })
    commits[which(unlist(theCommit))][[1]]$sha
}

# Call me like this:
# lapply(covs, upload_coverage, svninfo=svninfo)
upload_coverage <- function(cov, svninfo)
{
    pkg <- attr(cov, "package")$package
    print(pkg)

    git_commit_id <- getGitCommitId(pkg, svninfo[[pkg]])
    .stopifnot(sprintf("git_commit_id for %s is null!", pkg),
        !is.null(git_commit_id))
    token <- Sys.getenv("CODECOV_TOKEN")
    .stopifnot("CODECOV_TOKEN not set", nchar(token) > 0)
    url <- sprintf("https://codecov.io/api/github/Bioconductor-mirror/%s?access_token=%s", pkg, token)
    content <- content(GET(url))
    upload_token <- content$repo$upload_token
    .stopifnot("upload_token is null!", !is.null(upload_token))
    codecov(coverage=cov, token=upload_token, commit=git_commit_id,
        branch=getBranch())
}

getCoverage <- function(package, force=FALSE)
{
    tryCatch(evalWithTimeout(getCoverage0(package, force), timeout=TIMEOUT),
        TimeoutException=function(ex) "TimedOut", error=function(e)e)
}

getCoverage0 <- function(package, force=FALSE)
{
    if(!file.exists(file.path(package, "tests")))
        return(NULL)
    if((!force) && (!needs_update(package)))
    {
        print(sprintf("Skipping %s, it hasn't changed since last time.",
            package))
        return("skipped")
    }
    print(sprintf("Processing %s...", package))
    flog.info(sprintf("Processing %s...", package))
    ret <- tryCatch({cov <- package_coverage(package)}, error=function(e) e)
    save(ret, file=sprintf("/tmp/intermediate-coverage/%s.rda", package))
    if ("coverage" %in% class(ret))
    {
        rcpt <- upload_coverage(ret, svninfo)
        msg <- sprintf("Uploaded coverage for %s, status was %s.",
            package, rcpt$meta$status)
        print(msg)
        flog.info(msg)
        cat(svninfo[[package]], file=file.path(svncachedir, package))
    }
    ret
}



packages <- getPkgListFromManifest()

svncachedir <- "../svn-coverage-cache"
if (!file.exists(svncachedir))
    dir.create(svncachedir)


needs_update <- function(pkg)
{
    cachefile <- file.path(svncachedir, pkg)
    if(!file.exists(cachefile))
        return(TRUE)
    l <- readLines(cachefile, warn=FALSE)
    as.integer(svninfo[[pkg]]) > as.integer(l)
}


names(packages) <- packages


param <- MulticoreParam(5, timeout=900)#, log=TRUE)

# res <- bplapply(packages, getCoverage, BPPARAM=param)
res <- lapply(packages, getCoverage)
save(res, file="/tmp/res.rda")
