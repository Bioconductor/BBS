# How to set up a macOS Mojave machine for the daily builds



## 1. Initial setup (from administrator account)


This section describes the very first steps that need to be performed on
a pristine macOS Mojave installation (e.g. after creating a Mac instance on
MacStadium). Skip them and go directly to the next section if the biocbuild
account was created by someone else and if the devteam member public keys were
already installed.

Perform all the steps in this section from the administrator account (the only
account that should exist at this point).


### Set the hostnames

    sudo scutil --set ComputerName machv2
    sudo scutil --set LocalHostName machv2
    sudo scutil --set HostName machv2.bioconductor.org

TESTING:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername


### Set DNS servers

    sudo networksetup -setdnsservers 'Ethernet 1' 216.126.35.8 216.24.175.3 8.8.8.8

TESTING:

    networksetup -getdnsservers 'Ethernet 1'
    ping www.bioconductor.org


### Apply all software updates

    softwareupdate -l                  # to list all software updates
    sudo softwareupdate -ia --verbose  # install them all
    sudo reboot                        # reboot

TESTING: After reboot, check that the machine is running the latest release
of macOS Mojave i.e. 10.14.6. Check this with:

    system_profiler SPSoftwareDataType
    uname -a  # should show xnu-4903.278.25~1 (or higher)


### Create biocbuild account

    sudo dscl . -create /Users/biocbuild
    sudo dscl . -create /Users/biocbuild UserShell /bin/bash
    sudo dscl . -create /Users/biocbuild UniqueID "505"
    sudo dscl . -create /Users/biocbuild PrimaryGroupID 20
    sudo dscl . -create /Users/biocbuild NFSHomeDirectory /Users/biocbuild
    sudo dscl . -passwd /Users/biocbuild <password_for_biocbuild>
    sudo dscl . -append /Groups/admin GroupMembership biocbuild
    sudo cp -R /System/Library/User\ Template/English.lproj /Users/biocbuild
    sudo chown -R biocbuild:staff /Users/biocbuild


### Install devteam member public keys in biocbuild account

  TESTING: Logout and try to login again as biocbuild. From now on, you should
  never need the administrator account again. Do everything from the biocbuild
  account.



## 2. Check hardware, OS, and connectivity with central build node


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

If biocbuild doesn't belong to the admin group, then you can add with the
following command from your personal account (granted you belong to the
admin group, which you should) or from the administrator account:

    sudo dseditgroup -o edit -a biocbuild -t user admin

From now on everything must be done from the biocbuild account.


### Hardware requirements for running the BioC software builds

                          strict minimum  recommended
    Nb of logical cores:               8           16
    Memory:                         16GB         32GB

  Hard drive: 256GB if the plan is to run BBS only on the machine. More (e.g.
  512GB) if the plan is to also run the Single Package Builder.

Check nb of logical cores with:

    sysctl -n hw.ncpu

Check amount of RAM with:

    system_profiler SPHardwareDataType

Check hard drive with:

    system_profiler SPStorageDataType

Make sure the machine is running the latest release of macOS Mojave:

    system_profiler SPSoftwareDataType

If not, use your your personal account or the administrator account to
update to the latest with:

    sudo softwareupdate -ia --verbose

and reboot the machine.

Check the kernel version (should be Darwin 18 for macOS Mojave):

    uname -sr


### Connectivity

Check that you can ping the central build node. Depending on whether the
node you're ping'ing from is within RPCI's DMZ or not, use its short or
long (i.e. hostname+domain) hostname. For example:

    ping malbec2                   # from within RPCI's DMZ
    ping malbec2.bioconductor.org  # from anywhere else

Check that you can ssh to the central build node:

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    machv2:~ biocbuild$ ls -l .BBS/id_rsa
    -r--------  1 biocbuild  staff  884 Jan 12 12:19 .BBS/id_rsa

Then try to ssh to the central build node e.g.

    ssh -i .BBS/id_rsa malbec2                   # from within RPCI's DMZ
    ssh -i .BBS/id_rsa malbec2.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec2.bioconductor.org port 22: Operation timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>


### Check that you can send HTTPS requests to the central node

    curl http://malbec2.bioconductor.org

If this is blocked by RPCI's firewall, after a while you'll get:

    curl: (7) Failed connect to malbec2.bioconductor.org:80; Operation timed out

Contact the IT folks at RPCI if that's the case (see above). More details
on https implementation in `BBS/README.md`.



## 3. Install the developer tools and other core components needed by the builds


Everything in this section must be done from the biocbuild account.


### Install the Command Line Developer Tools

You only need this for the `ld`, `make`, and `clang` commands. Check whether
you already have them or not with:

    which ld     # /usr/bin/ld
    which make   # /usr/bin/make
    which clang  # /usr/bin/clang
    clang -v     # Apple LLVM version 10.0.1

If you do, skip this section.

--------------------------------------------------------------------------
The Command Line Developer Tools is a subset of Xcode that includes Apple
LLVM compiler (with Clang front-end), linker, Make, and other developer
tools that enable Unix-style development at the command line. It's all
that is needed to install/compile R packages with native code in them (note
that it even includes the svn and git clients).

The full Xcode IDE is much bigger (2.6G vs 103M) and is not needed.

IMPORTANT NOTE: For R 3.4, the CRAN folks actually decided to use a different
set of compilers for compiling R and packages with C and/or C++ code. So we
do the same, but we still need the Command Line Developer Tools for the `ld`
(linker) and `make` commands.

Go on https://developer.apple.com/ and pick up the last version for
macOS Mojave.

Install with:

    sudo hdiutil attach Command_Line_Tools_macOS_10.11_for_Xcode_8.2.dmg
    sudo installer -pkg "/Volumes/Command Line Developer Tools/Command Line Tools (macOS El Capitan version 10.11).pkg" -target /
    sudo hdiutil detach "/Volumes/Command Line Developer Tools"

TESTING:

    which make   # /usr/bin/make
    which clang  # /usr/bin/clang
    clang -v     # Apple LLVM version 10.0.1
--------------------------------------------------------------------------


### Install the C and C++ compilers used by the CRAN folks

This should no longer be needed. Last news is that Simon is planning to
use Apple clang from Xcode for the R-4.0 builds.

--------------------------------------------------------------------------
The CRAN folks use the clang version provided here:

    https://cran.r-project.org/bin/macosx/tools/

to compile R and produce binary packages on Mac.

So for example, for R 4.0, download and install with:

    curl -O https://cran.r-project.org/bin/macosx/tools/clang-8.0.0.pkg
    sudo installer -pkg clang-8.0.0.pkg -target /
    sudo chown -R biocbuild:admin /usr/local

Then in `/etc/profile` *prepend* `/usr/local/clang8/bin` to `PATH`.

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect.

    which clang  # /usr/local/clang8/bin/clang
    clang -v     # clang version 8.0.0
--------------------------------------------------------------------------


### Install gfortran

Simon uses Coudert's gfortran 8.2: https://github.com/fxcoudert/gfortran-for-macOS/releases

Download with:

    curl -OL https://github.com/fxcoudert/gfortran-for-macOS/releases/download/8.2/gfortran-8.2-Mojave.dmg

Install with:

    sudo hdiutil attach gfortran-8.2-Mojave.dmg
    sudo installer -pkg /Volumes/gfortran-8.2-Mojave/gfortran-8.2-Mojave/gfortran.pkg -target /
    sudo hdiutil detach /Volumes/gfortran-8.2-Mojave
    sudo chown -R biocbuild:admin /usr/local

TESTING:

    gfortran -v

Finally check that the gfortran libraries got installed in
`/usr/local/gfortran/lib` and make sure that `LOCAL_FORTRAN_DYLIB_DIR`
in `BBS/utils/macosx-inst-pkg.sh` points to this location.
Otherwise  we will produce broken binaries again (see
https://support.bioconductor.org/p/95587/#95631).


### Install XQuartz

Download it from https://xquartz.macosforge.org/

    curl -OL https://dl.bintray.com/xquartz/downloads/XQuartz-2.7.11.dmg

Install with:

    sudo hdiutil attach XQuartz-2.7.11.dmg
    sudo installer -pkg /Volumes/XQuartz-2.7.11/XQuartz.pkg -target /
    sudo hdiutil detach /Volumes/XQuartz-2.7.11
    cd /usr/local/include
    ln -s /opt/X11/include/X11 X11

TESTING: Logout and login again so that the changes made by the installer
to the `PATH` take effect. Then:

    which Xvfb        # should be /opt/X11/bin/Xvfb
    ls -l /usr/X11    # should be a symlink to /opt/X11


### Run Xvfb as service

`Xvfb` is run as global daemon controlled by launchd. We run this as a daemon
instead of an agent because agents are run on behalf of the logged in user
while a daemon runs in the background on behalf of the root user (or any user
you specify with the 'UserName' key).

    man launchd
    man launchctl

#### Create plist file

The plist files in `/Library/LaunchDaemons` specify how applications are
called and when they are started. We'll call our plist `local.xvfb.plist`.

    cd /Library/LaunchDaemons
    sudo vim local.xvfb.plist

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
the plist file. Logs are rotated with newsyslog and the config is in
`/etc/newsyslog.d/`.

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

NOTE: For testing, set `KeepAlive` to `false` in the plist file. Once
testing is done, reset the key to `true`.

The `RunAtLoad` directive in the plist file says to start the service
at boot. To test the service without a re-boot use the `start` and
`stop` commands with the service label.

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

When `KeepAlive` is set to 'true' in the plist file, the service will
be restarted if killed with:

    sudo kill -9 <PID>

If you really need to kill the service, change `KeepAlive` to `false`
in the plist, then kill the process.

#### Testing X11 from R

There are two scripts in `/Users/biocbuild/sandbox` for testing:

    merida2:sandbox biocbuild$ ls testX11*
    testX11.R	testX11.sh

Running the shell script when the `Xvfb` service is running should
result in output of "SUCCESS!":

    merida2:sandbox biocbuild$ ./testX11.sh
    [1] "SUCCESS!"


### Install Homebrew

First make sure `/usr/local` is writable by the `biocbuild` user and other
members of the `admin` group:

    sudo chown -R biocbuild:admin /usr/local

Then install with:

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

TESTING:

    brew doctor


### Install Python 3

    brew install python3

TESTING:

    python3 --version


### Install Python 3 module psutil

This module is needed by BBS.

    pip3 install psutil


### Install XZ Utils (includes lzma lib)

    brew install xz


### Install openssl

    brew install openssl

Then in `/etc/profile` add the following line, replacing '1.1.1d' with
the version installed:

    export OPENSSL_LIBS="/usr/local/Cellar/openssl@1.1/1.1.1d/lib/libssl.a /usr/local/Cellar/openssl@1.1/1.1.1d/lib/libcrypto.a"

This will trigger statically linking of the rtracklayer package against the
openssl libraries.


### [OPTIONAL] Install wget and pstree

These are just convenient to have when working interactively on a build
machine but are not required by the daily builds or propagation pipe.

Install with:

    brew install wget
    brew install pstree



## 4. Install BBS git tree and create bbs-3.y-bioc directory structure

Everything in this section must be done from the biocbuild account.


### Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS


### Compile chown-rootadmin

    cd ~/BBS/utils
    gcc chown-rootadmin.c -o chown-rootadmin
    sudo chown root:admin chown-rootadmin
    sudo chmod 4750 chown-rootadmin

TESTING: Check that the permissions on chown-rootadmin look like this:

    machv2:utils biocbuild$ ls -al chown-rootadmin
    -rwsr-x---  1 root  admin  8596 Jan 13 12:55 chown-rootadmin


### Create bbs-3.11-bioc directory structure

    cd
    mkdir bbs-3.11-bioc
    cd bbs-3.11-bioc
    mkdir log



## 5. Install R


This must be done from the `biocbuild` account.

If this is a new version of R on a builder rather than setting up R
for the first time, Remove the old R.framework directory.  This allows
for a clean install of R and removes the old version
`/Library/Frameworks/R.framework`.

If installing R devel: download R from https://mac.r-project.org/ (pick up
R-4.0-branch.pkg)

If installing R release: download R from CRAN (e.g. from
https://cloud.r-project.org/bin/macosx/). Pick up the 1st file
(e.g. R-3.6.3.pkg).

Download and install with:

    cd /Users/biocbuild/Downloads
    curl -LO https://mac.r-project.org/high-sierra/R-4.0-branch/R-4.0-branch.pkg

    sudo installer -pkg R-4.0-branch.pkg -target /

Note that, unlike what we do on the Linux and Windows builders, this is a
*system-wide* installation of R i.e. it can be started with `R` from any
account.

TESTING: Start the virtual X server, start R, and check X11:

    # From R
    capabilities()[["X11"]]  # should be TRUE
    X11()                    # nothing visible should happen
    q("no")

Then start R again and try to install a few packages *from source*:

    # CRAN packages
    # contains C++ code:
    install.packages("Rcpp", type="source", repos="https://cran.r-project.org")
    # contains Fortran code
    install.packages("minqa", type="source", repos="https://cran.r-project.org")
    # always good to have; try this even if CRAN binaries are not available
    install.packages("devtools", type="source", repos="https://cran.r-project.org")

    # Bioconductor packages
    install.packages("BiocManager", type="source", repos="https://cran.r-project.org")
    library(BiocManager)
    ## ONLY if release and devel are using the same version of R:
    BiocManager::install(version="devel")
    BiocManager::install("BiocCheck", type="source")
    BiocManager::install("rtracklayer", type="source")
    BiocManager::install("VariantAnnotation", type="source")

Quit R and check that rtracklayer got statically linked against the openssl
libraries with:

    otool -L /Library/Frameworks/R.framework/Resources/library/rtracklayer/libs/rtracklayer.so

WAIT!!! II'S NOT FINISHED YET! Now go to the "How to update R" section at the
end of this file and perform all steps from step 3.



## 6. Install MacTeX & Pandoc


Everything in this section should be done from the biocbuild account.


### Install MacTeX

Home page: https://www.tug.org/mactex/

Download:

    https://tug.org/mactex/mactex-download.html

On March 2020 the above paage was displaying "Downloading MacTeX 2019".

    cd /Users/biocbuild/Downloads
    curl -LO https://tug.org/cgi-bin/mactex-download/MacTeX.pkg

Install with:

    sudo installer -pkg MacTeX.pkg -target /

TESTING: Logout and login again so that the changes made by the installer
to the `PATH` take effect. Then:

    which tex

This is no longer needed (as of Dec 2019) since no package that uses
pstricks in their vignette should still need to use auto-pst-pdf:

    #Add shell_escape = t to /usr/local/texlive/2018/texmf.cnf
    #
    #  cd /usr/local/texlive/2018/
    #  sudo cp texmf.cnf texmf.cnf.original
    #  sudo vi texmf.cnf
    #  ## add shell_escape = t at the bottom of the file
    #
    # TESTING: Try to build a package using pstricks + auto-pst-pdf in its
    # vignette e.g.:
    #
    #   cd ~/sandbox
    #   git clone https://git.bioconductor.org/packages/affyContam
    #   R CMD build affyContam


### Install Pandoc

Download latest Pandoc from https://github.com/jgm/pandoc/releases/latest
(pick up .pkg file) e.g.:

    curl -LO https://github.com/jgm/pandoc/releases/download/2.9.2.1/pandoc-2.9.2.1-macOS.pkg

Install with:

    sudo installer -pkg pandoc-2.9.2.1-macOS.pkg -target /



## 7. Add crontab entries for daily builds


This must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    55 17 * * * /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.11/bioc/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.11-bioc/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run before
doing so.



## 8. Additional stuff to install for packages with special needs


Everything in this section must be done from the biocbuild account.


### Install Java

Visit https://www.java.com/en/download/faq/develop.xml, then click on the
"JDK downloads" link, then on the big Java DOWNLOAD button, then pick up
the Java SE Development Kit for Mac OS X. It's a big (> 220 MB) .dmg file
named something like jdk-8u191-macosx-x64.dmg

Install with:

    sudo hdiutil attach jdk-8u191-macosx-x64.dmg
    sudo installer -pkg "/Volumes/JDK 8 Update 191/JDK 8 Update 191.pkg" -target /
    sudo hdiutil detach "/Volumes/JDK 8 Update 191"

Then reconfigure R to use this new Java installation:

    sudo R CMD javareconf

TESTING: Try to install the rJava package:

    # install the CRAN binary
    install.packages("rJava", repos="https://cran.r-project.org")
    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")


### Install JPEG system library

Download and install with:

    curl -O https://mac.r-project.org/libs-4/jpeg-9-darwin.17-x86_64.tar.gz
    sudo tar fvxz jpeg-9-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install the jpeg package *from source*:

    install.packages("jpeg", type="source")
    library(jpeg)
    example(readJPEG)
    example(writeJPEG)


### Install TIFF system library

Download and install with:

    curl -O https://mac.r-project.org/libs-4/tiff-4.1.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz tiff-4.1.0-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install the tiff package *from source*:

    install.packages("tiff", type="source")
    library(tiff)
    example(readTIFF)
    example(writeTIFF)


### Install autoconf & automake

Install with:

    brew install autoconf
    brew install automake

TESTING:

    which autoconf
    which automake

Then try to install the flowWorkspace package *from source*:

    library(BiocManager)
    BiocManager::install("flowWorkspace", type="source")


### Install Cairo system library

MARCH 2020: THIS SHOULD NO LONGER BE NEEDED!
With R 4.0 on macOS Mojave, seems like Cairo can be installed from source
without the need to download/install the cairo library from mac.r-project.org
Check this with:

    install.packages("Cairo", type="source")

--------------------------------------------------------------------------
Download and install with:

    curl -O https://mac.r-project.org/libs-4/cairo-1.14.12-darwin.17-x86_64.tar.gz
    sudo tar fvxz cairo-1.14.12-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install and load the Cairo *binary* package:

    install.packages("Cairo")
    library(Cairo)

Note: As of Feb 22, 2017, CRAN still does not provide Mac binary packages
for R 3.4. However, it seems that the Cairo binary made for R 3.3 works
with R 3.4. Install and load with:

    contriburl <- "http://cran.case.edu/bin/macosx/mavericks/contrib/3.3"
    install.packages("Cairo", contriburl=contriburl)
    library(Cairo)
--------------------------------------------------------------------------


### Install NetCDF and HDF5 system library

Download and install with:

    curl -O https://mac.r-project.org/libs-4/netcdf-4.7.3-darwin.17-x86_64.tar.gz
    curl -O https://mac.r-project.org/libs-4/hdf5-1.12.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz netcdf-4.7.3-darwin.17-x86_64.tar.gz -C /
    sudo tar fvxz hdf5-1.12.0-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install the ncdf4 package *from source*:

    install.packages("ncdf4", type="source")

If you have time, you can also try to install the mzR package but be aware
that this takes much longer:

    library(BiocManager)
    BiocManager::install("mzR", type="source")  # takes between 7-10 min


### Install FFTW system library

Download and install with:

    curl -O https://mac.r-project.org/libs-4/fftw-3.3.8-darwin.17-x86_64.tar.gz
    sudo tar fvxz fftw-3.3.8-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install the fftwtools package *from source*:

    install.packages("fftwtools", type="source")


### Install GSL system library

Download and install with:

    curl -O https://mac.r-project.org/libs-4/gsl-2.6-darwin.17-x86_64.tar.gz
    sudo tar fvxz gsl-2.6-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local

TESTING: Try to install the GLAD package *from source*:

    library(BiocManager)
    BiocManager::install("GLAD", type="source")


### Install GTK2

Download and install with:

    curl -O https://mac.r-project.org/libs/GTK_2.24.17-X11.pkg
    sudo installer -allowUntrusted -pkg GTK_2.24.17-X11.pkg -target /

Create `pkg-config` symlink in `/usr/local/bin/` with:

    cd /usr/local/bin
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


### Install Python 3 modules needed by some CRAN/Bioconductor packages

    pip3 install numpy scipy sklearn h5py pandas mofapy
    pip3 install tensorflow tensorflow_probability
    pip3 install h5pyd
    pip3 install cwltool
    pip3 install nbconvert
    pip3 install matplotlib phate

TESTING:

Start python3 and try to import the above modules. Quit.

Try to build the BiocSklearn package (takes < 1 min):

      cd ~/bbs-3.11-bioc/meat
      R CMD build BiocSklearn


### Install JAGS

Download with:

    curl -LO https://sourceforge.net/projects/mcmc-jags/files/JAGS/4.x/Mac%20OS%20X/JAGS-4.3.0.dmg

Install with:

    sudo hdiutil attach JAGS-4.3.0.dmg
    sudo installer -pkg /Volumes/JAGS-4.3.0/JAGS-4.3.0.mpkg -target /
    sudo hdiutil detach /Volumes/JAGS-4.3.0

TESTING: Try to install the rjags package *from source*:

    install.packages("rjags", type="source")


### Install Open Babel

As of May 2017, we want Open Babel 2.4.1 which is the version available
with 'brew install'.

    brew install open-babel

TESTING:

    which babel
    babel -V

Then try to install the ChemmineOB package *from source*:

    library(BiocManager)
    BiocManager::install("ChemmineOB", type="source")


### Install libSBML

libSBML/rsbml require libxml-2.0 >= 2.6.22 but the version that comes with
El Capitan is 2.6.16 so we first need to install a more recent libxml-2.0.
Install a more recent libxml-2.0 with:

    brew install libxml2

Ignore the "This formula is keg-only..." caveat.

In `/etc/profile` *prepend* `/usr/local/opt/libxml2/lib/pkgconfig` to
`PKG_CONFIG_PATH`.

Logout and login again so that the changes to `/etc/profile` take
effect.

Finally install libSBML. As of December 2018, Homebrew was no longer
offering libsbml so we download it from SourceForge.

Download with:

    curl -LO https://sourceforge.net/projects/sbml/files/libsbml/5.13.0/stable/Mac%20OS%20X/libsbml-5.13.0-libxml2-macosx-elcapitan.dmg

Install with:

    sudo hdiutil attach libsbml-5.13.0-libxml2-macosx-elcapitan.dmg
    sudo installer -pkg "/Volumes/libsbml-5.13.0-libxml2/libSBML-5.13.0-libxml2-elcapitan.pkg" -target /
    sudo hdiutil detach "/Volumes/libsbml-5.13.0-libxml2"
    sudo chown -R biocbuild:admin /usr/local

Modify `/usr/local/lib/pkgconfig/libsbml.pc`:

    cd /usr/local/lib/pkgconfig
    cp libsbml.pc libsbml.pc.original

Modify these lines:

    prefix=/usr/local/share/libsbml
    libdir=/usr/local/lib
    includedir=/usr/local/include

TESTING: Try to install the rsbml package *from source*:

    library(BiocManager)
    BiocManager::install("rsbml", type="source")


### Install Clustal Omega

There is a standalone Mac binary at http://www.clustal.org/omega/
Downnload it with:

    curl -O http://www.clustal.org/omega/clustal-omega-1.2.3-macosx

Make it executable with:

    chmod +x clustal-omega-1.2.3-macosx

Move it to `/usr/local/bin` with:

    sudo mv -i clustal-omega-1.2.3-macosx /usr/local/bin/

Create clustalo symlink in `/usr/local/bin/` with:

    cd /usr/local/bin
    sudo ln -s clustal-omega-1.2.3-macosx clustalo

TESTING: Try to build the LowMACA package (takes about 5 min):

    cd ~/bbs-3.11-bioc/meat
    R CMD build LowMACA


### Set up ImmuneSpaceR package for connecting to ImmuneSpace

In `/etc/profile` add:

    export ISR_login=bioc@immunespace.org
    export ISR_pwd=1notCRAN

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to build the ImmuneSpaceR package:

    cd ~/bbs-3.11-bioc/meat
    R CMD build ImmuneSpaceR


### Install Open MPI

Install with:

    brew install open-mpi  # takes between 15-20 min

TESTING: Try to install the Rmpi package *from source*:

    install.packages("Rmpi", type="source")
    library(Rmpi)
    mpi.spawn.Rslaves()
    mpi.parReplicate(100, mean(rnorm(1000000)))
    mpi.close.Rslaves()
    mpi.quit()


### Install MySQL Community Server

Note that we only need this for the ensemblVEP package. RMySQL doesn't need
it as long as we can install the binary package.

Download `mysql-8.0.0-dmr-osx10.11-x86_64.dmg` from:

    https://downloads.mysql.com/archives/community/

e.g. with:

    curl -O https://downloads.mysql.com/archives/get/file/mysql-8.0.0-dmr-osx10.11-x86_64.dmg

Install with:

    sudo hdiutil attach mysql-8.0.0-dmr-osx10.11-x86_64.dmg
    sudo installer -pkg /Volumes/mysql-8.0.0-dmr-osx10.11-x86_64/mysql-8.0.0-dmr-osx10.11-x86_64.pkg -target /
    sudo hdiutil detach /Volumes/mysql-8.0.0-dmr-osx10.11-x86_64
    sudo chown -R biocbuild:admin /usr/local

Then in `/etc/profile` append `/usr/local/mysql/bin` to `PATH`,
`/usr/local/mysql/lib` to `DYLD_LIBRARY_PATH`, and
`/usr/local/mysql/lib/pkgconfig` to `PKG_CONFIG_PATH`.

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which mysql_config

Then try to install the RMySQL package *from source*:

    install.packages("RMySQL", type="source")


### Install Ensembl VEP script

In release 88, the primary script was renamed from "variant_effect_predictor.pl"
to "vep" and the directory structure of the tarball changed. The instructions
in this document are specific for installing versions >= 88.

Complete installation instructions are at
http://www.ensembl.org/info/docs/tools/vep/script/vep_download.html#installer

Move to location:

    cd /usr/local/

Download script:

    git clone https://github.com/Ensembl/ensembl-vep.git

Get correct branch (substitute 96 with desired version):

    cd ensembl-vep
    git pull
    git checkout release/96

Run the installer script:

    sudo perl INSTALL.pl

You may need to install the File::Copy::Recursive perl module:

    sudo cpan install File::Copy::Recursive

Modify the `PATH` and `DYLD_LIBRARY_PATH` variables:

The `/etc/profile` file has read only permissions (factory settings). To save
changes you will need to force save, e.g., with `vi` this is `w!`.

    sudo vi /etc/profile
    export PATH=$PATH:/usr/local/ensembl-vep
    export DYLD_LIBRARY_PATH=/usr/local/lib:/usr/local/ensembl-vep/htslib

Checks:

    echo $PATH
    echo $DYLD_LIBRARY_PATH
    PERL5LIB=/usr/local/ensembl-vep perl -e "use Bio::DB::HTS"
    PERL5LIB=/usr/local/ensembl-vep perl -e "use Bio::DB::HTS::Tabix"

If the above fails and it is not able to be found. The
`/usr/local/ensembl-vep/HTS.bundle` is a binary linked to
`/usr/local/lib/libhts.1.dylib`. The perl `Install.pl` script may create
this bundle in `/usr/local/ensembl-vep/htslib/` and not in `/usr/local/lib`.
Create the following symlink:

    /usr/local/lib/libhts.1.dylib -> /usr/local/ensembl-vep/htslib/libhts.1.dylib


### Install ROOT

xps wants ROOT 5, not 6. Unfortunately, there are no ROOT 5 binaries
for OS X 10.11 and for the version of clang we use on the builders
at https://root.cern.ch/ (well at least that was the case last time I
checked but you should check again). So we need to install from source.

Download source of latest ROOT 5 release (5.34/36):

    curl -O https://root.cern.ch/download/root_v5.34.36.source.tar.gz

Make sure cmake is installed:

    which cmake

If not, install it with:

    brew install cmake

ROOT supports 2 installation methods: "location independent" and "fix
location". Here we do "location independent" installation:

Build with:

    tar zxvf root_v5.34.36.source.tar.gz
    mkdir root_builddir
    cd root_builddir
    # Tell cmake to use clang8 (even though it comes before Apple's clang in
    # the PATH, by default cmake wants to use the latter).
    export CC=/usr/local/clang8/bin/clang
    export CXX=/usr/local/clang8/bin/clang++
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/root -Dgnuinstall=ON -Dfortran=OFF -Dmysql=OFF -Dsqlite=OFF ../root
    cmake --build . -- -j4  # takes about 10-15 min (> 45 min without -j4)

Install with:

    sudo cmake --build . --target install
    sudo chown -R biocbuild:admin /usr/local

Try to start a ROOT interactive session:

    source bin/thisroot.sh
    root  # then quit the session with .q

  #Installing a ROOT 6 pre-compiled binary for OS X 10.11.
  #WARNING: Don't do this! As of Apr 2017, xps can still not be compiled
  #against ROOT 6.
  #Download with:
  #
  #  curl -O https://root.cern.ch/download/root_v6.08.06.macosx64-10.11-clang80.dmg
  #
  #Install with:
  #
  #  sudo hdiutil attach root_v6.08.06.macosx64-10.11-clang80.dmg
  #  sudo installer -pkg /Volumes/root_v6.08.06.macosx64-10.11-clang80/root_v6.08.06.macosx64-10.11-clang80.mpkg -target /
  #  sudo hdiutil detach /Volumes/root_v6.08.06.macosx64-10.11-clang80

Then in `/etc/profile` add the following line (before the `PATH` and
`DYLD_LIBRARY_PATH` lines):

    export ROOTSYS="/usr/local/root"  # do NOT set ROOTSYS, it will break
                                      # xps configure script!

and append `$ROOTSYS/bin` to `PATH` and `$ROOTSYS/lib/root`
to `DYLD_LIBRARY_PATH`.

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which root-config      # /usr/local/root/bin/root-config
    root-config --version  # 5.34/36

Then try to install the xps package *from source*:

    library(BiocManager)
    BiocManager::install("xps", type="source")


### Install ImageMagick

APRIL 2019: THIS SHOULD NO LONGER BE NEEDED! (was required by the flowQ
package, which is now officially deprecated)

WARNING: Don't do 'brew install imagemagick'. This will install the jpeg-8d
lib on top of the previously installed jpeg-9 lib!!!
So we install a pre-built ImageMagick binary for El Capitan. Note that
these pre-built binaries seem very broken and need a bunch of symlinks
in order to work!

Download and install with:

    curl -O https://www.imagemagick.org/download/binaries/ImageMagick-x86_64-apple-darwin16.4.0.tar.gz
    sudo tar zxvf ImageMagick-x86_64-apple-darwin16.4.0.tar.gz -C /
    sudo chown -R biocbuild:admin /ImageMagick-7.0.5

Then in `/etc/profile` add the following line (before the `PATH` and
`DYLD_LIBRARY_PATH` lines):

    export MAGICK_HOME="/ImageMagick-7.0.5"

and append `$MAGICK_HOME/bin`, `$MAGICK_HOME/lib`, and
`$MAGICK_HOME/lib/pkgconfig` to `PATH`, `DYLD_LIBRARY_PATH`,
and `PKG_CONFIG_PATH`, respectively.

Logout and login again so that the changes to `/etc/profile` take effect.

Then create a bunch of symlinks:

    cd /usr/local/include
    ln -s $MAGICK_HOME/include/ImageMagick-7
    cd /usr/local/etc
    ln -s $MAGICK_HOME/etc/ImageMagick-7
    cd /usr/local/share
    ln -s $MAGICK_HOME/share/ImageMagick-7
    cd /usr/local/share/doc
    ln -s $MAGICK_HOME/share/doc/ImageMagick-7

    ## this creates 10 symlinks in /usr/local/lib
    cd /usr/local/lib
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

    cd ~/bbs-3.11-bioc/meat
    R CMD build flowQ


### Install ViennaRNA

Download with:

    curl -O https://www.tbi.univie.ac.at/RNA/download/osx/macosx/ViennaRNA-2.4.11-MacOSX.dmg

Install with:

    sudo hdiutil attach ViennaRNA-2.4.11-MacOSX.dmg
    sudo installer -pkg "/Volumes/ViennaRNA 2.4.11/ViennaRNA Package 2.4.11 Installer.pkg" -target /
    sudo hdiutil detach "/Volumes/ViennaRNA 2.4.11"

TESTING:

    which RNAfold  # /usr/local/bin/RNAfold

Then try to build the GeneGA package:

    cd ~/bbs-3.11-bioc/meat
    R CMD build GeneGA


### Install protobuf system dependencies

MARCH 2020: THIS SHOULD NO LONGER BE NEEDED! (GoogleGenomics is no longer
in Bioconductor)

These are needed for the CRAN RProtoBuf package which was 'Suggested' by
GoogleGenomics.

Install with:

    brew install protobuf



## 9. Additional stuff to install when CRAN Mac binary packages are not available


CRAN has a tradition of making Mac binary packages available at the last minute
before a new R release (new R releases normally happen in Spring). This means
that we need to be able to install many CRAN packages from source on our Mac
builders when the BioC devel builds use R devel. Some of these packages need
the following stuff (all available at https://mac.r-project.org/libs-4/):

    gmp for CRAN package gmp
    udunits for CRAN package units
    #gdal, geos, and xml2 for CRAN package sf

Download and install with:

    curl -O https://mac.r-project.org/libs-4/gmp-6.2.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz gmp-6.2.0-darwin.17-x86_64.tar.gz -C /
    curl -O https://mac.r-project.org/libs-4/udunits-2.2.24-darwin.17-x86_64.tar.gz
    sudo tar fvxz udunits-2.2.24-darwin.17-x86_64.tar.gz -C /
    #curl -O https://mac.r-project.org/libs-4/gdal-2.4.2-darwin.17-x86_64.tar.gz
    #sudo tar fvxz gdal-2.4.2-darwin.17-x86_64.tar.gz -C /
    #curl -O https://mac.r-project.org/libs-4/geos-3.7.2-darwin.17-x86_64.tar.gz
    #sudo tar fvxz geos-3.7.2-darwin.17-x86_64.tar.gz -C /
    #curl -O https://mac.r-project.org/libs-4/xml2-2.9.10-darwin.17-x86_64.tar.gz
    #sudo tar fvxz xml2-2.9.10-darwin.17-x86_64.tar.gz -C /
    sudo chown -R biocbuild:admin /usr/local



## 10. How to update R


Perform the following steps from the biocbuild account:

1. If you have enough disk space (i.e. if available disk space on the `/`
    filesystem is more than the size reported by
    `du -sh /Library/Frameworks/R.framework`)
    then `cd to /Library/Frameworks/` and rename
    `R.framework` -> `R.framework.old`.
    Otherwise, just delete it.

2. See "Install R" section previously in this file for how to install R.

3. Configure R to use the Java installed on the machine:
    ```
    sudo R CMD javareconf
    ```
    TESTING: Try to install the rJava package:
    ```
    # install the CRAN binary
    install.packages("rJava", repos="https://cran.r-project.org")
    ```
    See "Install Java" previously in this file for more testing.

4. TESTING: Try to install the RGtk2 package *from source*:
    ```
    install.packages("RGtk2", type="source", repos="https://cran.r-project.org")
    ```

5. If the builds are using R-devel and CRAN doesn't provide package binaries
    for Mac yet, install the following package binaries (these are the
    Bioconductor deps that are "difficult" to compile from source on Mac,
    as of Dec 2019):
    ```
    pkgs <- c("rJava", "Cairo", "units", "sf", "gsl", "RMySQL", "gdtools",
              "rsvg", "rtfbs", "magick", "rgeos", "V8", "pdftools", "PSCBS",
              "protolite", "RSQLite", "RPostgres", "glpkAPI")
    ```
    First try to install with:
    ```
    install.packages(pkgs, repos="https://cran.r-project.org")
    ```
    It should fail for most (if not all) packages. However, it's still worth
    doing it as it will be able to install many dependencies from source.
    Then try to install the binaries built with the current R release:
    ```
    contriburl <- "https://cran.r-project.org/bin/macosx/el-capitan/contrib/3.6"
    install.packages(pkgs, contriburl=contriburl)
    ```
    Please note that the binaries built with a previous version of R are not
    guaranteed to work with R-devel but if they can be loaded then it's
    **very** likely that they will. So make sure they can be loaded:
    ```
    for (pkg in pkgs) library(pkg, character.only=TRUE)
    ```
    Will probably fail for PSCBS (unless Bioconductor packages aroma.light
    and DNAcopy are already installed, install them if they are not).
    Weird that PSCBS depends on some Bioconductor packages but that somehow
    install.packages() didn't care about missing deps and installed PSCBS
    without reporting any issue!

6. Refresh the cache for AnnotationHub and ExperimentHub: remove all
    of `.AnnotationHub/`, `.AnnotationHubData/`, `.ExperimentHub/` and
    `.ExperimentHubData/` present in `C:\Users\biocbuild\`.

