# How to set up a macOS Monterey machine for the daily builds

Note: A Mac can be configured for the BBS with
https://github.com/Bioconductor/bioconductor_salt.

## 0. General information and tips


- For how to uninstall Mac packages (`.pkg` files) using native `pkgutil`:
  https://wincent.com/wiki/Uninstalling_packages_(.pkg_files)_on_Mac_OS_X
- Watch https://mac.r-project.org/ for changes in requirements. Binaries can be
  found at https://mac.r-project.org/bin/. These binaries should be preferred
  over others.
- As of April 2023, the minimum supported OS is MacOSX11.
- This document describes how to prepare both x86_64 and arm64 machines for
  the BBS.


## 1. Initial setup (from the administrator account)


This section describes the very first steps that need to be performed on
a pristine macOS Monterey installation (e.g. after creating a Mac instance on
MacStadium). Skip them and go directly to the next section if the biocbuild
account was created by someone else and if the core team member public keys
were already installed.

Everything in this section must be done **from the administrator account**
(the only account that should exist on the machine at this point).


### 1.1 Set the hostnames

    sudo scutil --set ComputerName merida1
    sudo scutil --set LocalHostName merida1
    sudo scutil --set HostName merida1

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
of macOS Monterey i.e. 12.6.4. Check this with:

    system_profiler SPSoftwareDataType
    uname -a  # should show xnu-8020.240.18.700.8~1/RELEASE_X86_64 (or higher)

IMPORTANT: The OS versions present on the build machines are listed
in the `BBS/nodes/nodespecs.py` file and the OS versions displayed on
the build reports are extracted from this file. So it's important to
keep this file in sync with the actual versions present on the builders.


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


### 1.5 Add biocbuild authorized_keys

Add authorized_keys to /Users/biocbuild/.ssh.


### 1.6 Set remote login

If you receive `Operation not permitted` when attempting to list
`/Users/biocbuild/Downloads`, you may need to set the remote login.

Testing:

    $ biocbuild$ cd Downloads/
    # Downloads biocbuild$ ls -la   # Operation not permitted

Fix:

    sudo systemsetup -setremotelogin On



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

Make sure the machine is running the latest release of macOS Monterey:

    system_profiler SPSoftwareDataType

If not, use your your personal account or the administrator account to
update to the latest with:

    sudo softwareupdate -ia --verbose

and reboot the machine.

Check the kernel version (should be Darwin 21 for macOS Monterey):

    uname -sr


### 2.4 Install XQuartz

Download it from https://xquartz.macosforge.org/

    cd ~/Downloads/
    curl -LO https://github.com/XQuartz/XQuartz/releases/download/XQuartz-2.8.5/XQuartz-2.8.5.pkg

Install with:

    sudo installer -pkg XQuartz-2.8.5.pkg -target /
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

#### Export global variable `DISPLAY`

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
    ld -v          # BUILD 20:07:01 Nov 7 2022
    which make     # /usr/bin/make
    make -v        # GNU Make 3.81
    which clang    # /usr/bin/clang
    clang -v       # Apple clang version 14.0.0 (clang-1400.0.29.202)
    which git      # /usr/bin/git
    git --version  # git version 2.37.1 (Apple Git-137.1)

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
macOS Monterey (`Command_Line_Tools_for_Xcode_14.dmg` as of April 12, 2023).
More recent versions of Xcode and the Command Line Tools are provided
as `xip` files.

If you got a `dmg` file, install with:

    sudo hdiutil attach Command_Line_Tools_for_Xcode_14.dmg
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
    clang -v     # Apple clang version 14.0.0 (clang-1400.0.29.202)
--------------------------------------------------------------------------


### 2.7 Install Minimum Supported SDK

As of April 2023, MacOSX11 is the minimum supported OS by CRAN, so Bioconductor
should also build packages for this operating system. If the latest SDK for
MacOSX11 is not in `/Library/Developer/CommandLineTools/SDKs`, download and
install:

    cd ~/Download
    curl -LO https://mac.r-project.org/sdk/MacOSX11.3.sdk.tar.xz
    sudo tar -zf MacOSX11.3.sdk.tar.xz -C /Library/Developer/CommandLineTools/SDKs

Make a symlink to the major version:

    cd https://mac.r-project.org/sdk/MacOSX11.3.sdk.tar.xz
    sudo ln -s /Library/Developer/CommandLineTools/SDKs/MacOSX11.3.sdk MacOSX11.sdk

To build for the minimum version, add the following to `/etc/profile`:

    export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX11.sdk
    export MACOSX_DEPLOYMENT_TARGET=11.0


### 2.8 Install gfortran

Simon uses the universal binary available at
https://github.com/R-macos/gcc-12-branch/releases/tag/12.2-darwin-r0.

Download with:

    cd ~/Downloads/
    curl -LO https://github.com/R-macos/gcc-12-branch/releases/download/12.2-darwin-r0/gfortran-12.2-darwin20-r0-universal.tar.xz

Install with:

    sudo tar -xf gfortran-12.2-darwin20-r0-universal.tar.xz -C /

Make sure /opt/gfortran/SDK points to the minimum required SDKROOT. By default,
it will point to `/Library/Developer/CommandLineTools/SDKs/MacOS11.sdk`:

    ln -sfn /Library/Developer/CommandLineTools/SDKs/MacOSX11.sdk /opt/gfortran/SDK

TESTING:

    gfortran --version  # GNU Fortran (GCC) 12.2.0

Finally check that the gfortran libraries got installed in
`/Library/Frameworks/R.framework/Resources/lib` and make sure that
`LOCAL_FORTRAN_DYLIB_DIR` in `BBS/utils/macosx-inst-pkg.sh` points to this
location.  Otherwise  we will produce broken binaries again (see
https://support.bioconductor.org/p/95587/#95631).


### 2.9 Install Homebrew

IMPORTANT NOTE: We use Homebrew to install some of the libraries and other
tools required by the Bioconductor daily builds. However, if those libraries
or tools are available as precompiled binaries in the `darwin20/x86_64`
or `darwin20/arm64` folders at https://mac.r-project.org/bin/, then they
should be preferred over an installation via Homebrew. We refer to those
binaries as Simon's binaries. They are used on the CRAN build machines.
They've been well-tested and are very stable. They're safer than installing
via Homebrew, which is known to sometimes cause problems. For all these
reasons, **Simon's binaries are preferred over Homebrew installs or any other
installs**.

First make sure `/usr/local` is writable by the `biocbuild` user and other
members of the `admin` group:

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then install with:

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

TESTING:

    brew doctor


### 2.10 Install openssl

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
  This will trigger statically linking of the **rtracklayer** package against
  the openssl libraries.

UPDATE (Sept 2022): Looks like `openssl` is available at
https://mac.r-project.org/bin/ (Simon's binaries). Installing this binary
should be preferred over installing via Homebrew. See IMPORTANT NOTE in
the _Install Homebrew_ section above. Also make sure to fix `/usr/local/`
permissions as described in the _Install Homebrew_ section if Simon's binary
gets extracted there (normally the case for the `darwin17/x86_64` binaries).


### 2.11 Install XZ Utils (includes lzma lib)

    brew install xz

UPDATE (Sept 2022): Looks like `xz` is available at
https://mac.r-project.org/bin/ (Simon's binaries). Installing this binary
should be preferred over installing via Homebrew. See IMPORTANT NOTE in
the _Install Homebrew_ section above. Also make sure to fix `/usr/local/`
permissions as described in the _Install Homebrew_ section if Simon's binary
gets extracted there (normally the case for the `darwin17/x86_64` binaries).


### 2.12 Install Python 3

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

    which python3
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

    which python3
    python3 --version  # Python 3.8.10


### 2.13 Set `RETICULATE_PYTHON` and install Python 3 modules

#### Set `RETICULATE_PYTHON` in `/etc/profile`

We need to make sure that, by default, the **reticulate** package will
use the system-wide Python interpreter that is in the `PATH`.

In the terminal, execute

    which python3

This is the reticulate path that must be set in `/etc/profile`. For example, if
the output of `which python3` is `/usr/local/bin/python3` then in `/etc/profile`
add

    export RETICULATE_PYTHON="/usr/local/bin/python3"  # same as 'which python3'

Logout and login again for the changes to `/etc/profile` to take effect.

TESTING: If R is already installed on the machine, start it, and do:

    if (!require(reticulate))
        install.packages("reticulate", repos="https://cran.r-project.org")
    ## py_config() should display the path to the system-wide Python
    ## interpreter returned by the 'which python3' command above.
    ## It should also display this note:
    ##   NOTE: Python version was forced by RETICULATE_PYTHON
    py_config()

#### Install Python 3 modules needed by BBS

`BBS_UBUNTU_PATH` must be the path to `BBS/Ubuntu-files/22.04`.

    sudo -H pip3 install -r $BBS_UBUNTU_PATH/pip_bbs.txt

#### Install Python modules required by Single Package Builder

    sudo -H pip3 install -r $BBS_UBUNTU_PATH/pip_spb.txt

#### Install Python modules required by CRAN/Bioconductor packages

    sudo -H pip3 install -r $BBS_UBUNTU_PATH/pip_pkgs.txt

Optionally, install all of the above with

    python3 -m pip install $(cat $BBS_UBUNTU_PATH/pip_*.txt | awk '/^[^#]/ {print $1}')

Note: it's ok if jupyter lab is not installed but everything else should be.
Tensorflow is currently not available for Mac OS arm64.

TESTING:

- `jupyter --version` should display something like this:
    ```
    merida1:~ biocbuild$ jupyter --version
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

- Start python3 and try to import the above modules. Quit.

- Try to build the **BiocSklearn** package (takes < 1 min):
    ```
    cd ~/bbs-3.18-bioc/meat/
    R CMD build BiocSklearn
    ```
    and the destiny package:
    ```
    R CMD build destiny
    ```


### 2.14 Install MacTeX

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


### 2.15 Install Pandoc

#### x86_64

Install Pandoc 2.7.3 instead of the latest Pandoc (2.9.2.1 as of April 2020).
The latter breaks `R CMD build` for 8 Bioconductor software packages
(**FELLA**, **flowPloidy**, **MACPET**, **profileScoreDist**, **projectR**,
**swfdr**, and **TVTB**) with the following error:

    ! LaTeX Error: Environment cslreferences undefined.

Download with:

    curl -LO https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-macOS.pkg > ~/Downloads/pandoc.pkg

#### arm64

Earlier releases are not available for arm64, so the latest version of pandoc
should be installed.

Download

    curl -LO https://github.com/jgm/pandoc/releases/download/3.1.8/pandoc-3.1.8-arm64-macOS.pkg > ~/Downloads/pandoc.pkg

#### For all macs

Install with:

    sudo installer -pkg pandoc.pkg -target /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive


### 2.16 Install pkg-config

NOVEMBER 2020: Who needs this? Is it really needed?

    brew install pkg-config

TESTING:

    which pkg-config       # /usr/local/bin/pkg-config
    pkg-config --list-all

UPDATE (Sept 2022): Looks like `pkgconfig` is available at
https://mac.r-project.org/bin/ (Simon's binaries). Installing this binary
should be preferred over installing via Homebrew. See IMPORTANT NOTE in
the _Install Homebrew_ section above. Also make sure to fix `/usr/local/`
permissions as described in the _Install Homebrew_ section if Simon's binary
gets extracted there (normally the case for the `darwin17/x86_64` binaries).


### 2.17 Install pstree

These are just convenient to have when working interactively on a build
machine but are not required by the daily builds or propagation pipe.

Install with:

    brew install pstree


### 2.18 Replace `/etc/ssl/cert.pm` with CA bundle if necessary

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



## 3. Set up the Bioconductor software builds

Everything in this section must be done **from the biocbuild account**.


### 3.1 Check connectivity with central builder

#### Check that you can ping the central builder

Depending on whether the node you're ping'ing from is within RPCI's DMZ
or not, use the central builder's short or long (i.e. hostname+domain)
hostname. For example:

    ping nebbiolo1                                  # from within RPCI's DMZ
    ping nebbiolo1.bioconductor.org                 # from anywhere else

#### Install biocbuild RSA private key

Add `~/.BBS/id_rsa` to the biocbuild home (copy `id_rsa` from another build
machine). Then `chmod 400 ~/.BBS/id_rsa` so permissions look like this:

    merida1:~ biocbuild$ ls -l .BBS/id_rsa
    -r--------  1 biocbuild  staff  884 Jan 12 12:19 .BBS/id_rsa

#### Check that you can ssh to the central build node

    ssh -i ~/.BBS/id_rsa nebbiolo1                   # from within DFCI's DMZ

#### Check that you can send HTTPS requests to the central node

    curl http://nebbiolo1                           # from within DFCI's DMZ

More details on https implementation in `BBS/README.md`.


### 3.2 Clone BBS git tree and create bbs-x.y-bioc directory structure

Must be done from the biocbuild account.

#### Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS

#### Compile `chown-rootadmin.c`

    cd ~/BBS/utils/
    gcc chown-rootadmin.c -o chown-rootadmin
    sudo chown root:admin chown-rootadmin
    sudo chmod 4750 chown-rootadmin

TESTING: Check that the permissions on the `chown-rootadmin` executable
look like this:

    merida1:utils biocbuild$ ls -al chown-rootadmin
    -rwsr-x---  1 root  admin  8596 Jan 13 12:55 chown-rootadmin

#### Create bbs-x.y-bioc directory structure

    mkdir -p bbs-3.18-bioc/log


### 3.3 Install R

Must be done from the `biocbuild` account.

#### Choose latest R binary for macOS

If installing R devel: download R from https://mac.r-project.org/ (e.g.
pick up `R-4.0-branch.pkg`). Unlike the installer image (`.pkg` file),
the tarball (`.tar.gz` file) does NOT include Tcl/Tk (which is needed
by R base package **tcltk**) so make sure to grab the former.

If installing R release: download R from CRAN (e.g. from
https://cloud.r-project.org/bin/macosx/). Make sure to pick the installer, not
the source tarball, as the former contains Tcl/Tk libraries that will install
in `/usr/local`.

#### Download and install

Remove the previous R installation:

    cd /Library/Frameworks/
    sudo rm -rf R.framework

For example, if installing for x86_64 mac, download and install with:

    cd ~/Downloads/
    curl -O https://cloud.r-project.org/bin/macosx/big-sur-x86_64/base/R-4.3.1-x86_64.pkg
    sudo installer -pkg R-4.3.1-x86_64.pkg -target /

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

Note that this semi-transparency problem breaks `R CMD build` on
the **chimeraviz** package. So we'll use `"cairo"` (which is the
default on Linux).

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


#### What if CRAN doesn't provide package binaries for macOS yet?

If the builds are using R-devel and CRAN doesn't provide package binaries
for Mac yet, install the following package binaries (these are the
Bioconductor deps that are "difficult" to compile from source on Mac,
as of Nov 2020):

    difficult_pkgs <- c("arrangements", "av", "fftw", "fftwtools", "gdtools",
          "gert", "ggiraph", "git2r", "glpkAPI", "gmp", "gsl", "hdf5r",
          "igraph", "jpeg", "lwgeom", "magick", "ncdf4", "pbdZMQ", "pdftools",
          "PoissonBinomial", "proj4", "protolite", "qqconf", "ragg",
          "RcppAlgos", "redux", "rJava", "RMariaDB", "Rmpfr", "RMySQL",
          "RPostgres", "rsvg", "sf", "svglite", "sysfonts", "terra",
          "textshaping", "tiff", "units", "V8", "XML", "xml2")

First try to install with:

    install.packages(setdiff(difficult_pkgs, rownames(installed.packages())), repos="https://cran.r-project.org")

It should fail for most (if not all) packages. However, it's still worth
doing it as it will be able to install many dependencies from source.
Then try to install the binaries built with the current R release:

    ## Replace 'x86_64' with 'arm64' if on arm64 Mac:
    contriburl <- "https://cran.r-project.org/bin/macosx/big-sur-x86_64/contrib/4.3"
    install.packages(setdiff(difficult_pkgs, rownames(installed.packages())), contriburl=contriburl)

NOTES:

- The binaries built for a previous version of R are not guaranteed to work
  with R-devel but if they can be loaded then it's **very** likely that they
  will. So make sure they can be loaded:
    ```
    for (pkg in difficult_pkgs) library(pkg, character.only=TRUE)
    ```

- Most binary packages in `difficult_pkgs` (e.g. **XML**, **rJava**, etc)
  contain a shared object (e.g. `libs/XML.so`) that is linked to `libR.dylib`
  via an absolute path that is specific to the version of R that was used
  when the object was compiled/linked e.g.
    ```
    /Library/Frameworks/R.framework/Versions/4.2/Resources/lib/libR.dylib
    ```
  So loading them in a different version of R (e.g. R 4.3) will fail with
  an error like this:
    ```
    > library(XML)
    Error: package or namespace load failed for ‘XML’:
     .onLoad failed in loadNamespace() for 'XML', details:
      call: dyn.load(file, DLLpath = DLLpath, ...)
      error: unable to load shared object '/Library/Frameworks/R.framework/Versions/4.3/Resources/library/XML/libs/XML.so':
      dlopen(/Library/Frameworks/R.framework/Versions/4.3/Resources/library/XML/libs/XML.so, 6): Library not loaded: /Library/Frameworks/R.framework/Versions/4.3/Resources/lib/libR.dylib
      Referenced from: /Library/Frameworks/R.framework/Versions/4.3/Resources/library/XML/libs/XML.so
      Reason: image not found
    ```
  However, they can easily be tricked by creating a symlink. Note that in R 4.3,
  paths became suffixed with `-x86_64`:
    ```
    cd /Library/Frameworks/R.framework/Versions
    ln -s 4.3-x86_64 4.2
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

- Try:
    ```
    library(ragg)
    agg_capture()

    library(ggplot2)
    ggsave("test.png")
    ```
  If these fail with a "Graphics API version mismatch" error, then it
  means that the **ragg** binary package (which was built with a previous
  version of R) is incompatible with this new version of R (current R
  devel in our case). In this case ragg needs to be installed from source:
    ```
    install.packages("ragg", type="source", repos="https://cran.r-project.org")
    ```
  Note that installing ragg from source requires the libwebp, JPEG, and TIFF
  system libraries. See "Additional stuff not needed in normal times" above in
  this file for how to do this.

- Test GLPK available:

    ```
    library(igraph)
    cluster_optimal(make_graph("Zachary"))
    ```
  Produces
    ```
    Error in cluster_optimal(make_graph("Zachary")) :
      At optimal_modularity.c:84 : GLPK is not available, Unimplemented function call
    ```


### 3.4 Add software builds to biocbuild's crontab

Must be done from the biocbuild account.

Add the following entry to biocbuild crontab:

    00 15 * * 0-5 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.18/bioc/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.18-bioc/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

Now you can proceed to the next section or wait for a complete build run
before doing so.



## 4. Install additional stuff for Bioconductor packages with special needs


Everything in this section must be done **from the biocbuild account**.


### 4.1 Install Java

Go to https://jdk.java.net/ and follow the link to the latest JDK. Then
download the tarball for your specific mac (e.g. `openjdk-18.0.1.1_macos-x64_bin.tar.gz`
or `openjdk-18.0.1.1_macos-aarch64_bin.tar.gz`) to `~/Downloads/`.

Install with:

    cd /usr/local/
    sudo tar zxvf ~/Downloads/openjdk-18.0.1.1_macos-x64_bin.tar.gz
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Then:

    cd /usr/local/bin/
    ln -s ../jdk-18.0.1.1.jdk/Contents/Home/bin/java
    ln -s ../jdk-18.0.1.1.jdk/Contents/Home/bin/javac
    ln -s ../jdk-18.0.1.1.jdk/Contents/Home/bin/jar

In `/etc/profile` add the following line:

    export JAVA_HOME=/usr/local/jdk-18.0.1.1.jdk/Contents/Home

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    java --version
    # openjdk 18.0.1.1 2022-04-22
    # OpenJDK Runtime Environment (build 18.0.1.1+2-6)
    # OpenJDK 64-Bit Server VM (build 18.0.1.1+2-6, mixed mode, sharing)

    javac --version
    # javac 18.0.1.1

Finally reconfigure R to use this new Java installation:

    sudo R CMD javareconf

TESTING: Try to install the **rJava** package:

    # install the CRAN binary
    install.packages("rJava", repos="https://cran.r-project.org")
    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")
    # [1] "18.0.1.1+2-6"


### 4.2 Install NetCDF and HDF5 system library

NetCDF is needed only if CRAN package **ncdf4** needs to be installed from
source which is usually NOT the case (most of the time a Mac binary should
be available on CRAN).

Download and extract Simon's binaries:

#### x86_64

    curl -O https://mac.r-project.org/bin/darwin17/x86_64/netcdf-4.8.1-darwin.17-x86_64.tar.xz > ~/Downloads/netcdf.tar.xz
    curl -O https://mac.r-project.org/bin/darwin17/x86_64/hdf5-1.12.1-darwin.17-x86_64.tar.xz > ~/Downloads/hdf5.tar.xz

#### arm64

    curl -O https://mac.r-project.org/bin/darwin20/arm64/netcdf-4.8.1-darwin.20-arm64.tar.xz > ~/Downloads/netcdf.tar.xz
    curl -O https://mac.r-project.org/bin/darwin20/arm64/hdf5-1.12.2-darwin.20-arm64.tar.xz > ~/Downloads/hdf5.tar.xz

#### All macs

    sudo tar fvxJ netcdf.tar.xz -C /
    sudo tar fvxJ hdf5.tar.xz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the **ncdf4** package *from source*:

    install.packages("ncdf4", type="source", repos="https://cran.r-project.org")

If you have time, you can also try to install the **mzR** package but be aware
that this takes much longer:

    library(BiocManager)
    BiocManager::install("mzR", type="source")  # takes between 7-10 min


### 4.3 Install GSL system library

Download and extract Simon's binary

#### x86_64

    curl -O https://mac.r-project.org/bin/darwin17/x86_64/gsl-2.7-darwin.17-x86_64.tar.xz > ~/Downloads/gsl.tar.xz

#### arm64

    curl -O https://mac.r-project.org/bin/darwin20/arm64/gsl-2.7.1-darwin.20-arm64.tar.xz > ~/Downloads/gsl.tar.xz

#### All macs

    sudo tar fvxJ gsl.tar.xz -C /
    
    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

TESTING: Try to install the **GLAD** package *from source*:

    library(BiocManager)
    BiocManager::install("GLAD", type="source")


### 4.4 Install JAGS

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

TESTING: Try to install the **rjags** package *from source*:

    install.packages("rjags", type="source", repos="https://cran.r-project.org")


### 4.5 Install CMake

Needed for CRAN package **nloptr**, which is used by a few Bioconductor
packages.

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
    curl -LO https://github.com/Kitware/CMake/releases/download/v3.23.0/cmake-3.23.0-macos-universal.dmg
    sudo hdiutil attach cmake-3.23.0-macos-universal.dmg
    cp -ri /Volumes/cmake-3.23.0-macos-universal/CMake.app /Applications/
    sudo hdiutil detach /Volumes/cmake-3.23.0-macos-universal

Then in `/etc/profile` *prepend* `/Applications/CMake.app/Contents/bin`
to `PATH`, or, if the file as not line setting `PATH` already, add the
following line:

    export PATH="/Applications/CMake.app/Contents/bin:$PATH"

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then:

    which cmake
    cmake --version


### 4.6 Install Open Babel

TODO: Modify instructions for arm64

The **ChemmineOB** package requires Open Babel 3. Note that the Open Babel
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
Bioconductor package **rsbml** but luckily not anymore (**rsbml** is no longer
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


### 4.7 Install Clustal Omega

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

TESTING: Try to build the **LowMACA** package (takes about 5 min):

    cd ~/bbs-3.18-bioc/meat/
    R CMD build LowMACA


### 4.8 Install the MySQL client

Note that we only need this for the **ensemblVEP** package. **RMySQL**
doesn't need it as long as we can install the binary package.

Even though we only need the MySQL client, we used to install the MySQL
Community Server because it was an easy way to get the MySQL client.
Not anymore! Our attempt to use the recent binaries available at
https://dev.mysql.com/downloads/ for macOS Monterey gave us too much
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

Then try to install the **RMySQL** package *from source*:

    library(BiocManager)
    install("RMySQL", type="source")


### 4.9 Install Ensembl VEP script

TODO: Modify instructions for arm64

Required by Bioconductor packages **ensemblVEP** and **MMAPPR2**.

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

#### Edit `/etc/profile`

In `/etc/profile` append `/usr/local/ensembl-vep` to `PATH`.
Note that the `/etc/profile` file has read-only permissions (factory
settings). To save changes you will need to force save, e.g., in the
`vi` editor this is `w!`.

Logout and login again so that the changes to `/etc/profile` take effect.

#### Testing

Try to build and check the **ensemblVEP** and **MMAPPR2** packages:

    cd ~/bbs-3.18-bioc/meat/

    R CMD build ensemblVEP
    R CMD check --no-vignettes ensemblVEP_X.Y.Z.tar.gz

    R CMD build MMAPPR2
    R CMD check --no-vignettes MMAPPR2_X.Y.Z.tar.gz


### 4.10 Install ViennaRNA

Required by Bioconductor package **GeneGA**.

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

Then try to build the **GeneGA** package:

    cd ~/bbs-3.18-bioc/meat/
    R CMD build GeneGA


### 4.11 Set up ImmuneSpaceR package for connecting to ImmuneSpace

Required by Bioconductor package **ImmuneSpaceR**. Get credentials from
Bitwarden.

In `/etc/profile` add:

    export ISR_login=*****
    export ISR_pwd=*****

TESTING: Logout and login again so that the changes to `/etc/profile` take
effect. Then try to build the **ImmuneSpaceR** package:

    cd ~/bbs-3.18-bioc/meat/
    R CMD build ImmuneSpaceR

### 4.12 Install mono

Required by Bioconductor package **rawrr**.

Install with:

    brew install mono

TESTING

    which mono  # /usr/local/bin/mono

Then try to install/build/check the **rawrr** package:

    cd ~/bbs-3.18-bioc/meat/
    R CMD INSTALL rawrr
    R CMD build rawrr
    R CMD check --no-vignettes rawrr_X.Y.Z.tar.gz


### 4.13 Install macFUSE

Required by Bioconductor package **Travel**.

Download latest stable release from https://osxfuse.github.io/ e.g.:

    cd ~/Downloads/
    curl -LO https://github.com/osxfuse/osxfuse/releases/download/macfuse-4.5.0/macfuse-4.5.0.dmg

Install with:

    sudo hdiutil attach macfuse-4.5.0.dmg
    sudo installer -pkg "/Volumes/macFUSE/Install macFUSE.pkg" -target /
    sudo hdiutil detach /Volumes/macFUSE

You may need to enable support for third party kernel extensions if installing
macFUSE for the first time. See https://github.com/macfuse/macfuse/wiki/Getting-Started.

TESTING: Try to install the **Travel** package *from source*:

    library(BiocManager)
    BiocManager::install("Travel", type="source")


### 4.14 Install .NET Runtime

Required by Bioconductor package **rmspc**.

#### Install the runtime

Visit https://docs.microsoft.com/en-us/dotnet/core/install/macos. Download and
install the 6.0 .NET runtime corresponding to the build system's macOS.

##### x86_64

    curl -O https://download.visualstudio.microsoft.com/download/pr/2ef12357-499b-4a5b-a488-da45a5f310e6/fbe35c354bfb50934a976fc91c6d8d81/dotnet-runtime-6.0.13-osx-x64.pkg > ~/Downloads/dotnet.pkg

##### arm64

    curl -O https://download.visualstudio.microsoft.com/download/pr/aa3b3150-80cb-4d30-87f8-dc36fa1dcf26/8ec9ff6836828175f1a6a60aefd4e63b/dotnet-runtime-6.0.13-osx-arm64.pkg > ~/Downloads/dotnet.pkg

##### For all macs

    shasum -a 512 dotnet.pkg
    sudo installer -pkg dotnet.pkg -target /

#### Testing

You might need to logout and login again before trying this:

    cd ~/bbs-3.18-bioc/meat/
    R CMD build rmspc
    R CMD check --no-vignettes rmspc_X.Y.Z.tar.gz


### 4.15 Install GLPK

Required by Bioconductor package **MMUPHin**.

Download and extract Simon's binary with:

#### x86_64

    curl -O https://mac.r-project.org/bin/darwin20/x86_64/glpk-5.0-darwin.20-x86_64.tar.xz > ~/Download/glpk.tar.xz

#### arm64

    curl -O https://mac.r-project.org/bin/darwin20/arm64/glpk-5.0-darwin.20-arm64.tar.xz > ~/Download/glpk.tar.xz

#### For all macs

    sudo tar fvxJ glpk.tar.xz -C /

    # Fix /usr/local/ permissions:
    sudo chown -R biocbuild:admin /usr/local/*
    sudo chown -R root:wheel /usr/local/texlive

Note: You may need to reinstall `igraph`.

TESTING: The **MMUPHin** package uses `igraph::cluster_optimal()` internally
which requires GLPK:

    library(igraph)
    cluster_optimal(make_graph("Zachary"))

If GLPK is not available, one gets:

    Error in cluster_optimal(make_graph("Zachary")) :
      At optimal_modularity.c:84 : GLPK is not available, Unimplemented function call



## 5. Set up other builds


### 5.1 Annotation builds

Not run on Mac at the moment.


### 5.2 Experimental data builds

Not run on Mac at the moment.


### 5.3 Worflows builds

From the biocbuild account:

    mkdir -p ~/bbs-3.18-workflows/log

Then add the following entry to biocbuild's crontab:

    # BIOC 3.18 WORKFLOWS BUILDS
    # --------------------------
    
    00 08 * * 2,5 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.18/workflows/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.18-workflows/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'


### 5.4 Books builds

Not run on Mac at the moment.


### 5.5 Long Tests builds

From the biocbuild account:

    mkdir -p ~/bbs-3.18-bioc-longtests/log

Then add the following entry to biocbuild's crontab:

    # BIOC 3.18 SOFTWARE LONGTESTS BUILDS
    # -----------------------------------
    
    00 08 * * 6 /bin/bash --login -c 'cd /Users/biocbuild/BBS/3.18/bioc-longtests/`hostname -s` && ./run.sh >>/Users/biocbuild/bbs-3.18-bioc-longtests/log/`hostname -s`-`date +\%Y\%m\%d`-run.log 2>&1'

