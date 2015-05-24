#!/usr/bin/env Rscript --vanilla

# be sure and call me with the --vanilla option
# so that no extraneous things are printed out.

# extracts maintainer information from
# DESCRIPTION file if and only if there is
# an Authors@R field with valid name
# and email. Python will first look
# for an old-school Maintainer field
# and call this if that is not found.
getMaintainer <- function(descriptionFile)
{
    if (!file.exists(descriptionFile))
        return(NULL)
    dcf <- try(read.dcf(descriptionFile), silent=TRUE)
    if (inherits(dcf, "try-error"))
        return(NULL)
    if (!"Authors@R" %in% colnames(dcf))
        return(NULL)
    authors <- dcf[, 'Authors@R']
    # Theoretically any R code that resolves
    # to a 'person' object is valid, but in order
    # to avoid nasty R injection attacks, we only allow
    # the 'c' and 'person' functions to be called.
    env <- new.env(parent=emptyenv())
    env[["c"]] = c
    env[["person"]] <- person
    people <- try({
            pp <- parse(text=authors)
            eval(pp, env)
        }, silent=TRUE)
    if (inherits(people, "try-error"))
        return(NULL)
    if (is.null(people) || is.na(people))
        return(NULL)
    for (person in people)
    {
        # Assume there is only one person with role 'cre' and 
        # return the first one we encounter.
        if ("cre" %in% person$role)
        {
            email <- person$email
            if (is.null(email))
                return(NULL)
            given <- paste(person$given, collapse=" ")
            if (is.null(given))
                given <- ""
            family <- paste(person$family, collapse=" ")
            if (is.null(family))
                family <- ""
            if (given == "" && family == "")
                return(NULL)
            res <- sprintf("%s %s <%s>", given, family, email)
            res <- sub("^ +", "", res)
            return(res)
        }
    }
    return(NULL)
}

args <- commandArgs(TRUE)
if (length(args) == 0)
{
    cat("NULL")
    q("no")
}
res <- getMaintainer(args[1])

if (is.null(res))
{
    cat("NULL")
} else {
    cat(res)
}


