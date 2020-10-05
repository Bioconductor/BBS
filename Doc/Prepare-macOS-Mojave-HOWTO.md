# How to set up a macOS Mojave machine for the daily builds



## 0. General information and tips


- For how to uninstall Mac packages (`.pkg` files) using native `pkgutil`:
  https://wincent.com/wiki/Uninstalling_packages_(.pkg_files)_on_Mac_OS_X



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
    clang -v     # Apple clang version 11.0.0 (clang-1100.0.33.17)

If you do, skip this section.

--------------------------------------------------------------------------
The Command Line Developer Tools is a subset of Xcode that includes Apple
LLVM compiler (with Clang front-end), linker, Make, and other developer
tools that enable Unix-style development at the command line. It's all
that is needed to install/compile R packages with native code in them (note
that it even includes the svn and git clients).

The full Xcode IDE is much bigger (2.6G vs 220M) and is not needed.

Go on https://developer.apple.com/ and pick up the last version for
macOS Mojave (`Command_Line_Tools_for_Xcode_11.3.1.dmg` as of May 13, 2020,
note that Command Line Tools for Xcode 11.4 requires Catalina or higher).

Install with:

    sudo hdiutil attach Command_Line_Tools_for_Xcode_11.3.1.dmg
    sudo installer -pkg "/Volumes/Command Line Developer Tools/Command Line Tools.pkg" -target /
    sudo hdiutil detach "/Volumes/Command Line Developer Tools"

TESTING:

    which make   # /usr/bin/make
    which clang  # /usr/bin/clang
    clang -v     # Apple clang version 11.0.0 (clang-1100.0.33.17)
--------------------------------------------------------------------------


### Install gfortran

Simon uses Coudert's gfortran 8.2: https://github.com/fxcoudert/gfortran-for-macOS/releases

Download with:

    cd ~/Downloads
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


### Install XQuartz

Download it from https://xquartz.macosforge.org/

    cd ~/Downloads
    curl -LO https://dl.bintray.com/xquartz/downloads/XQuartz-2.7.11.dmg

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

#### Testing X11 from R

There are two scripts in `/Users/biocbuild/sandbox` for testing:

    merida2:sandbox biocbuild$ ls testX11*
    testX11.R	testX11.sh

Running the shell script when the `Xvfb` service is running should
result in output of "SUCCESS!":

    merida2:sandbox biocbuild$ ./testX11.sh
    [1] "SUCCESS!"


### Install CMake

MAY 2020: We only need this for compiling Open Babel from source at the moment
(Open Babel is needed by the ChemmineOB package).

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

    cd ~/Downloads
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


### Install Homebrew

First make sure `/usr/local` is writable by the `biocbuild` user and other
members of the `admin` group:

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then install with:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

TESTING:

    brew doctor


### Install Python 3

    brew install python3

Some python3 deps (e.g. openssl, readline, sqlite) will be installed
as keg-only. This is expected and should not be a problem.

TESTING:

    python3 --version  # Python 3.7.7


### Install Python 3 module psutil

This module is needed by BBS.

    pip3 install psutil


### Install Python3 module virtualenv

This module is needed by the SPB. Module venv has subtle differences that
have proven problematic.

    pip3 install virtualenv


### Install XZ Utils (includes lzma lib)

    brew install xz


### Install openssl

Installing Python 3 should have taken care of this already but you still
need to manually edit `/etc/profile` as instructed below.

    brew install openssl

Then in `/etc/profile`:

- Append `/usr/local/opt/openssl@1.1/bin` to `PATH`.

- Add `/usr/local/opt/openssl@1.1/lib/pkgconfig` to `PKG_CONFIG_PATH`.

- Add the following line, replacing '1.1.1g' with the version installed:
    ```
    export OPENSSL_LIBS="/usr/local/Cellar/openssl@1.1/1.1.1g/lib/libssl.a /usr/local/Cellar/openssl@1.1/1.1.1g/lib/libcrypto.a"
    ```
  This will trigger statically linking of the rtracklayer package against
  the openssl libraries.


### [OPTIONAL] Install wget and pstree

These are just convenient to have when working interactively on a build
machine but are not required by the daily builds or propagation pipe.

Install with:

    brew install wget
    brew install pstree



## 4. Clone BBS git tree and create bbs-3.y-bioc directory structure


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


### Install the latest R binary for macOS

Remove the previous R installation:

    sudo rm -rf /Library/Frameworks/R.framework

If installing R devel: download R from https://mac.r-project.org/ (e.g.
pick up `R-4.0-branch.pkg`)

If installing R release: download R from CRAN (e.g. from
https://cloud.r-project.org/bin/macosx/). Pick up the 1st file
(e.g. `R-3.6.3.pkg`).

Download and install with:

    cd ~/Downloads
    curl -O https://cloud.r-project.org/bin/macosx/R-4.0.0.pkg
    sudo installer -pkg R-4.0.0.pkg -target /

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
    # contains Fortran code:
    install.packages("minqa", type="source", repos="https://cran.r-project.org")
    # always good to have; try this even if CRAN binaries are not available
    install.packages("devtools", type="source", repos="https://cran.r-project.org")

    # Bioconductor packages

    install.packages("BiocManager", repos="https://cran.r-project.org")
    library(BiocManager)
    ## ONLY if release and devel are using the same version of R:
    BiocManager::install(version="devel")

    BiocManager::install("BiocCheck", type="source")
    BiocManager::install("rtracklayer", type="source")
    BiocManager::install("VariantAnnotation", type="source")

Quit R and check that rtracklayer got statically linked against the openssl
libraries with:

    otool -L /Library/Frameworks/R.framework/Resources/library/rtracklayer/libs/rtracklayer.so


### Configure R to use the Java installed on the machine

    sudo R CMD javareconf

TESTING: See "Install Java" below in this file for how to test Java/rJava.


### Try to install RGtk2 from source

    install.packages("RGtk2", type="source", repos="https://cran.r-project.org")

See "Install GTK2" below in this file for what to install in order to
compile RGtk2.


### Refresh the cache for AnnotationHub and ExperimentHub

It is still best practice to remove the cache occassionally to ensure 
resources are still available.

Remove AnnotationHub and ExperimentHub caches present in `/Users/biocbuild/Library/Caches/`.

Should we remove package specific caches? 

### Known issues and workarounds

#### What if CRAN doesn't provide package binaries for macOS yet?

If the builds are using R-devel and CRAN doesn't provide package binaries
for Mac yet, install the following package binaries (these are the
Bioconductor deps that are "difficult" to compile from source on Mac,
as of Dec 2019):

    pkgs <- c("rJava", "Cairo", "units", "sf", "gsl", "RMySQL",
              "gdtools", "rsvg", "magick", "rgeos", "V8", "pdftools",
              "protolite", "RSQLite", "RPostgres", "glpkAPI")

First try to install with:

    install.packages(pkgs, repos="https://cran.r-project.org")

It should fail for most (if not all) packages. However, it's still worth
doing it as it will be able to install many dependencies from source.
Then try to install the binaries built with the current R release:

    contriburl <- "https://cran.r-project.org/bin/macosx/el-capitan/contrib/3.6"
    install.packages(pkgs, contriburl=contriburl)

Please note that the binaries built with a previous version of R are not
guaranteed to work with R-devel but if they can be loaded then it's
**very** likely that they will. So make sure they can be loaded:

    for (pkg in pkgs) library(pkg, character.only=TRUE)

Will probably fail for PSCBS (unless Bioconductor packages aroma.light
and DNAcopy are already installed, install them if they are not).
Weird that PSCBS depends on some Bioconductor packages but that somehow
`install.packages()` didn't care about missing deps and installed PSCBS
without reporting any issue!

#### Compilation issue with Rcpp 1.0.4

Some Rcpp clients (e.g. mzR, msa, csaw, BiocNeighbors, DropletUtils, and about
20 more Bioconductor software packages) won't compile with R 4.0.0 alpha and
the Rcpp version currently on CRAN (version 1.0.4). For example:

    library(BiocManager)
    install("BiocNeighbors", type="source")
    # will fail with
    #   error: unknown type name 'uuid_t'; did you mean 'uid_t'?

The issue is addressed in the GitHub version of Rcpp so the workaround is
to re-install Rcpp from GitHub:

    library(BiocManager)
    install("RcppCore/Rcpp")

TESTING: Try to install BiocNeighbors from source again.

#### The nasty fonts/XQuartz issue on macOS High Sierra or higher

The following code produces a `polygon edge not found` error and a bunch
of `no font could be found for family "Arial"` warnings on macOS High Sierra
or higher:

    library(ggplot2)
    png(type="quartz")
    ggplot(data.frame(), aes(1, 1))
    dev.off()

See https://github.com/tidyverse/ggplot2/issues/2252#issuecomment-398268742

This breaks `R CMD build` on > 300 Bioconductor packages at the moment!
(March 2020)

Simpler code (that doesn't involve ggplot2) that reproduces the warnings
about the missing font family:

    png(type="quartz")
    plot(density(rnorm(1000)))
    dev.off()

We don't really have a fix for this yet, only a dirty workaround. The workaround
is to avoid the use of the `"quartz"` device, which is the default on macOS.
However we can't do this via an `Rprofile` file (it's ignored by `R CMD build`
and `R CMD check`) so we use the following hack:

Put:

    options(bitmapType="Xlib")

in `/Library/Frameworks/R.framework/Resources/library/grDevices/R/grDevices`
at the beginning of the `local()` block.

Not a totally satisfying solution because code that explicitly resets the
device to `"quartz"` will still fail.

TESTING:

- Start R, then:
    ```
    getOption("bitmapType")  # would show "quartz" without our hack
    png()
    plot(density(rnorm(1000)))
    library(ggplot2)
    ggplot(data.frame(), aes(1, 1))
    dev.off()
    ```
- Try to `R CMD build` DESeq2 and plyranges.

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

    cd ~/bbs-3.11-bioc
    mkdir rdownloads
    cd rdownloads
    download latest R source tarball, extract, rename

    cd ~/bbs-3.11-bioc
    mkdir R
    cd R
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

    cd ~/bbs-3.11-bioc
    R/bin/R CMD config CC
    # Start R
    pkgs <- c("rJava", "Cairo", "units", "sf", "gsl", "RMySQL", "gdtools",
              "rsvg", "rtfbs", "magick", "rgeos", "V8", "pdftools", "PSCBS",
              "protolite", "RSQLite", "RPostgres", "glpkAPI")
    install.packages(pkgs, repos="https://cran.r-project.org")
    for (pkg in pkgs) library(pkg, character.only=TRUE)

Unfortunately, most packages crash the session when loaded. [According to Simon](https://stat.ethz.ch/pipermail/r-sig-mac/2020-April/013328.html), this is expected somehow.



## 6. Install MacTeX & Pandoc


Everything in this section should be done from the biocbuild account.


### Install MacTeX

Home page: https://www.tug.org/mactex/

Download:

    https://tug.org/mactex/mactex-download.html

As of May 2020 the above page is displaying "Downloading MacTeX 2020".

    cd ~/Downloads
    curl -LO https://tug.org/cgi-bin/mactex-download/MacTeX.pkg

Install with:

    sudo installer -pkg MacTeX.pkg -target /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Logout and login again so that the changes made by the installer
to the `PATH` take effect. Then:

    which tex


### Install Pandoc

Install Pandoc 2.7.3 instead of the latest Pandoc (2.9.2.1 as of April 2020).
The latter breaks `R CMD build` for 8 Bioconductor software packages
(ChIPSeqSpike, FELLA, flowPloidy, MACPET, profileScoreDist, projectR,
swfdr, and TVTB) with the following error:

    ! LaTeX Error: Environment cslreferences undefined.

Download with:

    cd ~/Downloads
    curl -LO https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-macOS.pkg

Install with:

    sudo installer -pkg pandoc-2.7.3-macOS.pkg -target /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive



## 7. Add crontab entries for daily builds


This must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    00 16 * * * /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.11/bioc/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.11-bioc/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run before
doing so.



## 8. Additional stuff to install for packages with special needs


Everything in this section must be done from the biocbuild account.


### Install Java

Go to https://jdk.java.net/ and follow the link to the latest JDK (JDK
14 as of April 1, 2020). Then download the tarball for macOS/x64 (e.g.
`openjdk-14.0.1_osx-x64_bin.tar.gz`) to `~/Downloads/`.

Install with:

    cd /usr/local
    sudo tar zxvf ~/Downloads/openjdk-14.0.1_osx-x64_bin.tar.gz
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then:

    cd /usr/local/bin
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


### [OPTIONAL] Install JPEG system library

This is needed only if CRAN package jpeg needs to be installed from source
which is usually NOT the case (most of the time a Mac binary should be
available on CRAN).

Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs-4/jpeg-9-darwin.17-x86_64.tar.gz
    sudo tar fvxz jpeg-9-darwin.17-x86_64.tar.gz -C /

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the jpeg package *from source*:

    install.packages("jpeg", type="source", repos="https://cran.r-project.org")
    library(jpeg)
    example(readJPEG)
    example(writeJPEG)


### [OPTIONAL] Install TIFF system library

This is needed only if CRAN package tiff needs to be installed from source
which is usually NOT the case (most of the time a Mac binary should be
available on CRAN).

Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs-4/tiff-4.1.0-darwin.17-x86_64.tar.gz
    sudo tar fvxz tiff-4.1.0-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the tiff package *from source*:

    install.packages("tiff", type="source", repos="https://cran.r-project.org")
    library(tiff)
    example(readTIFF)
    example(writeTIFF)


### [OPTIONAL] Install FFTW system library

This is needed only if CRAN package fftwtools needs to be installed from
source which is usually NOT the case (most of the time a Mac binary should
be available on CRAN).

Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs-4/fftw-3.3.8-darwin.17-x86_64.tar.gz
    sudo tar fvxz fftw-3.3.8-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the fftwtools package *from source*:

    install.packages("fftwtools", type="source", repos="https://cran.r-project.org")


### [OPTIONAL] Install autoconf & automake

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


### Install Cairo system library

MARCH 2020: THIS SHOULD NO LONGER BE NEEDED!
With R 4.0 on macOS Mojave, seems like Cairo can be installed from source
without the need to download/install the cairo library from mac.r-project.org
Check this with:

    install.packages("Cairo", type="source", repos="https://cran.r-project.org")

--------------------------------------------------------------------------
Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs-4/cairo-1.14.12-darwin.17-x86_64.tar.gz
    sudo tar fvxz cairo-1.14.12-darwin.17-x86_64.tar.gz -C /

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install and load the Cairo **binary** package:

    install.packages("Cairo", repos="https://cran.r-project.org")
    library(Cairo)

Note: As of Feb 22, 2017, CRAN still does not provide Mac binary packages
for R 3.4. However, it seems that the Cairo binary made for R 3.3 works
with R 3.4. Install and load with:

    contriburl <- "http://cran.case.edu/bin/macosx/mavericks/contrib/3.3"
    install.packages("Cairo", contriburl=contriburl)
    library(Cairo)
--------------------------------------------------------------------------


### Install NetCDF and HDF5 system library

NetCDF is needed only if CRAN package ncdf4 needs to be installed from
source which is usually NOT the case (most of the time a Mac binary should
be available on CRAN).

Download and install with:

    cd ~/Downloads
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


### Install GSL system library

Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs-4/gsl-2.6-darwin.17-x86_64.tar.gz
    sudo tar fvxz gsl-2.6-darwin.17-x86_64.tar.gz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the GLAD package *from source*:

    library(BiocManager)
    BiocManager::install("GLAD", type="source")


### Install GTK2

Download and install with:

    cd ~/Downloads
    curl -O https://mac.r-project.org/libs/GTK_2.24.17-X11.pkg
    sudo installer -allowUntrusted -pkg GTK_2.24.17-X11.pkg -target /

TESTING: Try to install and load the RGtk2 **binary** package:

    install.packages("RGtk2", repos="https://cran.r-project.org")
    library(RGtk2)

The following is needed only if CRAN package RGtk2 needs to be installed
from source which is usually NOT the case (most of the time a Mac binary
should be available on CRAN).

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

    pip3 install numpy scipy sklearn h5py pandas mofapy mofapy2
    pip3 install tensorflow tensorflow_probability
    pip3 install h5pyd
    pip3 install cwltool
    pip3 install nbconvert jupyter
    pip3 install matplotlib phate

TESTING:

- `jupyter --version` should display something like this:
    ```
    machv2:~ biocbuild$ jupyter --version
    jupyter core     : 4.6.3
    jupyter-notebook : 6.0.3
    qtconsole        : 4.7.4
    ipython          : 7.14.0
    ipykernel        : 5.2.1
    jupyter client   : 6.1.3
    jupyter lab      : not installed
    nbconvert        : 5.6.1
    ipywidgets       : 7.5.1
    nbformat         : 5.0.6
    traitlets        : 4.3.3
    ```
    Note that it's ok if jupyter lab is not installed but everything else
    should be.

- Start python3 and try to import the above modules. Quit.

- Try to build the BiocSklearn package (takes < 1 min):
    ```
    cd ~/bbs-3.11-bioc/meat
    R CMD build BiocSklearn
    ```
    and the destiny package:
    ```
    R CMD build destiny
    ```


### Install JAGS

Download with:

    cd ~/Downloads
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


### Install Open Babel

Don't install via Homebrew! This used to work and was installing Open Babel
2.4.1 (as of May 2017). However, as of April 2020, `brew install open-babel`
installs Open Babel 3.0.0 which includes a broken `.pc`
file (`pkg-config --cflags openbabel-3` will return
`-I/usr/local/Cellar/open-babel/3.0.0/include/openbabel-2.0`
which is wrong) and is not compatible with the ChemmineOB package
(ChemmineOB includes `openbabel/rand.h` but this is no longer
in open-babel 3.0.0). What is strange is that according to the
Open Babel website (http://openbabel.org/), the latest Open Babel
version is still 2.4.0. There is no mention of a 2.4.1 or 3.0.0 version!

#### Compile/install openbabel 2.4.1 from source

See http://openbabel.org/wiki/Install_(source_code) for full instructions
(Installing globally with root access). Here is the quick way if TLDR:

- Make sure CMake is installed (see "Install CMake" section previously
  in this file for how to do this).

- Download openbabel-2.4.1.tar.gz from
  https://sourceforge.net/projects/openbabel/files/openbabel/2.4.1/

- Then:

    cd ~/sandbox
    tar zxvf ~/Downloads/openbabel-2.4.1.tar.gz
    mv openbabel-2.4.1 ob-src
    mkdir ob-build
    cd ob-build
    cmake ../ob-src 2>&1 | tee cmake.out
    make 2>&1 | tee make.out  # takes 10-15 min.
    make install

TESTING:

    which babel
    babel -V

#### Install ChemmineOB from source

Now try to install the ChemmineOB package *from source*:

    library(BiocManager)
    BiocManager::install("ChemmineOB", type="source")


### Install libSBML

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

    cd ~/Downloads
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

    cd /usr/local/opt
    mkdir libsbml
    cd libsbml
    ln -s ../../include
    ln -s ../../lib

[NOT CLEAR THIS IS NEEDED] In `/etc/profile` add the following line:

    export DYLD_LIBRARY_PATH="/usr/local/lib"

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to install the rsbml package *from source*:

    library(BiocManager)
    BiocManager::install("rsbml", type="source")


### Install Clustal Omega

There is a standalone Mac binary at http://www.clustal.org/omega/
Downnload it with:

    cd ~/Downloads
    curl -O http://www.clustal.org/omega/clustal-omega-1.2.3-macosx

Make it executable with:

    chmod +x clustal-omega-1.2.3-macosx

Move it to `/usr/local/bin` with:

    mv -i clustal-omega-1.2.3-macosx /usr/local/bin/

Create clustalo symlink in `/usr/local/bin/` with:

    cd /usr/local/bin
    ln -s clustal-omega-1.2.3-macosx clustalo

Then:

    which clustalo

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

This is needed to install CRAN package Rmpi from source (unfortunately no
Mac binary is available on CRAN).

Install with:

    brew install open-mpi

Notes:
- This will install many deps: gmp, isl, mpfr, libmpc, gcc, hwloc and libevent
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


### Install ViennaRNA

Download with:

    cd ~/Downloads
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

    cd ~/bbs-3.11-bioc/meat
    R CMD build GeneGA


### Install the MySQL client

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

    cd /usr/local/Cellar/mysql-client/8.0.18/lib
    ln -s /usr/local/Cellar/openssl\@1.1/1.1.1g/lib/libssl.dylib
    ln -s /usr/local/Cellar/openssl\@1.1/1.1.1g/lib/libcrypto.dylib


--------------------------------------------------------------------------
NO LONGER NEEDED (kept for the record only)

Installing the MySQL Community Server

Download `mysql-8.0.0-dmr-osx10.11-x86_64.dmg` from:

    https://downloads.mysql.com/archives/community/

e.g. with:

    cd ~/Downloads
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

    cd /usr/local/mysql/lib
    otool -L libmysqlclient.21.dylib
    otool -l libmysqlclient.21.dylib  # look for path in LC_RPATH section
    install_name_tool -add_rpath /usr/local/mysql/lib libmysqlclient.21.dylib

    #install_name_tool -change @rpath/libmysqlclient.21.dylib /usr/local/mysql/lib/libmysqlclient.21.dylib libmysqlclient.21.dylib
    otool -l libmysqlclient.21.dylib  # look for path in LC_RPATH section

--------------------------------------------------------------------------

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which mysql_config

Then try to install the RMySQL package *from source*:

    library(BiocManager)
    install("RMySQL", type="source")


### Install Ensembl VEP script

Required by Bioconductor packages ensemblVEP and MMAPPR2.

Complete installation instructions are at
https://www.ensembl.org/info/docs/tools/vep/script/vep_download.html

- Make sure the MySQL client is installed on the system (see "Install
  the MySQL client" above in this file).

- According to ensembl-vep README, the following Perl modules are required:

    ## Needed by both ensemblVEP and MMAPPR2:
    sudo cpan install Archive::Zip
    sudo cpan install File::Copy::Recursive
    sudo cpan install DBI
    sudo cpan install DBD::mysql  # MySQL client needed!
    
    ## Needed by MMAPPR2 only:
    sudo cpan install -f XML::DOM::XPath  # -f to force install despite tests failing
    sudo cpan install Bio::SeqFeature::Lite
    brew install htslib
    sudo cpan install Bio::DB::HTS::Tabix

- Then:

    cd /usr/local
    sudo git clone https://github.com/Ensembl/ensembl-vep.git
    cd ensembl-vep
    sudo chown -R biocbuild:admin .
    #sudo git checkout release/100  # select desired branch

    # Avoid the hassle of getting HTSlib to compile because ensemblVEP and
    # MMAPPR2 pass 'R CMD build' and 'R CMD check' without that and that's
    # all we care about. No sudo!
    perl INSTALL.pl --NO_HTSLIB
    # When asked if you want to install any cache files - say no
    # When asked if you want to install any FASTA files - say no
    # When asked if you want to install any plugins - say no

- Finally in `/etc/profile` append `/usr/local/ensembl-vep` to `PATH`.
  Note that the `/etc/profile` file has read-only permissions (factory
  settings). To save changes you will need to force save, e.g., in the
  `vi` editor this is `w!`.

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    cd ~/bbs-3.11-bioc/meat
    R CMD build ensemblVEP
    R CMD check ensemblVEP_X.Y.Z.tar.gz  # replace X.Y.Z with current version
    R CMD build MMAPPR2
    R CMD check MMAPPR2_X.Y.Z.tar.gz     # replace X.Y.Z with current version


### Install ROOT

APRIL 2020: THIS IS NO LONGER NEEDED! Was needed for the xps package
which is no longer supported on Mac (since BioC 3.11).

xps wants ROOT 5, not 6. Unfortunately, there are no ROOT 5 binaries
for OS X 10.11 and for the version of clang we use on the builders
at https://root.cern.ch/ (well at least that was the case last time I
checked but you should check again). So we need to install from source.

- Download source of latest ROOT 5 release (5.34/36):
    ```
    cd ~/Downloads
    curl -O https://root.cern.ch/download/root_v5.34.36.source.tar.gz
    ```

- Make sure CMake is installed (see "Install CMake" section previously
  in this file for how to do this).

ROOT supports 2 installation methods: "location independent" and "fix
location". We will do "location independent" installation.

- Build with:
    ```
    cd ~/sandbox
    tar zxvf ~/Downloads/root_v5.34.36.source.tar.gz
    mkdir root_builddir
    cd root_builddir
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/root -Dgnuinstall=ON -Dfortran=OFF -Dmysql=OFF -Dsqlite=OFF ~/sandbox/root
    cmake --build . -- -j8  # takes about 10-15 min (> 45 min without -j8)
    ```

- Install with:
    ```
    sudo cmake --build . --target install
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive
    ```

- Try to start a ROOT interactive session:
    ```
    source bin/thisroot.sh
    root  # then quit the session with .q
    ```

- Finally in `/etc/profile` add the following line (before the `PATH` and
  `DYLD_LIBRARY_PATH` lines):
    ```
    export ROOTSYS="/usr/local/root"  # do NOT set ROOTSYS, it will break
                                      # xps configure script!
    ```
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

    cd ~/Downloads
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


### Install protobuf system dependencies

MARCH 2020: THIS SHOULD NO LONGER BE NEEDED! (GoogleGenomics is no longer
in Bioconductor)

These are needed for the CRAN RProtoBuf package which was 'Suggested' by
GoogleGenomics.

Install with:

    brew install protobuf



## 9. More stuff to install when CRAN Mac binary packages are not available


CRAN has a tradition of making Mac binary packages available at the last minute
before a new R release (new R releases normally happen in Spring). This means
that we need to be able to install many CRAN packages from source on our Mac
builders when the BioC devel builds use R devel. Some of these packages need
the following stuff (all available at https://mac.r-project.org/libs-4/):

    gmp for CRAN package gmp
    udunits for CRAN package units
    #gdal, geos, and xml2 for CRAN package sf

Download and install with:

    cd ~/Downloads
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
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

