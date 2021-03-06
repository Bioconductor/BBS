
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager", repos="https://cran.rstudio.com")

deps <- c("httr", "yaml", "R.utils")

for (dep in deps)
{
    if (!do.call(require, list(dep)))
    {
        BiocManager::install(dep)
        do.call(library, list(dep))
    }
}

defaultMirror <- function()
{
    unname(sub("http:", "https:", biocinstallRepos()["BioCsoft"], TRUE))
}

testHttps <- function(mirrorUrl=defaultMirror())
{
    oldwarn <- getOption('warn')
    on.exit(options(warn=oldwarn))
    options(warn=2)
    print(sprintf("Trying %s ...", mirrorUrl))
    tryCatch({
        withTimeout(download.packages("Biobase", tempdir(), repos=mirrorUrl),
            timeout=30, onTimeout="error")
        TRUE
        },
        error=function(e) FALSE)
}

getMirrors <- function()
{
    yaml <- content(GET("http://bioconductor.org/config.yaml"))
    obj <- yaml.load(yaml)
    mirrors <- unlist(lapply(obj$mirrors, function(x) {
        x=unlist(unname(x))
        unlist(unname(x[names(x)=="mirror_url"]))
    }))
    mirrors <- sub("http:", "https:", mirrors, TRUE)
    mirrors <- paste0(mirrors, "packages/", BiocManager::version(), "/", "bioc")
    mirrors <- c(defaultMirror(), mirrors)
    names(mirrors) <- mirrors
    mirrors
}


unlist(lapply(getMirrors(), testHttps))
