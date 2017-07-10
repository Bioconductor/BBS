Building Bi-Arch R and Packages on Windows
===========================================

Part 1: Building Bi-Arch R
--------------------------

These instructions will tell you how to build an executable installer
of R which will install both 32- and 64-bit R. This is a similar
process to the one that CRAN uses to create the windows binary
they distribute. 

### Getting the source

* Obtain a "Windows-and-Unix ready" source tarball by running one
  of the download-R-*.sh scripts in $HOME/BBS/utils on the main
  build node for the version of R you want to build (example: I want
  to build R-2.14, so I use wilson2 which is the main build node for
  Bioconductor 2.9. Current R-devel is 2.14 so I will run the 
  download-R-devel.sh script).
* Copy this tarball to the Windows machine where you intend to build
  bi-arch R.
  
### Preparing the build machine

Please note that the machine where you build R does not have to be one
of the build nodes in the build system. The end-product of the R build
is a single executable installer that can then be copied to another
machine and run.

The machine should be configured with the following:

* The latest version of [Rtools](http://www.murdoch-sutherland.com/Rtools/).
  Use Rtools' suggestions to modify your PATH, making sure that all Rtools 
  items are first in the PATH.
* The [InnoSetup installer](http://jrsoftware.org/isinfo.php). Be sure and
  install the Unicode version of the installer. Don't install it in the
  default location, instead install in c:\packages\Inno. The 
  [manual](http://cran.fhcrc.org/doc/manuals/R-admin.html#The-Inno-Setup-installer)
  and the MkRules.local script say you can use a custom location here,
  but I find that problematic. It works if the default value, which is
  c:/Packages/inno (note forward slashes) is left in place in the
  MkRules.local file.
* [MiKTeX](http://miktex.org/). I have found that [MiKTeX Portable]
  (http://miktex.org/portable/about) is the most hassle-free to install.
  Be sure the MIKTEX_HOME\miktex\bin directory is in your PATH.
* Create a directory c:\tmp and point the environment variables
  TEMP, TMP, TEMPDIR, and TMPDIR to it (use forward slashes).

### Setting up the build directories.

* Create a root build directory, such as c:\R_build.
* Untar two copies of your source tarball and rename each copy for
  an architecture, for example:


    C:\R_build>tar --no-same-owner -zxf c:\Downloads\R-2.14.r55655.tgz
    C:\R_build>mv R-2.14.r55655 R32
    C:\R_build>tar --no-same-owner -zxf c:\Downloads\R-2.14.r55655.tgz
    C:\R_build>mv R-2.14.r55655 R64
   
* Obtain a copy of R64_Tcl_8-5-8.zip which can be found in 
  the d:\biocbld\bbs-2.9-bioc directory on gewurz, and put it
  in your C:\R_build directory. 

### Build 32-bit R

    C:\R_build>cd R32\src\gnuwin32
    C:\R_build\R32\src\gnuwin32>make all
    C:\R_build\R32\src\gnuwin32>make recommended
    C:\R_build\R32\src\gnuwin32>make bitmapdll
    
I have found that the "make all" step sometimes, needs to be run twice.
The first time, it may end with the following error (experienced in
both R-2.13 and R-2.14). However, sometimes it works fine the first time.

    building package 'compiler'
    installing parsed NAMESPACE files
    installing parsed Rd: base stats utilsmake[3]: *** [methods.Rdts] Error 1
    make[2]: *** [Rdobjects] Error 2
    make[1]: *** [docs] Error 2
    make: *** [all] Error 2

When this error occurs, running "make all" again completes without error.

* Test that R seems to have built correctly:

    C:\R_build\R32>..\..\bin\R

    R version 2.14.0 Under development (unstable) (2011-04-26 r55655)
    Copyright (C) 2011 The R Foundation for Statistical Computing
    ISBN 3-900051-07-0
    Platform: i386-pc-mingw32/i386 (32-bit)

    R is free software and comes with ABSOLUTELY NO WARRANTY.
    You are welcome to redistribute it under certain conditions.
    Type 'license()' or 'licence()' for distribution details.

      Natural language support but running in an English locale

    R is a collaborative project with many contributors.
    Type 'contributors()' for more information and
    'citation()' on how to cite R or R packages in publications.

    Type 'demo()' for some demos, 'help()' for on-line help, or
    'help.start()' for an HTML browser interface to help.
    Type 'q()' to quit R.

    >

### Build 64-bit R

    C:\R_build>cd R64
    C:\R_build\R64>rm -rf Tcl
    C:\R_build\R64>unzip ..\R64_Tcl_8-5-8.zip
    C:\R_build\R64>cd src\gnuwin32
    C:\R_build\R64\src\gnuwin32>cp MkRules.dist MkRules.local
    
* Edit MkRules.local with an editor that understands Unix line
  endings, such as WordPad or vim-nox (Cygwin's version of vim).
* Make the following changes:

1. Change WIN = 32 to WIN = 64
2. Change HOME32 to the root directory of the 32-bit R installation,
   in this case C:/R_build/R32. Use forward slashes.
   
Build 64-bit R as follows:

    C:\R_build\R64\src\gnuwin32>make all
    C:\R_build\R64\src\gnuwin32>make recommended
    C:\R_build\R64\src\gnuwin32>make bitmapdll
    
Test that R seems to have built correctly:

    C:\R_build\R64>..\..\bin\R

    R version 2.14.0 Under development (unstable) (2011-04-26 r55655)
    Copyright (C) 2011 The R Foundation for Statistical Computing
    ISBN 3-900051-07-0
    Platform: x86_64-pc-mingw32/x64 (64-bit)

    R is free software and comes with ABSOLUTELY NO WARRANTY.
    You are welcome to redistribute it under certain conditions.
    Type 'license()' or 'licence()' for distribution details.

      Natural language support but running in an English locale

    R is a collaborative project with many contributors.
    Type 'contributors()' for more information and
    'citation()' on how to cite R or R packages in publications.

    Type 'demo()' for some demos, 'help()' for on-line help, or
    'help.start()' for an HTML browser interface to help.
    Type 'q()' to quit R.

    >


### Build Installer

    C:\R_build\R64\src\gnuwin32>make manuals
    C:\R_build\R64\src\gnuwin32>make rinstaller


Note that the "make manuals" step ends in an error. However, it does
enough so that the installer can be created. Whether the resulting installer
is broken requires further investigation. It does pass the trivial tests
below.

This creates a file in C:\R_build\R64\src\gnuwin32\installer called
R-2.14.0dev-win.exe. (The name of your exe will vary depending on 
which version of R you are building.) This standalone installer can
be copied to another machine and installed there.

### Test Installer

Run the executable created in the previous step. Tell it to install R
in c:\handbuiltR.

Test that it is a bi-arch R. By default, the 32-bit R should be
invoked:

    C:\>c:\handbuiltR\bin\R

    R version 2.14.0 Under development (unstable) (2011-04-26 r55655)
    Copyright (C) 2011 The R Foundation for Statistical Computing
    ISBN 3-900051-07-0
    Platform: i386-pc-mingw32/i386 (32-bit)

    R is free software and comes with ABSOLUTELY NO WARRANTY.
    You are welcome to redistribute it under certain conditions.
    Type 'license()' or 'licence()' for distribution details.

      Natural language support but running in an English locale

    R is a collaborative project with many contributors.
    Type 'contributors()' for more information and
    'citation()' on how to cite R or R packages in publications.

    Type 'demo()' for some demos, 'help()' for on-line help, or
    'help.start()' for an HTML browser interface to help.
    Type 'q()' to quit R.

    >
    
    Save workspace image? [y/n/c]: n

    C:\>c:\handbuiltR\bin\R --arch x64

    R version 2.14.0 Under development (unstable) (2011-04-26 r55655)
    Copyright (C) 2011 The R Foundation for Statistical Computing
    ISBN 3-900051-07-0
    Platform: x86_64-pc-mingw32/x64 (64-bit)

    R is free software and comes with ABSOLUTELY NO WARRANTY.
    You are welcome to redistribute it under certain conditions.
    Type 'license()' or 'licence()' for distribution details.

      Natural language support but running in an English locale

    R is a collaborative project with many contributors.
    Type 'contributors()' for more information and
    'citation()' on how to cite R or R packages in publications.

    Type 'demo()' for some demos, 'help()' for on-line help, or
    'help.start()' for an HTML browser interface to help.
    Type 'q()' to quit R.

    >

Part 2: Building Packages on Bi-Arch R
--------------------------------------

The objective is to find the set of command lines that can be 
used to build, check and install packages, in such a way that only one
command line is needed for each operation, and that the command line will
fail if any one of the architectures built, checked, or installed
fails.

It's worth noting that CRAN seems to use a somewhat different approach.
In their [build code]
(https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/Doc/CRANbuild.zip),
they  have config files called "ForceBiarch", "MergeMultiarch", etc.
Each file contains a list of packages to be installed with the specified
command-line switch.

## Discussion of different options available

### R CMD build

We only use R CMD build to generate a source tarball, so generally
speaking, this command does not need to be architecture-specific. 
However, this command does generate the vignette, and if the
vignette code cannot be run on the default architecture for some reason,
the other architecture should be specified in the command.
We may want to do this if the package is supported on 64-bit
windows but not 32-bit (a rare case, probably).

### R CMD check

The [Writing R Extensions]
(http://cran.r-project.org/doc/manuals/R-exts.html#Checking-packages)
manual suggests a couple of different options for R CMD check:


"Multiple sub-architectures: On systems which support multiple
sub-architectures (principally Windows and Mac OS X), R CMD check
will install and check a package which contains compiled code under
all available sub-architectures. (Use option --force-multiarch to
force this for packages without compiled code, which are otherwise
only checked under the main sub-architecture.) This will run the
loading tests, examples and tests directory under each installed
sub-architecture in turn, and give an error if any fail. Where
environment variables (including PATH(this is needed on Windows
to select the appropriate GTK+ and ‘graphviz’ DLLs.)) need to be
set differently for each sub-architecture, these can be set in
architecture-specific files such as R_HOME/etc/i386/Renviron.site.

"An alternative approach is to use R CMD check --no-multiarch to
check the primary sub-architecture, and then to use something like
R --arch=x86_64 CMD check --extra-arch or
(Windows) /path/to/R/bin/x64/Rcmd check --extra-arch to run for
each additional sub-architecture just the checks (loading, examples,
tests, vignettes) which differ by sub-architecture."

The last approach suggested here would involve two separate command lines
and so would probably not be practical. 

For safety, we should probably use --force-multiarch. Even if a package
has no compiled code, it might depend on other packages with 
architecture-specific code and R CMD check could find problems.

When one of the architectures is not supported, we should
use the "alternative approach" described above (just the first part).

Incidentally, we will definitely need to modify the PATH
variable in an architecture-specific fashion as suggested above.

### R CMD INSTALL

The [Installation and Administration manual]
(http://cran.r-project.org/doc/manuals/R-admin.html#Windows-packages)
says:

"For almost all packages R CMD INSTALL will attempt to install both 32-
and 64-bit builds of a package if run from a 32/64-bit install of R 
on a 64-bit version of Windows. It will report success if the installation
of the architecture of the running R succeeded, whether or not the other
architecture was successfully installed.

"The exceptions are packages with a non-empty configure.win script or which
make use of src/Makefile.win. If configure.win does something appropriate
to both architectures use option --force-biarch (for a small number of CRAN
packages where this is known to be safe and is needed by the autobuilder 
this is the default. Look at the source of tools:::.install_packages for 
the list.) : otherwise R CMD INSTALL --merge-multiarch can be applied to 
a source tarball to merge separate 32- and 64-bit installs. (This can only
be applied to a tarball, and will only succeed if both installs succeed.)"

(NB, the list of CRAN packages referred to in the previous paragraph is here:
AnalyzeFMRI, CORElearn, PearsonDS, RBGL, RNetCDF, RODBC, 
RSiena, Rcpp, Runuran, cairoDevice, foreign, fastICA, glmnet, gstat, 
mvabund, png, proj4, randtoolbox, rngWELL, tcltk2.)

It appears from this that --merge-multiarch would be the best option
for our purposes, because we definitely do not want installs to appear
to succeed even if one architecture was not successfully installed.

However, we need to investigate and figure out if we have packages
where --force-biarch "...is needed by the autobuilder". If we do,
we may have to code a special case into the build system that uses
--force-biarch for these packages, for which we could not rely on the
error code of the INSTALL process to tell us whether it was successful
on both architectures.


## Command Lines

This testing was performed on a 64-bit Windows Server 2008 R2
Enterprise server-based virtual machine.

I have tested all the following command lines, on the following versions
of R:

* 2.13.0 from CRAN binary
* 2.14.0 from CRAN binary (2011-04-25 r55638)
* 2.13.0 from hand-built biarch installer
* 2.14.0 (2011-04-26 r55655) from hand-built biarch installer

Unless otherwise specified, all versions of R produced the same output/result.


Package types and example packages used
---------------------------------------

* Package Type A: No native code (BSgenome)
* Package Type B: Native code but no configure script (Biobase)
* Package Type C: Native code and a configure script (Rsamtools)

When testing with R-2.13, the sources from the BioC 2.8 branch were used.
When testing with R-2.14, the sources from trunk (BioC 2.9) were used.

For each of these package types, we want to try to do each of the following tasks,
using a single command line for each one, for either both architectures or one specified architecture:

* build
* check
* INSTALL

Part I: build
---------------


### Package Type A

#### 1) both archs

    
    R CMD build --keep-empty-dirs --no-resave-data BSgenome & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0



#### 2) i386

(probably not necessary for this package type)


#### 3) x64 

(probably not necessary for this package type)


### Package Type B

#### 1) Both archs

    R CMD build --keep-empty-dirs --no-resave-data Biobase ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

Note: This and other long command lines have been broken into
multiple lines in this document for readability. However, actually
entering the command as a multi-line command causes the return 
code to change, so it is not recommended for obtaining accurate
results.

#### 2) i386

    R --arch i386 CMD build --keep-empty-dirs --no-resave-data Biobase ^
    --install-args=--no-multiarch & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0


#### 3) x64


    R --arch i386 CMD build --keep-empty-dirs --no-resave-data Biobase ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0




### Package Type C

#### 1) Both archs

    R CMD build --keep-empty-dirs --no-resave-data Rsamtools ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0
    

#### 2) i386

    R --arch i386 CMD build --keep-empty-dirs --no-resave-data Rsamtools ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0



#### 3) x64

    R --arch x64 CMD build --keep-empty-dirs --no-resave-data Rsamtools ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0


Part 2: check
-----------------

### Package Type A

#### 1) Both archs

    R CMD check --force-multiarch --no-vignettes --timings ^
    BSgenome_1.20.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 2) i386

The "--arch i386" flag could be omitted in the following command,
since i386 is the default architecture, however in these examples
it is included to make our intention more explicit.
    
    R --arch i386 CMD check --no-multiarch --no-vignettes --timings ^
    BSgenome_1.20.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0


#### 3) x64

    R --arch x64 CMD check --no-multiarch --no-vignettes --timings ^
    BSgenome_1.20.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0


### Package Type B

#### 1) Both archs

    R CMD check --force-multiarch --no-vignettes --timings ^
    Biobase_2.12.1.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 2) i386

    R --arch i386 CMD check --no-multiarch --no-vignettes --timings ^
    Biobase_2.12.1.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0
    
#### 3) x64


    R --arch x64 CMD check --no-multiarch --no-vignettes --timings ^
    Biobase_2.12.1.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0



### Package Type C

#### 1) Both archs

    R CMD check --force-multiarch --no-vignettes --timings ^
    Rsamtools_1.4.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 2) i386

    R --arch i386 CMD check --no-multiarch --no-vignettes ^
    --timings Rsamtools_1.4.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 3) x64

    R --arch x64 CMD check --no-multiarch --no-vignettes ^
    --timings Rsamtools_1.4.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0



Part 3: INSTALL
---------------------

I verified that these did the right thing by looking in the created .zip file
to make sure that only the DLL for the intended architecture(s) was built.

### Package Type A


#### 1) Both archs

    R CMD INSTALL --build --merge-multiarch BSgenome_1.20.0.tar.gz ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0



#### 2) i386
	
Not applicable.




#### 3) x64

Not applicable.

### Package Type B

#### 1) Both archs

    R CMD INSTALL --build --merge-multiarch Biobase_2.12.1.tar.gz ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0


#### 2) i386

    R --arch i386 CMD INSTALL --build --no-multiarch ^
    Biobase_2.12.1.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 3) x64

    R --arch x64 CMD INSTALL --build --no-multiarch ^
    Biobase_2.12.1.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

### Package Type C




#### 1) Both archs

    R CMD INSTALL --build --merge-multiarch Rsamtools_1.4.0.tar.gz ^
    & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0

#### 2) i386

    R --arch i386 CMD INSTALL --build --no-multiarch ^
    Rsamtools_1.4.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0
    

#### 3) x64

    R --arch x64 CMD INSTALL --build --no-multiarch ^
    Rsamtools_1.4.0.tar.gz & echo retcode: %ERRORLEVEL%
    (...)
    retcode: 0
    