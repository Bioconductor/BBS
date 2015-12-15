# How to Update R on the build machines

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

`curl -LO <URL>`

### Untarring

Untar in the `~src` directory. 
If the directory created by untarring does not have
a descriptive name (containing a date or svn revision
number) then please rename accordingly.

Directory should have a name like `R-3.2.r67960`
or `R-devel-20151026`.

### Building

If the machine you are on builds Bioconductor 3.3,
go to the `~/bbs-3.3-bioc` directory.
If there is an `R.old` directory, remove it.
If there is an `R` directory, rename it to
`R.old`. That way if there is something really
wrong with the new R, you can switch back 
to the old one just by renaming `R.old` to `R`.
Create an `R` directory and `cd` to it.

Build R as follows.

    ~/src/<DIRECTORY_WHERE_R_WAS_UNTARRED>/configure --enable-R-shlib
    make 

Instead of `make` you can also do `make -j` to use
all cores or `make -jN` to use `N` cores.

### After building

Go to the `etc` directory and then run:

    ~/BBS/utils/R-fix-flags.sh 

This sets the C/C++ compilation flags appropriately
for the build system (i.e. showing additional
warnings useful for package developers).

Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")

If you are on a devel build machine, do this:

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

If you are on a devel build machine, do this:

    useDevel()



## Windows

### Where to get R

 * Release: [https://cran.r-project.org/bin/windows/](https://cran.r-project.org/bin/windows/)
 * Patched: [https://cran.r-project.org/bin/windows/base/rpatched.html](https://cran.r-project.org/bin/windows/base/rpatched.html)
 * Devel: [https://cran.r-project.org/bin/windows/base/rdevel.html](https://cran.r-project.org/bin/windows/base/rdevel.html)

### Before Downloading

If you are building Bioconductor 3.3, go to
`X:\biocbld\bbs-3.3-bioc` (where `X` is the appropriate
drive letter).
If there is an `R.old` directory, remove it.
If there is an `R` directory, rename it to `R.old`.



### Downloading

 You can download R from within a browser, which
 means it will be downloaded to
 `c:\Users\biocbuild\Downloads`.

### Installing

You can double-click the .exe you just downloaded.
This runs an installation wizard. You can pick all
the default settings except that you want to install
to `X:\biocbld\bbs-Y.Z-bioc\R` where `X` is the
appropriate drive letter and `Y.Z` is the version
of Bioconductor.

You can also uncheck the options for creating
desktop shortcuts and associating R files with
R.

Run R and install Bioconductor:

    source("https://bioconductor.org/biocLite.R")

If you are on a devel build machine, do this:

    useDevel()


