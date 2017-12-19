## NOTE: The appropriate config file should be sourced prior
## to running this, so that environment variables are set correctly.
## ALSO, be sure X11 (Xvfb) is running.

suppressMessages({

    if(!require("BiocInstaller", quietly=TRUE))
        stop("BiocInstaller not installed!")

    reqs <- c("covr", "futile.logger", "R.utils")
    for(x in reqs) {
        if(!do.call(require, list(package=x, quietly=TRUE))) {
            biocLite(x)
            do.call(require, list(package=x, quietly=TRUE))
        }
    }

})

TIMEOUT <- 2400 # 40 minutes

# Run in the meat directory
setwd(Sys.getenv("BBS_MEAT_PATH"))

bbs_workdir <- Sys.getenv("BBS_WORK_TOPDIR")

.stopifnot <- function(msg, expr) {
    if (!expr) {
        flog.info(msg)
        stopifnot(expr)
    }
}

getPkgListFromManifest <- function(manifestFile) {
    lines <- readLines(manifestFile)
    pattern <- "^Package:[[:blank:]]*([^[:blank:]]+).*"
    lines <- grep(pattern, lines, value = TRUE)
    sub(pattern, "\\1", lines)
}

manifestFilePath <- function() {
    file.path(Sys.getenv("BBS_BIOC_MANIFEST_CLONE_PATH"),
              Sys.getenv("BBS_BIOC_MANIFEST_FILE"))
}

packages <- getPkgListFromManifest(manifestFilePath())

get_git_commit <- function(pkg) {
  file <- file.path(bbs_workdir, "gitlog", paste0("git-log-", pkg, ".txt"))
  if (file.exists(file)) {
      dcf <- read.dcf(file)
      ret <- dcf[,"Last Commit"]
      names(ret) <- pkg
      ret
  }
}

gitlog <- unlist(Filter(Negate(is.null), lapply(packages, get_git_commit)))

getCoverage <- function(package, force=FALSE) {
    if(!file.exists(file.path(package, "tests"))) {
        flog.info("Skipping %s, it contains no tests", package)
        return(NA_integer_)
    }
    if((!force) && (!needs_update(package)) && (!is.na(coverage[package,]))) {
	cov <- as.integer(coverage[package,])
        flog.info("Skipping %s, it hasn't changed since last run", package)
    }
    else {
        flog.info("Processing %s...", package)
        cov <- tryCatch(withTimeout(as.integer(percent_coverage(package_coverage(package))), timeout=TIMEOUT),
            TimeoutException = function(ex) stop("timed out"),
            error = function(e) {
                flog.error("%s failed: %s", package, e$message);
                NA_integer_
            })
        if(is.integer(cov)) cat(gitlog[[package]], file=file.path(gitcachedir, package))
    }
    cov
}

gitcachedir <- file.path(bbs_workdir, "git-coverage-cache")
if (!file.exists(gitcachedir))
    dir.create(gitcachedir)

cov_file <- Sys.getenv("COVERAGE_FILE")

if (file.exists(cov_file)) {
    coverage <- data.frame(read.dcf(cov_file, all=TRUE), row.names="Package")
} else {
    coverage <- data.frame(Coverage = character(0L), stringsAsFactors=FALSE)
}

needs_update <- function(pkg) {
    cachefile <- file.path(gitcachedir, pkg)
    if(!file.exists(cachefile))
        return(TRUE)
    gitlog[[pkg]] != readLines(cachefile, warn=FALSE)
}

coverage <- data.frame(Package = packages, Coverage = sapply(packages, getCoverage))

write.dcf(coverage, cov_file)
