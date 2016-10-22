#!/usr/bin/env Rscript --vanilla

# be sure and call me with the --vanilla option
# so that no extraneous things are printed out.

getMaintainer <- function(desc_file)
{
    FIELD <- "Maintainer"
    desc <- tools:::.read_description(desc_file)
    m <- match(FIELD, names(desc))
    if (!is.na(m))
        return(desc[[m]])
    suppressWarnings(
        fields <- tools:::.expand_package_description_db_R_fields(desc)
    )
    fields[[FIELD]]
}

args <- commandArgs(TRUE)

maintainer <- try(getMaintainer(args[[1L]]), silent=TRUE)
if (inherits(maintainer, "try-error") || maintainer == "")
    maintainer <- "NA"
cat(maintainer)

