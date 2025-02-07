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
  dir.create(meta_dir, recursive = TRUE)

  biocViews::build_db_from_source(file.path(meat_dir, pkgs), bbs_central_rdir)

  aliases_db_file <- file.path(meta_dir, "aliases.rds")
  biocViews::build_meta_aliases_db(web_dir, aliases_db_file, TRUE)

  rdxrefs_db_file <- file.path(meta_dir, "rdxrefs.rds")
  biocViews::build_meta_rdxrefs_db(web_dir, rdxrefs_db_file, TRUE)
}
