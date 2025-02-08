makeMetaDbs <- function(outgoing_path, db_filepath) {

  meat_dir <- Sys.getenv("BBS_MEAT_PATH")
  bbs_central_rdir <- Sys.getenv("BBS_CENTRAL_RDIR")
  prop_status <- read.dcf(file.path(bbs_central_rdir, db_filepath))

  pkgs <- c()
  for (i in 1:dim(prop_status)[2]) {
    pkg_type_stage <- strsplit(colnames(prop_status)[i], "#")[[1]]
    if ("source" %in% pkg_type_stage &&
        strsplit(prop_status[i], ",")[[1]][1] %in% c("YES", "UNNEEDED")) {
        pkgs <- c(pkgs, pkg_type_stage[1])
    }
  }

  # Because the location is always recreated, we always create the Meta
  # directory and always create all the databases
  web_dir <- file.path(bbs_central_rdir, "web", "packages")
  meta_dir <- file.path(bbs_central_rdir, "OUTGOING", "Meta")
  if (!dir.exists(meta_dir)) {
    dir.create(meta_dir, recursive = TRUE)
  }

  pkg_paths <- file.path(meat_dir, pkgs)
  for (pkg_path in pkg_paths) {
    biocViews::build_db_from_source(pkg_path, bbs_central_rdir)
  }

  aliases_db_file <- file.path(meta_dir, "aliases.rds")
  meta_aliases_db <- biocViews::build_meta_aliases_db(web_dir, aliases_db_file,
                                                      TRUE)
  saveRDS(meta_aliases_db, aliases_db_file, version = 2)

  rdxrefs_db_file <- file.path(meta_dir, "rdxrefs.rds")
  meta_rdxrefs_db <- biocViews::build_meta_rdxrefs_db(web_dir, rdxrefs_db_file,
                                                      TRUE)
  saveRDS(meta_rdxrefs_db, rdxrefs_db_file, version = 2)
}
