# How to propagate packages from the build system to master.bioconductor.org



This document explains how to propagate the packages produced by the build
system to the public CRAN-style repositories hosted on master.bioconductor.org.



## 1. Introduction


### What we propagate

The Bioconductor daily builds (a.k.a. software builds) produce 3 types of
packages:
- **source packages** a.k.a. _package source tarballs_ (`tar.gz` extension)
- **Windows binary packages** (`zip` extension)
- **Mac binary packages** (`tgz` extension)
At the end of a daily run, packages that pass the _propagation criteria_
are propagated to the public CRAN-style repositories hosted on
master.bioconductor.org. The URLs for these repositories are of
the form https://bioconductor.org/packages/X.Y/bioc where X.Y
is the Bioconductor version. These are the repositories used by
`BiocManager::install()` to install packages.

Other builds (e.g. data-experiment, workflows, and books) also produce
packages, but, unlike the daily builds, they only produce **source packages**.

Some builds like the Long Test builds don't produce any package so there's
nothing propagate.


### The propagation scripts

The scripts we use for propagating packages are called the _propagation
scripts_. They are run on the _central_ builder which is where all the build
products are collected during a build run. (Note that the central builder is
always the Linux builder.)

The propagation scripts are run after the builds are finished and after
the central builder has generated the build report. Note that, like running
the builds, generating the report is done from the biocbuild account (by
running the `postrun.sh` script). However, the propagation scripts are run
from a different account, the biocpush account.


### The propagation criteria

A given package is allowed to propagate for a given platform if the 3
following conditions are satisfied:
1. It has no ERROR or TIMEOUT on that platform.
2. Its version was bumped since the last time it propagated. In other words,
   its current version must be strictly greater than the version that is
   already publicly available via `BiocManager::install()`.
3. The propagated package will not have _impossible dependencies_.
   An impossible dependency is a dependency that `BiocManager::install()`
   won't be able to satisfy because it's not available or because it does
   not have the minimum requested version.

The criteria is used independently for each platform so for example it
could be that for a given package, the source tarball and Mac binary are
allowed to propagate but not the Windows binary.

The little LED in the rightmost column of the build report indicates the
propagation status e.g. a green LED means that propagation is allowed.

The rest of this document explains how to achieve this setup.



## 2. Set up the biocpush account


If the central builder is a new machine that was recently configured to run
the builds, it should already have the biocbuild account from which the builds
are run, as well as some personal accounts for the Bioconductor Core Team
members in charge of the machine. Note that these personal accounts should
have sudo rights.

If the biocpush account doesn't exist yet, we need to create it.


### Create the account

From your personal account (sudoer), create the biocpush user. Use the same
commands that were used to create the biocbuild user. See _Set up the
biocbuild account_ section in the Prepare-Ubuntu-20.04-HOWTO.md document
for the details (replace `biocbuild` with `biocpush`). Use the same password
as for biocbuild.


### Install SSH keys

From the biocpush account:

- Create `~/.ssh` folder.
- Copy `authorized_keys` and `id_rsa` from the biocbuild account.
- Make sure `~/.ssh/id_rsa` is readonly by its owner only:
  `chmod 400 ~/.ssh/id_rsa`

TESTING: You should be able to ssh to master from the biocpush account. Try:

    ssh -A webadmin@master.bioconductor.org


### Clone BBS

Clone BBS in biocpush's home:

    cd
    git clone https://github.com/bioconductor/BBS

Then create symlink:

    ln -s BBS/propagation



## 3. Create the destination folder on master


This is the the folder at https://bioconductor.org/packages/X.Y where X.Y
is the Bioconductor version.


### Go on master

From the biocpush account:
```
ssh -A webadmin@master.bioconductor.org
```


### Once on master

Say we're setting up propagation for Bioconductor 3.14:

    cd /extra/www/bioc/packages

If the `3.14` folder doesn't exist yet:

    mkdir 3.14

Create empty package repositories inside 3.14:

    cd 3.14
    repos="bioc data/annotation data/experiment workflows books"
    mkdir -p $repos

For now we'll just populate them with symlinks that redirect to the 3.13 repos:

    previous_release=/extra/www/bioc/packages/3.13
    for repo in $repos; do
        mkdir -p $repo/src
        ln -s $previous_release/$repo/src/contrib $repo/src
    done


### Testing

`tree` should show the following:
```
.
├── bioc
│   └── src
│       └── contrib -> /extra/www/bioc/packages/3.13/bioc/src/contrib
├── books
│   └── src
│       └── contrib -> /extra/www/bioc/packages/3.13/books/src/contrib
├── data
│   ├── annotation
│   │   └── src
│   │       └── contrib -> /extra/www/bioc/packages/3.13/data/annotation/src/contrib
│   └── experiment
│       └── src
│           └── contrib -> /extra/www/bioc/packages/3.13/data/experiment/src/contrib
└── workflows
    └── src
        └── contrib -> /extra/www/bioc/packages/3.13/workflows/src/contrib

11 directories, 5 files
```

This tricks `install.packages()` into believing that the 3.14 repos exist
even though they don't. So for example now this should work but it will
install the version of the BiocGenerics package that belongs to BioC 3.13:
```
repo <- "https://bioconductor.org/packages/3.14/bioc"
## From R:
install.packages("BiocGenerics", repos=repo)
```
This is a temprary situation only, until we propagate the packages produced
by the 3.14 daily builds.



## 4. Install R


Choose the version of R that matches the version of Bioconductor that we're
going to propagate. For example, for BioC 3.14, this is R 4.1.

From the biocpush account:

- Create folders `rdownloads`, `R-4.1`, `bin`, and `pkgs_to_install` in
  biocpush's home. Note that `~/bin` will automatically be added to the
  `PATH` next time you login as biocpush, but it's a good idea to logout
  and login again now so it takes effect now.

- Download and extract latest R source tarball to `~/rdownloads`.

- Configure and compile in `~/R-4.1`.

- Create symlinks in `~/bin`:
    ```
    cd ~/bin
    ln -s ~/R-4.1/bin/R R-4.1
    ln -s ~/R-4.1/bin/Rscript Rscript-4.1
    ```
- Install the most current version of the biocViews package:
    ```
    ## First install it from R with BiocManager::install(). This is the
    ## easiest way to get all the dependencies installed:
    install.packages("BiocManager", repos="https://cran.r-project.org")
    library(BiocManager)
    BiocManager::install("biocViews")
    ```
    ```
    ## Then quit R and reinstall it directly from git.bioconductor.org. This
    ## is to make sure that we're actually getting the most current version
    ## even if it was modified very recently (e.g. <24h ago) and didn't have
    ## time to propagate to the public package repos. This is particularly
    ## important after the biocViews vocab has changed.
    cd ~/pkgs_to_install
    git clone https://git.bioconductor.org/packages/biocViews
    R-4.1 CMD INSTALL biocViews
    ```

- Install Bioconductor package DynDoc:
    ```
    BiocManager::install("DynDoc")
    ```

- Install CRAN packages knitr, knitcitations, and commonmark:
    ```
    ## From R:
    install.packages("knitr", repos="https://cran.r-project.org")
    install.packages("knitcitations", repos="https://cran.r-project.org")
    install.packages("commonmark", repos="https://cran.r-project.org")
    ```



## 5. Create the staging package repositories

    cd
    mkdir PACKAGES

TODO



## 6. Add propagation scripts to crontab

- create ~/cron.log/3.14

TODO

