# How to Update R on the build machines

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

## Windows

TBA







