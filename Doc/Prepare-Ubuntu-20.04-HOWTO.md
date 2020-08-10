# How to set up an Ubuntu 20.04 system for the daily builds



## 1. Initial setup (from a sudoer account)


Everything in this section must be done **from a sudoer account**.


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


### 1.6 Run Xvfb as a service

Some Bioconductor packages like adSplit, GeneAnswers, or maSigPro have examples
that need access to an X11 display. However, when running `R CMD check` in the
context of the daily builds, no X11 display is available. If R is already
installed, an easy way to reproduce the CHECK error that will happen to the
above packages during the builds is with:

    /path/to/Rscript -e 'png("fig2.png", type="Xlib")'
    #Error in .External2(C_X11, paste0("png::", filename), g$width, g$height,  :
    #  unable to start device PNG
    #Calls: png
    #In addition: Warning message:
    #In png("fig2.png", type = "Xlib") :
    #  unable to open connection to X11 display ''
    #Execution halted

Running Xvfb as a service addresses that.

#### Install Xvfb

    sudo apt-get install xvfb

#### Create /etc/init.d/xvfb

Create `/etc/init.d/xvfb` with the following content:

    #! /bin/sh
    ### BEGIN INIT INFO
    # Provides:          Xvfb
    # Required-Start:    $remote_fs $syslog
    # Required-Stop:     $remote_fs $syslog
    # Default-Start:     2 3 4 5
    # Default-Stop:      0 1 6
    # Short-Description: Loads X Virtual Frame Buffer
    # Description:       This file should be used to construct scripts to be
    #                    placed in /etc/init.d.
    #
    #                    A virtual X server is needed to non-interactively run
    #                    'R CMD build' and 'R CMD check on some BioC packages.
    #                    The DISPLAY variable is set in /etc/profile.d/xvfb.sh.
    ### END INIT INFO
    
    XVFB=/usr/bin/Xvfb
    XVFBARGS=":1 -screen 0 800x600x16"
    PIDFILE=/var/run/xvfb.pid
    case "$1" in
      start)
        echo -n "Starting virtual X frame buffer: Xvfb"
        start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile --background --exec $XVFB -- $XVFBARGS
        echo "."
        ;;
      stop)
        echo -n "Stopping virtual X frame buffer: Xvfb"
        start-stop-daemon --stop --quiet --pidfile $PIDFILE
        sleep 2
        rm -f $PIDFILE
        echo "."
        ;;
      restart)
        $0 stop
        $0 start
        ;;
      *)
        echo "Usage: /etc/init.d/xvfb {start|stop|restart}"
        exit 1
    esac
    
    exit 0

Change permissions on `/etc/init.d/xvfb`:

    sudo chmod 755 /etc/init.d/xvfb

Test the script:

    sudo /etc/init.d/xvfb start
    sudo /etc/init.d/xvfb restart
    sudo /etc/init.d/xvfb stop

#### Create runlevel symlinks from /etc/rc.d/ to /etc/init.d/xvfb

Install `init-system-helpers`:

    sudo apt-get install init-system-helpers

Create the symlinks:

    sudo update-rc.d xvfb defaults

You can see the new symlinks with:

    ls -al /etc/rc*.d/*xvfb

These symlinks make the application behave as a system service,
by starting when the device boots and stopping at shutdown, as
configured by `Default-Start` and `Default-Stop` in the header
of the `/etc/init.d/xvfb` script.

Check current status of the service with:

    service xvfb status

Start/restart/stop the service:

    sudo service xvfb start
    service xvfb status
    
    sudo service xvfb restart
    service xvfb status
    
    sudo service xvfb stop
    service xvfb status

Service will automatically restart after each reboot.

#### Set DISPLAY environment variable in /etc/profile.d/xvfb.sh

Create `/etc/profile.d/xvfb.sh` with the following content:

    ## Set DISPLAY environment variable for use with Xvfb.
    ## See /etc/init.d/xvfb for start / stop configuration.
    
    export DISPLAY=:1.0

Change permissions on `/etc/profile.d/xvfb.sh`:

    sudo chmod 644 /etc/profile.d/xvfb.sh

You'll need to logout and login again to see the `DISPLAY` variable in your
environment. For now `echo $DISPLAY` should show nothing.

#### Reboot

    sudo reboot

#### Test

    service xvfb status  # should be up and running
    echo $DISPLAY        # :1.0
    /path/to/Rscript -e 'png("fig2.png", type="Xlib")'  # no more error!


### 1.7 Install Ubuntu/deb packages

Install with:

    sudo apt-get install <pkg>

#### Always nice to have

    tree
    manpages-dev (includes man pages for the C standard lib)

#### Packages required by the build system itself (BBS)

    python3-minimal
    python3-pip
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
    texlive-font-utils (for epstopdf)
    texlive-pstricks (for pstricks.sty)
    texlive-latex-extra (for fullpage.sty)
    texlive-fonts-extra (for incosolata.sty)
    texlive-bibtex-extra (for unsrturl.bst)
    texlive-science (for algorithm.sty)
    texi2html
    texinfo
    pandoc and pandoc-citeproc (used by CRAN package knitr)
    #ttf-mscorefonts-installer

#### Packages needed by some CRAN and/or BioC packages

    libglu1-mesa-dev (for rgl)
    librsvg2-dev (for rsvg)
    libgmp-dev (for gmp)
    libssl-dev (for openssl and mongolite)
    libsasl2-dev (for mongolite)
    libxml2-dev (for XML)
    libcurl4-openssl-dev (for RCurl)
    mpi-default-dev (for Rmpi)
    libudunits2-dev (for units)
    libv8-dev (for V8)
    libmpfr-dev (for Rmpfr)
    libfftw3-dev (for fftw and fftwtools)
    libmysqlclient-dev (for RMySQL)
    libpq-dev (for RPostgreSQL and RPostgres)
    libmagick++-dev (for magick)
    libgeos-dev (for rgeos)
    libproj-dev (for proj4)
    libgdal-dev (for sf)
    libpoppler-cpp-dev (for pdftools)
    libgtk2.0-dev (for RGtk2)
    jags (for rjags)
    libprotobuf-dev and protobuf-compiler (for protolite)
    cwltool (for Rcwl)
    libglpk-dev (for glpkAPI)

    graphviz and libgraphviz-dev (for RGraphviz)
    libgtkmm-2.4-dev (for HilbertVisGUI)
    libgsl-dev (for all the packages that depend on the GSL)
    libsbml5-dev (for rsbml)
    automake (for RProtoBufLib)
    libnetcdf-dev (for xcms, RNetCDF, etc...)
    libopenbabel-dev (for ChemmineOB)
    ocl-icd-opencl-dev (for gpuMagic)


### 1.8 Install Python 3 modules

#### Python 3 modules needed by some CRAN/Bioconductor packages

Some CRAN/Bioconductor packages interact with Python 3 and use Python
modules. Note that we deliberately install the modules _system wide_
(with `sudo -H pip3 install <module>`). This will make them available to
_all the builds_, independently of which account they will run from (e.g.
biocbuild for BBS or pkgbuild for the Single Package Builder). Since we
only install _trusted_ modules, this should not be a security concern. See
https://askubuntu.com/questions/802544/is-sudo-pip-install-still-a-broken-practice)

    sudo -H pip3 install numpy scipy sklearn h5py pandas mofapy
    sudo -H pip3 install tensorflow tensorflow_probability
    sudo -H pip3 install h5pyd
    sudo -H pip3 install cwltool
    sudo -H pip3 install nbconvert jupyter
    sudo -H pip3 install matplotlib phate

Notes:

- `scipy` is needed by Bioconductor package MOFA but also by the `sklearn`
  module (when `sklearn` is imported and `scipy` is not present, the former
  breaks). However, for some reason, `sudo -H pip3 install sklearn` does not
  install `scipy` and completes successfully even if `scipy` is not installed.

- `numpy`, `sklearn`, `h5py`, and `pandas` are needed by Bioconductor packages
  BiocSklearn and MOFA, and `numpy` is also needed by Bioconductor package
  DChIPRep.

- `mofapy` is needed by Bioconductor package MOFA.

- `tensorflow` is needed by Bioconductor packages scAlign and netReg. Note that
  trying to load the module in a Python 3 session might raise the following error:
    ```
    >>> import tensorflow
    2020-08-08 16:52:56.617223: W tensorflow/stream_executor/platform/default/dso_loader.cc:59] Could not load dynamic library 'libcudart.so.10.1'; dlerror: libcudart.so.10.1: cannot open shared object file: No such file or directory
    2020-08-08 16:52:56.617255: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
    ```
  Even though the message says that the error can be ignored, you can get rid
  of it by installing the libcudart10.1 package:
    ```
    sudo apt-get install libcudart10.1
    ```

- `tensorflow_probability` is needed by Bioconductor package netReg.

- `h5pyd` is needed by Bioconductor package rhdf5client.

- `cwltool` is needed by Bioconductor package Rcwl.

- `nbconvert` and `jupyter` are needed by CRAN package nbconvertR which is
  itself used by Bioconductor package destiny. Note that `jupyter --version`
  should display something like this (as of Aug. 2020):
    ```
    hpages@nebbiolo1:~$ jupyter --version
    jupyter core     : 4.6.3
    jupyter-notebook : 6.1.1
    qtconsole        : 4.7.5
    ipython          : 7.17.0
    ipykernel        : 5.3.4
    jupyter client   : 6.1.6
    jupyter lab      : not installed
    nbconvert        : 5.6.1
    ipywidgets       : 7.5.1
    nbformat         : 5.0.7
    traitlets        : 4.3.3
    ```
  It's ok if jupyter lab is not installed but everything else should be.

- `matplotlib` and `phate` are needed by CRAN package phateR which is itself
  used by Bioconductor package phemd.

#### Python 3 modules needed by the Single Package Builder only

`virtualenv` is used by the Single Package Builder. Despite python3 shipping
with `venv`, `venv` is not sufficient. The SPB must use `virtualenv`.

    sudo -H pip3 install virtualenv


### 1.9 Logout and login again as biocbuild

Everything in the next section must be done from the biocbuild account.



## 2. Configure the Bioconductor software builds


Everything in this section must be done **from the biocbuild account**.


### 2.1 Check connectivity with central builder

Needed only if the machine is being configured as a secondary build node.

#### Install biocbuild RSA private key

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    biocbuild@nebbiolo1:~$ ls -l .BBS/id_rsa
    -r-------- 1 biocbuild biocbuild 883 Aug  6 17:21 .BBS/id_rsa

#### Check that you can ping the central builder

Check that you can ping the central builder. Depending on whether the
node you're ping'ing from is within RPCI's DMZ or not, use its short or
long (i.e. hostname+domain) hostname. For example:

    ping malbec1                                 # from within RPCI's DMZ
    ping malbec1.bioconductor.org                # from anywhere else

#### Check that you can ssh to the central builder

    ssh -i .BBS/id_rsa malbec1                   # from within RPCI's DMZ
    ssh -i .BBS/id_rsa malbec1.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec1.bioconductor.org port 22: Connection timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

#### Check that you can send HTTPS requests to the central builder

    curl https://malbec1                         # from within RPCI's DMZ
    curl https://malbec1.bioconductor.org        # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to malbec1.bioconductor.org:443

Contact the IT folks at RPCI if that's the case (see above).

More details on https implementation in `BBS/README.md`.


### 2.2 Clone BBS git tree and create bbs-3.y-bioc directory structure

Must be done from the biocbuild account.

#### Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS

#### Create bbs-x.y-bioc directory structure

For example, for the BioC 3.12 software builds:

    cd
    mkdir bbs-3.12-bioc
    cd bbs-3.12-bioc
    mkdir rdownloads log


### 2.3 Install R

Must be done from the biocbuild account.

#### Get R source from CRAN

Download and extract R source tarball from CRAN in `~/bbs-3.12-bioc/rdownloads`.
The exact tarball to download depends on whether we're configuring the
release or devel builds.

For example:

    cd ~/bbs-3.12-bioc/rdownloads
    wget https://cran.r-project.org/src/base/R-4/R-4.0.2.tar.gz
    tar zxvf R-4.0.2.tar.gz

#### Configure and compile R

    cd ~/bbs-3.12-bioc/
    mkdir R    # possibly preceded by mv R R.old if previous installation
    cd R
    ../rdownloads/R-4.0.2/configure --enable-R-shlib
    make -j20  # takes about 5 min.
    cd etc
    ~/BBS/utils/R-fix-flags.sh

Do NOT run `make install`!

#### Testing

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


### 2.4 Add crontab entries for nightly builds

Must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    00 16 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.12/bioc/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.12-bioc/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run
before doing so (great opportunity to catch up on your favorite Netflix
show and relax).



## 3. Install additional stuff for Bioconductor packages with special needs


Everything in this section must be done **from a sudoer account**.


### 3.1 Install BibTeX style humannat.bst

Required by Bioconductor package destiny.

Used to be part of earlier Ubuntu versions (in texlive-bibtex-extra) but
is no longer here in Ubuntu 20.04.

Install with:

    cd /usr/share/texlive/texmf-dist/bibtex/bst
    sudo mkdir beebe
    cd beebe
    sudo wget https://ctan.org/tex-archive/biblio/bibtex/contrib/misc/humannat.bst
    sudo texhash


TO BE CONTINUED

