# How to Update R on the build machines

*NOTE*: Throughout this document, `$BIOC_VERSION` 
(or `%BIOC_VERSION%` on Windows) is
used to represent the Bioconductor version, to make
commands more copy-pastable (assuming `$BIOC_VERSION`
is defined).

## When to update

Make sure software builds are not running or about
to run in the next 30 minutes or so.

Make sure data/experiment builds are not running
(Wed/Sat during the day).

Don't update after the software builds run
but before the data/experiment builds run.
(The data/experiment builds depend on
the software builds having run first.)



## Linux

Note that we build R *from source* on Linux, we do not
install a package for a Linux distribution
(i.e. we don't use `apt-get on Ubuntu).

### Where to find R

#### R-devel

[https://stat.ethz.ch/R/daily/](https://stat.ethz.ch/R/daily/)

#### Release

[https://cran.r-project.org/](https://cran.r-project.org/)

#### Alpha, beta, RC, etc.

[https://cran.r-project.org/src/base-prerelease/](https://cran.r-project.org/src/base-prerelease/)

### Downloading


As the `biocbuild` user, download to `~/public_html/BBS`
on the Linux build node.

The file you download should have a descriptive name, including
a version or a date, such as `R-3.2.r67960.tar.gz` or
`R-devel_2015-11-08.tar.gz`. If the file does not have such
a name (i.e., it's just caled R-devel.tar.gz) please rename
it after downloading.

Download with 

    curl -LO <URL>

### Untarring

Untar in the `~src` directory. 
If the directory created by untarring does not have
a descriptive name (containing a date or svn revision
number) then please rename accordingly.

Directory should have a name like `R-3.2.r67960`
or `R-devel-20151026`.

### Building


    cd ~/bbs-$BIOC_VERSION-bioc
    # if R.old exists:
    mv R.old R.deleteme 
    nohup rm -rf R.deleteme > /dev/null 2>&1 & # takes some time
    # if R directory exists:
    mv R R.old
    mkdir R    
    cd R


Build R as follows.

    ~/src/<DIRECTORY_WHERE_R_WAS_UNTARRED>/configure --enable-R-shlib
    make 

Instead of `make` you can also do `make -j` to use
all cores or `make -jN` to use `N` cores.

### After building

Run a script to fix compilation flags:

    cd ./etc
    ~/BBS/utils/R-fix-flags.sh 

This sets the C/C++ compilation flags appropriately
for the build system (i.e. showing additional
warnings useful for package developers).

Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")

If you are on a devel build machine (and not running
R-devel), do this:

    useDevel()



## Mac


### Before downloading

R is installed in `/Library/Frameworks/R.framework`.
Go to `/Library/Frameworks`.
If `R.framework.old` exists, remove it.
If `R.framework` exists, rename it to `R.framework.old`.


### Where to get R

Release versions can be found at
[https://cran.r-project.org/bin/macosx/](https://cran.r-project.org/bin/macosx/).

All other versions (devel, beta, etc.) are at
[http://r.research.att.com/](http://r.research.att.com/).

Download to the `~/Downloads` directory (as `biocbuild`).

Before downloading, if a file of the same name
that you are about to download already exists,
rename it to the same name with the date appended,
i.e., rename `R-3.2-branch-mavericks-signed.pkg`
to `R-3.2-branch-mavericks-signed.pkg.20150721`.
Download the file with 

    curl -LO <URL>

### Installing

sudo installer -pkg <NAME_OF_PKG_FILE> -target /

### After installing

Go to `/Library/Frameworks/R.framework/Versions/Current/Resources/etc`.

#### Mavericks

Run

    ~/BBS/utils/mavericks-R-fix-flags.sh 

#### Snow Leopard

    ~/BBS/utils/snow-leopard-R-fix-flags.sh 


### After installation, part 2.

Also, install the Cairo binary package. This should be available
in `~/Downloads`:

    R CMD INSTALL Cairo_*.tgz

If you don't do this, the build system will try and
fail to install this package from source.

Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")

If you are on a devel build machine (and not running
R-devel), do this:

    useDevel()



## Windows

In this section %DRIVELETTER% refers to
the data drive (D: on moscato1, E: on moscato2;
in cloud deployments probably everything will be
on the C: drive).

Install as the `biocbuild` user.

### Where to get R

 * Release: [https://cran.r-project.org/bin/windows/](https://cran.r-project.org/bin/windows/)
 * Patched: [https://cran.r-project.org/bin/windows/base/rpatched.html](https://cran.r-project.org/bin/windows/base/rpatched.html)
 * Devel: [https://cran.r-project.org/bin/windows/base/rdevel.html](https://cran.r-project.org/bin/windows/base/rdevel.html)

### Before Downloading


    cd %DRIVELETTER%:\biocbld\bbs-%BIOC_VERSION%-bioc 
    rem If there is an R.old directory:
    mv R.old R.deleteme
    rem This will take some time:
    nohup rm -rf R.deleteme > /dev/null 2>&1 &
    rem If there is an R directory:
    mv R R.old

### Downloading

 You can download R from within a browser, which
 means it will be downloaded to
 `c:\Users\biocbuild\Downloads`.

### Installing

You can double-click the .exe you just downloaded.
But to run it from the command line, do:

    R-devel-win.exe /SILENT /DIR=%DRIVELETTER%:\biocbld\bbs-%BIOC_VERSION%-bioc\R /NOICONS

If you run by double-clicking, be sure and choose
`%DRIVELETTER%:\biocbld\bbs-Y.Z-bioc\R` as the
destination directory. Choose to NOT create a
start menu item and to NOT associate .R files
with R.


Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")

If you are on a devel build machine (and not
running R-devel), do this:

    useDevel()

#### R for Single Package Builder

SPB has its own R on windows
when you update R-devel, you need to update the pkgbuild one as well.
Do this as the `pkgbuild` user. The steps are basically the same as
above except R is installed in `X:\packagebuilder` (where `X`
is the appropriate drive letter).


