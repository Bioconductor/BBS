# How to set up a macOS Mojave machine for the daily builds



## 0. General information and tips


- For how to uninstall Mac packages (`.pkg` files) using native `pkgutil`:
  https://wincent.com/wiki/Uninstalling_packages_(.pkg_files)_on_Mac_OS_X



## 1. Initial setup (from the administrator account)


This section describes the very first steps that need to be performed on
a pristine macOS Mojave installation (e.g. after creating a Mac instance on
MacStadium). Skip them and go directly to the next section if the biocbuild
account was created by someone else and if the core team member public keys
were already installed.

Everything in this section must be done **from the administrator account**
(the only account that should exist on the machine at this point).


### 1.1 Set the hostnames

    sudo scutil --set ComputerName machv2
    sudo scutil --set LocalHostName machv2
    sudo scutil --set HostName machv2.bioconductor.org

TESTING:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername


### 1.2 Set DNS servers

    sudo networksetup -setdnsservers 'Ethernet 1' 216.126.35.8 216.24.175.3 8.8.8.8

TESTING:

    networksetup -getdnsservers 'Ethernet 1'
    ping www.bioconductor.org


### 1.3 Apply all software updates

    softwareupdate -l                  # to list all software updates
    sudo softwareupdate -ia --verbose  # install them all
    sudo reboot                        # reboot

TESTING: After reboot, check that the machine is running the latest release
of macOS Mojave i.e. 10.14.6. Check this with:

    system_profiler SPSoftwareDataType
    uname -a  # should show xnu-4903.278.44~1 (or higher)


### 1.4 Create the biocbuild account

    sudo dscl . -create /Users/biocbuild
    sudo dscl . -create /Users/biocbuild UserShell /bin/bash
    sudo dscl . -create /Users/biocbuild UniqueID "505"
    sudo dscl . -create /Users/biocbuild PrimaryGroupID 20
    sudo dscl . -create /Users/biocbuild NFSHomeDirectory /Users/biocbuild
    sudo dscl . -passwd /Users/biocbuild <password_for_biocbuild>
    sudo dscl . -append /Groups/admin GroupMembership biocbuild
    sudo cp -R /System/Library/User\ Template/English.lproj /Users/biocbuild
    sudo chown -R biocbuild:staff /Users/biocbuild

From now on we assume that the machine has a biocbuild account with admin
privileges (i.e. who belongs to the admin group). Note that on the Linux and
Windows builders the biocbuild user is just a regular user with no admin
privileges (not even a sudoer on Linux). However, on a Mac builder, during
STAGE5 of the builds (i.e. BUILD BIN step), the biocbuild user needs to be
able to set ownership and group of the files in the binary packages to
root:admin (this is done calling the chown-rootadmin executable, see below
in this document for the details), and then remove all these files at the
beginning of the next run. It needs to belong to the admin group in order
to be able to do this. Check this with:

    groups biocbuild

Because biocbuild belongs to the admin group, it automatically is a sudoer.
So all the configuration and management of the builds can and should be done
from the biocbuild account.


### 1.5 Install core team member public keys in the biocbuild account

TESTING: Logout and try to login again as biocbuild.

FROM NOW ON, YOU SHOULD NEVER NEED THE ADMINISTRATOR ACCOUNT AGAIN (except
for subsection 2.1 below). DO **EVERYTHING** FROM THE biocbuild ACCOUNT!



## 2. Check hardware, OS, and connectivity with central build node


Except for 2.1, everything in this section must be done **from the
biocbuild account**.


### 2.1 Check that biocbuild belongs to the admin group

Check with:

    groups biocbuild

If biocbuild doesn't belong to the admin group, then you can add with the
following command from the administrator account:

    sudo dseditgroup -o edit -a biocbuild -t user admin

From now on everything must be done **from the biocbuild account**.


### 2.2 Check hardware requirements

These are the requirements for running the BioC software builds:

                          strict minimum  recommended
    Nb of logical cores:              16           24
    Memory:                         32GB         64GB

Hard drive: 512GB if the plan is to run BBS only on the machine. More (e.g.
768GB) if the plan is to also run the Single Package Builder.

Check nb of cores with:

    sysctl -n hw.logicalcpu   # logical cores
    sysctl -n hw.ncpu         # should be the same as 'sysctl -n hw.logicalcpu'
    sysctl -n hw.activecpu    # should be the same as 'sysctl -n hw.logicalcpu'
    sysctl -n hw.physicalcpu  # physical cores

Check amount of RAM with:

    system_profiler SPHardwareDataType  # will also report nb of physical cores

Check hard drive with:

    system_profiler SPStorageDataType


### 2.3 Apply any pending system updates and reboot

Make sure the machine is running the latest release of macOS Mojave:

    system_profiler SPSoftwareDataType

If not, use your your personal account or the administrator account to
update to the latest with:

    sudo softwareupdate -ia --verbose

and reboot the machine.

Check the kernel version (should be Darwin 18 for macOS Mojave):

    uname -sr


### 2.4 Install XQuartz

Download it from https://xquartz.macosforge.org/

    cd ~/Downloads/
    curl -LO https://dl.bintray.com/xquartz/downloads/XQuartz-2.7.11.dmg

Install with:

    sudo hdiutil attach XQuartz-2.7.11.dmg
    sudo installer -pkg /Volumes/XQuartz-2.7.11/XQuartz.pkg -target /
    sudo hdiutil detach /Volumes/XQuartz-2.7.11
    cd /usr/local/include/
    ln -s /opt/X11/include/X11 X11

TESTING: Logout and login again so that the changes made by the installer
to the `PATH` take effect. Then:

    which Xvfb        # should be /opt/X11/bin/Xvfb
    ls -l /usr/X11    # should be a symlink to /opt/X11


### 2.5 Run Xvfb as service

`Xvfb` is run as global daemon controlled by launchd. We run this as a daemon
instead of an agent because agents are run on behalf of the logged in user
while a daemon runs in the background on behalf of the root user (or any user
you specify with the 'UserName' key).

    man launchd
    man launchctl

#### Create plist file

The plist files in `/Library/LaunchDaemons` specify how applications are
called and when they are started. We'll call our plist `local.xvfb.plist`.

    sudo vim /Library/LaunchDaemons/local.xvfb.plist

Paste these contents into `local.xvfb.plist`:

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
      <dict>
        <key>KeepAlive</key>
          <true/>
        <key>Label</key>
          <string>local.xvfb</string>
        <key>ProgramArguments</key>
          <array>
            <string>/opt/X11/bin/Xvfb</string>
            <string>:1</string>
            <string>-screen</string>
            <string>0</string>
            <string>800x600x16</string>
          </array>
        <key>RunAtLoad</key>
          <true/>
        <key>ServiceDescription</key>
          <string>Xvfb Virtual X Server</string>
        <key>StandardOutPath</key>
          <string>/var/log/xvfb/xvfb.stdout.log</string>
        <key>StandardErrorPath</key>
          <string>/var/log/xvfb/xvfb.stderror.log</string>
      </dict>
    </plist>

NOTE: The `KeepAlive` key means the system will try to restart the service if
it is killed.  When testing the set up, you should set `KeepAlive` to `false`
so you can manually start/stop the service. Once you are done testing, set
`KeepAlive` back to `true`.

#### Logs

stdout and stderror logs are output to `/var/log/xvfb` as indicated in
`/Library/LaunchDaemons/local.xvfb.plist`. Logs are rotated with `newsyslog`
and the config is in `/etc/newsyslog.d/`.

Create `xvfb.conf`:

    sudo vim /etc/newsyslog.d/xvfb.conf

Add these contents:

    # logfilename          [owner:group]    mode count size when  flags [/pid_file] [sig_num]
    /var/log/xvfb/xvfb.stderror.log         644  5     5120 *     JN
    /var/log/xvfb/xvfb.stdout.log           644  5     5120 *     JN

These instructions rotate logs when they reached a file size of 5MB. Once
the `xvfb.conf` file is in place, simulate a rotation:

    sudo newsyslog -nvv

#### Export global variable DISPLAY

    sudo vim /etc/profile

Add this line to `/etc/profile`:

    export DISPLAY=:1.0

Log out and log back in as biocbuild to confirm $DISPLAY is defined:

    echo $DISPLAY

#### Load the service

    sudo launchctl load /Library/LaunchDaemons/local.xvfb.plist

`xvfb` should appear in the list of loaded services:

    sudo launchctl list | grep xvfb

If a PID is assigned that means the daemon is running. The service is
scheduled to start on boot so at this point there probably is no PID
assigned (service is loaded but not started).

#### Test starting/stopping the service

NOTE: For testing, set `KeepAlive` to `false` in
`/Library/LaunchDaemons/local.xvfb.plist`. Once testing is done,
reset the key to `true`.

The `RunAtLoad` directive in `/Library/LaunchDaemons/local.xvfb.plist`
says to start the service at boot. To test the service without a re-boot
use the `start` and `stop` commands with the service label.

    sudo launchctl start local.xvfb

Check the service has started with either of these commands:

    sudo launchctl list | grep xvfb
    ps aux | grep -v grep | grep Xvfb

Stop the service:

    sudo launchctl stop local.xvfb

If you have problems starting the service set the log level to debug
and check (or tail) the log file:

    sudo launchctl log level debug
    sudo tail -f /var/log/xvfb/xvfb.stderror.log &

Try to start the job again:

    sudo launchctl start local.xvfb

#### Reboot

Reboot the server and confirm the service came up:

    ps aux | grep -v grep | grep Xvfb

#### Kill the process

When `KeepAlive` is set to 'true' in `/Library/LaunchDaemons/local.xvfb.plist`,
the service will be restarted if killed with:

    sudo kill -9 <PID>

If you really need to kill the service, change `KeepAlive` to `false`
in the plist file, then kill the process.

#### Test

    sudo launchctl list | grep xvfb                     # should be running
    echo $DISPLAY                                       # :1.0
    /path/to/Rscript -e 'png(tempfile(), type="Xlib")'  # no more error!


### 2.6 Install Apple's Command Line Tools

You only need this for the `ld`, `make`, and `clang` commands. Check whether
you already have them or not with:

    which ld       # /usr/bin/ld
    ld -v          # BUILD 18:57:17 Dec 13 2019
    which make     # /usr/bin/make
    make -v        # GNU Make 3.81
    which clang    # /usr/bin/clang
    clang -v       # Apple clang version 11.0.0 (clang-1100.0.33.17)
    which git      # /usr/bin/git
    git --version  # git version 2.21.1 (Apple Git-122.3)

If you do, skip this section.

--------------------------------------------------------------------------
The Command Line Tools for Xcode is a subset of Xcode that includes Apple
LLVM compiler (with Clang front-end), linker, Make, and other developer
tools that enable Unix-style development at the command line. It's all
that is needed to install/compile R packages with native code in them (note
that it even includes the `svn` and `git` clients, and the most recent
versions include `python3`).

The full Xcode IDE is much bigger (e.g. 10.8 GB for Xcode 12.3 vs 431MB
for the Command Line Tools for Xcode 12.3) and is not needed.

Go on https://developer.apple.com/ and pick up the last version for
macOS Mojave (`Command_Line_Tools_for_Xcode_11.3.1.dmg` as of May 13, 2020,
note that Command Line Tools for Xcode 11.4 requires Catalina or higher).
More recent versions of Xcode and the Command Line Tools are provided
as `xip` files.

If you got a `dmg` file, install with:

    sudo hdiutil attach Command_Line_Tools_for_Xcode_11.3.1.dmg
    sudo installer -pkg "/Volumes/Command Line Developer Tools/Command Line Tools.pkg" -target /
    sudo hdiutil detach "/Volumes/Command Line Developer Tools"

If you got an `xip` file, install with:

    ## Check the file first:
    pkgutil --verbose --check-signature path/to/xip

    ## Install in /Applications
    cd /Applications
    xip --expand path/to/xip

    ## Agree to the license:
    sudo xcodebuild -license

TESTING:

    which make   # /usr/bin/make
    which clang  # /usr/bin/clang
    clang -v     # Apple clang version 11.0.0 (clang-1100.0.33.17)
--------------------------------------------------------------------------


### 2.7 Install gfortran

Simon uses Coudert's gfortran 8.2: https://github.com/fxcoudert/gfortran-for-macOS/releases

Download with:

    cd ~/Downloads/
    curl -LO https://github.com/fxcoudert/gfortran-for-macOS/releases/download/8.2/gfortran-8.2-Mojave.dmg

Install with:

    sudo hdiutil attach gfortran-8.2-Mojave.dmg
    sudo installer -pkg /Volumes/gfortran-8.2-Mojave/gfortran-8.2-Mojave/gfortran.pkg -target /
    sudo hdiutil detach /Volumes/gfortran-8.2-Mojave
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Ignore message:

    chown: /usr/local: Operation not permitted

TESTING:

    gfortran --version  # GNU Fortran (GCC) 8.2.0

Finally check that the gfortran libraries got installed in
`/usr/local/gfortran/lib` and make sure that `LOCAL_FORTRAN_DYLIB_DIR`
in `BBS/utils/macosx-inst-pkg.sh` points to this location.
Otherwise  we will produce broken binaries again (see
https://support.bioconductor.org/p/95587/#95631).


### 2.8 Install Homebrew

First make sure `/usr/local` is writable by the `biocbuild` user and other
members of the `admin` group:

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then install with:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

TESTING:

    brew doctor


### 2.9 Install openssl

    brew install openssl

Note that the installation is keg-only i.e. not symlinked into /usr/local
because macOS provides LibreSSL.

Then in `/etc/profile`:

- Append `/usr/local/opt/openssl@1.1/bin` to `PATH`.

- Add `/usr/local/opt/openssl@1.1/lib/pkgconfig` to `PKG_CONFIG_PATH`.

- Add the following line, replacing '1.1.1h' with the version installed:
    ```
    export OPENSSL_LIBS="/usr/local/opt/openssl@1.1/lib/libssl.a /usr/local/opt/openssl@1.1/lib/libcrypto.a"
    ```
  This will trigger statically linking of the rtracklayer package against
  the openssl libraries.


### 2.10 Install XZ Utils (includes lzma lib)

    brew install xz


### 2.11 Install Python 3

NOTE: As of Feb 3, 2021, the tensorflow module is not available yet for
Python 3.9 so we install Python 3.8.

    #brew install python3  # don't do this yet, it will install Python 3.9!

The brew formula for Python 3.8 (`python@3.8` as of Nov 3rd, 2020) will
install dependencies `gdbm`, `readline` and `sqlite`:

    brew install python@3.8

Note that the installation is keg-only i.e. not symlinked into `/usr/local`,
because this is an alternate version of the python3 formula (which is an
alias for python@3.9).

Note that installation of `readline` and `sqlite` are keg-only, which is
as expected.

Then, install Python 3.9. It is needed by Open Babel 3:

    brew install python3  # will install Python 3.9

Python 3.9 is now the main Python 3 installation (it's in the `PATH`):

    python3 --version  # Python 3.9.0

HOWEVER, WE DON'T WANT THIS! We want to make Python 3.8 the main Python 3
installation. To do this, we need to manually fix a bunch of symlinks:

- In `/usr/local/bin/`: Fix symlinks `2to3`, `idle3`, `pip3`, `pydoc3`,
  `python3`, `python3-config`, and `wheel3` (e.g. have them point to
   stuff in `../Cellar/python@3.8/3.8.10/bin/` instead of stuff in
   `../Cellar/python@3.9/3.9.5/bin/`).

- In `/usr/local/lib/pkgconfig/`: Fix symlinks `python3-embed.pc`
  and `python3.pc` in the same manner.

- In `/usr/local/opt/`: Fix symlinks `python`, `python3`, and `python@3`
  (e.g. have them point to `../Cellar/python@3.8/3.8.10` instead of
  `../Cellar/python@3.9/3.9.5`).

TESTING:

    python3 --version  # Python 3.8.10


### 2.12 Install Python 3 modules

#### Python 3 modules needed by BBS

    pip3 install psutil

#### Python 3 modules needed by the Single Package Builder only

`virtualenv` is used by the Single Package Builder. Despite python3 shipping
with `venv`, `venv` is not sufficient. The SPB must use `virtualenv`.

    pip3 install virtualenv

#### Install Python 3 modules needed by some CRAN/Bioconductor packages

    pip3 install numpy scipy sklearn h5py pandas mofapy mofapy2
    pip3 install tensorflow tensorflow_probability
    pip3 install h5pyd
    pip3 install nbconvert jupyter
    pip3 install matplotlib phate

TESTING:

- `jupyter --version` should display something like this:
    ```
    machv2:~ biocbuild$ jupyter --version
    jupyter core     : 4.6.3
    jupyter-notebook : 6.1.4
    qtconsole        : 4.7.7
    ipython          : 7.19.0
    ipykernel        : 5.3.4
    jupyter client   : 6.1.7
    jupyter lab      : not installed
    nbconvert        : 6.0.7
    ipywidgets       : 7.5.1
    nbformat         : 5.0.8
    traitlets        : 5.0.5
    ```
    Note that it's ok if jupyter lab is not installed but everything else
    should be.

- Start python3 and try to import the above modules. Quit.

- Try to build the BiocSklearn package (takes < 1 min):
    ```
    cd ~/bbs-3.14-bioc/meat/
    R CMD build BiocSklearn
    ```
    and the destiny package:
    ```
    R CMD build destiny
    ```


### 2.13 Install MacTeX

Home page: https://www.tug.org/mactex/

Download:

    https://tug.org/mactex/mactex-download.html

As of May 2020 the above page is displaying "Downloading MacTeX 2020".

    cd ~/Downloads/
    curl -LO https://tug.org/cgi-bin/mactex-download/MacTeX.pkg

Install with:

    sudo installer -pkg MacTeX.pkg -target /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Logout and login again so that the changes made by the installer
to the `PATH` take effect. Then:

    which tex


### 2.14 Install Pandoc

Install Pandoc 2.7.3 instead of the latest Pandoc (2.9.2.1 as of April 2020).
The latter breaks `R CMD build` for 8 Bioconductor software packages
(ChIPSeqSpike, FELLA, flowPloidy, MACPET, profileScoreDist, projectR,
swfdr, and TVTB) with the following error:

    ! LaTeX Error: Environment cslreferences undefined.

Download with:

    cd ~/Downloads/
    curl -LO https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-macOS.pkg

Install with:

    sudo installer -pkg pandoc-2.7.3-macOS.pkg -target /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive


### 2.15 Install pkg-config

NOVEMBER 2020: Who needs this? Is it really needed?

    brew install pkg-config

TESTING:

    which pkg-config       # /usr/local/bin/pkg-config
    pkg-config --list-all


### 2.16 Install wget and pstree

These are just convenient to have when working interactively on a build
machine but are not required by the daily builds or propagation pipe.

Install with:

    brew install wget
    brew install pstree


### 2.17 Replace /etc/ssl/cert.pm with CA bundle if necessary

#### curl: (60) SSL certificate problem: certificate has expired

To test for the issue, curl a URL. The output should state that the
certificate has expired. For example

    merida1:~ biocbuild$ curl https://stat.ethz.ch/
    curl: (60) SSL certificate problem: certificate has expired
    More details here: https://curl.haxx.se/docs/sslcerts.html
    
    curl performs SSL certificate verification by default, using a "bundle"
     of Certificate Authority (CA) public keys (CA certs). If the default
     bundle file isn't adequate, you can specify an alternate file
     using the --cacert option.
    If this HTTPS server uses a certificate signed by a CA represented in
     the bundle, the certificate verification probably failed due to a
     problem with the certificate (it might be expired, or the name might
     not match the domain name in the URL).
    If you'd like to turn off curl's verification of the certificate, use
     the -k (or --insecure) option.
    HTTPS-proxy has similar options --proxy-cacert and --proxy-insecure.

#### Install a new CA bundle

First move and rename the old cert.pem. For example

    mv  /etc/ssl/cert.pem /etc/ssl/certs/cert.pem.org

Then go to https://curl.haxx.se/docs/sslcerts.html and find the link to the
CA bundle generated by Mozilla. You can

    sudo curl --insecure https://curl.se/ca/cacert.pem -o /etc/ssl/cert.pem

TESTING

    merida1:~ biocbuild$ curl https://stat.ethz.ch/

It should not produce any output that the certificate has expired.


### 2.18 [OPTIONAL] Additional stuff not needed in normal times

Should not be needed. Kept only for the record.

CRAN has a tradition of making Mac binary packages available at the last
minute before a new R release (new R releases normally happen in Spring).
This means that the build system will need to be able to install many CRAN
packages from source on a Mac builder when the BioC devel builds use R devel.
However some packages are difficult (e.g. fftwtools) because they require
system libraries that we don't normally install on a Mac builder. The good
news is that pre-compiled versions of these libraries are available here:
https://mac.r-project.org/libs-4/

In this section we only describe the case of installing CRAN packages jpeg,
tiff, and fftwtools, from source, which require system libraries JPEG, TIFF,
and FFTW, respectively. The prodecure for other CRAN packages is similar.

UPDATE: We don't need to install any of this! See _What if CRAN doesn't
provide package binaries for macOS yet?_ subsection in the _Install R_
section below in this document for a better way to handle this situation.

#### [OPTIONAL] Install JPEG system library

This is needed only if CRAN package jpeg needs to be installed from source
which is usually NOT the case (most of the time a Mac binary should be
available on CRAN).

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs-4/jpeg-9-darwin.17-x86_64.tar.gz
    sudo tar fvxz jpeg-9-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: If R is already installed on the machine, try to install the jpeg
package *from source*:

    install.packages("jpeg", type="source", repos="https://cran.r-project.org")
    library(jpeg)
    example(readJPEG)
    example(writeJPEG)

#### [OPTIONAL] Install TIFF system library

This is needed only if CRAN package tiff needs to be installed from source
which is usually NOT the case (most of the time a Mac binary should be
available on CRAN).

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs-4/tiff-4.1.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz tiff-4.1.0-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: If R is already installed on the machine, try to install the tiff
package *from source*:

    install.packages("tiff", type="source", repos="https://cran.r-project.org")
    library(tiff)
    example(readTIFF)
    example(writeTIFF)

#### [OPTIONAL] Install FFTW system library

This is needed only if CRAN package fftwtools needs to be installed from
source which is usually NOT the case (most of the time a Mac binary should
be available on CRAN).

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs-4/fftw-3.3.8-darwin.17-x86_64.tar.gz
    sudo tar fvxz fftw-3.3.8-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: If R is already installed on the machine, try to install the fftwtools
package *from source*:

    install.packages("fftwtools", type="source", repos="https://cran.r-project.org")



## 3. Set up the Bioconductor software builds


Everything in this section must be done **from the biocbuild account**.


### 3.1 Check connectivity with central builder

#### Check that you can ping the central builder

Depending on whether the node you're ping'ing from is within RPCI's DMZ
or not, use the central builder's short or long (i.e. hostname+domain)
hostname. For example:

    ping malbec1                                   # from within RPCI's DMZ
    ping malbec1.bioconductor.org                  # from anywhere else

#### Install biocbuild RSA private key

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    machv2:~ biocbuild$ ls -l .BBS/id_rsa
    -r--------  1 biocbuild  staff  884 Jan 12 12:19 .BBS/id_rsa

#### Check that you can ssh to the central build node

    ssh -i ~/.BBS/id_rsa malbec2                   # from within RPCI's DMZ
    ssh -i ~/.BBS/id_rsa malbec2.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec2.bioconductor.org port 22: Operation timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

#### Check that you can send HTTPS requests to the central node

    curl http://malbec2                           # from within RPCI's DMZ
    curl http://malbec2.bioconductor.org          # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    curl: (7) Failed connect to malbec2.bioconductor.org:80; Operation timed out

Contact the IT folks at RPCI if that's the case (see above).

More details on https implementation in `BBS/README.md`.


### 3.2 Clone BBS git tree and create bbs-x.y-bioc directory structure

Must be done from the biocbuild account.

#### Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS

#### Compile chown-rootadmin.c

    cd ~/BBS/utils/
    gcc chown-rootadmin.c -o chown-rootadmin
    sudo chown root:admin chown-rootadmin
    sudo chmod 4750 chown-rootadmin

TESTING: Check that the permissions on the `chown-rootadmin` executable
look like this:

    machv2:utils biocbuild$ ls -al chown-rootadmin
    -rwsr-x---  1 root  admin  8596 Jan 13 12:55 chown-rootadmin

#### Create bbs-x.y-bioc directory structure

    cd
    mkdir bbs-3.14-bioc
    cd bbs-3.14-bioc/
    mkdir log


### 3.3 Install R

Must be done from the `biocbuild` account.

#### Choose latest R binary for macOS

If installing R devel: download R from https://mac.r-project.org/ (e.g.
pick up `R-4.0-branch.pkg`). Unlike the installer image (`.pkg` file),
the tarball (`.tar.gz` file) does NOT include Tcl/Tk (which is needed
by R base package tcltk) so make sure to grab the former.

If installing R release: download R from CRAN (e.g. from
https://cloud.r-project.org/bin/macosx/). Pick up the 1st file
(e.g. `R-3.6.3.pkg`). Make sure to pick the installer, not the
source tarball, as the former contains Tcl/Tk libraries that will
install in `/usr/local`.

#### Download and install

Remove the previous R installation:

    cd /Library/Frameworks/
    sudo rm -rf R.framework

Download and install with:

    cd ~/Downloads/
    curl -O https://cran.r-project.org/bin/macosx/base/R-4.1.0.pkg
    sudo installer -pkg R-4.1.0.pkg -target /

Note that, unlike what we do on the Linux and Windows builders, this is a
*system-wide* installation of R i.e. it's in the `PATH` for all users on the
machine so can be started with `R` from anywhere.

#### Basic testing

Start R, check the version displayed by the startup message, then:

    # --- check capabilities ---

    capabilities()  # all should be TRUE
    X11()           # nothing visible should happen
    dev.off()

    # --- install rgl and try to load it ---
    install.packages("rgl", repos="https://cran.r-project.org")
    library(rgl)

If `library(rgl)` fails with an error like:

    Error: package or namespace load failed for ‘rgl’:
     .onLoad failed in loadNamespace() for 'rgl', details:
      call: grDevices::quartz()
      error: unable to create quartz() device target, given type may not be supported
    In addition: Warning message:
    In grDevices::quartz() : No displays are available

then add `export RGL_USE_NULL=TRUE` to `/etc/profile`, logout and login
again (so that the change takes effect), and try `library(rgl)` again.

    # --- install a few CRAN packages *from source* ---

    # Contains C++ code:
    install.packages("Rcpp", type="source", repos="https://cran.r-project.org")
    # Contains Fortran code:
    install.packages("minqa", type="source", repos="https://cran.r-project.org")
    # Only if CRAN doesn't provide the binary for macOS yet:
    install.packages("Cairo", type="source", repos="https://cran.r-project.org")

#### Install BiocManager + BiocCheck

From R:

    install.packages("BiocManager", repos="https://cran.r-project.org")

    library(BiocManager)  # This displays the version of Bioconductor
                          # that BiocManager is pointing at.

    ## IMPORTANT: Switch to "devel" **ONLY** if you are installing R for
    ## the devel builds and if BioC devel uses the same version of R as
    ## BioC release!
    BiocManager::install(version="devel")

    BiocManager::install("BiocCheck")  # required by SPB

If some CRAN packages failed to compile, see _What if CRAN doesn't provide
package binaries for macOS yet?_ subsection below.

#### [OPTIONAL] More testing

From R:

    # Always good to have; try this even if CRAN binaries are not available:
    install.packages("devtools", repos="https://cran.r-project.org")
    BiocManager::install("BiocStyle")

    BiocManager::install("rtracklayer")
    BiocManager::install("VariantAnnotation")
    BiocManager::install("rhdf5")

Quit R and check that rtracklayer got statically linked against the openssl
libraries with:

    otool -L /Library/Frameworks/R.framework/Resources/library/rtracklayer/libs/rtracklayer.so

#### Configure R to use the Java installed on the machine

    sudo R CMD javareconf

TESTING: See "Install Java" below in this file for how to test Java/rJava.

#### [OPTIONAL] Try to install RGtk2

From R:

    ## First try to install the binary:
    install.packages("RGtk2", repos="https://cran.r-project.org")

    ## If there's no binary, try to install from source:
    install.packages("RGtk2", type="source", repos="https://cran.r-project.org")

See "Install GTK2" below in this file for what is needed in order to
be able to compile RGtk2.

#### Flush the data caches

When R is updated, it's a good time to flush the cache for AnnotationHub,
ExperimentHub, and BiocFileCache. This is done by removing the corresponding
folders present in `~/Library/Caches/`.

Removing these folders means all packages using these resources will have
to re-download the files. This ensures that resources are still available.
However it also contributes to an increased runtime for the builds.

Should we also remove package specific caches?

#### MAJOR ISSUE: fonts/XQuartz issue on macOS High Sierra or higher

There is a nasty issue with fonts/XQuartz on macOS High Sierra or higher
that breaks `R CMD build` on hundreds Bioconductor packages at the moment!
(> 300 as of March 2020)

The following code produces a `polygon edge not found` error and a bunch
of `no font could be found for family "Arial"` warnings on macOS High Sierra
or higher:

    library(ggplot2)
    png(tempfile(), type="quartz")
    ggplot(data.frame(), aes(1, 1))
    dev.off()

See https://github.com/tidyverse/ggplot2/issues/2252#issuecomment-398268742

This breaks `R CMD build` on hundreds of Bioconductor packages!

Simpler code (that doesn't involve ggplot2) that reproduces the warnings
about the missing font family:

    png(tempfile(), type="quartz")
    plot(density(rnorm(1000)))  # generates a bunch of warnings
    dev.off()

We don't have a clean fix for this yet, only a hacky workaround. The workaround
is to avoid the use of the `"quartz"` type, which seems to be the default
for the macOS builds from CRAN and mac.r-project.org. The other supported types
are `"Xlib"` and `"cairo"`. Using `"Xlib"` solves the above issue but introduces
another one:

    png(tempfile(), type="Xlib")
    plot.new()
    lines(c(0, 15), c(0, 15), col="#FF000088")
    # Warning message:
    # In plot.xy(xy.coords(x, y), type = type, ...) :
    #   semi-transparency is not supported on this device: reported only once per page
    dev.off()

Note that this semi-transparency problem breaks `R CMD build` on the chimeraviz
package. So we'll use `"cairo"` (which is the default on Linux).

One caveat is that this default cannot be changed via an `Rprofile` file (this
file is ignored by `R CMD build` and `R CMD check`).

So we use the following hack. Put:

    options(bitmapType="cairo")

in `/Library/Frameworks/R.framework/Resources/library/grDevices/R/grDevices`
at the beginning of the `local({...})` block.

Not a totally satisfying solution because code that explicitly resets the
type to `"quartz"` will still fail.

TESTING:

- Start R, then:
    ```
    getOption("bitmapType")  # would show "quartz" without our hack
    png(tempfile())
    plot.new()
    lines(c(0, 15), c(0, 15), col="#FF000088")
    plot(density(rnorm(1000)))
    library(ggplot2)
    ggplot(data.frame(), aes(1, 1))
    dev.off()
    ```
- [Optional] Try to `R CMD build` DESeq2 and plyranges.

For the record, here are a couple of things we tried that didn't work:

- Found [here](https://stackoverflow.com/questions/55933524/r-can-not-find-fonts-to-be-used-in-plotting):
    ```
    library(showtext)
    font_add("Arial", "/Library/Fonts/Arial.ttf")  # use the actual file path
    showtext_auto()
    ```
    This fixes the problem in an interactively session but not in the context
    of `R CMD DESeq2` (where do we put the 3 lines above?)

- We also tried to compile R from source:
    ```
    brew install pcre2

    cd ~/bbs-3.14-bioc/
    mkdir rdownloads
    cd rdownloads/
    download latest R source tarball, extract, rename

    cd ~/bbs-3.14-bioc/
    mkdir R
    cd R/
    ## Use same settings as Simon:
    ## https://svn.r-project.org/R-dev-web/trunk/QA/Simon/R4/conf.high-sierra-x86_64
    CC="clang -mmacosx-version-min=10.13" CXX="clang++ -mmacosx-version-min=10.13" OBJC="clang -mmacosx-version-min=10.13" FC="gfortran -mmacosx-version-min=10.13" F77="gfortran -mmacosx-version-min=10.13" CFLAGS='-Wall -g -O2' CXXFLAGS='-Wall -g -O2' OBJCFLAGS='-Wall -g -O2' FCFLAGS='-Wall -g -O2' F77FLAGS='-Wall -g -O2' ../rdownloads/R-4.0.r78132/configure --build=x86_64-apple-darwin17.0

    make -j8
    ```

    Then create `R/etc/Rprofile.site` with the following line in it:
    ```
    options(pkgType="mac.binary")
    ```

TESTING:

    cd ~/bbs-3.14-bioc/
    R/bin/R CMD config CC
    # Start R
    pkgs <- c("rJava", "gsl", "V8", "magick", "rsvg", "pdftools",
              "sf", "glpkAPI", "RPostgres", "RMySQL", "protolite")
    install.packages(pkgs, repos="https://cran.r-project.org")
    for (pkg in pkgs) library(pkg, character.only=TRUE)

Unfortunately, most packages crash the session when loaded. [According to Simon](https://stat.ethz.ch/pipermail/r-sig-mac/2020-April/013328.html), this is expected somehow.

#### What if CRAN doesn't provide package binaries for macOS yet?

If the builds are using R-devel and CRAN doesn't provide package binaries
for Mac yet, install the following package binaries (these are the
Bioconductor deps that are "difficult" to compile from source on Mac,
as of Nov 2020):

    difficult_pkgs <- c("XML", "rJava", "gdtools", "units", "gsl", "V8",
              "magick", "rsvg", "gmp", "xml2", "jpeg", "tiff", "ncdf4",
              "fftw", "fftwtools", "proj4", "textshaping", "ragg",
              "Rmpfr", "pdftools", "av", "rgeos", "sf", "RcppAlgos",
              "glpkAPI", "RGtk2", "gert", "RPostgres", "RMySQL", "RMariaDB",
              "protolite", "arrangements", "terra", "PoissonBinomial")

First try to install with:

    install.packages(difficult_pkgs, repos="https://cran.r-project.org")

It should fail for most (if not all) packages. However, it's still worth
doing it as it will be able to install many dependencies from source.
Then try to install the binaries built with the current R release:

    contriburl <- "https://cran.r-project.org/bin/macosx/contrib/4.1"
    install.packages(difficult_pkgs, contriburl=contriburl)

NOTES:

- The binaries built for a previous version of R are not guaranteed to work
  with R-devel but if they can be loaded then it's **very** likely that they
  will. So make sure they can be loaded:
    ```
    for (pkg in difficult_pkgs) library(pkg, character.only=TRUE)
    ```

- Most binary packages in `difficult_pkgs` (e.g. XML, rJava, etc) contain a
  shared object (e.g. `libs/XML.so`) that is linked to `libR.dylib` via an
  absolute path that is specific to the version of R that was used when the
  object was compiled/linked e.g.
    ```
    /Library/Frameworks/R.framework/Versions/4.1/Resources/lib/libR.dylib
    ```
  So loading them in a different version of R (e.g. R 4.2) will fail with
  an error like this:
    ```
    > library(XML)
    Error: package or namespace load failed for ‘XML’:
     .onLoad failed in loadNamespace() for 'XML', details:
      call: dyn.load(file, DLLpath = DLLpath, ...)
      error: unable to load shared object '/Library/Frameworks/R.framework/Versions/4.2/Resources/library/XML/libs/XML.so':
      dlopen(/Library/Frameworks/R.framework/Versions/4.2/Resources/library/XML/libs/XML.so, 6): Library not loaded: /Library/Frameworks/R.framework/Versions/4.1/Resources/lib/libR.dylib
      Referenced from: /Library/Frameworks/R.framework/Versions/4.2/Resources/library/XML/libs/XML.so
      Reason: image not found
    ```
  However, they can easily be tricked by creating a symlink like this:
    ```
    cd /Library/Frameworks/R.framework/Versions
    ln -s 4.2 4.1
    ```

- Do NOT install the Cairo binary built for a previous version of R (hopefully
  you'll manage to install it from source). Even though it can be loaded,
  it's most likely to not work properly e.g. it might produce errors like
  this:
    ```
    library(Cairo)
    Cairo(600, 600, file="plot.png", type="png", bg="white")
    # Error in Cairo(600, 600, file = "plot.png", type = "png", bg = "white") : 
    #   Graphics API version mismatch
    ```


### 3.4 Add software builds to biocbuild's crontab

Must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    00 16 * * 0-5 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.14/bioc/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.14-bioc/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run
before doing so.



## 4. Install additional stuff for Bioconductor packages with special needs


Everything in this section must be done **from the biocbuild account**.


### 4.1 Install Java

Go to https://jdk.java.net/ and follow the link to the latest JDK (JDK
14 as of April 1, 2020). Then download the tarball for macOS/x64 (e.g.
`openjdk-14.0.1_osx-x64_bin.tar.gz`) to `~/Downloads/`.

Install with:

    cd /usr/local/
    sudo tar zxvf ~/Downloads/openjdk-14.0.1_osx-x64_bin.tar.gz
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then:

    cd /usr/local/bin/
    ln -s ../jdk-14.0.1.jdk/Contents/Home/bin/java
    ln -s ../jdk-14.0.1.jdk/Contents/Home/bin/javac
    ln -s ../jdk-14.0.1.jdk/Contents/Home/bin/jar

In `/etc/profile` add the following line:

    export JAVA_HOME=/usr/local/jdk-14.0.1.jdk/Contents/Home

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    java --version
    # openjdk 14.0.1 2020-04-14
    # OpenJDK Runtime Environment (build 14.0.1+7)
    # OpenJDK 64-Bit Server VM (build 14.0.1+7, mixed mode, sharing)

    javac --version
    # javac 14.0.1

Finally reconfigure R to use this new Java installation:

    sudo R CMD javareconf

TESTING: Try to install the rJava package:

    # install the CRAN binary
    install.packages("rJava", repos="https://cran.r-project.org")
    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")
    # [1] "14.0.1+7"


### 4.2 Install NetCDF and HDF5 system library

NetCDF is needed only if CRAN package ncdf4 needs to be installed from
source which is usually NOT the case (most of the time a Mac binary should
be available on CRAN).

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs-4/netcdf-4.7.3-darwin.17-x86_64.tar.gz
    curl -O https://mac.r-project.org/libs-4/hdf5-1.12.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz netcdf-4.7.3-darwin.17-x86_64.tar.gz -C /
    sudo tar fvxz hdf5-1.12.0-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the ncdf4 package *from source*:

    install.packages("ncdf4", type="source", repos="https://cran.r-project.org")

If you have time, you can also try to install the mzR package but be aware
that this takes much longer:

    library(BiocManager)
    BiocManager::install("mzR", type="source")  # takes between 7-10 min


### 4.3 Install GSL system library

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs-4/gsl-2.6-darwin.17-x86_64.tar.gz
    sudo tar fvxz gsl-2.6-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the GLAD package *from source*:

    library(BiocManager)
    BiocManager::install("GLAD", type="source")


### 4.4 Install Open MPI

This is needed to install CRAN package Rmpi from source (unfortunately no
Mac binary is available on CRAN).

Install with:

    brew install open-mpi

Notes:
- This will install many deps: `gmp`, `isl`, `mpfr`, `libmpc`, `gcc`, `hwloc`,
  and `libevent`.
- During installation of gcc, you might see the following error:
    ```
    Error: The `brew link` step did not complete successfully
    The formula built, but is not symlinked into /usr/local
    Could not symlink bin/gfortran
    Target /usr/local/bin/gfortran
    already exists. You may want to remove it:
      rm '/usr/local/bin/gfortran'
    ```
  Please ignore it. In particular do NOT try to perform any of the suggested
  actions (e.g. `rm /usr/local/bin/gfortran` or `brew link --overwrite gcc`).

TESTING: Try to install the Rmpi package *from source*:

    install.packages("Rmpi", type="source", repos="https://cran.r-project.org")
    library(Rmpi)
    mpi.spawn.Rslaves(nslaves=3)
    mpi.parReplicate(100, mean(rnorm(1000000)))
    mpi.close.Rslaves()
    mpi.quit()


### 4.5 Install JAGS

Download with:

    cd ~/Downloads/
    curl -LO https://sourceforge.net/projects/mcmc-jags/files/JAGS/4.x/Mac%20OS%20X/JAGS-4.3.0.dmg

Install with:

    sudo hdiutil attach JAGS-4.3.0.dmg
    sudo installer -pkg /Volumes/JAGS-4.3.0/JAGS-4.3.0.mpkg -target /
    sudo hdiutil detach /Volumes/JAGS-4.3.0
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the rjags package *from source*:

    install.packages("rjags", type="source", repos="https://cran.r-project.org")


### 4.6 Install libSBML

SEPT 2020: THIS SHOULD NO LONGER BE NEEDED! (starting with BioC 3.12, rsbml is
no longer supported on macOS)

Required by Bioconductor package rsbml.

#### Install a more recent libxml-2.0

libSBML/rsbml require libxml-2.0 >= 2.6.22 but the version that comes with
Mojave is still 2.6.16 (this has not changed since El Capitan). So we first
install a more recent libxml-2.0 with:

    brew install libxml2

Ignore the "This formula is keg-only..." caveat.

In `/etc/profile` **prepend** `/usr/local/opt/libxml2/bin`
to `PATH` and `/usr/local/opt/libxml2/lib/pkgconfig` to
`PKG_CONFIG_PATH` (in particular it's important to put this **before**
`/Library/Frameworks/GTK+.framework/Resources/lib/pkgconfig` which
contains a broken `libxml-2.0.pc` file).

Logout and login again so that the changes to `/etc/profile` take
effect then check that `pkg-config` picks up the right libxml-2.0:

    which xml2-config
    # /usr/local/opt/libxml2/bin/xml2-config

    xml2-config --cflags
    # -I/usr/local/Cellar/libxml2/2.9.10_1/include/libxml2

    xml2-config --libs
    # -L/usr/local/Cellar/libxml2/2.9.10_1/lib -lxml2 -lz -lpthread -liconv -lm

    pkg-config --cflags libxml-2.0
    # -I/usr/local/Cellar/libxml2/2.9.10_1/include/libxml2

    pkg-config --libs libxml-2.0
    # -L/usr/local/Cellar/libxml2/2.9.10_1/lib -lxml2

#### Install libSBML

Home page http://sbml.org/Software/libSBML
As of December 2018, Homebrew was no longer offering libsbml so we download
it from SourceForge:

- Go to https://sourceforge.net/projects/sbml/files/libsbml/, click on
  the latest version (5.18.0 as of April 2020), choose "stable", then
  "Mac OS X", then download libSBML installer for Mojave
  (`libsbml-5.18.0-libxml2-macosx-mojave.dmg`) with:

    cd ~/Downloads/
    curl -LO https://sourceforge.net/projects/sbml/files/libsbml/5.18.0/stable/Mac%20OS%20X/libsbml-5.18.0-libxml2-macosx-mojave.dmg

    #curl -LO https://sourceforge.net/projects/sbml/files/libsbml/5.13.0/stable/Mac%20OS%20X/libsbml-5.13.0-libxml2-macosx-elcapitan.dmg

Install with:

    sudo hdiutil attach libsbml-5.18.0-libxml2-macosx-mojave.dmg
    sudo installer -pkg "/Volumes/libsbml-5.18.0-libxml2/libSBML-5.18.0-libxml2-mojave.pkg" -target /
    sudo hdiutil detach "/Volumes/libsbml-5.18.0-libxml2"
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

    #sudo hdiutil attach libsbml-5.13.0-libxml2-macosx-elcapitan.dmg
    #sudo installer -pkg "/Volumes/libsbml-5.13.0-libxml2/libSBML-5.13.0-libxml2-elcapitan.pkg" -target /
    #sudo hdiutil detach "/Volumes/libsbml-5.13.0-libxml2"
    # Fix /usr/local/ permissions:
    #sudo chown -R biocbuild:admin /usr/local/*
    #sudo chown -R root:wheel /usr/local/texlive

The `.pc` file included in the installer (`/usr/local/lib/pkgconfig/libsbml.pc`)
is broken:

    pkg-config --cflags libsbml
    # -I/usr/local/Cellar/libxml2/2.9.10_1/include/libxml2 -I/Users/frank/gitrepo/libsbml-build-scripts/common/mac_installer/installer/libsbml-dist/include

Someone should tell Frank. Fix it by replacing the broken settings with
the following:

    prefix=/usr/local
    exec_prefix=${prefix}
    libdir=${exec_prefix}/lib
    includedir=${prefix}/include

Check that `pkg-config` picks the new settings:

    pkg-config --cflags libsbml
    # -I/usr/local/Cellar/libxml2/2.9.10_1/include/libxml2 -I/usr/local/include

#### Install rsbml from source

[NOT CLEAR THIS IS NEEDED] Create a few symlinks:

    cd /usr/local/opt/
    mkdir libsbml
    cd libsbml/
    ln -s ../../include
    ln -s ../../lib

[NOT CLEAR THIS IS NEEDED] In `/etc/profile` add the following line:

    export DYLD_LIBRARY_PATH="/usr/local/lib"

WARNING!!! Unfortunately setting `DYLD_LIBRARY_PATH` to `/usr/local/lib`
will put `/usr/local/lib/libPng.dylib` before
`/System/Library/Frameworks/ImageIO.framework/Versions/A/Resources/libPng.dylib`
and this will break things like `pkg-config` or Python module `h5pyd` with the
following error:

    dyld: Symbol not found: __cg_png_create_info_struct

Note that `/usr/local/lib/libPng.dylib` is a symlink to

    /usr/local/lib/Cellar/libpng/1.6.37/lib/libpng.dylib

that gets created by things like 'brew install cairo'.
See IMPORTANT NOTE in _4.8 Install Open Babel_ section below in this
document for more information.

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to install the rsbml package *from source*:

    library(BiocManager)
    BiocManager::install("rsbml", type="source")


### 4.7 Install CMake

OCT 2020: This is no longer needed. We used to need this only for compiling
Open Babel from source (Open Babel is needed by the ChemmineOB package).

Home page: https://cmake.org/

Let's make sure it's not already installed:

    which cmake

Note that installing CMake via Homebrew (`brew install cmake`) should be
avoided. In our experience, even though it leads to a `cmake` command that
works at the beginning, it might break in the future (and it has in our case)
as we install more and more components to the machine. So, if for any reason
you already have a brewed CMake on the machine, make sure to remove it:

    brew uninstall cmake

Then:

    cd ~/Downloads/
    curl -LO https://github.com/Kitware/CMake/releases/download/v3.16.5/cmake-3.16.5-Darwin-x86_64.dmg
    sudo hdiutil attach cmake-3.16.5-Darwin-x86_64.dmg
    cp -ri /Volumes/cmake-3.16.5-Darwin-x86_64/CMake.app /Applications/
    sudo hdiutil detach /Volumes/cmake-3.16.5-Darwin-x86_64

Then in `/etc/profile` *prepend* `/Applications/CMake.app/Contents/bin`
to `PATH`, or, if the file as not line setting `PATH` already, add the
following line:

    export PATH="/Applications/CMake.app/Contents/bin:$PATH"

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which cmake
    cmake --version


### 4.8 Install Open Babel

The ChemmineOB package requires Open Babel 3. Note that the Open Babel
website seems very outdated:

    http://openbabel.org/

The latest news reported in the News feed is from 2016-09-21 (as of
Oct 23rd, 2020) and it announces the release of Open Babel 2.4.0!
However, there seems to be a version 3.0. It's on GitHub:
https://github.com/openbabel/openbabel

Before anything else, do:

    python3 --version

and record the current version of Python 3. This is the version that
we installed earlier with all the modules required for the builds.
This is our primary Python 3 installation.

The brew formulae (`3.1.1_1` as of Oct 23rd, 2020) will install a bunch
of dependencies e.g. `python@3.9`, `glib`, `cairo`, `eigen`, and possibly
many more (e.g. `libpng`, `freetype`, `fontconfig`, `gettext`, `libffi`,
`pcre`, `lzo`, `sqlite`, `pixman`) depending on what's already installed:

    brew install eigen
    brew install open-babel

If another Python 3 was already installed via `brew` (e.g. `python@3.8`),
then `python@3.9` will get installed as keg-only because it's an alternate
version of another formulae. This means it doesn't get put on the `PATH`.
Check this with:

    python3 --version

Hopefully this will still display the version of our primary Python 3
installation.

IMPORTANT NOTE: The automatic installation of `libpng` triggered by
`brew install open-babel` can break `pkg-config` and some other things
like Python 3 module `h5pyd`:

    pkg-config
    # dyld: Symbol not found: __cg_png_create_info_struct
    #   Referenced from: /System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO
    #   Expected in: /usr/local/lib/libPng.dylib
    #  in /System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO
    # Abort trap: 6

    python3
    # Python 3.8.6 (default, Oct 27 2020, 08:56:44) 
    # [Clang 11.0.0 (clang-1100.0.33.17)] on darwin
    # Type "help", "copyright", "credits" or "license" for more information.
    >>> import h5pyd
    # Traceback (most recent call last):
    # ...
    # from _scproxy import _get_proxy_settings, _get_proxies
    # ImportError: dlopen(/usr/local/Cellar/python@3.8/3.8.6_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/lib-dynload/_scproxy.cpython-38-darwin.so, 2): Symbol not found: __cg_png_create_info_struct
    #   Referenced from: /System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO
    #   Expected in: /usr/local/lib/libPng.dylib
    #  in /System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO

This will happen if `DYLD_LIBRARY_PATH` is set to `/usr/local/lib` so make
sure that this is not the case. Note that we used to need this setting for
Bioconductor package rsbml but luckily not anymore (rsbml is no longer
supported on macOS).

Initial testing:

    which obabel  # /usr/local/bin/obabel
    obabel -V
    # dyld: Library not loaded: /usr/local/opt/boost/lib/libboost_iostreams-mt.dylib
    #   Referenced from: /usr/local/bin/obabel
    #   Reason: image not found
    # Abort trap: 6

This suggests that the current `3.1.1_1` formulae is buggy (it doesn't
properly specify its dependencies).

Install `boost` (this will install `icu4c` if not already installed):

    brew install boost

Finally create the following symlink:

    cd /usr/local/lib
    ln -s ../Cellar/open-babel/3.1.1_1/lib openbabel3

TESTING:

    obabel -V
    # Open Babel 3.1.0 -- Oct 21 2020 -- 21:57:42  # version looks wrong!
    
    pkg-config --cflags openbabel-3
    # -I/usr/local/Cellar/open-babel/3.1.1_1/include/openbabel3
    
    pkg-config --libs openbabel-3
    # -L/usr/local/Cellar/open-babel/3.1.1_1/lib -lopenbabel

Then try to install ChemmineOB from source. From R:

    library(BiocManager)
    BiocManager::install("ChemmineOB", type="source")


### 4.9 Install Clustal Omega

There is a standalone Mac binary at http://www.clustal.org/omega/
Downnload it with:

    cd ~/Downloads/
    curl -O http://www.clustal.org/omega/clustal-omega-1.2.3-macosx

Make it executable with:

    chmod +x clustal-omega-1.2.3-macosx

Move it to `/usr/local/bin` with:

    mv -i clustal-omega-1.2.3-macosx /usr/local/bin/

Create clustalo symlink in `/usr/local/bin/` with:

    cd /usr/local/bin/
    ln -s clustal-omega-1.2.3-macosx clustalo

Then:

    which clustalo

TESTING: Try to build the LowMACA package (takes about 5 min):

    cd ~/bbs-3.14-bioc/meat/
    R CMD build LowMACA


### 4.10 Install the MySQL client

Note that we only need this for the ensemblVEP package. RMySQL doesn't need
it as long as we can install the binary package.

Even though we only need the MySQL client, we used to install the MySQL
Community Server because it was an easy way to get the MySQL client.
Not anymore! Our attempt to use the recent binaries available at
https://dev.mysql.com/downloads/ for macOS Mojave gave us too much
headache when trying to install Perl module DBD::mysql or install RMySQL
from source. So we switched to installing the MySQL client only via brew:

    brew install mysql-client

Then in `/etc/profile` append `/usr/local/opt/mysql-client/bin` to `PATH`
and `/usr/local/opt/mysql-client/lib/pkgconfig` to `PKG_CONFIG_PATH`.

Finally, make sure that you have a brewed `openssl` (`brew install openssl`,
see above in this file) and create the following symlinks (without them
`sudo cpan install DBD::mysql` won't be able to find the `ssl` or `crypto`
libraries and will fail):

    cd /usr/local/opt/mysql-client/lib/
    ln -s /usr/local/opt/openssl/lib/libssl.dylib
    ln -s /usr/local/opt/openssl/lib/libcrypto.dylib


--------------------------------------------------------------------------
NO LONGER NEEDED (kept for the record only)

Installing the MySQL Community Server

Download `mysql-8.0.0-dmr-osx10.11-x86_64.dmg` from:

    https://downloads.mysql.com/archives/community/

e.g. with:

    cd ~/Downloads/
    curl -O https://downloads.mysql.com/archives/get/file/mysql-8.0.0-dmr-osx10.11-x86_64.dmg

Install with:

    sudo hdiutil attach mysql-8.0.18-macos10.14-x86_64.dmg
    sudo installer -pkg /Volumes/mysql-8.0.18-macos10.14-x86_64/mysql-8.0.18-macos10.14-x86_64.pkg -target /
    sudo hdiutil detach /Volumes/mysql-8.0.18-macos10.14-x86_64
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then in `/etc/profile` append `/usr/local/mysql/bin` to `PATH`,
`/usr/local/mysql/lib` to `DYLD_LIBRARY_PATH`, and
`/usr/local/mysql/lib/pkgconfig` to `PKG_CONFIG_PATH`.

And finally (needed only for some MySQL builds that seem broken):

    cd /usr/local/mysql/lib/
    otool -L libmysqlclient.21.dylib
    otool -l libmysqlclient.21.dylib  # look for path in LC_RPATH section
    install_name_tool -add_rpath /usr/local/mysql/lib libmysqlclient.21.dylib

    #install_name_tool -change @rpath/libmysqlclient.21.dylib /usr/local/mysql/lib/libmysqlclient.21.dylib libmysqlclient.21.dylib
    otool -l libmysqlclient.21.dylib  # look for path in LC_RPATH section

--------------------------------------------------------------------------

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which mysql_config  # /usr/local/opt/mysql-client/bin/mysql_config

Then try to install the RMySQL package *from source*:

    library(BiocManager)
    install("RMySQL", type="source")


### 4.11 Install Ensembl VEP script

Required by Bioconductor packages ensemblVEP and MMAPPR2.

Complete installation instructions are at
https://www.ensembl.org/info/docs/tools/vep/script/vep_download.html

#### Install Perl modules

- Make sure the MySQL client is installed on the system (see "Install
  the MySQL client" above in this file).

- According to ensembl-vep README, the following Perl modules are required:
    ```
    ## Needed by both ensemblVEP and MMAPPR2:
    sudo cpan install Archive::Zip
    sudo cpan install File::Copy::Recursive
    sudo cpan install DBI
    sudo cpan install DBD::mysql  # MySQL client needed!
    
    ## Needed by MMAPPR2 only:
    sudo cpan install -f XML::DOM::XPath  # -f to force install despite tests failing
    sudo cpan install IO::String
    sudo cpan install Bio::SeqFeature::Lite
    brew install htslib
    sudo cpan install Bio::DB::HTS::Tabix
    ```

#### Install ensembl-vep

    cd /usr/local/
    sudo git clone https://github.com/Ensembl/ensembl-vep.git
    cd ensembl-vep/
    sudo chown -R biocbuild:admin .
    #git checkout release/100  # select desired branch

    # Avoid the hassle of getting HTSlib to compile because ensemblVEP and
    # MMAPPR2 pass 'R CMD build' and 'R CMD check' without that and that's
    # all we care about. No sudo!
    perl INSTALL.pl --NO_HTSLIB
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

Try to build and check the ensemblVEP and MMAPPR2 packages:

    cd ~/bbs-3.14-bioc/meat/

    R CMD build ensemblVEP
    R CMD check --no-vignettes ensemblVEP_X.Y.Z.tar.gz

    R CMD build MMAPPR2
    R CMD check --no-vignettes MMAPPR2_X.Y.Z.tar.gz


### 4.12 Install ViennaRNA

Required by Bioconductor package GeneGA.

Download with:

    cd ~/Downloads/
    curl -O https://www.tbi.univie.ac.at/RNA/download/osx/macosx/ViennaRNA-2.4.11-MacOSX.dmg

Install with:

    sudo hdiutil attach ViennaRNA-2.4.11-MacOSX.dmg
    sudo installer -pkg "/Volumes/ViennaRNA 2.4.11/ViennaRNA Package 2.4.11 Installer.pkg" -target /
    sudo hdiutil detach "/Volumes/ViennaRNA 2.4.11"
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING:

    which RNAfold  # /usr/local/bin/RNAfold

Then try to build the GeneGA package:

    cd ~/bbs-3.14-bioc/meat/
    R CMD build GeneGA


### 4.13 Set up ImmuneSpaceR package for connecting to ImmuneSpace

In `/etc/profile` add:

    export ISR_login=bioc@immunespace.org
    export ISR_pwd=1notCRAN

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to build the ImmuneSpaceR package:

    cd ~/bbs-3.14-bioc/meat/
    R CMD build ImmuneSpaceR


### 4.14 Install GTK2

Download and install with:

    cd ~/Downloads/
    curl -O https://mac.r-project.org/libs/GTK_2.24.17-X11.pkg
    sudo installer -allowUntrusted -pkg GTK_2.24.17-X11.pkg -target /

TESTING: Try to install and load the RGtk2 **binary** package:

    install.packages("RGtk2", repos="https://cran.r-project.org")
    library(RGtk2)

The following is needed only if CRAN package RGtk2 needs to be installed
from source which is usually NOT the case (most of the time a Mac binary
should be available on CRAN).

Create `pkg-config` symlink in `/usr/local/bin/` with:

    cd /usr/local/bin/
    sudo ln -s /Library/Frameworks/GTK+.framework/Resources/bin/pkg-config

Note that starting with El Capitan, the `/usr/bin` folder is locked,
even for root, so it's not possible to create symlinks in it. See
https://en.wikipedia.org/wiki/System_Integrity_Protection for more
info about that security feature.

Try:

    which pkg-config

Then in `/etc/profile` add the following line:

    export PKG_CONFIG_PATH=/Library/Frameworks/GTK+.framework/Resources/lib/pkgconfig:/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:/usr/X11/lib/pkgconfig

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to install the RGtk2 package *from source*:

    install.packages("RGtk2", type="source", repos="https://cran.r-project.org")


### 4.15 Install Infernal

Required by Bioconductor package inferrnal.

Install with:

    brew tap brewsci/bio
    brew install infernal

TESTING:

    which cmsearch  # /usr/local/bin/cmsearch
    which cmalign   # /usr/local/bin/cmalign
    which cmbuild   # /usr/local/bin/cmbuild

Then try to build the inferrnal package:

    cd ~/bbs-3.14-bioc/meat/
    R CMD build inferrnal


### 4.16 Install mono

Required by Bioconductor package rawrr.

Install with:

    brew install mono

TESTING

    which mono  # /usr/local/bin/mono

Then try to install/build/check the rawrr package:

    cd ~/bbs-3.14-bioc/meat/
    R CMD INSTALL rawrr
    R CMD build rawrr
    R CMD check --no-vignettes rawrr_X.Y.Z.tar.gz


### 4.17 Install macFUSE

Required by Bioconductor package Travel.

Download latest stable release from https://osxfuse.github.io/ e.g.:

    cd ~/Downloads/
    curl -LO https://github.com/osxfuse/osxfuse/releases/download/macfuse-4.0.5/macfuse-4.0.5.dmg

Install with:

    sudo hdiutil attach macfuse-4.0.5.dmg
    sudo installer -pkg "/Volumes/macFUSE/Install macFUSE.pkg" -target /
    sudo hdiutil detach /Volumes/macFUSE

TESTING: Try to install the Travel package *from source*:

    library(BiocManager)
    BiocManager::install("Travel", type="source")


### 4.18 Install .NET 5.0 Runtime

Required by Bioconductor package rmspc.

#### Install the runtime

Visit https://docs.microsoft.com/en-us/dotnet/core/install/macos. Download and
install the 5.0 .NET runtime corresponding to the build system's macOS.

    curl -O https://download.visualstudio.microsoft.com/download/pr/a847df19-d530-41c8-b766-cb60ee8af9a4/7edd7c2eae38d25d0d7c90350eefea64/dotnet-runtime-5.0.9-osx-x64.pkg
    shasum -a 512 dotnet-runtime-5.0.9-osx-x64.pkg
    sudo installer -pkg dotnet-runtime-5.0.9-osx-x64.pkg -target /

#### Testing

You might need to logout and login again before trying this:

    cd ~/bbs-3.14-bioc/meat/
    R CMD build rmspc
    R CMD check --no-vignettes rmspc_X.Y.Z.tar.gz


### 4.19 [OPTIONAL] Install autoconf & automake

MAY 2020: Who needs this? Is this still needed?

Install with:

    brew install autoconf
    brew install automake

TESTING:

    which autoconf
    which automake

Then try to install the flowWorkspace package *from source*:

    library(BiocManager)
    BiocManager::install("flowWorkspace", type="source")


### 4.20 [OPTIONAL] Install ImageMagick

APRIL 2019: THIS SHOULD NO LONGER BE NEEDED! (was required by the flowQ
package, which is now officially deprecated)

WARNING: Don't do 'brew install imagemagick'. This will install the jpeg-8d
lib on top of the previously installed jpeg-9 lib!!!
So we install a pre-built ImageMagick binary for El Capitan. Note that
these pre-built binaries seem very broken and need a bunch of symlinks
in order to work!

Download and install with:

    cd ~/Downloads/
    curl -O https://www.imagemagick.org/download/binaries/ImageMagick-x86_64-apple-darwin16.4.0.tar.gz
    sudo tar zxvf ImageMagick-x86_64-apple-darwin16.4.0.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then in `/etc/profile` add the following line (before the `PATH` and
`DYLD_LIBRARY_PATH` lines):

    export MAGICK_HOME="/ImageMagick-7.0.5"

and append `$MAGICK_HOME/bin`, `$MAGICK_HOME/lib`, and
`$MAGICK_HOME/lib/pkgconfig` to `PATH`, `DYLD_LIBRARY_PATH`,
and `PKG_CONFIG_PATH`, respectively.

Logout and login again so that the changes to `/etc/profile` take effect.

Then create a bunch of symlinks:

    cd /usr/local/include/
    ln -s $MAGICK_HOME/include/ImageMagick-7
    cd /usr/local/etc/
    ln -s $MAGICK_HOME/etc/ImageMagick-7
    cd /usr/local/share/
    ln -s $MAGICK_HOME/share/ImageMagick-7
    cd /usr/local/share/doc/
    ln -s $MAGICK_HOME/share/doc/ImageMagick-7

    ## this creates 10 symlinks in /usr/local/lib
    cd /usr/local/lib/
    ln -s $MAGICK_HOME/lib/ImageMagick-7.0.5
    for lib in libMagick++-7 libMagickCore-7 libMagickWand-7; do
      ln -s $MAGICK_HOME/lib/$lib.Q16HDRI.0.dylib
      ln -s $MAGICK_HOME/lib/$lib.Q16HDRI.dylib
      ln -s $MAGICK_HOME/lib/$lib.Q16HDRI.la
    done

TESTING:

    which magick
    magick logo: logo.gif
    identify logo.gif
    identify <some-PDF-file>  # important test! (flowQ uses this)
    #display logo.gif         # fails but flowQ does not use this

Then try to build the flowQ package (the package makes system calls to
standalone commands `convert`, `identify`, and `montage`):

    cd ~/bbs-3.14-bioc/meat/
    R CMD build flowQ



## 5. Set up other builds


### 5.1 Annotation builds

Not run on Mac at the moment.


### 5.2 Experimental data builds

Not run on Mac at the moment.


### 5.3 Worflows builds

From the biocbuild account:

    mkdir -p ~/bbs-3.14-workflows/log

Then add the following entry to biocbuild's crontab:

    # BIOC 3.14 WORKFLOWS BUILDS
    # --------------------------
    
    00 09 * * 2,5 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.14/workflows/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.14-workflows/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'


### 5.4 Books builds

Not run on Mac at the moment.


### 5.5 Long Tests builds

From the biocbuild account:

    mkdir -p ~/bbs-3.14-bioc-longtests/log

Then add the following entry to biocbuild's crontab:

    # BIOC 3.14 SOFTWARE LONGTESTS BUILDS
    # -----------------------------------
    
    00 16 * * 6 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.14/bioc-longtests/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.14-bioc-longtests/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

