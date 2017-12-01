## NOTE: The appropriate config file should be sourced prior
## to running this, so that environment variables are set correctly.
## ALSO, be sure X11 (Xvfb) is running.

if(!require("BiocInstaller", quietly=TRUE))
    stop("BiocInstaller not installed!")

reqs <- c("covr", "futile.logger", "R.utils")
lapply(reqs, function(x) {
    if(!do.call(require, list(package=x, quietly=TRUE))) {
        biocLite(x)
        do.call(require, list(package=x, quietly=TRUE))
    }
})

TIMEOUT <- 2400 # 40 minutes

# Assume that we are running in the meat directory

.stopifnot <- function(msg, expr) {
    if (!expr) {
        flog.info(msg)
        print(msg)
        stopifnot(expr)
    }
}

getPkgListFromManifest <- function() {
    manifestFile <- normalizePath(file.path("..", "manifest", "software.txt"))
    lines <- readLines(manifestFile)
    pattern <- "^Package:[[:blank:]]*([^[:blank:]]+).*"
    lines <- grep(pattern, lines, value = TRUE)
    sub(pattern, "\\1", lines)
}

packages <- getPkgListFromManifest()

get_git_commit <- function(pkg) {
  file <- normalizePath(paste0("../gitlog/git-log-", pkg, ".txt"))
  if (file.exists(file)) {
      dcf <- read.dcf(file)
      ret <- dcf[,"Last Commit"]
      names(ret) <- pkg
      ret
  }
}

gitlog <- unlist(Filter(Negate(is.null), lapply(packages, get_git_commit)))

getCoverage <- function(package, force=FALSE) {
    tryCatch(evalWithTimeout(getCoverage0(package, force), timeout=TIMEOUT),
        TimeoutException=function(ex) "TimedOut", error=function(e)e)
}

getCoverage0 <- function(package, force=FALSE) {
    if(!file.exists(file.path(package, "tests")))
        return(NULL)
    if((!force) && (!needs_update(package)) && (!is.null(coverage[package]))) {
        print(sprintf("Skipping %s, it hasn't changed since last time.", package))
        return("skipped")
    }
    print(sprintf("Processing %s...", package))
    flog.info(sprintf("Processing %s...", package))
    ret <- tryCatch({cov <- percent_coverage(package_coverage(package))}, error = function(e) e)
    cat(gitlog[[package]], file=file.path(gitcachedir, package))
    ret
}

gitcachedir <- file.path("..", "git-coverage-cache")
if (!file.exists(gitcachedir))
    dir.create(gitcachedir)

cov_file <- "coverage.txt"
coverage <- if (file.exists(cov_file)) read.dcf(cov_file) else NULL

needs_update <- function(pkg) {
    cachefile <- file.path(gitcachedir, pkg)
    if(!file.exists(cachefile))
        return(TRUE)
    gitlog[[pkg]] != readLines(cachefile, warn=FALSE)
}

coverage <- sapply(packages, getCoverage)

write.dcf(coverage, cov_file)
