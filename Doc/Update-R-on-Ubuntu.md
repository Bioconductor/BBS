# How to Update R on the Linux build machines

*NOTE*: Throughout this document, `$BIOC_VERSION` 
used to represent the Bioconductor version, to make
commands more copy-pastable (assuming `$BIOC_VERSION`
is defined).

## Updating R on Mac OSX and Windows:

This document only describes updating R on Linux. We do not have a
HOWTO document for configuring a Linux builders but instead use a Chef
recipe.

  https://github.com/Bioconductor/BBS-provision-cookbook

Because the Chef recipe doesn't have an obvious place for this sort of 
documentation we've included it here.

The HOWTWO doc for Mac OSX describes how to install R on that platform:

  https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-MacOSX-El-Capitan-HOWTO.TXT

The HOWTO doc for Windows describes how to install R on that platform:

  https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-Windows-Server-2012-HOWTO.TXT

## When to update

Make sure software builds are not running or about to run in the next 30
minutes or so. Make sure data/experiment builds are not running. Don't forget
to update R on all the nodes participating to the builds. Also, try to have the
same R (same revision number) on all the nodes.

Don't update after the software builds run but before the data/experiment
builds run.  (The data/experiment builds depend on the software builds having
run first.)

Build start times and duration change over time. The 'Build Machine Daily 
Schedule' keeps record of when the different builds are running. Consult this
schedule to pick an appropriate time for the update:

  https://docs.google.com/document/d/1Ubp7Tcxr1I1HQ8Xrp9f73P40YQ0qhWQ_hSmHs05Ln_M/edit#heading=h.r7sorafgdpnf

## R for biocbuild

### Where to find R

Note that we build R *from source* on Linux, we do not
install a package for a Linux distribution
(i.e. we don't use `apt-get on Ubuntu).

#### R-devel

[https://stat.ethz.ch/R/daily/](https://stat.ethz.ch/R/daily/)

#### Release

[https://cran.r-project.org/](https://cran.r-project.org/)

#### Alpha, beta, RC, etc.

[https://cran.r-project.org/src/base-prerelease/](https://cran.r-project.org/src/base-prerelease/)

### Downloading

As the `biocbuild` user, download to `~/bbs-3.*-bioc/rdownloads`
on the Linux build node.

The file you download should have a descriptive name, including
a version or a date, such as `R-3.2.r67960.tar.gz` or
`R-devel_2015-11-08.tar.gz`. If the file does not have such
a name (i.e., it's just caled R-devel.tar.gz) please rename
it after downloading.

Download with wget or curl: 

    curl -LO <URL>

Check the date:

    ls -altr

### Untarring

Remove the old R-devel folder if present:

    rm R-devel/
 
Untar the download with

    tar -zvxf

If the directory created by untarring is called something like `R-devel`
and does not have a descriptive name (containing a date or svn revision
number) then please rename accordingly.

Directory should have a name like `R-3.2.r67960`
or `R-devel-20151026`.

Check version and revision:

    cat R-devel_2017-02-13/VERSION
    cat R-devel_2017-02-13/SVN-REV

### Building

    cd ~/bbs-$BIOC_VERSION-bioc
    # if R.old exists:
    mv R.old R.deleteme 
    nohup rm -rf R.deleteme > /dev/null 2>&1 & # takes some time
    # if R directory exists:
    mv R R.old
    mkdir R 
    cd R

Build R as follows from within the ~/bbs-3.*-bioc/R/ directory:

    ~/bbs-3.*-bioc/rdownloads/<DIRECTORY_WHERE_R_WAS_UNTARRED>/configure --enable-R-shlib
    time make

Instead of `make` you can also do `make -j` to use
all cores or `make -jN` to use `N` cores.

### After building

Run a script to fix compilation flags by modifying Makeconf. It's very
important to run this from the ~/bbs-3.*-bioc/R/etc/ directory and not one 
level up. Both locations have Makefiles.

    cd ~/bbs-3.8-bioc/R/etc
    ~/BBS/utils/R-fix-flags.sh 

This sets the C/C++ compilation flags appropriately for the build system, e.g.,
-Wall, which show additional warnings useful for package developers.

Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")


If you are on a devel build machine (and not running
R-devel), do this:

    useDevel()

### Testing

Start the new R. Check the date and revision number displayed
at startup:

  ~/bbs-3.*-bioc/R/bin/R

Install a few packages and their dependencies:

    biocLite("Biobase", type="source")
    biocLite("IRanges", type="source")
    biocLite("zlibbioc", type="source")
    biocLite("GLAD")
    biocLite("PICS")

Try to load them with library().

Quit the session. Try to install GLAD and PICS from the shell:

    cd ~/bbs-3.*-bioc/meat
    $ R CMD INSTALL GLAD 
    $ R CMD INSTALL PICS 

### The first build cycle after a fresh R install

Note that, when using a freshly built R, the builds take longer because all
the dependencies need to be re-installed (this is done automatically during
STAGE2).

### Flushing

Historically we used to 'flush' the whole build pipe by removing all current
packages. (I don't think this is done anymore as of BioC 3.5) When that is
done, the empty PACKAGES, PACKAGES.gzip and PACKAGES.rds must be recreated.

Also, when a CRAN-style dir tree is created by hand, a 'replisting' file must
be present in its root because the biocViews package (use by prepareRepos-*.sh
family) seems to need it.

## R for biocadmin

Updating/preparing the staging repos is done from the biocadmin account by
running the prepareRepos-*.sh scripts. Most of the work done by the
prepareRepos-*.sh scripts is actually done in R by calling functions defined in
the biocViews package.

All these scripts share some configuration variables via the 
BBS/propagation-pipe/3.7/config.sh file.

BIOC_VERSION="3.7"
R_VERSION="3.5"
R="$HOME/bin/R-$R_VERSION"

- Download the new R tarball to /home/biocadmin/rdownloads.
- Untar and name directory to something like R-3.5.
- Move the un-tared directory up one level (same level as bin/).
- From within R-3.5 directory
    ./configure --enable-R-shlib && make
- Modify the symlink in bin/

    biocadmin@malbec2:~$ ls -l bin
    total 0
    lrwxrwxrwx 1 biocadmin biocadmin 27 Oct 23 11:44 R-3.5 -> /home/biocadmin/R-3.5/bin/R

- Start R and download biocLite:

    ./bin/R-3.5
    source("https://bioconductor.org/biocLite.R");

- Install the packages in /home/biocbuild/pkgs_to_install/ + knitr and
  knitcitations:

    biocadmin@malbec2:~$ ls pkgs_to_install/
    BiocInstaller  biocViews  DynDoc  graph  README

    biocLite(c('biocViews','DynDoc','graph', 'knitr', 'knitcitations'))
