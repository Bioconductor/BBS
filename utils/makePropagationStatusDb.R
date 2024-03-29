### =========================================================================
### Used by stage6c to compute package propagation status
### -------------------------------------------------------------------------


### Same as in build_pkg_dep_graph.R and installNonTargetPkg.R
.get_non_target_repos <- function()
{
    non_target_repos <- readLines(Sys.getenv('BBS_NON_TARGET_REPOS_FILE'))
    gsub("BBS_BIOC_VERSION", Sys.getenv('BBS_BIOC_VERSION'),
         non_target_repos, fixed=TRUE)
}

.prettymsg <- function(...)
{
    if (nzchar(Sys.getenv("BBS_HOME"))) {
        indent <- "  Rscript> "
    } else {
        indent <- ""
    }
    message(indent, ..., appendLF=FALSE)
}

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
### The workhorse behind makePropagationStatusDb().
###

.stop_if_bad_OUTGOING_pkgs <- function(OUTGOING_pkgs)
{
    stopifnot(is.matrix(OUTGOING_pkgs))
    expected <- c("Package", "Version", "Depends", "Imports", "LinkingTo")
    current <- head(colnames(OUTGOING_pkgs), n=length(expected))
    stopifnot(identical(current, expected))
}

.stop_if_bad_available_pkgs <- function(available_pkgs)
{
    stopifnot(is.matrix(available_pkgs))
    expected <- c("Package", "Version")
    current <- head(colnames(available_pkgs), n=length(expected))
    stopifnot(identical(current, expected))
}

.update_available_pkgs <- function(available_pkgs, new_pkgs)
{
    replace_idx <- which(available_pkgs[ , "Package"] %in%
                         new_pkgs[ , "Package"])
    if (length(replace_idx) != 0L)
        available_pkgs <- available_pkgs[-replace_idx, , drop=FALSE]
    rbind(available_pkgs, new_pkgs[ , colnames(available_pkgs)])
}

### Simulate propagation by adding approved candidates to 'available_pkgs'.
.update_available_pkgs_with_approved_pkgs <-
        function(available_pkgs, candidate_pkgs, candidate_statuses)
{
    approved_pkgs <- candidate_pkgs[candidate_statuses$propagate, , drop=FALSE]
    .update_available_pkgs(available_pkgs, approved_pkgs)
}

### Return a data.frame with 3 cols: Package, propagate, explain.
### The "propagate" and "explain" cols are initialized with FALSE's
### and NA_character_'s, respectively.
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
    clean_field <- function(x) {
        x[is.na(x)] <- ""
        x <- gsub("[ \n\t]", "", x)
        x <- sub(",*$", "", x)  # remove trailing commas
        x
    }
    Depends <- clean_field(pkgs[ , "Depends"])
    Imports <- clean_field(pkgs[ , "Imports"])
    LinkingTo <- clean_field(pkgs[ , "LinkingTo"])

    sep1 <- sep2 <- character(nrow(pkgs))
    sep1[nzchar(Depends) & nzchar(Imports)] <- ","
    sep2[(nzchar(Depends) | nzchar(Imports)) & nzchar(LinkingTo)] <- ","
    deps <- paste0(Depends, sep1, Imports, sep2, LinkingTo)

    setNames(strsplit(deps, ",", fixed=TRUE), pkgs[ , "Package"])
}

.extract_required_pkgs <- function(deps)
{
    pattern <- "([[:alpha:]][A-Za-z0-9.]*).*"
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

.explain_insufficient_available_version <-
    function(required_pkg, version, op, available_version, candidate_statuses)
{
    m <- match(required_pkg, candidate_statuses$Package)
    required_pkg_is_approved <- !is.na(m) && candidate_statuses$propagate[m]
    if (required_pkg_is_approved) {
        is_or_will_become <- "will become"
    } else {
        is_or_will_become <- "is"
    }
    fmt <- paste0("NO, package requires version %s %s of '%s' ",
                  "but only version %s %s available")
    sprintf(fmt, op, version, required_pkg, available_version,
                 is_or_will_become)
}

### Return TRUE or a single string explaining the impossible dep.
.check_required_version <- function(required_pkg, required_version,
                                    available_version, candidate_statuses)
{
    if (is.na(required_version))
        return(TRUE)
    pattern <- "^([>=]+)([0-9.-]+)$"
    if (!grepl(pattern, required_version))
        return(TRUE)
    op <- sub(pattern, "\\1", required_version)
    version <- numeric_version(sub(pattern, "\\2", required_version))
    available_version <- numeric_version(available_version)
    if (op == ">=") {
        if (available_version >= version)
            return(TRUE)
    } else if (op == ">") {
        if (available_version > version)
            return(TRUE)
    } else {
        return(TRUE)
    }
    .explain_insufficient_available_version(required_pkg, version, op,
                                            available_version,
                                            candidate_statuses)
}

### Return TRUE or a single string explaining the impossible dep.
.check_candidate_deps <- function(pkg, required_pkgs, required_versions,
                                  available_pkgs, candidate_statuses,
                                  available_srcpkgs=NULL)
{
    stopifnot(length(required_pkgs) == length(required_versions))
    if (!is.null(available_srcpkgs)) {
        needs_compil <- tolower(available_srcpkgs[ , "NeedsCompilation"])
        available_nocompil_srcpkgs <-
            available_srcpkgs[needs_compil %in% "no", , drop=FALSE]
    }
    ignored_deps <- c("R", .get_base_packages())
    for (j in seq_along(required_pkgs)) {
        required_pkg <- required_pkgs[[j]]
        if (required_pkg %in% ignored_deps)
            next
        m <- match(required_pkg, available_pkgs[ , "Package"])
        if (!is.na(m)) {
            available_version <- available_pkgs[m, "Version"]
        } else {
            fmt <- "NO, package depends on '%s' which is "
            if (is.null(available_srcpkgs)) {
                fmt <- c(fmt, "not available")
                return(sprintf(paste(fmt, collapse=""), required_pkg))
            }
            m <- match(required_pkg, available_nocompil_srcpkgs[ , "Package"])
            if (is.na(m)) {
                m <- match(required_pkg, available_srcpkgs[ , "Package"])
                if (is.na(m)) {
                    fmt <- c(fmt, "not available")
                } else {
                    fmt <- c(fmt, "only available as a source ",
                                  "package that needs compilation")
                }
                return(sprintf(paste(fmt, collapse=""), required_pkg))
            }
            available_version <- available_nocompil_srcpkgs[m, "Version"]
        }
        required_version <- required_versions[[j]]
        res <- .check_required_version(required_pkg, required_version,
                                       available_version, candidate_statuses)
        if (!isTRUE(res))
            return(res)
    }
    TRUE
}

.update_candidate_statuses <- function(candidate_statuses,
                                       candidate_required_pkgs,
                                       candidate_required_versions,
                                       available_pkgs,
                                       available_srcpkgs=NULL)
{
    .stop_if_bad_statuses(candidate_statuses)
    stopifnot(is.list(candidate_required_pkgs),
              identical(names(candidate_required_pkgs),
                        candidate_statuses$Package),
              is.list(candidate_required_versions),
              identical(lengths(candidate_required_pkgs),
                        lengths(candidate_required_versions)))
    .stop_if_bad_available_pkgs(available_pkgs)

    unapproved_idx <- which(!candidate_statuses$propagate)
    for (i in unapproved_idx) {
        pkg <- candidate_statuses[i, "Package"]
        required_pkgs <- candidate_required_pkgs[[i]]
        required_versions <- candidate_required_versions[[i]]
        res <- .check_candidate_deps(pkg, required_pkgs, required_versions,
                                     available_pkgs, candidate_statuses,
                                     available_srcpkgs=available_srcpkgs)
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
### The "explain" col should contain "YES" or "NO, some explanation" strings
### for **all** packages, so no NA_character_'s.
.compute_candidate_statuses <- function(candidate_pkgs, available_pkgs,
                                        available_srcpkgs=NULL)
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
        .prettymsg("  - pass #", pass, " ... ")
        updated_statuses <-
            .update_candidate_statuses(candidate_statuses,
                                       candidate_required_pkgs,
                                       candidate_required_versions,
                                       available_pkgs,
                                       available_srcpkgs=available_srcpkgs)
        total_approved <- sum(updated_statuses$propagate)
        message("OK ==> total approved candidates = ", total_approved)
        if (identical(updated_statuses$propagate, candidate_statuses$propagate))
            break
        candidate_statuses <- updated_statuses
        ## We simulate propagation by adding approved candidates
        ## to 'available_pkgs'. This might allow other candidates to
        ## propagate at the next iteration.
        available_pkgs <- .update_available_pkgs_with_approved_pkgs(
                                        available_pkgs,
                                        candidate_pkgs, candidate_statuses)
        pass <- pass + 1L
    }
    updated_statuses
}

### Return a data.frame with 3 cols: Package, propagate, explain.
compute_propagation_statuses <- function(OUTGOING_pkgs, available_pkgs,
                                         available_srcpkgs=NULL)
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
    ## In this case, propagate only if the propagated package will not
    ## have impossible dependencies.
    candidate_idx <- which(is.na(outgoing2available) |
                           OUTGOING_version > published_version)
    .prettymsg("  - nb of candidates = ", length(candidate_idx),
               " (based on version > published version)\n")
    if (length(candidate_idx) != 0L) {
        candidate_pkgs <- OUTGOING_pkgs[candidate_idx, , drop=FALSE]
        candidate_statuses <- .compute_candidate_statuses(candidate_pkgs,
                                       available_pkgs,
                                       available_srcpkgs=available_srcpkgs)
        stopifnot(!any(is.na(candidate_statuses$explain)))
        statuses[candidate_idx, ] <- candidate_statuses
    }
    statuses
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### makePropagationStatusDb()
###

.write_PACKAGES_to_OUTGOING_subdir <- function(OUTGOING_subdir, type)
{
    PACKAGES_path <- file.path(OUTGOING_subdir, "PACKAGES")
    if (file.exists(PACKAGES_path)) {
        .prettymsg("- File ", PACKAGES_path, " exists!\n")
        .prettymsg("    ==> skip write_PACKAGES()\n")
        return(invisible(NULL))
    }
    .prettymsg("- write_PACKAGES() to ", OUTGOING_subdir, "/ ... ")
    type <- gsub(".big-sur-(arm64|x86_64)", "", type, fixed=FALSE)
    tools::write_PACKAGES(OUTGOING_subdir, type=type)
    message("OK")
}

.load_OUTGOING_pkgs <- function(OUTGOING_subdir, type)
{
    PACKAGES_path <- file.path(OUTGOING_subdir, "PACKAGES")
    OUTGOING_fields <- c("Package", "Version",
                         "Depends", "Imports", "LinkingTo")
    if (type == "source")
        OUTGOING_fields <- c(OUTGOING_fields, "NeedsCompilation")
    read.dcf(PACKAGES_path, fields=OUTGOING_fields)
}

.fetch_available_pkgs <- function(final_repo, type, non_target_repos)
{
    all_contrib_urls <- contrib.url(final_repo, type=type)
    ## We always look at availability of source packages in the non-target
    ## repos, even when computing the propagation status of Windows or
    ## Mac binaries. This is a feature!
    if (length(non_target_repos) != 0L) {
        contrib_urls <- contrib.url(non_target_repos, type="source")
        all_contrib_urls <- c(all_contrib_urls, contrib_urls)
    }
    if (type == "source") {
        available_pkgs <- available.packages(all_contrib_urls,
                                             fields="NeedsCompilation")
        available_pkgs[ , c("Package", "Version", "NeedsCompilation")]
    } else {
        available_pkgs <- available.packages(all_contrib_urls)
        available_pkgs[ , c("Package", "Version")]
    }
}

.write_statuses_to_db <- function(statuses, type, out)
{
    .stop_if_bad_statuses(statuses)
    if (nrow(statuses) == 0L)
        return(invisible(NULL))
    explain <- statuses$explain
    explain[is.na(explain)] <- "UNNEEDED, same version is already published"
    lines <- sprintf("%s#%s#propagate: %s", statuses$Package, type, explain)
    cat(lines, file=out, sep="\n")
}

makePropagationStatusDb <- function(OUTGOING_dir, final_repo,
                                    non_target_repos=.get_non_target_repos(),
                                    db_filepath="PROPAGATION_STATUS_DB.txt")
{
    if (!file.exists(OUTGOING_dir))
        stop("directory ", OUTGOING_dir, "/ not found")
    .prettymsg("START creating ", db_filepath, " ...\n")
    out <- file(db_filepath, "w")
    on.exit(close(out))
    final_repo <- gsub("-mac-arm64", "", final_repo, fixed=TRUE)
    ## Type "source" must be first.
    OUTGOING_types <- c("source", "win.binary",
                        "mac.binary.big-sur-arm64",
                        "mac.binary.big-sur-x86_64")
    available_srcpkgs <- NULL
    for (type in OUTGOING_types) {
        OUTGOING_subdir <- file.path(OUTGOING_dir, type)
        if (!file.exists(OUTGOING_subdir))
            next
        .write_PACKAGES_to_OUTGOING_subdir(OUTGOING_subdir, type)
        OUTGOING_pkgs <- .load_OUTGOING_pkgs(OUTGOING_subdir, type)
        .prettymsg("- Start computing propagation statuses for \"",
                   type, "\" packages:\n")
        available_pkgs <- .fetch_available_pkgs(final_repo, type,
                                                non_target_repos)
        if (type == "source") {
            statuses <- compute_propagation_statuses(OUTGOING_pkgs,
                                            available_pkgs)
        } else {
            if (is.null(available_srcpkgs))
                available_srcpkgs <- .fetch_available_pkgs(final_repo, "source",
                                                           non_target_repos)
            statuses <- compute_propagation_statuses(OUTGOING_pkgs,
                                            available_pkgs,
                                            available_srcpkgs=available_srcpkgs)
        }
        .prettymsg("- Done computing propagation statuses for \"",
                   type, "\" packages.\n")
        .prettymsg("- Write computed statuses to ", db_filepath, " ... ")
        .write_statuses_to_db(statuses, type, out)
        message("OK")
        if (type == "source") {
            available_srcpkgs <- .update_available_pkgs_with_approved_pkgs(
                                               available_pkgs,
                                               OUTGOING_pkgs, statuses)
        }
    }
    .prettymsg("DONE creating ", db_filepath, ".\n")
}


### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### TESTING
###

if (FALSE) {
  #OUTGOING_dir <- "~/public_html/BBS/3.13/bioc/OUTGOING"
  #final_repo <- "file://home/biocpush/PACKAGES/3.13/bioc"
  #OUTGOING_dir <- "~/public_html/BBS/3.13/workflows/OUTGOING"
  #final_repo <- "file://home/biocpush/PACKAGES/3.13/workflows"
  #makePropagationStatusDb(OUTGOING_dir, final_repo)

  OUTGOING_source_pkgs <- data.frame(
      Package=letters[1:6],
      Version=c(1:3, 1, 1, 1),
      Depends=c(NA, NA, "b, i", "c", "z", "b (>= 3)"),
      NeedsCompilation=c(NA, "no", "no", "yes", NA, NA))

  OUTGOING_pkgs <- list(
      source                      = OUTGOING_source_pkgs,
      win.binary                  = OUTGOING_source_pkgs,
      `mac.binary.big-sur-arm64`  = OUTGOING_source_pkgs,
      `mac.binary.big-sur-x86_64` = OUTGOING_source_pkgs
  )

  final_repo_pkgs <- list(
      source                      = data.frame(Package=letters[7:9],
                                               Version=1:3),
      win.binary                  = data.frame(Package=letters[7:8],
                                               Version=1:2),
      `mac.binary.big-sur-arm64`  = data.frame(Package=c(letters[7:8], "b"),
                                               Version=c(1:2, 2)),
      `mac.binary.big-sur-x86_64` = data.frame(Package=c(letters[7:8], "b"),
                                               Version=c(1:2, 3))
  )

  create_OUTGOING_dir <- function(OUTGOING_dir, OUTGOING_pkgs)
  {
      unlink(OUTGOING_dir, recursive=TRUE)
      dir.create(OUTGOING_dir)
      types <- c("source", "win.binary",
                           "mac.binary.big-sur-arm64",
                           "mac.binary.big-sur-x86_64")
      for (type in types) {
          OUTGOING_subdir <- file.path(OUTGOING_dir, type)
          dir.create(OUTGOING_subdir)
          pkgs <- OUTGOING_pkgs[[type]]
          write.dcf(pkgs, file.path(OUTGOING_subdir, "PACKAGES"))
      }
  }

  create_final_repo <- function(final_repo_dir, final_repo_pkgs)
  {
      unlink(final_repo_dir, recursive=TRUE)
      dir.create(final_repo_dir)
      types <- c("source", "win.binary",
                           "mac.binary.big-sur-arm64",
                           "mac.binary.big-sur-x86_64")
      for (type in types) {
          repo_subdir <- contrib.url(final_repo_dir, type=type)
          dir.create(repo_subdir, recursive=TRUE)
          pkgs <- final_repo_pkgs[[type]]
          write.dcf(pkgs, file.path(repo_subdir, "PACKAGES"))
      }
  }

  test_makePropagationStatusDb <-
          function(OUTGOING_dir, final_repo_dir,
                   non_target_repos=NULL,
                   db_filepath="PROPAGATION_STATUS_DB.txt")
  {
      if (missing(OUTGOING_dir)) {
          OUTGOING_dir <- file.path(tempdir(), "OUTGOING")
          create_OUTGOING_dir(OUTGOING_dir, OUTGOING_pkgs)
      }
      if (missing(final_repo_dir)) {
          final_repo_dir <- file.path(tempdir(), "final_repo")
          create_final_repo(final_repo_dir, final_repo_pkgs)
      }
      final_repo <- paste0("file:/", final_repo_dir)
      makePropagationStatusDb(OUTGOING_dir, final_repo,
                              non_target_repos=non_target_repos,
                              db_filepath=db_filepath)
  }

  test_makePropagationStatusDb()
}

