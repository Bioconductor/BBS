# How to propagate packages from the central builder to master.bioconductor.org



## Introduction

- what's propagation
- from where to where
- what



## From your personal account (sudoer)

- create biocpush (use same password as for biocbuild)



## From the biocpush account


### Install SSH keys

- create `~/.ssh` folder and copy `authorized_keys` and `id_rsa` from the
  biocbuild account.


### Install R

- create folders `rdownloads`, `R-4.1`, `bin`, and `pkgs_to_install` in home.

  Note that `~/bin` will automatically be added to the PATH next time you
  login as biocpush, but it's a good idea to logout and login again now so
  it takes effect now.

- download and extract latest R source tarball to `~/rdownloads`

- configure and compile in R-4.1

- create symlinks in `~/bin`:

    cd ~/bin
    ln -s ~/R-4.1/bin/R R-4.1
    ln -s ~/R-4.1/bin/Rscript Rscript-4.1

- install the most current version of the biocViews package:
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

- install Bioconductor package DynDoc:
    ```
    BiocManager::install("DynDoc")
    ```

- install CRAN packages knitr, knitcitations, and commonmark:
    ```
    ## From R:
    install.packages("knitr", repos="https://cran.r-project.org")
    install.packages("knitcitations", repos="https://cran.r-project.org")
    install.packages("commonmark", repos="https://cran.r-project.org")
    ```


### Clone BBS

- clone BBS in biocpush's home:

    cd
    git clone https://github.com/bioconductor/BBS

  Then create symlink:

    ln -s BBS/propagation


### Create the staging package repositories

    cd
    mkdir PACKAGES



### Add propagation scripts to crontab

- create ~/cron.log/3.14

