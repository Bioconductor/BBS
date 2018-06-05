updateNonTargetPkgs <- function()
{
    ## No update for the workflows builds
}

injectDESCRIPTION <- function()
{
    target_pkgs <- file.path(Sys.getenv('BBS_WORK_TOPDIR'),
                             "STAGE2_tmp", "target_pkgs.txt")
    targets <- read.table(target_pkgs, stringsAsFactors=FALSE)[,1]
    for (pkg in targets) {
        # Fields from git-log-* file
        gitlog_file <- paste0("git-log-", pkg, ".txt")
        gitlog_path <- file.path(Sys.getenv('BBS_GITLOG_PATH'), gitlog_file)
        if (file.exists(gitlog_path)) {
            git_fields <- read.dcf(gitlog_path)[1,]

            # DESCRIPTION
            desc_file <- file.path(Sys.getenv('BBS_MEAT_PATH'), 
                                  pkg, "DESCRIPTION")
            desc <- read.dcf(desc_file)[1,]
            # If field exists in DESCRIPTION --> remove
            fields <- c("git_url", "git_last_commit", 
                        "git_last_commit_date")
            exists <- names(desc) %in% fields
            if (any(exists))
                desc <- desc[!exists]

            desc["git_url"] <- git_fields["URL"]
            desc["git_last_commit"] <- git_fields["Last Commit"]
            desc["git_last_commit_date"] <- git_fields["Last Changed Date"]
            write.dcf(rbind(desc), desc_file)
        } else {
            sprintf("could not find %s --> skipping", gitlog_path)
        }
    }
}
