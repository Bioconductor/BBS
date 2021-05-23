### =========================================================================
### Used during stage6b to compute package propagation status
### -------------------------------------------------------------------------


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### explain_propagation_status()
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

.extract_pkg_names <- function(deps)
{
    pattern <- " *([^ ]+).*"
    sub(pattern, "\\1", deps)
}

.extract_pkg_minversions <- function(deps)
{
    minversions <- character(length(deps))
    pattern <- ".*\\((.*)\\).*"
    idx <- grep(pattern, deps)
    minversions[idx] <- sub(pattern, "\\1", deps[idx])
    minversions
}

### Return TRUE or a single string describing the impossible dep.
.check_deps <- function(pkg, required_pkgs, required_minversions,
                        available_pkgs)
{
    stopifnot(length(required_pkgs) == length(required_minversions))
    TRUE
}

.update_candidate_status <- function(candidate_status,
                                     candidate_deps_pkgs,
                                     candidate_deps_minversions,
                                     available_pkgs)
{
    stopifnot(is.data.frame(candidate_status),
              identical(colnames(candidate_status),
                        c("Package", "approved", "explain")),
              is.list(candidate_deps_pkgs),
              identical(names(candidate_deps_pkgs),
                        candidate_status[ , "Package"]),
              is.list(candidate_deps_minversions),
              identical(lengths(candidate_deps_pkgs),
                        lengths(candidate_deps_minversions)))
    .stop_if_bad_available_pkgs(available_pkgs)

    NO_idx <- which(!candidate_status$approved)
    for (i in NO_idx) {
        pkg <- candidate_status[i, "Package"]
        required_pkgs <- candidate_deps_pkgs[[i]]
        required_minversions <- candidate_deps_minversions[[i]]
        res <- .check_deps(pkg, required_pkgs, required_minversions,
                           available_pkgs)
        if (isTRUE(res)) {
            candidate_status$approved[i] <- TRUE
            candidate_status$explain[i] <- "YES"
        } else {
            candidate_status$explain[i] <- res
        }
    }
    candidate_status
}

.compute_candidate_status <- function(candidate_pkgs, available_pkgs)
{
    .stop_if_bad_OUTGOING_pkgs(candidate_pkgs)
    .stop_if_bad_available_pkgs(available_pkgs)

    candidate_status <- data.frame(Package=candidate_pkgs[ , "Package"],
                                   approved=logical(nrow(candidate_pkgs)),
                                   explain=rep.int(NA_character_,
                                                   nrow(candidate_pkgs)))
    candidate_deps <- .extract_deps(candidate_pkgs)
    candidate_deps_pkgs <- lapply(candidate_deps,
                                  .extract_pkg_names)
    candidate_deps_minversions <- lapply(candidate_deps,
                                         .extract_pkg_minversions)
    while (TRUE) {
        new_candidate_status <- .update_candidate_status(candidate_status,
                                        candidate_deps_pkgs,
                                        candidate_deps_minversions,
                                        available_pkgs)
        if (identical(new_candidate_status$approved, candidate_status$approved))
            break
        candidate_status <- new_candidate_status
        ## We simulate propagation by adding approved candidates
        ## to 'available_pkgs'. This might allow other candidates to
        ## propagate at the next iteration.
        approved_pkgs <- candidate_pkgs[candidate_status$approved,
                                        c("Package", "Version"), drop=FALSE]
        add_idx <- which(!(approved_pkgs[ , "Package"] %in%
                           available_pkgs[ , "Package"]))
        available_pkgs <- rbind(available_pkgs,
                                approved_pkgs[add_idx, , drop=FALSE])
    }
    candidate_status
}

explain_propagation_status <- function(OUTGOING_pkgs, available_pkgs)
{
    .stop_if_bad_OUTGOING_pkgs(OUTGOING_pkgs)
    .stop_if_bad_available_pkgs(available_pkgs)

    outgoing2available <- match(OUTGOING_pkgs[ , "Package"],
                                available_pkgs[ , "Package"])
    OUTGOING_version <- OUTGOING_pkgs[ , "Version"]
    OUTGOING_version <- numeric_version(OUTGOING_version)
    published_version <- available_pkgs[outgoing2available, "Version"]
    published_version <- numeric_version(published_version, strict=FALSE)

    explain_status <- rep.int(NA_character_, nrow(OUTGOING_pkgs))
    names(explain_status) <- OUTGOING_pkgs[ , "Package"]

    ## Handle "OUTGOING version < published version" case.
    lower_version_idx <- which(!is.na(outgoing2available) &
                               OUTGOING_version < published_version)
    explain_status[lower_version_idx] <-
        sprintf("NO, version to propagate (%s) is lower than published version (%s)",
                OUTGOING_version[lower_version_idx],
                published_version[lower_version_idx])

    ## Handle "OUTGOING version > published version" case.
    ## In this case, propagate only if the propagated package will not have
    ## impossible dependencies.
    candidate_idx <- which(is.na(outgoing2available) |
                           OUTGOING_version > published_version)
    candidate_pkgs <- OUTGOING_pkgs[candidate_idx, , drop=FALSE]
    candidate_status <- .compute_candidate_status(candidate_pkgs,
                                                  available_pkgs)
    explain_status[candidate_idx] <- candidate_status$explain
    explain_status
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### createPropagationStatusDb()
###

.load_OUTGOING_pkgs <- function(OUTGOING_dirpath, OUTGOING_type)
{
    PACKAGES_path <- file.path(OUTGOING_dirpath, OUTGOING_type, "PACKAGES")
    fields <- c("Package", "Version", "Depends", "Imports", "LinkingTo")
    read.dcf(PACKAGES_path, fields=fields)
}

.fetch_available_pkgs <- function(staging_repo, bioc_repos, type)
{
    all_repos <- c(staging_repo, bioc_repos)
    contrib_urls <- contrib.url(all_repos, type=type)
    available_pkgs <- available.packages(contrib_urls)
    available_pkgs[ , c("Package", "Version")]
}

createPropagationStatusDb <- function(OUTGOING_dirpath, OUTGOING_type,
                                      staging_repo, bioc_repos, db_filepath)
{
    OUTGOING_pkgs <- .load_OUTGOING_pkgs(OUTGOING_dirpath, OUTGOING_type)
    available_pkgs <- .fetch_available_pkgs(staging_repo, bioc_repos,
                                            OUTGOING_type)
    explain_status <- explain_propagation_status(OUTGOING_pkgs, available_pkgs)
    explain_status
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### TESTING
###

if (FALSE) {
  #OUTGOING_dirpath <- "~/public_html/BBS/3.13/bioc/OUTGOING"
  #OUTGOING_type <- "win.binary"
  #staging_repo <- "file://home/biocpush/PACKAGES/3.13/bioc"

  OUTGOING_dirpath <- "~/public_html/BBS/3.13/workflows/OUTGOING"
  OUTGOING_type <- "source"
  staging_repo <- "file://home/biocpush/PACKAGES/3.13/workflows"

  library(BiocManager)
  ## We can't just use BiocManager::repositories() here because of the
  ## following issue:
  ##   https://github.com/Bioconductor/BiocManager/issues/46#issuecomment-548017624
  bioc_version <- BiocManager::version()
  bioc_repos <- BiocManager:::.repositories(character(), version=bioc_version)
  db_filepath <- "PROPAGATE_STATUS_DB.txt"

  createPropagationStatusDb(OUTGOING_dirpath, OUTGOING_type,
                            staging_repo, bioc_repos, db_filepath)
}

