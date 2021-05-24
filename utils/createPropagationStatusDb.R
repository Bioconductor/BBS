### =========================================================================
### Used during stage6b to compute package propagation status
### -------------------------------------------------------------------------


.BASE_PACKAGES <- NULL

.get_base_packages <- function()
{
    if (is.null(.BASE_PACKAGES)) {
        installed_pkgs <- installed.packages()
        Priority <- installed_pkgs[ , "Priority"]
        base_packages <- installed_pkgs[Priority %in% "base", "Package"]
        .BASE_PACKAGES <<- unname(base_packages)
    }
    .BASE_PACKAGES
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### compute_propagation_statuses()
###
### The workhorse behind createPropagationStatusDb().
###

.stop_if_bad_OUTGOING_pkgs <- function(OUTGOING_pkgs)
{
    OUTGOING_fields <- c("Package", "Version",
                         "Depends", "Imports", "LinkingTo")
    stopifnot(is.matrix(OUTGOING_pkgs),
              identical(colnames(OUTGOING_pkgs), OUTGOING_fields))
}

.stop_if_bad_available_pkgs <- function(available_pkgs)
{
    stopifnot(is.matrix(available_pkgs),
              identical(colnames(available_pkgs), c("Package", "Version")))
}

.init_statuses <- function(pkgnames)
{
    data.frame(Package=pkgnames,
               propagate=logical(length(pkgnames)),
               explain=rep.int(NA_character_, length(pkgnames)))
}

.stop_if_bad_statuses <- function(statuses)
{
    stopifnot(is.data.frame(statuses),
              identical(colnames(statuses),
                        c("Package", "propagate", "explain")))
}

.extract_deps <- function(pkgs)
{
    Depends <- pkgs[ , "Depends"]
    Depends[is.na(Depends)] <- ""
    Imports <- pkgs[ , "Imports"]
    Imports[is.na(Imports)] <- ""
    LinkingTo <- pkgs[ , "LinkingTo"]
    LinkingTo[is.na(LinkingTo)] <- ""

    sep1 <- sep2 <- character(nrow(pkgs))
    sep1[nzchar(Depends) & nzchar(Imports)] <- ","
    sep2[(nzchar(Depends) | nzchar(Imports)) & nzchar(LinkingTo)] <- ","
    deps <- paste0(Depends, sep1, Imports, sep2, LinkingTo)

    deps <- gsub("\n", "", deps, fixed=TRUE)
    setNames(strsplit(deps, " *, *"), pkgs[ , "Package"])
}

.extract_required_pkgs <- function(deps)
{
    pattern <- " *([^ ]+).*"
    sub(pattern, "\\1", deps)
}

.extract_required_versions <- function(deps)
{
    required_versions <- rep.int(NA_character_, length(deps))
    pattern <- ".*\\((.*)\\).*"
    idx <- grep(pattern, deps)
    required_versions[idx] <- sub(pattern, "\\1", deps[idx])
    required_versions
}

### Return TRUE or a single string describing the impossible dep.
.check_required_version <- function(required_pkg, required_version,
                                    available_version)
{
    if (is.na(required_version))
        return(TRUE)
    pattern <- "^ *([>=]+) *([0-9.-]+) *$"
    if (!grepl(pattern, required_version))
        return(TRUE)
    op <- sub(pattern, "\\1", required_version)
    version <- numeric_version(sub(pattern, "\\2", required_version))
    available_version <- numeric_version(available_version)
    fmt <- paste0("NO, package requires version %s %s of '%s' ",
                  "but only version %s is available")
    if (op == ">=") {
        if (available_version >= version)
            return(TRUE)
        ans <- sprintf(fmt, op, version, required_pkg, available_version)
        return(ans)
    }
    if (op == ">") {
        if (available_version > version)
            return(TRUE)
        ans <- sprintf(fmt, op, version, required_pkg, available_version)
        return(ans)
    }
    TRUE
}

### Return TRUE or a single string describing the impossible dep.
.check_deps <- function(pkg, required_pkgs, required_versions,
                        available_pkgs)
{
    stopifnot(length(required_pkgs) == length(required_versions))
    ignored_deps <- c("R", .get_base_packages())
    for (j in seq_along(required_pkgs)) {
        required_pkg <- required_pkgs[[j]]
        if (required_pkg %in% ignored_deps)
            next
        m <- match(required_pkg, available_pkgs[ , "Package"])
        if (is.na(m)) {
            ans <- sprintf("NO, package depends on '%s' which is not available",
                           required_pkg)
            return(ans)
        }
        required_version <- required_versions[[j]]
        available_version <- available_pkgs[m, "Version"]
        res <- .check_required_version(required_pkg, required_version,
                                       available_version)
        if (!isTRUE(res))
            return(res)
    }
    TRUE
}

.update_candidate_statuses <- function(candidate_statuses,
                                       candidate_required_pkgs,
                                       candidate_required_versions,
                                       available_pkgs)
{
    .stop_if_bad_statuses(candidate_statuses)
    stopifnot(is.list(candidate_required_pkgs),
              identical(names(candidate_required_pkgs),
                        candidate_statuses[ , "Package"]),
              is.list(candidate_required_versions),
              identical(lengths(candidate_required_pkgs),
                        lengths(candidate_required_versions)))
    .stop_if_bad_available_pkgs(available_pkgs)

    unapproved_idx <- which(!candidate_statuses$propagate)
    for (i in unapproved_idx) {
        pkg <- candidate_statuses[i, "Package"]
        required_pkgs <- candidate_required_pkgs[[i]]
        required_versions <- candidate_required_versions[[i]]
        res <- .check_deps(pkg, required_pkgs, required_versions,
                           available_pkgs)
        if (isTRUE(res)) {
            candidate_statuses$propagate[i] <- TRUE
            candidate_statuses$explain[i] <- "YES"
        } else {
            candidate_statuses$explain[i] <- res
        }
    }
    candidate_statuses
}

### Return a data.frame with 3 cols: Package, propagate, explain.
.compute_candidate_statuses <- function(candidate_pkgs, available_pkgs)
{
    .stop_if_bad_OUTGOING_pkgs(candidate_pkgs)
    .stop_if_bad_available_pkgs(available_pkgs)

    candidate_statuses <- .init_statuses(candidate_pkgs[ , "Package"])
    candidate_deps <- .extract_deps(candidate_pkgs)
    candidate_required_pkgs <- lapply(candidate_deps, .extract_required_pkgs)
    candidate_required_versions <- lapply(candidate_deps,
                                          .extract_required_versions)
    pass <- 1L
    while (TRUE) {
        message("  - pass #", pass, " ... ", appendLF=FALSE)
        updated_statuses <- .update_candidate_statuses(candidate_statuses,
                                    candidate_required_pkgs,
                                    candidate_required_versions,
                                    available_pkgs)
        total_approved <- sum(updated_statuses$propagate)
        message("OK ==> total approved candidates = ", total_approved)
        if (identical(updated_statuses$propagate, candidate_statuses$propagate))
            break
        candidate_statuses <- updated_statuses
        ## We simulate propagation by adding approved candidates
        ## to 'available_pkgs'. This might allow other candidates to
        ## propagate at the next iteration.
        approved_pkgs <- candidate_pkgs[candidate_statuses$propagate,
                                        c("Package", "Version"), drop=FALSE]
        add_idx <- which(!(approved_pkgs[ , "Package"] %in%
                           available_pkgs[ , "Package"]))
        available_pkgs <- rbind(available_pkgs,
                                approved_pkgs[add_idx, , drop=FALSE])
        pass <- pass + 1L
    }
    updated_statuses
}

### Return a data.frame with 3 cols: Package, propagate, explain.
compute_propagation_statuses <- function(OUTGOING_pkgs, available_pkgs)
{
    .stop_if_bad_OUTGOING_pkgs(OUTGOING_pkgs)
    .stop_if_bad_available_pkgs(available_pkgs)

    outgoing2available <- match(OUTGOING_pkgs[ , "Package"],
                                available_pkgs[ , "Package"])
    OUTGOING_version <- OUTGOING_pkgs[ , "Version"]
    OUTGOING_version <- numeric_version(OUTGOING_version)
    published_version <- available_pkgs[outgoing2available, "Version"]
    published_version <- numeric_version(published_version, strict=FALSE)

    statuses <- .init_statuses(OUTGOING_pkgs[ , "Package"])

    ## Handle "OUTGOING version < published version" case.
    lower_version_idx <- which(!is.na(outgoing2available) &
                               OUTGOING_version < published_version)
    fmt <- paste0("NO, version to propagate (%s) is ",
                  "lower than published version (%s)")
    statuses$explain[lower_version_idx] <-
        sprintf(fmt, OUTGOING_version[lower_version_idx],
                     published_version[lower_version_idx])

    ## Handle "OUTGOING version > published version" case.
    ## In this case, propagate only if the propagated package will not have
    ## impossible dependencies.
    candidate_idx <- which(is.na(outgoing2available) |
                           OUTGOING_version > published_version)
    message("  - nb of candidates = ", length(candidate_idx),
            " (based on version > published version)")
    if (length(candidate_idx) != 0L) {
        candidate_pkgs <- OUTGOING_pkgs[candidate_idx, , drop=FALSE]
        candidate_statuses <- .compute_candidate_statuses(candidate_pkgs,
                                                          available_pkgs)
        statuses[candidate_idx, ] <- candidate_statuses
    }
    statuses
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### createPropagationStatusDb()
###

.write_PACKAGES_to_OUTGOING_subdir <- function(OUTGOING_subdir, type)
{
    PACKAGES_path <- file.path(OUTGOING_subdir, "PACKAGES")
    if (file.exists(PACKAGES_path)) {
        message("- File ", PACKAGES_path, " exists!")
        message("    ==> skip write_PACKAGES()")
        return(invisible(NULL))
    }
    message("- write_PACKAGES() to ", OUTGOING_subdir, "/ ... ", appendLF=FALSE)
    tools::write_PACKAGES(OUTGOING_subdir, type=type)
    message("OK")
}

.load_OUTGOING_pkgs <- function(OUTGOING_subdir, type)
{
    PACKAGES_path <- file.path(OUTGOING_subdir, "PACKAGES")
    fields <- c("Package", "Version", "Depends", "Imports", "LinkingTo")
    read.dcf(PACKAGES_path, fields=fields)
}

.fetch_available_pkgs <- function(staging_repo, type)
{
    if (!requireNamespace("BiocManager", quietly=TRUE))
        install.packages("BiocManager", repos="https://cran.rstudio.com")
    ## We can't just use BiocManager::repositories() here because of the
    ## following issue:
    ##   https://github.com/Bioconductor/BiocManager/issues/46#issuecomment-548017624
    bioc_version <- BiocManager::version()
    bioc_repos <- BiocManager:::.repositories(character(), version=bioc_version)
    all_repos <- c(staging_repo, bioc_repos)
    contrib_urls <- contrib.url(all_repos, type=type)
    available_pkgs <- available.packages(contrib_urls)
    available_pkgs[ , c("Package", "Version")]
}

.write_statuses_to_db <- function(statuses, type, out)
{
    .stop_if_bad_statuses(statuses)
    if (nrow(statuses) == 0L)
        return(invisible(NULL))
    lines <- sprintf("%s#%s#propagate: %s", statuses$Package, type,
                                            statuses$explain)
    cat(lines, file=out, sep="\n")
}

createPropagationStatusDb <- function(OUTGOING_dir, staging_repo, db_filepath)
{
    if (!file.exists(OUTGOING_dir)) {
        message("Directory ", OUTGOING_dir, "/ not found!")
        message("  ==> skip creation of ", db_filepath)
        return(invisible(NULL))
    }
    message("START creating ", db_filepath, " ...")
    out <- file(db_filepath, "w")
    on.exit(close(out))
    OUTGOING_types <- c("source", "win.binary", "mac.binary")
    for (type in OUTGOING_types) {
        OUTGOING_subdir <- file.path(OUTGOING_dir, type)
        if (!file.exists(OUTGOING_subdir))
            next
        .write_PACKAGES_to_OUTGOING_subdir(OUTGOING_subdir, type)
        OUTGOING_pkgs <- .load_OUTGOING_pkgs(OUTGOING_subdir, type)
        message("- Start computing propagation statuses for \"",
                type, "\" packages:")
        available_pkgs <- .fetch_available_pkgs(staging_repo, type)
        statuses <- compute_propagation_statuses(OUTGOING_pkgs, available_pkgs)
        message("- Done computing propagation statuses for \"",
                type, "\" packages.")
        message("- Write computed statuses to ", db_filepath, " ... ",
                appendLF=FALSE)
        .write_statuses_to_db(statuses, type, out)
        message("OK")
    }
    message("DONE creating ", db_filepath, ".")
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### TESTING
###

if (FALSE) {
  #OUTGOING_dir <- "~/public_html/BBS/3.13/bioc/OUTGOING"
  #staging_repo <- "file://home/biocpush/PACKAGES/3.13/bioc"
  OUTGOING_dir <- "~/public_html/BBS/3.13/workflows/OUTGOING"
  staging_repo <- "file://home/biocpush/PACKAGES/3.13/workflows"
  db_filepath <- "PROPAGATION_STATUS_DB.txt"
  createPropagationStatusDb(OUTGOING_dir, staging_repo, db_filepath)
}

