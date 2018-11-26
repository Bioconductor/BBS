# Update R on the Linux build machines

This document describes how to update update (not install) R on Linux. Normally
both installation and update instructions would be included in the
HOWTO doc but we don't have one for Linux. Instead, we have a Chef recipe
which documents how to configure the Linux builder (which includes installing
R):

  https://github.com/Bioconductor/BBS-provision-cookbook

The Chef recipe doesn't have an obvious place for 'update' instructions so
we've included them here.

*NOTE*: Throughout this document, `$BIOC_VERSION` 
used to represent the Bioconductor version, to make
commands more copy-pastable (assuming `$BIOC_VERSION`
is defined).

## Table of Contents
- [When to update](#when-to-update)
- [R for biocbuild](#biocbuild)
  - [Where to find R](#where-to-find)
  - [Downloading](#downloading)
  - [Untarring](#untarring)
  - [Building](#building)
  - [After Building](#after-building)
  - [Testing](#testing)
  - [First build cycle after a fresh R install](#first-cycle)
  - [Flushing AnnotationHub and ExperimentHub cache](#flushing-hubs)
  - [Flushing the build pipe](#flushing)
- [R for biocadmin](#biocadmin)
- [Updating R on Mac OSX and Windows](mac-and-windows)

<a name="when-to-update"></a>
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

<a name="biocbuild"></a>
## R for biocbuild

<a name="where-to-find"></a>
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

<a name="downloading"></a>
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

<a name="untarring"></a>
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

<a name="building"></a>
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

<a name="after-building"></a>
### After building

Run a script to fix compilation flags by modifying Makeconf. It's very
important to run this from the ~/bbs-3.*-bioc/R/etc/ directory and not one 
level up. Both locations have Makefiles.

    cd ~/bbs-3.8-bioc/R/etc
    ~/BBS/utils/R-fix-flags.sh 

This sets the C/C++ compilation flags appropriately for the build system, e.g.,
-Wall, which show additional warnings useful for package developers.

Run R and install Bioconductor:

    install.packages("BiocManager", repos="https://cran.r-project.org")
    BiocManager::install()

<a name="testing"></a>
### Testing

Start the new R and check the date and revision number displayed
at startup:

  ~/bbs-3.*-bioc/R/bin/R


FIXME: What testing is relevant on Linux? Same as on Mac after an
       R update? (section 'I' in Prepare-MacOSX-ElCapitan-HOWTO.TXT)


<a name="first-cycle"></a>
### First build cycle after a fresh R install

Note that, when using a freshly built R, the builds take longer because all
the dependencies need to be re-installed (this is done automatically during
STAGE2).

<a name="flushing-hubs"></a>
### Flushing AnnotationHub and ExperimentHub cache

When R is updated, the cache for AnnotationHub and ExperimentHub should be
refreshed. This is done by removing all of .AnnotationHub/,
.AnnotationHubData/, .ExperimentHub/ and .ExperimentHubData/ that are
present in /home/biocbuild/.

Removing these directories means all packages using these resources
will have to re-download the files. This also contributes to an increased
runtime for the builds.

<a name="flushing"></a>
### Flushing the build pipe

Historically we used to 'flush' the whole build pipe by removing all current
packages. (I don't think this is done anymore as of BioC 3.5) When that is
done, the empty PACKAGES, PACKAGES.gzip and PACKAGES.rds must be recreated.

Also, when a CRAN-style dir tree is created by hand, a 'replisting' file must
be present in its root because the biocViews package (use by prepareRepos-*.sh
family) seems to need it.

<a name="biocadmin"></a>
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

- Start R and install BiocManager:

    ./bin/R-3.5
    install.packages("BiocManager")

- Install the packages in /home/biocbuild/pkgs_to_install/ + knitr and
  knitcitations:

    biocadmin@malbec2:~$ ls pkgs_to_install/
    BiocManager  biocViews  DynDoc  graph  README

    install.packages("BiocManager")
    BiocManager::install(c('biocViews','DynDoc','graph', 'knitr', 'knitcitations'))

<a name="mac-and-windows"></a>
## Updating R on Mac OSX and Windows:

Instructions for installing and updating R on Mac OSX are in the HOWTO doc:

  https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-MacOSX-El-Capitan-HOWTO.TXT

Instructions for installing and updating R on Windows are in the HOWTO doc:

  https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-Windows-Server-2012-HOWTO.TXT
