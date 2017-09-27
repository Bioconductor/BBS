###
### Find "old" packages in a given directory. "old" means that the directory
### contains a package with same name and a greater version.
### Typical use:
###   > oldpkgs <- list.old.pkgs(suffix=".zip")
###   > file.remove(oldpkgs)
###
list.old.pkgs <- function(path=".", suffix=".tar.gz")
{
    ans <- character(0)
    pattern <- paste(gsub(".", "\\.", suffix, fixed=TRUE), "$", sep="")
    pkgs0 <- list.files(path, pattern=pattern)
    if (length(pkgs0) == 0L) {
        warning("no pkgs found in dir ", path)
        return(ans)
    }
    pkgs <- substr(pkgs0, 1L, nchar(pkgs0) - nchar(suffix))
    pkglist <- strsplit(pkgs, "_", fixed=TRUE)
    pkg2version <- sapply(pkglist, function(x) x[2L])
    names(pkg2version) <- sapply(pkglist, function(x) x[1L])
    pkg2version <- strsplit(pkg2version, "[.-]")
    bad_version_format <- sapply(pkg2version, length) != 3L
    if (any(bad_version_format)) {
        nicelist <- paste(pkgs0[bad_version_format], collapse=", ")
        warning("pkgs with bad version format: ", nicelist)
    }
    dup_pkgs <- unique(names(pkg2version)[duplicated(names(pkg2version))])
    for (pkg in dup_pkgs) {
        pkgset <- which(names(pkg2version) == pkg)
        versions <- unname(
            lapply(pkgset,
                   function(i) {
                       v <- suppressWarnings(as.integer(pkg2version[[i]]))
                       if (any(is.na(v)))
                           warning("pkg ", pkgs0[i], " has a ",
                                   "non-numeric version string")
                       v
                   }))
        nparts <- max(sapply(versions, length))
        ## Transpose the conceptual 'versions' matrix
        parts <- lapply(seq_len(nparts),
                     function(i) {
                         part <- sapply(versions, function(v) v[i])
                         part[is.na(part)] <- -1L
                         part
                    }
                 )
        ## Break ties by looking at the mtime
        mtimes <- file.info(pkgs0[pkgset])$mtime
        ii <- do.call(order, c(parts, list(as.double(mtimes))))
        old_pkgs <- pkgs0[pkgset[ii[-length(ii)]]]
        ans <- c(ans, old_pkgs)
    }
    ans
}

###
### Move old package versions to Archive/ in release and remove them in devel.
###
manage.old.pkgs <- function(path=".", suffix=".tar.gz")
{
    oldpkgs <- list.old.pkgs(path, suffix)
    library(BiocInstaller)
    if (!isDevel()) {
        for (pkg in oldpkgs) {
            path <- paste0("./Archive/", strsplit(pkg, "_")[[1]][1], "/")
            if (!dir.exists(path))
                dir.create(path, recursive=TRUE)
            file.copy(pkg, path, overwrite=FALSE)
        }
    }
    removed <- file.remove(oldpkgs)
    names(removed) <- oldpkgs
    removed
}
