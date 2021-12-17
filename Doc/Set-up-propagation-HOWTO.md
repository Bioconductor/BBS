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
commands that were used to create the biocbuild account. In particular, like
the biocbuild account, biocpush should be set up as a regular account i.e it
should NOT have sudo privileges. See _Set up the biocbuild account_ section
in the Prepare-Ubuntu-20.04-HOWTO.md document for the details (replace
`biocbuild` with `biocpush`). Use the same password as for biocbuild.


### Install RSA keys

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



## 3. Create https://bioconductor.org/packages/X.Y on master


This is the the folder at https://bioconductor.org/packages/X.Y where X.Y
is the Bioconductor version.


### Go to master

From the biocpush account:

    ssh -A webadmin@master.bioconductor.org


### Create https://bioconductor.org/packages/X.Y

Say we're setting up propagation for Bioconductor 3.15:

    cd /extra/www/bioc/packages

If the `3.15` folder doesn't exist yet:

    mkdir 3.15

Note that we cannot test the https://bioconductor.org/packages/X.Y URL
because trying to open it in a browser is not expected to work at this
moment.


### Create fake X.Y repositories

Create empty package repositories inside 3.15:

    cd 3.15
    repos="bioc data/annotation data/experiment workflows books"
    mkdir -p $repos

For now we'll just populate them with symlinks that redirect to the 3.14 repos:

    previous_release=/extra/www/bioc/packages/3.14
    for repo in $repos; do
        ln -s $previous_release/$repo/VIEWS $repo/
        mkdir -p $repo/src
        ln -s $previous_release/$repo/src/contrib $repo/src/
    done

Note that this is temporary only, until each repository gets populated by the
propagation scripts. When this happens, the symlinks will get automatically
replaced with real content.

`tree` should show the following:
```
.
├── bioc
│   └── src
│       └── contrib -> /extra/www/bioc/packages/3.14/bioc/src/contrib
├── books
│   └── src
│       └── contrib -> /extra/www/bioc/packages/3.14/books/src/contrib
├── data
│   ├── annotation
│   │   └── src
│   │       └── contrib -> /extra/www/bioc/packages/3.14/data/annotation/src/contrib
│   └── experiment
│       └── src
│           └── contrib -> /extra/www/bioc/packages/3.14/data/experiment/src/contrib
└── workflows
    └── src
        └── contrib -> /extra/www/bioc/packages/3.14/workflows/src/contrib

11 directories, 5 files
```

The symlinks will trick `install.packages()` into believing that the 3.15
repos exist even though they don't.

#### When devel and release use different versions of R

The above solution works when devel and release use the same version of R;
however, when devel and release are different, the following warning appears
for macos because it expected `4.2` where `4.1` only existed.

    The downloaded source packages are in
       '/private/var/folders/1w/xf7rrsr1483d4rg7vwbkdy780000gp/T/RtmpSo8mys/downloaded_packages'
    Warning messages:
    1: In .inet_warning(msg) :
      unable to access index for repository https://bioconductor.org/packages/3.15/data/annotation/bin/macosx/contrib/4.2:
      cannot open URL 'https://bioconductor.org/packages/3.15/data/annotation/bin/macosx/contrib/4.2/PACKAGES'
    2: In .inet_warning(msg) :
      unable to access index for repository https://cloud.r-project.org/bin/macosx/contrib/4.2:
      cannot open URL 'https://cloud.r-project.org/bin/macosx/contrib/4.2/PACKAGES' 

The solution is to create a symlink from `4.1` to `4.2` in `/home/biocpush/PACKAGES/3.14/data/annotation/bin/macosx/contrib`
and in `/home/biocpush/PACKAGES/3.14/data/annotation/bin/windows/contrib` then run `./pushRepos-data-annotation.sh` to put
it on `master.bioconductor.org`.

    oses="macosx windows"
    data_annotation=/home/biocpush/PACKAGES/3.14/data/annotation/bin
    for os in $oses; do
        ln -s $data_annotation/$os/contrib/4.1 4.2
    done
    ./pushRepos-data-annotation.sh


### Testing

Thanks to the symlinks, the following should work. However it's important
to realize that it will install the version of the BiocGenerics package
that belongs to BioC 3.14:

    ## From R:
    repo <- "https://bioconductor.org/packages/3.15/bioc"
    install.packages("BiocGenerics", repos=repo)

This is a temprary situation only, until we propagate the packages produced
by the 3.15 daily builds.

Note that trying to open the https://bioconductor.org/packages/3.15/bioc
URL in a browser is not expected to work at this point (you should get
"Error 403 - Access Forbidden").



## 4. Create the staging package repositories


From the biocpush account.

Create `~/PACKAGES/3.15` and the 4 CRAN-style package repos: `bioc` (software),
`data/experiment`, `workflows`, and `books` below it. No `data/annotation`
repo for now:

    mkdir -p ~/PACKAGES/3.15/bioc
    mkdir -p ~/PACKAGES/3.15/data/experiment/
    mkdir -p ~/PACKAGES/3.15/workflows
    mkdir -p ~/PACKAGES/3.15/books

Each repo must be set up as a CRAN-style repository so must follow the
official CRAN layout. For an empty repo, this layout is:
```
.
├── bin
│   ├── macosx
│   │   └── contrib
│   │       └── 4.2
│   │           └── PACKAGES
│   └── windows
│       └── contrib
│           └── 4.2
│               └── PACKAGES
└── src
    └── contrib
        └── PACKAGES
```
where `PACKAGES` are empty files.

The above layout needs to be manually created inside each repo. For example
to create it inside the software repository:

    cd ~/PACKAGES/3.15/bioc
    mkdir -p src/contrib bin/windows/contrib/4.2 bin/macosx/contrib/4.2
    touch src/contrib/PACKAGES
    touch bin/windows/contrib/4.2/PACKAGES
    touch bin/macosx/contrib/4.2/PACKAGES

Then check the layout with `tree`.



## 5. Install R


From the biocpush account:

- Choose the version of R that matches the version of Bioconductor that
  we're going to propagate. For example, for BioC 3.15, this is R 4.2.

- Create folders `rdownloads`, `R-4.2`, `bin`, and `pkgs_to_install` in
  biocpush's home. Note that `~/bin` will automatically be added to the
  `PATH` next time you login as biocpush, but it's a good idea to logout
  and login again now so it takes effect now.

- Download and extract latest R source tarball to `~/rdownloads`.

- Configure and compile in `~/R-4.2`.

- Create symlinks in `~/bin`:
    ```
    cd ~/bin
    ln -s ~/R-4.2/bin/R R-4.2
    ln -s ~/R-4.2/bin/Rscript Rscript-4.2
    ```

- Install the BiocManager package:
    ```
    install.packages("BiocManager", repos="https://cran.r-project.org")

    ## This displays the version of Bioconductor that BiocManager is pointing
    ## at. Make sure that this is the same as the version of Bioconductor to
    ## propagate.
    library(BiocManager)

    ## IMPORTANT: Do this ONLY if BiocManager is pointing at the wrong version
    ## of Bioconductor.
    BiocManager::install(version="devel")
    ```

If you get a message that Bioconductor doesn't build and check for packages for
your R version then use the following hack in the local `biocViews` in
`~/pkgs_to_install/biocViews/R/repository.R:

    ```
    # Replace
    # all_repos <- repositories()
    all_repos <- BiocManager:::.repositories(character(), version="3.15")
    ```

Save but don't commit.

- Install the most current version of the biocViews package:
    ```
    ## First install it from R with BiocManager::install(). This is the
    ## easiest way to get all the dependencies installed:
    library(BiocManager)
    BiocManager::install("biocViews")
    ```
    ```
    ## Then quit R and reinstall it directly from git.bioconductor.org. This
    ## is to make sure that we're actually getting the most current version
    ## in case it was modified very recently (e.g. <24h ago) and didn't have
    ## time to propagate to the public package repos. This is particularly
    ## important after the biocViews vocab has changed.
    cd ~/pkgs_to_install
    git clone https://git.bioconductor.org/packages/biocViews
    R-4.2 CMD INSTALL biocViews
    ```

If you previously got the message that BiocManager doesn't support your version
of R, you can use the following hack to to install biocViews:

    ```
    repos <- BiocManager:::.repositories(character(), version="3.14")
    install.packages("biocViews", repos=repos)
    ```

Then you can install biocViews in the `~/pkgs_to_install` directory.

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



## 6. Add propagation scripts to biocpush's crontab


From the biocpush account.

The propagation scripts for BioC 3.15 are located in the `~/propagation/3.15/`
folder. For the software packages, they are: `updateReposPkgs-bioc.sh`,
`prepareRepos-bioc.sh`, and `pushRepos-bioc.sh`.


### Before running the scripts

Three important things before we run these scripts:

1. Create `~/cron.log/3.15`.

2. From the biocbuild account: Make sure to uncomment the
   `export BBS_OUTGOING_MAP=...` line in `~/BBS/3.15/bioc/nebbiolo2/config.sh`
   before `postrun.sh` runs. If `postrun.sh` has run already and the report
   has already been published, uncomment the line anyway and rerun `postrun.sh`.
   This 2nd run of `postrun.sh` will take much longer because the script now
   needs to do a few more things that are related to propagation. One of them
   is to generate the propagation status db.
   Once `postrun.sh` is finished, check the build report again (reload the
   page in your browser if you already had it there). Now you should see
   many little green LEDs in the rightmost column of the report indicating
   propagation status.

3. Check that `~/bin/Rscript-4.2` works and that it can load the biocViews
   package:
    ```
    ~/bin/Rscript-4.2 -e 'library(biocViews);cat("SUCCESS!\n")'
    ```


### Manual run

It's a good idea to try to run the scripts manually the first time so we can
make sure that they work as expected. They must be run in the following order:
1. `updateReposPkgs-bioc.sh`
2. `prepareRepos-bioc.sh`
3. `pushRepos-bioc.sh`

(Adjust the names if setting up propagation for other builds e.g. replace
`-bioc.sh` with `-data-experiment.sh`.)

#### Manual run of updateReposPkgs-bioc.sh

We can only run the first script (`updateReposPkgs-bioc.sh`) after the
`postrun.sh` script was run (from the biocbuild account) and before the
next builds start (`prerun.sh` script). Note that in the case of the software
builds which are run every day, this leaves us with a limited time window
that goes from about 12:20 pm EST to 14:50 pm EST.

Run it with:

    cd ~/propagation/3.15
    ./updateReposPkgs-bioc.sh >>~/cron.log/3.15/updateReposPkgs-bioc.first-run.log 2>&1 &

This script should not take long, typically < 1 min.

Check that it was successful with:

    tail ~/cron.log/3.15/updateReposPkgs-bioc.first-run.log

The last line should be:

    DONE.

Also if some packages were allowed ot propagate, you should see them in
`~/PACKAGES/3.15/bioc`.

#### Manual run of prepareRepos-bioc.sh

This script can be run any time, except when another instance of the script
is already running. Run it with:

    cd ~/propagation/3.15
    ./prepareRepos-bioc.sh >>~/cron.log/3.15/prepareRepos-bioc.first-run.log 2>&1 &

For big repositories like software and data-experiment, it can take a while
e.g. between 15 min. (software) and more than 1 hour (data-experiment).

Check that it was successful with:

    tail ~/cron.log/3.15/prepareRepos-bioc.first-run.log

The last line should be:

    DONE.

#### Manual run of pushRepos-bioc.sh

This script should be run right after `prepareRepos-bioc.sh`. All it does
is rsync the content of the public software repo on master (https://bioconductor.org/packages/3.15/bioc) with the local `~/PACKAGES/3.15/bioc` repo (a.k.a.
staging software repo).

    cd ~/propagation/3.15
    ./pushRepos-bioc.sh

If you run it a 2nd time after that, it should only display something like
this:

    sending incremental file list
    
    sent 888,710 bytes  received 14,229 bytes  85,994.19 bytes/sec
    total size is 15,023,471,508  speedup is 16,638.41

which indicates that nothing was transferred (because the public repo is
already in sync with the staging repo).


### Add crontab entry

Add the following lines to the crontab:

- For propagation of software packages:
    ```
    # PROPAGATE BIOC 3.15 SOFTWARE PACKAGES
    # -------------------------------------
    
    # Must start **after** 'biocbuild' has finished its "postrun.sh" job!
    00 12 * * 1-6 cd /home/biocpush/propagation/3.15 && (./updateReposPkgs-bioc.sh && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh) >>/home/biocpush/cron.log/3.15/propagate-bioc-`date +\%Y\%m\%d`.log 2>&1
    ```

- For propagation of data annotation packages:

    ```
    # PROPAGATE BIOC 3.15 DATA ANNOTATION PACKAGES
    # --------------------------------------------
    
    # Must start **after** 'biocbuild' has finished its "postrun.sh" job!
    00 07 * * 3 cd /home/biocpush/propagation/3.15 && (./updateReposPkgs-data-annotation.sh && ./prepareRepos-data-annotation.sh && ./pushRepos-data-annotation.sh) >>/home/biocpush/cron.log/3.15/propagate-data-annotation-`date +\%Y\%m\%d`.log 2>&1
    ```

- For propagation of data experiment packages:
    ```
    # PROPAGATE BIOC 3.15 DATA EXPERIMENT PACKAGES
    # --------------------------------------------
    
    # Must start **after** 'biocbuild' has finished its "postrun.sh" job!
    45 15 * * 2,4 cd /home/biocpush/propagation/3.15 && (./updateReposPkgs-data-experiment.sh && ./prepareRepos-data-experiment.sh && ./pushRepos-data-experiment.sh) >>/home/biocpush/cron.log/3.15/propagate-data-experiment-`date +\%Y\%m\%d`.log 2>&1
    ```
- For propagation of workflow packages:
    ```
    # PROPAGATE BIOC 3.15 WORKFLOWS
    # -----------------------------
    
    # Must start **after** 'biocbuild' has finished its "postrun.sh" job!
    45 14 * * 2,5 cd /home/biocpush/propagation/3.15 && (./updateReposPkgs-workflows.sh && ./prepareRepos-workflows.sh && ./pushRepos-workflows.sh) >>/home/biocpush/cron.log/3.15/propagate-workflows-`date +\%Y\%m\%d`.log 2>&1
    ```
- For propagation of books:
    ```
    # PROPAGATE BIOC 3.15 BOOKS
    # -------------------------
    
    # Must start **after** 'biocbuild' has finished its "postrun.sh" job!
    35 14 * * 1,3,5 cd /home/biocpush/propagation/3.15 && (./updateReposPkgs-books.sh && ./prepareRepos-books.sh && ./pushRepos-books.sh && ./deploy-books.sh) >>/home/biocpush/cron.log/3.15/propagate-books-`date +\%Y\%m\%d`.log 2>&1
    ```
  Note that for books, we run one more script, the `deploy-books.sh` script.



## 7. Update https://bioconductor.org/config.yaml


This file needs to be updated to reflect availability of new public
repositories (so the corresponding package landing pages are generated).
Ask Lori to help with this.

