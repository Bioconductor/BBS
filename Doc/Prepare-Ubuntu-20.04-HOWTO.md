# How to set up an Ubuntu 20.04 system for the daily builds



## 1. Initial setup (from a sudoer account)


### 1.1 Standalone vs non-standalone builder

The machine could either be configured as a _standalone_ builder or as
a _non-standalone_ builder. A _non-standalone_ builder is a build node that
participates to builds run by a group of build machines. For example the
BioC 3.11 software builds are currently run by 3 nodes (as of Aug 2020):
https://bioconductor.org/checkResults/3.11/bioc-LATEST/

When part of a group of build machines, one machine must be setup as the
_central_ builder (a.k.a. _primary node_) e.g. malbec2 in the case of the
BioC 3.11 software builds. All the other machines (called _secondary nodes_)
must be able to communicate (SSH and HTTP/S) with the central builder.
Note that this communication generates some fair amount of data transfer
back and forth between each secondary node and the central builder (> 5GB
every day on normal days).


### 1.2 Check system requirements

For a _central_ builder:

- At least 800GB of disk space

- At least 32 cores

- At least 48GB of RAM

For a _secondary node_ or _standalone_ builder:

- At least 400GB of disk space

- At least 20 cores

- At least 32GB of RAM

These requirements are _very_ approximate and tend to increase over time (as
Bioconductor grows). The above numbers reflect the current state of affairs
as of Aug 2020.


### 1.3 Apply any pending system updates and reboot

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot


### 1.4 Run Apache server as service

Required only for a standalone or central builder.

Install Apache server:

    sudo apt-get install apache2

Start it:

    sudo service apache2 start

Check its status:

    service apache2 status

Service will automatically restart after each reboot.


### 1.5 Create the biocbuild account

    sudo adduser biocbuild

This should be set up as a regular account. In particular it should NOT have
sudo privileges.

Install devteam member public keys in biocbuild account.

TESTING: Logout and try to login again as biocbuild. Then logout and login
again as before (sudoer account).


### 1.6 Run Xvfb as service

See Prepare-Ubuntu-HOWTO.TXT


### 1.7 Install Ubuntu/deb packages

Install with:

    sudo apt-get install <pkg>

#### Always nice to have

    tree
    manpages-dev (includes man pages for the C standard lib)

#### Packages required by the build system itself (BBS)

    python3-minimal
    git

#### Packages required to compile R

Strictly required:

    build-essential
    gfortran
    libreadline-dev
    libx11-dev
    libxt-dev
    zlib1g-dev
    libbz2-dev
    liblzma-dev
    libpcre2-dev
    libcurl4-openssl-dev

Optional (still possible to compile R without these packages but some
capabilities will be missing):

    gobjc
    libpng-dev
    libjpeg-dev
    libtiff-dev
    libcairo2-dev
    libicu-dev
    tcl-dev
    tk-dev
    default-jdk

#### Packages needed to build vignettes and reference manuals

    texlive
    texlive-latex-extra (for fullpage.sty)
    texlive-fonts-extra (for incosolata.sty)
    texlive-bibtex-extra (for unsrturl.bst)
    texlive-science (for algorithm.sty)
    texi2html
    texinfo
    pandoc and pandoc-citeproc (used by CRAN package knitr)
    #ttf-mscorefonts-installer

#### Packages needed by some CRAN and/or BioC packages

    automake (for RProtoBufLib)
    libssl-dev (for openssl)
    libxml2-dev (for XML)
    libcurl4-openssl-dev (for RCurl)
    libgtk2.0-dev (for RGtk2)
    libnetcdf-dev (for xcms, RNetCDF, etc...)
    graphviz and libgraphviz-dev (for RGraphviz)
    libgsl-dev (for all the packages that depend on the GSL)
    libmysqlclient-dev (for RMySQL)

    #libglu1-mesa-dev (for rgl)
    #libopenbabel-dev (for ChemmineOB)
    #libgmpv4-dev (for gmp)
    #libncurses-dev
    #jags (for rjags)
    #pandoc-citeproc (for dagLogo)
    #libmpfr-dev (for Rmpfr)
    #libudunits2-dev (for ggraph)
    #libv8-3.14-dev (for DiagrammeRsvg)
    #libapparmor-dev (for sys)
    #protobuf-compiler (for protolite)
    #libpq-dev (for RPostgreSQL)
    #ocl-icd-opencl-dev (for gpuMagic)

#### No longer needed (to be confirmed)

Remove this last subsection after confirmation.

    #libmagick++-dev (for EBImage)
    #libpq-dev (for RdbiPgSQL)
    #libhdf5-dev (for ncdfFlow)


### 1.8 Logout and login again as biocbuild

From now on everything must be done from the biocbuild account.



## 2. Check connectivity with central builder


Needed only if the machine is being configured as a secondary build node.

Must be done from the biocbuild account.

### 2.1 Install biocbuild RSA private key

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    biocbuild@nebbiolo1:~$ ls -l .BBS/id_rsa
    -r-------- 1 biocbuild biocbuild 883 Aug  6 17:21 .BBS/id_rsa

### 2.2 Check that you can ping the central builder

Check that you can ping the central builder. Depending on whether the
node you're ping'ing from is within RPCI's DMZ or not, use its short or
long (i.e. hostname+domain) hostname. For example:

    ping malbec1                                 # from within RPCI's DMZ
    ping malbec1.bioconductor.org                # from anywhere else

### 2.3 Check that you can ssh to the central builder

    ssh -i .BBS/id_rsa malbec1                   # from within RPCI's DMZ
    ssh -i .BBS/id_rsa malbec1.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec1.bioconductor.org port 22: Connection timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

### 2.4 Check that you can send HTTPS requests to the central builder

    curl https://malbec1                         # from within RPCI's DMZ
    curl https://malbec1.bioconductor.org        # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to malbec1.bioconductor.org:443 

Contact the IT folks at RPCI if that's the case (see above).

More details on https implementation in `BBS/README.md`.



## 3. Clone BBS git tree and create bbs-3.y-bioc directory structure


Must be done from the biocbuild account.

### 3.1 Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS

### 3.2 Create bbs-x.y-bioc directory structure

For example, for the BioC 3.12 software builds:

    cd
    mkdir bbs-3.12-bioc
    cd bbs-3.12-bioc
    mkdir rdownloads log



## 4. Install R


Must be done from the biocbuild account.


### 4.1 Get R source from CRAN

Download and extract R source tarball from CRAN in `~/bbs-3.12-bioc/rdownloads`.
The exact tarball to download depends on whether we're configuring the
release or devel builds.

For example:

    cd ~/bbs-3.12-bioc/rdownloads
    wget https://cran.r-project.org/src/base/R-4/R-4.0.2.tar.gz
    tar zxvf R-4.0.2.tar.gz


### 4.2 Configure and compile R

    cd ~/bbs-3.12-bioc/
    mkdir R    # possibly preceded by mv R R.old if previous installation
    cd R
    ../rdownloads/R-4.0.2/configure --enable-R-shlib
    make -j20  # takes about 5 min.
    cd etc
    ~/BBS/utils/R-fix-flags.sh

Do NOT run `make install`!


### 4.3 Testing

Start R:

    cd ~/bbs-3.12-bioc/
    R/bin/R

Then from R:

    # --- check capabilities ---

    capabilities()  # all should be TRUE except aqua and profmem
    X11()           # nothing visible should happen

    # --- install a few CRAN packages ---

    # with C++ code:
    install.packages("Rcpp", repos="https://cran.r-project.org")
    # with Fortran code:
    install.packages("minqa", repos="https://cran.r-project.org")
    # a possibly difficult package:
    install.packages("rJava", repos="https://cran.r-project.org")
    # another possibly difficult package:
    install.packages("RGtk2", repos="https://cran.r-project.org")
    # always good to have:
    install.packages("devtools", repos="https://cran.r-project.org")

    # --- install a few Bioconductor packages ---

    install.packages("BiocManager", repos="https://cran.r-project.org")
    library(BiocManager)
    ## ONLY if release and devel are using the same version of R:
    BiocManager::install(version="devel")

    BiocManager::install("BiocCheck")
    BiocManager::install("rtracklayer")
    BiocManager::install("VariantAnnotation")
    BiocManager::install("rhdf5")



## 5. Add crontab entries for nightly builds


Must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    00 16 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.12/bioc/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.12-bioc/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run
before doing so (great opportunity to catch up on your favorite Netflix
show and relax).



## 6. Additional stuff to install for packages with special needs


Must be done from the biocbuild account.

TODO

