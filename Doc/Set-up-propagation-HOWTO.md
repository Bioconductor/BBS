# How to propagate packages from the central builder to master.bioconductor.org



## Introduction

- what's propagation
- from where to where
- what



## Set up the biocpush account

### Create the account

From your personal account (sudoer)

- create biocpush (use same password as for biocbuild)

### Install SSH keys

From the biocpush account

- create `~/.ssh` folder and copy `authorized_keys` and `id_rsa` from the
  biocbuild account.



## Create 3.14 destination on master.bioconductor.org


We need to create the folder where all the 3.14 package repositories will
be located on master.bioconductor.org.


### Go on master

From the biocpush account:
```
ssh -A webadmin@master.bioconductor.org
```


### Once on master

```
cd /extra/www/bioc/packages
```
If the `3.14` folder doesn't exist yet:
```
mkdir 3.14
```
Create empty package repositories inside 3.14:
```
cd 3.14
repos="bioc data/annotation data/experiment workflows books"
mkdir -p $repos
```
For now we'll just populate them with symlinks that redirect to the 3.13 repos:
```
previous_release=/extra/www/bioc/packages/3.13
for repo in $repos; do
    mkdir -p $repo/src
    ln -s $previous_release/$repo/src/contrib $repo/src
done
```


### TESTING

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
even though they don't. So for example this should work now:
```
repo <- "https://bioconductor.org/packages/3.14/bioc"
## From R:
install.packages("BiocGenerics", repos=repo)
```



## From the biocpush account


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

