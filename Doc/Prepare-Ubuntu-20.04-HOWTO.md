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


### 1.4 Create the biocbuild account

    sudo adduser biocbuild

This should be set up as a regular account. In particular it should NOT have
sudo privileges.

Install devteam member public keys in biocbuild account.

TESTING: Logout and try to login again as biocbuild. Then logout and login
again as before (sudoer account).


### 1.5 Run Xvfb as a service

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


### 1.6 Install Ubuntu/deb packages

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
    texlive-luatex (for luatex85.sty)
    texlive-lang-european (for language definition files e.g. swedish.ldf)
    texi2html
    texinfo
    pandoc and pandoc-citeproc (used by CRAN package knitr)
    biber
    #ttf-mscorefonts-installer

#### Packages needed by some CRAN and/or BioC packages

    libglu1-mesa-dev (for rgl)
    librsvg2-dev (for rsvg)
    libgmp-dev (for gmp)
    libssl-dev (for openssl and mongolite)
    libsasl2-dev (for mongolite)
    libxml2-dev (for XML)
    libcurl4-openssl-dev (for RCurl and curl)
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
    libglpk-dev (for glpkAPI and to compile igraph with GLPK support)

    graphviz and libgraphviz-dev (for RGraphviz)
    libgtkmm-2.4-dev (for HilbertVisGUI)
    libgsl-dev (for all the packages that depend on the GSL)
    libsbml5-dev (for rsbml)
    automake (for RProtoBufLib)
    libnetcdf-dev (for xcms, RNetCDF, etc...)
    libopenbabel-dev (for ChemmineOB)
    clustalo (LowMACA)
    ocl-icd-opencl-dev (for gpuMagic)


### 1.7 Install Python 3 modules

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


### 1.8 Run Apache server as a service

Required only for a standalone or central builder.

Install Apache server:

    sudo apt-get install apache2

Start it:

    sudo service apache2 start

Check its status:

    service apache2 status

Service will automatically restart after each reboot.


### 1.9 Logout and login again as biocbuild

Almost everything in the next section must be done from the biocbuild account.



## 2. Configure the Bioconductor software builds


### 2.1 Set Apache server DocumentRoot

Required only for a standalone or central builder.

Create `/home/biocbuild/public_html/BBS` from the biocbuild account:

    cd
    mkdir -p public_html/BBS

Then edit `/etc/apache2/sites-enabled/000-default.conf` **from a sudoer
account**. First make a copy of the original file:

    cd /etc/apache2/sites-enabled
    sudo cp -i 000-default.conf 000-default.conf.original

and make the following changes:

- Set `DocumentRoot` to `/home/biocbuild/public_html`

- Add the following lines inside the `VirtualHost` section:
    ```
    <VirtualHost *:80>
            ...

            # Add the 5 lines below.
            <Directory /home/biocbuild/public_html/>
                    Options Indexes FollowSymLinks
                    AllowOverride None
                    Require all granted
            </Directory>

    </VirtualHost>
    ```

Restart the Apache server:

    sudo service apache2 restart

TESTING: From any account on the machine, you should be able to do:

    # This should print an HTML document showing the index
    # of the /home/biocbuild/public_html/BBS/ folder:
    curl http://localhost/BBS/



### 2.2 Check connectivity with central builder

Needed only if the machine is being configured as a secondary build node.

Must be done from the biocbuild account.

#### Check that you can ping the central builder

Check that you can ping the central builder. Depending on whether the
node you're ping'ing from is within RPCI's DMZ or not, use the central
builder's short or long (i.e. hostname+domain) hostname. For example:

    ping malbec1                                   # from within RPCI's DMZ
    ping malbec1.bioconductor.org                  # from anywhere else

#### Install biocbuild RSA private key

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    biocbuild@nebbiolo1:~$ ls -l .BBS/id_rsa
    -r-------- 1 biocbuild biocbuild 883 Aug  6 17:21 .BBS/id_rsa

#### Check that you can ssh to the central builder

    ssh -i ~/.BBS/id_rsa malbec1                   # from within RPCI's DMZ
    ssh -i ~/.BBS/id_rsa malbec1.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec1.bioconductor.org port 22: Connection timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

#### Check that you can send HTTPS requests to the central builder

    curl https://malbec1                           # from within RPCI's DMZ
    curl https://malbec1.bioconductor.org          # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to malbec1.bioconductor.org:443

Contact the IT folks at RPCI if that's the case (see above).

More details on https implementation in `BBS/README.md`.


### 2.3 Clone BBS git tree and create bbs-3.y-bioc directory structure

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


### 2.4 Install R

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

#### Basic testing

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

#### Install BiocManager + packages required by SPB and book builds

From R:

    install.packages("BiocManager", repos="https://cran.r-project.org")
    library(BiocManager)

    ## IMPORTANT: Switch to "devel" ONLY if installing R for the devel builds
    ## and if BioC devel uses the same version of R as BioC release!
    BiocManager::install(version="devel")

    BiocManager::install("BiocCheck")    # required by SPB
    BiocManager::install("LTLA/rebook")  # required by book builds

    # always good to have:
    install.packages("devtools", repos="https://cran.r-project.org")

#### [OPTIONAL] More testing

From R:

    BiocManager::install("rtracklayer")
    BiocManager::install("VariantAnnotation")
    BiocManager::install("rhdf5")


### 2.5 Add software builds to biocbuild crontab

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


### 3.2 Install ensembl-vep

Required by Bioconductor packages ensemblVEP and MMAPPR2.

Complete installation instructions are at
https://www.ensembl.org/info/docs/tools/vep/script/vep_download.html

#### Install Perl modules

According to ensembl-vep README, the following Perl modules are required:

    ## Needed by both ensemblVEP and MMAPPR2:
    sudo cpan install Archive::Zip
    sudo cpan install File::Copy::Recursive
    sudo cpan install DBI
    sudo cpan install DBD::mysql  # MySQL client needed!
    
    ## Needed by MMAPPR2 only:
    sudo cpan install -f XML::DOM::XPath  # -f to force install despite tests failing
    sudo cpan install Bio::SeqFeature::Lite
    sudo apt-get install libhts-dev  # HTSlib
    cd /usr/lib
    sudo ln -s x86_64-linux-gnu/libhts.so
    sudo ln -s x86_64-linux-gnu/libhts.a
    sudo cpan install Bio::DB::HTS::Tabix

#### Install ensembl-vep

    cd /usr/local
    sudo git clone https://github.com/Ensembl/ensembl-vep.git
    cd ensembl-vep
    #sudo git checkout release/100  # select desired branch

    # Avoid the hassle of getting HTSlib to compile because ensemblVEP and
    # MMAPPR2 pass 'R CMD build' and 'R CMD check' without that and that's
    # all we care about.
    sudo perl INSTALL.pl --NO_HTSLIB
    # When asked if you want to install any cache files - say no
    # When asked if you want to install any FASTA files - say no
    # When asked if you want to install any plugins - say no

#### Edit /etc/profile

In `/etc/profile` append `/usr/local/ensembl-vep` to `PATH`.
Note that the `/etc/profile` file has read-only permissions (factory
settings). To save changes you will need to force save, e.g., in the
`vi` editor this is `w!`.

Logout and login again so that the changes to `/etc/profile` take effect.

#### Testing

From the biocbuild account:

    cd ~/bbs-3.12-bioc/meat
    ../R/bin/R CMD build ensemblVEP
    ../R/bin/R CMD check ensemblVEP_X.Y.Z.tar.gz  # replace X.Y.Z with current version
    ../R/bin/R CMD build MMAPPR2
    ../R/bin/R CMD check MMAPPR2_X.Y.Z.tar.gz     # replace X.Y.Z with current version


### 3.3 Install ViennaRNA

Required by Bioconductor package GeneGA.

#### Download and install

    ## No Ubuntu package for 20.04 yet (as of Aug. 2020) but the package for
    ## Ubuntu 19.04 seems to work alright.
    wget https://www.tbi.univie.ac.at/RNA/download/ubuntu/ubuntu_19_04/viennarna_2.4.14-1_amd64.deb
    sudo dpkg -i viennarna_2.4.14-1_amd64.deb

#### Testing

From the biocbuild account:

    which RNAfold  # /usr/bin/RNAfold

Finally try to build the GeneGA package:

    cd ~/bbs-3.12-bioc/meat
    ../R/bin/R CMD build GeneGA


### 3.4 Install ImmuneSpace credentials

Required by Bioconductor package ImmuneSpaceR.

#### Edit /etc/profile

In `/etc/profile` add:

    export ISR_login=bioc@immunespace.org
    export ISR_pwd=1notCRAN

#### Testing

From the biocbuild account:

    cd ~/bbs-3.12-bioc/meat
    ../R/bin/R CMD build ImmuneSpaceR


### 3.5 Install Perl module XML::Simple

Required by Bioconductor package LowMACA.

#### Install

    sudo cpan install XML::Simple

#### Testing

From the biocbuild account:

    cd ~/bbs-3.12-bioc/meat
    ../R/bin/R CMD build LowMACA


### 3.6 Install ROOT

Required by Bioconductor package xps.

xps wants ROOT 5, not 6.

ROOT supports 2 installation methods: "location independent" and "fix
location". We will do "location independent" installation.

#### Prerequisite

    sudo apt-get install cmake
    sudo apt-get install libxpm-dev

#### Build

    cd ~/sandbox
    ## Unfortunately ROOT v5-34-00 fails to compile on Ubuntu 20.04 so
    ## we install ROOT v6-22-00 (current stable release as of July 2020).
    ## We know that xps wants ROOT 5, not 6, so even though compiling
    ## ROOT v6-22-00 is succesful we kind of anticipate bad things to
    ## happen later.
    #git clone --branch v5-34-00-patches https://github.com/root-project/root.git root_src
    git clone --branch v6-22-00-patches https://github.com/root-project/root.git root_src
    mkdir root_build
    cd root_build
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/root -Dgnuinstall=ON -Dfortran=OFF -Dmysql=OFF -Dsqlite=OFF ../root_src
    cmake --build . -- -j20  # takes about 10 min.

#### Install

    sudo cmake --build . --target install

Try to start a ROOT interactive session:

    source bin/thisroot.sh
    root  # then quit the session with .q

#### Edit /etc/profile

In `/etc/profile` add the following line (before the `PATH` and
`DYLD_LIBRARY_PATH` lines):

    export ROOTSYS="/usr/local/root"  # do NOT set ROOTSYS, it will break
                                      # xps configure script!

Also append `$ROOTSYS/bin` to `PATH` and `$ROOTSYS/lib/root` to
`DYLD_LIBRARY_PATH`.

#### Testing

From the biocbuild account:

    which root-config      # /usr/local/root/bin/root-config
    root-config --version  # 6.22/01

Finally try to install the xps package:

    cd ~/bbs-3.12-bioc/meat
    ../R/bin/R CMD INSTALL xps

As expected, this currently fails (with xps 1.49.0):

    * installing to library ‘/home/biocbuild/bbs-3.12-bioc/R/library’
    * installing *source* package ‘xps’ ...
    ** using staged installation
    checking for gcc... gcc
    checking for C compiler default output file name... a.out
    checking whether the C compiler works... yes
    checking whether we are cross compiling... no
    checking for suffix of executables...
    checking for suffix of object files... o
    checking whether we are using the GNU C compiler... yes
    checking whether gcc accepts -g... yes
    checking for gcc option to accept ANSI C... none needed
    checking how to run the C preprocessor... gcc -E
    checking for gcc... (cached) gcc
    checking whether we are using the GNU C compiler... (cached) yes
    checking whether gcc accepts -g... (cached) yes
    checking for gcc option to accept ANSI C... (cached) none needed
    found ROOT version 6.22/01 in directory /usr/local/root
    ** libs
    ** arch -
    Unknown argument "--dicttype"!
    Usage: root-config [--prefix[=DIR]] [--exec-prefix[=DIR]] [--version] [--cflags] [--auxcflags] [--ldflags] [--new] [--nonew] [--libs] [--glibs] [--evelibs] [--bindir] [--libdir] [--incdir] [--etcdir] [--tutdir] [--srcdir] [--noauxcflags] [--noauxlibs] [--noldflags] [--has-<feature>] [--arch][--python-version] [--python2-version] [--python3-version] [--cc] [--cxx] [--f77] [--ld ] [--help]
    c++ -I/usr/local/root/include -O2 -Wall -fPIC -pthread -std=c++11 -m64 -I/usr/local/root/include/root -c TMLMath.cxx
    TMLMath.cxx:1111: warning: "xmax" redefined
     1111 | #define xmax  2.5327372760800758e+305
          |
    ...
    ...
    c++ -I/usr/local/root/include -O2 -Wall -fPIC -pthread -std=c++11 -m64 -I/usr/local/root/include/root -c rwrapper.cxx
    Generating dictionary xpsDict.cxx...
    rootcint: error while loading shared libraries: libRIO.so: cannot open shared object file: No such file or directory
    make: *** [Makefile:112: xpsDict.cxx] Error 127
    ERROR: compilation failed for package ‘xps’
    * removing ‘/home/biocbuild/bbs-3.12-bioc/R/library/xps’



## 4. Known issues


### 4.1 curl SSLv3 alert handshake failure

Affects several Bioconductor packages:

#### MouseFM and martini

An Ensembl server misconfiguration + increased security level
in Ubuntu 20.04 + a bug in OpenSSL 1.1.1 cause the examples in
`?MouseFM::annotate_consequences` and some unit test in martini to fail:

    library(curl)
    
    ## At a very low level the examples in `?MouseFM::annotate_consequences` do:
    url <- "https://rest.ensembl.org/vep/mouse/id"
    curl_fetch_memory(url)
    #Error in curl_fetch_memory(url) :
    #  error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure
    
    ## The code in test_snp2gene.R in martini does:
    url <- "https://rest.ensembl.org/taxonomy/id/9606?content-type=application/json"
    curl_fetch_memory(url)
    #Error in curl_fetch_memory(url) :
    #  error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure

See https://github.com/Ensembl/ensembl-rest/issues/427 for the details.

Easy way to reproduce:

    curl https://rest.ensembl.org  # works fine on Ubuntu < 20.04

#### AnnotationHubData

Internally `test_GencodeFasta()` does:

    library(RCurl)
    getURL("https://www.gencodegenes.org/human/releases")
    #Error in function (type, msg, asError = TRUE)  :
    #  error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure

This causes AnnotationHubData's unit tests to fail.

Easy way to reproduce:

    curl https://www.gencodegenes.org  # works fine on Ubuntu < 20.04

I reported the issue by filling a form here https://www.gencodegenes.org/pages/contact.html on Aug 20, 2020. Message sent:

--------------------------------------------------------------------------
Subject: curl SSLv3 alert handshake failure when accessing the
gencodegenes.org website from Ubuntu 20.04

Hi,

This fails with Ubuntu 20.04:

    curl https://www.gencodegenes.org
    #curl: (35) error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure

but works fine with Ubuntu < 20.04 and on Windows and macOS Mojave.

This seems to happen with some websites because of a combination of three reasons: server misconfiguration, increased TLS security level in Ubuntu 20.04 by default, and a bug in OpenSSL 1.1.1. See https://github.com/Ensembl/ensembl-rest/issues/427 for a similar issue with the Ensembl server.

FWIW this breaks Bioconductor package AnnotationHubData: https://bioconductor.org/checkResults/3.12/bioc-LATEST/AnnotationHubData/nebbiolo1-checksrc.html

Internally the package tries to access www.gencodegenes.org with the following R code:

    > library(RCurl)

    > getURL("https://www.gencodegenes.org/human/releases")
    Error in function (type, msg, asError = TRUE)  :
      error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure

    > sessionInfo()
    R version 4.0.2 Patched (2020-08-04 r78971)
    Platform: x86_64-pc-linux-gnu (64-bit)
    Running under: Ubuntu 20.04.1 LTS

    Matrix products: default
    BLAS:   /home/hpages/R/R-4.0.r78971/lib/libRblas.so
    LAPACK: /home/hpages/R/R-4.0.r78971/lib/libRlapack.so

    locale:
     [1] LC_CTYPE=en_US.UTF-8       LC_NUMERIC=C              
     [3] LC_TIME=en_US.UTF-8        LC_COLLATE=en_US.UTF-8    
     [5] LC_MONETARY=en_US.UTF-8    LC_MESSAGES=en_US.UTF-8   
     [7] LC_PAPER=en_US.UTF-8       LC_NAME=C                 
     [9] LC_ADDRESS=C               LC_TELEPHONE=C            
    [11] LC_MEASUREMENT=en_US.UTF-8 LC_IDENTIFICATION=C       

    attached base packages:
    [1] stats     graphics  grDevices utils     datasets  methods   base     

    other attached packages:
    [1] RCurl_1.98-1.2

    loaded via a namespace (and not attached):
    [1] compiler_4.0.2 bitops_1.0-6  

Thanks!

Hervé Pagès

Program in Computational Biology

Division of Public Health Sciences

Fred Hutchinson Cancer Research Center

1100 Fairview Ave. N, M1-B514

P.O. Box 19024

Seattle, WA 98109-1024

E-mail: xxxxxx@xxxxxxxxx.org

Phone:  (XXX) XXX-XXXX

Fax:    (XXX) XXX-XXXX

--------------------------------------------------------------------------

#### rfaRm

Internally `rfaRm:::rfamGetClanDefinitions()` does:

    library(xml2)
    read_xml("https://rfam.xfam.org/clans")
    #Error in open.connection(x, "rb") :
    #  error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure

Note that `rfaRm:::rfamGetClanDefinitions()` is called at **installation time**
so rfaRm doesn't even install!

Easy way to reproduce:

    curl https://rfam.xfam.org  # works fine on Ubuntu < 20.04

I reported the issue here on Aug 20, 2020:
https://github.com/Rfam/rfam-website/issues/39

## 5. Updating R

#### Flushing the caches

When R is updated, the cache for AnnotationHub and ExperimentHub should be refreshed. This is done by removing AnnotationHub and ExperimentHub present in `/home/biocbuild/.cache/`.

Removing these directories means all packages using these resources will have to re-download the files. This also contributes to an increased runtime for the builds.

Should we also remove package specific caches?
