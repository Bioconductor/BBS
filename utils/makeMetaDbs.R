makeMetaDbs <- function(db_filepath, repos_root, meta_path) {

  meat_dir <- Sys.getenv("BBS_MEAT_PATH")
  prop_status <- read.dcf(db_filepath)

  pkgs <- c()
  for (i in 1:dim(prop_status)[2]) {
    pkg_type_stage <- strsplit(colnames(prop_status)[i], "#")[[1]]
    if ("source" %in% pkg_type_stage &&
        strsplit(prop_status[i], ",")[[1]][1] %in% c("YES", "UNNEEDED")) {
        pkgs <- c(pkgs, pkg_type_stage[1])
    }
  }

  web_dir <- file.path(repos_root "web", "packages")
  meta_dir <- file.path(meta_path)
  if (!dir.exists(meta_dir)) {
    dir.create(meta_dir, recursive = TRUE)
  }

  pkg_paths <- file.path(meat_dir, pkgs)
  for (pkg_path in pkg_paths) {
    biocViews::build_db_from_source(pkg_path, repos_root)
  }

  aliases_db_file <- file.path(meta_dir, "aliases.rds")
  meta_aliases_db <- biocViews::build_meta_aliases_db(web_dir, aliases_db_file)
  saveRDS(meta_aliases_db, aliases_db_file, version = 2)

  rdxrefs_db_file <- file.path(meta_dir, "rdxrefs.rds")
  meta_rdxrefs_db <- biocViews::build_meta_rdxrefs_db(web_dir, rdxrefs_db_file)
  saveRDS(meta_rdxrefs_db, rdxrefs_db_file, version = 2)
}
