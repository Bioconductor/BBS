# How to set up a Windows Server 2019 machine for the daily builds



## 0. General information and tips


### Disconnect vs logoff

Using Disconnect when ending your rdesktop session does NOT log you off.
To log off, use the `logoff` command in a PowerShell window.


### How to open Task Manager

Use CTRL+Shift+Esc


### Managing environment variables

#### Display the value of an environment variable in a PowerShell window

E.g. to see the `Path`:
```
Get-ChildItem Env:Path
```
Pretty bad though because it doesn't display the full thing.

#### Edit an environment variable

Always from a _personal administrator account_ (see below about this):

Open File Explorer -> This PC -> right-click on This PC -> Properties -> Advanced system settings -> Environment Variables...

Always go to *System variables* (at the bottom) to add new variables or edit
existing variables. Do not add or edit user variables (at the top).



## 1. Initial setup (from a sudoer account)


Everything in this section must be done **from the Administrator account**.


### Install Google Chrome


### Install Python 3 (for all users)

Download the Latest Python 3 Release from:

  https://www.python.org/downloads/windows/

(Choose the "Windows x86-64 executable installer".)

When running the installer:
- Select "Add Python 3.8 to PATH" then click on "Customize installation".
- In the "Optional Features" screen, click Next without changing anything.
- In "Advanced Options" choose "Install for all users" and change install
  location from `C:\Program Files\Python38` to `C:\Python38`, then click
  on "Install".

ALSO: You need to explicitly associate .py files with Python by:
- Double-clicking on a .py file.
- A popup window will ask you: How do you want to open this type of file
  (.py)? Click on "More options".
- Check the "Use this app for all .py files" box then scroll all the way
  down and click on "Look for another app on this PC". This opens the File
  Explorer.
- In the File Explorer find the python file in `C:\Python38` and
  double-click on it.


### Upgrade to the latest pip

In a PowerShell window:

    python -m pip install --upgrade pip


### Install Python module psutil

This module is needed by BBS.

    pip install psutil


### Install Python modules needed by some CRAN/Bioconductor packages

In a PowerShell window:

    pip install numpy scipy sklearn h5py pandas mofapy
    pip install tensorflow tensorflow_probability
    pip install h5pyd
    pip install cwltool
    pip install nbconvert
    pip install matplotlib phate
    pip install virtualenv

Notes:
- scipy is needed by Bioconductor package MOFA but also by the sklearn
  module (when sklearn is imported and scipy is not present, the former
  breaks). However, for some reason, `pip install sklearn` does not
  install scipy and completes successfully even if scipy is not installed.
- numpy, sklearn, h5py, and pandas are needed by Bioconductor packages
  BiocSklearn and MOFA, and numpy is also needed by Bioconductor package
  DChIPRep.
- mofapy is needed by Bioconductor package MOFA.
- tensorflow is needed by Bioconductor packages scAlign and netReg.
- tensorflow_probability is needed by Bioconductor package netReg.
- h5pyd is needed by Bioconductor package rhdf5client.
- cwltool is needed by Bioconductor package Rcwl.
- nbconvert is needed by CRAN package nbconvertR which is itself used by
  Bioconductor package destiny.
- matplotlib and phate are needed by CRAN package phateR which is itself
  used by Bioconductor package phemd.
- virtualenv is used by the single package builder. Despite python3 shipping
  with venv, venv is not sufficient. The SPB must use virtualenv.


### Create personal administrator accounts

Go in Computer Management
      -> System Tools
         -> Local Users and Groups
            -> Users

Then in the Actions panel (on the right):
      -> Users
         -> More Actions
            -> New User

- Username: mtmorgan / Full name: Martin Morgan

- Username: hpages / Full name: Hervé Pagès

- Username: lshepherd / Full name: Lori Shepherd

For all these accounts:
- [x] User must change password at next logon
- [ ] User cannot change password
- [ ] Password never expires
- [ ] Account is disabled

Then make these users members of the Administrators group.


### Create the biocbuild account

Username: biocbuild

For this account:
- [ ] User must change password at next logon
- [x] User cannot change password
- [x] Password never expires
- [ ] Account is disabled

By default, the home folder will be `C:\Users\biocbuild`. If this needs to
be changed (e.g. to `D:\biocbuild`), double-click on the biocbuild user and
make the change in the Profile tab. Note that the `C:\Users\biocbuild` folder
will still be created and populated at first logon.

Make the biocbuild user member of the Remote Desktop Users group.


### Grant the biocbuild user "Log on as batch job" rights

(This is needed in order to define scheduled tasks run by the `biocbuild`
user.)

Go in Local Security Policy
  -> Local Policies
     -> User Rights Assignment

In the right pane, right-click on 'Log on as a batch job' -> Properties

Add `biocbuild` user.


### Install 32-bit Cygwin

Cygwin is needed for: `ssh`, `rsync`, `curl`, and `vi`.

Download and run `setup-x86.exe` to install or update Cygwin.

Install for all users.

Make sure packages `openssh`, `rsync`, and `curl` are selected (the 3 of
them are in the Net category).

Note that this installs the Cygwin 32-bit DLL.

Prepend `C:\cygwin\bin` to `Path` (see "How to edit an environment variable"
in "General information and tips" at the top of this document for how to do
this).

TESTING: Open a PowerShell window and try to run `ssh`, `rsync`, or `curl`
in it. Do this by just typing the name of the command followed by <Enter>.
If `Path` was set correctly, the command should be found (the Cygwin
executables are in `C:\cygwin\bin`).


### Install git client for Windows

Available at https://git-scm.com/download/win

Keep all the default settings when running the installer.

TESTING: Open a PowerShell window and try to run `git --version`


### Install MiKTeX

If this is a reinstallation of MiKTeX, make sure to uninstall
MiKTeX first (from the Administrator account) and to manually
remove `C:\Users\biocbuild\AppData\Roaming\MiKTeX\` and
`C:\Users\pkgbuild\AppData\Roaming\MiKTeX\` (better done from
the `biocbuild` and `pkgbuild` accounts, respectively) before reinstalling.

Go to https://miktex.org/download

Download latest Basic MiKTeX 64-bit Installer (`basic-miktex-20.6.29-x64.exe`
as of Aug. 2020) and run it:

- Install MiKTeX for all users
- Preferred paper: Letter
- Install missing packages on-the-fly: Yes

IMPORTANT: After the installer finishes, do NOT check for updates by
unchecking the "Check for updates now" on the "Update Check" screen.
We're going to do this from the MiKTeX Console.

Open the MiKTeX Console by going to the Windows start menu:

- Switch to administrator mode
- Check for updates
- Go to the Updates page
- Click on "Update now"

This is no longer needed (as of Dec 2019) since no package that uses
pstricks in their vignette should still need to use auto-pst-pdf:

> Set environment variable `MIKTEX_ENABLEWRITE18=t` (this is for packages
> using auto-pst-pdf in their vignette). See "How to edit an environment
> variable" in "General information and tips" at the top of this document
> for how to do this.

> Then in a PowerShell window:
>
>    initexmf --edit-config-file=miktex\config\pdflatex.ini
>
> The command above will open an editor. Put `EnableWrite18=t` in it, then
> save and exit. Without this, `R CMD build` will fail on packages using
> auto-pst-pdf in their vignette (e.g. affyContam, arrayMvout, ArrayTools,
> BioSeqClass, BrainStars, clst, clstutils, GeneAnswers, GGtools, maSigPro,
> MassArray, PLPE, ppiStats, randPack, rbsurv, rnaSeqMap, vtpnet, xmapbridge).
> With the following error:
>
>    LaTeX errors:
>    df.sty:134: Package auto-pst-pdf Error:
>        "shell escape" (or "write18") is not enabled:
>        auto-pst-pdf will not work!


From now on, all administrative tasks should be performed from one of the
personal accounts instead of the Administrator account.



## 2. From a personal administrator account


Unless stated otherwise, everything in this section must be done **from
a personal administrator account**.


### Install Pandoc

Go to https://pandoc.org/installing.html#windows

Download latest installer for Windows x86\_64
(`pandoc-2.9-windows-x86_64.msi` as of Dec. 2019) and run it.

Note: There is a Pandoc/rmarkdown issue that was introduced in Pandoc 2.8. 
It caused build failures with the ERROR `Environment cslreferences undefined`.  
Until we know it is resolved we have downgraded pandoc to 2.7.3. 


### Install Rtools

Download Rtools from https://CRAN.R-project.org/bin/windows/Rtools/

Choose rtools40 for Windows 64-bit: `rtools40-x86_64.exe`

Run the installer and keep all the defaults. This will install rtools40
in `C:\rtools40`.

Do **NOT** follow the "Putting Rtools on the PATH" instructions given
on Rtools webpage as they put Rtools on the PATH only in the context of
running R. We want Rtools to **always** be on the PATH, not just in the
context of an R session.

Prepend `C:\rtools40\usr\bin;C:\rtools40\mingw32\bin;C:\rtools40\mingw64\bin;`
to `Path` (see "How to edit an environment variable" in "General information
and tips" at the top of this document for how to do this).

IMPORTANT: On a Windows build machine, `C:\rtools40\usr\bin;`,
`C:\rtools40\mingw32\bin;` and `C:\rtools40\mingw64\bin;` should
**always be first** in the `Path`.

TESTING: Log out and on again so that the changes to `Path` take effect. Then
in a PowerShell window:

    which ssh      # /c/cygwin/bin/ssh
    which rsync    # /usr/bin/rsync, because rsync from rtools40 should be
                   # before rsync from Cygwin in Path
    which curl     # /usr/bin/curl, because curl from rtools40 should be
                   # before curl from Cygwin in Path
    which vi       # /usr/bin/vi, because vi from rtools40 should be
                   # before vi from Cygwin in Path
    rsync          # Will crash if 64-bit Cygwin was installed instead
                   # of 32-bit!
    which make     # /usr/bin/make
    which gcc      # /mingw32/bin/gcc
    gcc --version  # gcc.exe (Built by Jeroen for the R-project) 8.3.0


### Allow cc1plus.exe access to a 3GB address space

Needed to compile large software projects (e.g. mzR) on 32-bit Windows. See:
https://www.intel.com/content/www/us/en/programmable/support/support-resources/knowledge-base/embedded/2016/cc1plus-exe--out-of-memory-allocating-65536-bytes.html

Get the `editbin` command by installing Visual Studio Community 2019. **From
the Administrator account**:

- Download it from https://www.microsoft.com/express/Windows/

- Start the installer:

  - On the first screen, go to "Individual components" and select the
    latest "MSVC v142 - VS 2019 C++ x64/x86 build tools" in the "Compilers,
    build tools, and runtimes" section.
    Total space required (bottom right) should go up from 699MB to 2.47GB.
    Click Install. When asked "Do you want to continue without workloads?",
    click on "Continue".

  - Click on Restart at the end of the installation.

Then **from the Administrator account** again, in the Developer Command
Prompt for VS 2019:

    bcdedit /set IncreaseUserVa 3072
    editbin /LARGEADDRESSAWARE "C:\rtools40\mingw32\lib\gcc\i686-w64-mingw32\8.3.0\cc1plus.exe"


### Create and populate C:\extsoft

Download `local323.zip`, `spatial324.zip`, and `curl-7.40.0.zip` from
https://www.stats.ox.ac.uk/pub/Rtools/goodies/multilib/ and unzip them
**in that order** in `C:\extsoft`.

When extacting all file from `curl-7.40.0.zip`, you'll be asked if you want
to replace or skip the files with the same names (these are the `libz.a`
files located in `lib\i386\` and `lib\x64\`, respectively). Choose "Skip
these files".



## 3. Install BBS git tree and create bbs-3.y-bioc directory structure


All the steps described in this section should be performed in a PowerShell
window and from the `biocbuild` account. Don't use the Cygwin terminal!
Generally speaking, the PowerShell window should always be the preferred
command line environment when working interactively on a Windows build machine.


### Clone BBS git tree

In a PowerShell Window:

    cd D:\biocbuild  
    git clone https://github.com/Bioconductor/BBS


### Install biocbuild RSA private key

In `D:\biocbuild`, create the `.BBS/id_rsa` file as follow:

    mkdir .BBS
    cd .BBS
    
    # Use vi (included in Rtools and Cygwin) to create the id_rsa file
    # (copy/paste its content from another builder e.g. malbec1 or tokay1).
    
    chmod 400 id_rsa

Having the RSA key installed allows the `biocbuild` user to ssh to the
central node.

TESTING: Open a PowerShell window and try to ssh to the central node with:

    ssh -i D:\biocbuild\.BBS\id_rsa biocbuild@malbec1 -o StrictHostKeyChecking=no

If malbec1 not in DNS, replace with 172.29.0.3


### Create bbs-3.12-bioc directory structure

From `D:\biocbuild`:

    mkdir bbs-3.12-bioc
    cd bbs-3.12-bioc
    mkdir log
    mkdir tmp
    mkdir tmpdir



## 4. Install R


This must be done from the `biocbuild` account.


### 4.1 Download R Windows binary from CRAN

https://cran.rstudio.com/bin/windows/base/

Choose the binary that matches the BioC version to build (see links
in "Other builds" section if you need the latest R devel binary).

When running the installer:
- Ignore warning about the current user not being an admin
- Select destination location `D:\biocbuild\bbs-3.12-bioc\R`
- Don't create a Start Menu Folder
- Don't create a desktop or QuickLaunch shortcut


### 4.2 Install BiocManager

Start R (with `R\bin\R` from `D:\biocbuild\bbs-3.12-bioc`) and install
BiocManager:

    install.packages("BiocManager")

Check that BiocManager is pointing to the correct version of Bioconductor:

    library(BiocManager)  # This displays the version of Bioconductor
                          # that BiocManager is pointing at.
    ## ONLY if BiocManager is pointing to release when it should be pointing
    ## to devel. Then make it point to devel with:
    install(version="devel")

TESTING: Start R and try to install/compile IRanges, Biobase, and zlibbioc
**from source** with:

    library(BiocManager)
    install("IRanges", type="source")
    install("Biobase", type="source")
    install("zlibbioc", type="source")

Quit R (do NOT save the workspace image).


### 4.3 Point R to C:/extsoft

`LOCAL_SOFT` needs to be set to `C:/extsoft` in `R\etc\{i386,x64}\Makeconf`:

- `R\etc\i386\Makeconf`

   From `D:\biocbuild\bbs-3.12-bioc`:
   ```
   cd R\etc\i386
   C:\rtools40\usr\bin\cp.exe -i Makeconf Makeconf.original
   vi Makeconf
   # Replace line
   #     LOCAL_SOFT ?=
   # with
   #     LOCAL_SOFT = C:/extsoft
   # Save and quit vi.
   ```
   Check your changes with:
   ```
   C:\rtools40\usr\bin\diff.exe Makeconf.original Makeconf
   ```

- `R\etc\x64\Makeconf`

   From `D:\biocbuild\bbs-3.12-bioc`:
   ```
   cd R\etc\x64
   C:\rtools40\usr\bin\cp.exe -i Makeconf Makeconf.original
   vi Makeconf
   # Replace line
   #     LOCAL_SOFT ?=
   # with
   #     LOCAL_SOFT = C:/extsoft
   # Save and quit vi.
   ```
   Check your changes with:
   ```
   C:\rtools40\usr\bin\diff.exe Makeconf.original Makeconf
   ```

TESTING: 

- Try to compile a package that uses libcurl (provided by `C:\extsoft`) e.g.
  open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
  (this folder should be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL Rhtslib

- Try to compile a package that uses the GSL (also provided by `C:\extsoft`):

    ..\R\bin\R CMD INSTALL flowPeaks
    ..\R\bin\R CMD INSTALL GLAD
    ..\R\bin\R CMD INSTALL PICS

- Try to compile a package that uses netCDF (also provided by `C:\extsoft`):

    ..\R\bin\R CMD INSTALL mzR  # will take about 10-15 min!


### 4.4 Install BiocCheck

BiocCheck is needed for the Single Package Builder:

    library(BiocManager)
    ## This installs all BiocCheck deps as binaries if they are available,
    ## which is much faster than installing from source.
    install("BiocCheck")
    ## IMPORTANT: BiocCheck needs to be loaded at least once for a full
    ## installation (this will install the BiocCheck and BiocCheckGitClone
    ## scripts).
    library(BiocCheck)


### 4.5 Install Cairo

Note that a recurrent problem is to see the Cairo package that is currently
installed on the Windows builders suddenly break after CRAN publishes a newer
version of the package: https://cran.r-project.org/package=Cairo

Here is what we think is happening: Often the Windows binary available on CRAN
lags behind the source package for several days so when the build system tries
to update all the deps at the beginning of a run, it picks up the source
package but for some reason sometimes fails to compile it. To make it worse
it seems that for some reason R also fails to restore the previous installation
of the package. So as a result Cairo ends up in a broken state and can no
longer be loaded (on one arch or the other).

This typically breaks `R CMD build` or `R CMD check` on the following software
packages: a4Base, animalcules, bigPint, CATALYST, DAPAR, debrowser,
DiscoRhythm, dittoSeq, explorase, GeneTonic, GRmetrics, MetaVolcanoR,
ngsReports, OUTRIDER, PECA, Prostar, scde, singscore, TIN.

This can sometimes be remedied by (re)installing Cairo manually from source:

    library(BiocManager)
    install("Cairo", type="source", INSTALL_opts="--merge-multiarch")

TESTING: Try to load the package (with `library(Cairo)`) on both archs:

    R --arch x64
    R --arch i386


### 4.6 If updating R

If you are updating R, the cache for AnnotationHub and ExperimentHub
should be refreshed. This is done by removing all of .AnnotationHub/,
`.AnnotationHubData/`, `.ExperimentHub/` and `.ExperimentHubData/`
present in `D:\biocbuild\` and `C:\Users\biobuild\Documents\AppData\`.



## 5. Add tasks to Task Scheduler


All the installation in this section should be made **from a personal
administrator account**.


### 5.1 Add loggon_biocbuild_at_startup task to Task Scheduler

This task is a workaround for the following issue with the Task Scheduler.
The issue happens under the following conditions:
- The task is run under a regular user (e.g. `biocbuild`)
- It's configured to 'Run whether user is logged on or not'
- The user under which the task is running is not logged on when the
  task starts
Under these conditions the environment seen by the running task is not the
same as if the user under which the task is running was already logged on
when the task started.
This issue causes some MiKTeX commands like pdflatex to fail mysteriously
during the nightly builds.

The following task automatically loggon the `biocbuild` user at system
startup. It's not a "real" loggon (e.g. it's not reported in the Task
Manager in the Users tab), just a loggon in batch mode, but that seems
to be enough to have the nightly builds run in the correct environment
(i.e. the environment that is seen by the task when the `biocbuild` user
is already logged on when the task starts).

Configure the task as follow:

- Open Task Scheduler

- In the right pane (Actions) click on Enable All Tasks History

- In the left pane create new `BBS` folder next to Microsoft folder

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `loggon_biocbuild_at_startup`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task At startup

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `C:\Python38\python.exe`
      - Add arguments: `D:\biocbuild\BBS\utils\do_nothing_forever.py`
      - Start in: `D:\biocbuild\log`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild` password)

Before the task can be started, the `D:\biocbuild\log` folder should
be created from the `biocbuild` account. The first time the task will be
started, the `D:\biocbuild\log\loggon_biocbuild_at_startup.log` file
will be created and the task will write 1 line to it. Each subsequent time
the task will be started in the future (i.e. each time the machine will be
rebooted), 1 additional line will be added to this file. So this file will
actually keep track of the reboot history.

Now either start the task manually or reboot the machine (the task should
start automatically after reboot).

When this task is running (and from now on it should always be running),
the 2 following processes should be seen in the Task Manager: `python.exe`
and `conhost.exe` (Open the Task Manager with CTRL+Shift+Esc, click on the
Details tab, and sort processes by user name).
These should be the _only_ processes running as `biocbuild` when the
builds are not running and the `biocbuild` user is not logged on.


### 5.2 Add software builds (a.k.a. nightly builds) to Task Scheduler

- Open Task Scheduler

- In the right pane (Actions) click on Enable All Tasks History (if not
  already done)

- In the left pane create new `BBS` folder next to Microsoft folder (if not
  already done)

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.12-bioc`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Daily - At 4:00 PM - Recur every 1 day
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.12\bioc\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.12-bioc\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.12\bioc\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild` password)


### 5.3 Schedule daily server reboot

This is not mandatory but HIGHLY RECOMMENDED.

Leftover processes from the previous builds often get in the way of the next
builds, causing catastrophic build failures. Until BBS does a better job at
killing these leftover processes (see bbs.jobs.killProc() function in BBS
source code), rebooting the server will do it. Blunt but efficient.
Best time for this reboot is a few minutes (e.g. 15) before the prerun script
starts on the central node. This is because if, for some reason, the builds
were still running on the Windows node, that would kill them before the
prerun script starts. Which is good because otherwise the Windows node would
still be sending build products to the "central folder" on the central node,
and the prerun script would fail to delete this folder.

- Open Task Scheduler

- In the right pane (Actions) click on Enable All Tasks History (if not
  already done)

- In the left pane create new `BBS` folder next to Microsoft folder (if not
  already done)

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `DAILY REBOOT`
    - In Security options:
      - When running the task, use the following account: `SYSTEM`
      - Run whether user is logged on or not
      - Run with highest privileges
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
    - In Settings:
        Daily - At 3:00 PM - Recur every 1 day
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `C:\WINDOWS\system32\shutdown.exe`
      - Add arguments: `-r -f -t 01`

  - Tab Conditions:
      nothing should be checked

  - Tab Settings:
      nothing should be checked

  - Then click OK on bottom right


### 5.4 Schedule installation of system updates before daily reboot

This is not mandatory but HIGHLY RECOMMENDED.

NOTE: Instructions below are for Windows Server 2012. TODO: Update them
for Windows Server 2019.

- Open Control Panel.

- Click on System and Security.

- Click on Windows Update.

- On the left panel click on Change Settings.

  - Important updates:
    - Make sure "Install updates automatically (recommended)" is selected.
    - Click on Updates will be automatically installed during the maintenance
      window.
    - Change the time for "Run maintenance tasks daily at" to 1:00 PM (default
      is 2:00 AM).
    - Check "Allow scheduled maintenance to wake up my computer at the
      scheduled time".
    - Then click OK on bottom.

  - Recommended updates:
    - Check "Give me recommended updates the same way I receive important
      updates".

- Then click OK on bottom.



## 6. Additional stuff to install for packages with special needs


All the installation in this section should be made **from a personal
administrator account**.


### Install libxml2 and google protocol buffer

This is needed in order to compile the RProtoBufLib and flowWorkspace
packages.

Download libxml2 and google protocol buffer Windows binaries from

  https://rglab.github.io/binaries/

Extract all the files to `C:\libxml2` and to `C:\protobuf` respectively.
Set environment variables `LIB_XML2` and `LIB_PROTOBUF` to `C:/libxml2`
and `C:/protobuf`, respectively (see "How to edit an environment variable"
in "General information and tips" at the top of this document for how to do
this). Make sure to use `/` instead of `\` as the directory delimiter.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the flowWorkspace package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL RProtoBufLib
    ..\R\bin\R CMD INSTALL flowWorkspace


### Install Java

You need the JDK (Java Development Kit). Available at:

  https://www.oracle.com/technetwork/java/javase/downloads/index.html

Choose "JDK Download" then download the "Windows x64 Installer".
Note that Oracle no longer provides the JDK for 32-bit windows so any
Bioconductor package that depends on rJava/Java needs to be marked as
unsupported on 32-bit Windows.

Use the default settings when running the installers.

Make sure that `C:\rtools40\usr\bin;`, `C:\rtools40\mingw32\bin;`
and `C:\rtools40\mingw64\bin;` are still first in the `Path`. In case
the installer prepended something to the `Path` (e.g. something like
`C:\ProgramData\Oracle\Java\javapath;`), move it towards the end of
`Path` (e.g. anywhere after `C:\Program Files\Git\cmd`). See "How to
edit an environment variable" in "General information and tips" at the
top of this document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this
account if you were already logged on) try to load the rJava package for
the 64-bit arch (this package will be automatically installed after the
1st build run but cannot be loaded if Java is not found on the system).
To do this: open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc`,
start 64-bit R (with `R\bin\R --arch x64`, or just `R\bin\R` since x64
is the default), then:

    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")

Note that `library(rJava)` should fail in 32-bit R (e.g. in an R session
started with `R\bin\R --arch i386`).


### Install Ghostscript

Available at: http://www.ghostscript.com/download/gsdnld.html

Choose Ghostscript AGPL Release for 64 bit Windows.

Use the default settings when running the installer.

Append `C:\Program Files\gs\gs9.19\bin` to `Path` (see "How to edit an
environment variable" in "General information and tips" at the top of this
document for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Ghostscript
for its vignette e.g. open a PowerShell window, `cd` to
`D:\biocbuild\bbs-3.12-bioc\meat` (this folder will be automatically
created after the 1st build run), then:

    ..\R\bin\R CMD build clustComp
    ..\R\bin\R CMD build MANOR
    ..\R\bin\R CMD build OrderedList
    ..\R\bin\R CMD build twilight


### Install Perl

Download and install Active Perl Community Edition for 64-bit Windows
When running the installer, choose "Typical" setup

Note that the installer will prepend `C:\Perl64\site\bin;C:\Perl64\bin;`
to the `Path`. However, on a Windows build machine, `C:\rtools40\usr\bin;`,
`C:\rtools40\mingw32\bin;` and `C:\rtools40\mingw64\bin;` should always
be first in `Path`, so move this towards the end of `Path` (e.g. anywhere
after `C:\Program Files\Git\cmd`). See "How to edit an environment variable"
in "General information and tips" at the top of this document for how to
do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Perl e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build COHCAP


### Install JAGS

Go to http://www.sourceforge.net/projects/mcmc-jags/files

You'll see:

  Looking for the latest version? Download JAGS-X.Y.Z.html

Click on that link. It downloads an HTML file.

Open the downloaded file with Chrome and choose the installer that
corresponds to the version of R used for the builds.

Use the default settings when running the installer, except that we do not
need to create shortcuts (check the "Do not create shortcuts" box).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to load the rjags package e.g. open a
PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat` (this
folder will be automatically created after the 1st build run), start R
(with `..\R\bin\R`), then:

    library(rjags)


### Install Open Babel

Follow instructions in `ChemmineOB/INSTALL` for this.

IMPORTANT: Unlike all the other things here that need to be installed from
a personal administrator account, this one needs to be installed from the
`biocbuild` account. That's because the compilation process described in
`ChemmineOB/INSTALL` needs to access stuff under

    c:/Users/biocbuild/bbs-3.12-bioc/R/library/zlibbioc/

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the ChemmineOB package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL ChemmineOB


### Install libSBML

Download `64-bit/libSBML-5.18.0-win-x64.exe` and
`32-bit/libSBML-5.18.0-win-x86.exe` from

  https://sourceforge.net/projects/sbml/files/libsbml/5.18.0/stable/Windows/

Run the 2 installers and keep all the default settings.

Create `C:\libsbml` folder and copy
`C:\Program Files\SBML\libSBML-5.18.0-libxml2-x64\win64` and
`C:\Program Files (x86)\SBML\libSBML-5.18.0-libxml2-x86\win32` to it.
Rename `C:\libsbml\win64` and `C:\libsbml\win32` -> `C:\libsbml\x64`
and `C:\libsbml\i386`, respectively.

Set environment variable `LIBSBML_PATH` to `C:/libsbml` (use slash,
not backslash). See "How to edit an environment variable" in "General
information and tips" at the top of this document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the rsbml package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL rsbml


### Install Clustal Omega

Download Windows 64-bit zip file from http://www.clustal.org/omega/

Extract all the files in `C:\ClustalO`

Append `C:\ClustalO` to `Path` (see "How to edit an environment variable"
in "General information and tips" at the top of this document for how
to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Clustal Omega
e.g. open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build LowMACA

(Note that this package also needs Perl.)


### Set up ImmuneSpaceR package for connecting to ImmuneSpace

Set environment variable `ISR_login` and `ISR_pwd` to `bioc@immunespace.org`
and `1notCRAN`, respectively. See "How to edit an environment variable"
in "General information and tips" at the top of this document for how to
do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build the ImmuneSpaceR package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build ImmuneSpaceR


### Set up GoogleGenomics package to authenticate for Google Genomics API

Set environment variable `GOOGLE_API_KEY` to
`AIzaSyDOIu6mUVWneDXkfbEQXi1CHnlgUQHkka4` (see "How to edit an environment
variable" in "General information and tips" at the top of this document
for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to run the `getReads` example in the
GoogleGenomics package e.g. open a PowerShell window, `cd` to
`D:\biocbuild\bbs-3.12-bioc\meat` (this folder will be automatically
created after the 1st build run), then:

- Install the GoogleGenomics package if it's not already installed (check
  whether it's already installed or not by starting R with `..\R\bin\R` and
  try `library(GoogleGenomics)`):

    ..\R\bin\R CMD INSTALL GoogleGenomics

- Then from within R (start it with `..\R\bin\R`):

    library(GoogleGenomics)
    example(getReads)


### Install gtkmm

Download `gtkmm-win64-devel-2.22.0-2.exe` from

  http://ftp.gnome.org/mirror/gnome.org/binaries/win64/gtkmm/2.22/

Run it (use default settings). This installs gtkmm in `C:\gtkmm64`

Set `GTK_PATH` to `C:\gtkmm64`

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the HilbertVisGUI package
for the x64 arch only e.g. open a PowerShell window, `cd` to
`D:\biocbuild\bbs-3.12-bioc\meat` (this folder will be automatically
created after the 1st build run), then:

    ..\R\bin\R --arch x64 CMD INSTALL --no-multiarch HilbertVisGUI


### Install GGobi

Download Windows 64-bit and 32-bit versions from

  http://www.ggobi.org/downloads/

Make sure to remove any old versions of GGobi.

Install the new versions.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to load the rggobi package for the
2 archs (this package will be automatically installed after the 1st build
run but cannot be loaded if GGobi is not found on the system) e.g. open a
PowerShell window, `cd` to `D:\biocbuild\bbs-3.12-bioc`, then

- start R in 64-bit mode with `R\bin\R --arch x64` and do `library(rggobi)`

- start R in 32-bit mode with `R\bin\R --arch i386` and do `library(rggobi)`



## 7. Single Package Builder Requirements


### Create the pkgbuild account:

Username: pkgbuild

For this account:
- [ ] User must change password at next logon
- [x] User cannot change password
- [x] Password never expires
- [ ] Account is disabled


### Make the pkgbuild user member of the Remote Desktop Users group


### Grant the pkgbuild user "Log on as batch job" rights

(This is needed in order to define scheduled tasks run by the `pkgbuild`
user.)

Go in Local Security Policy
  -> Local Policies
     -> User Rights Assignment

In the right pane, right-click on 'Log on as a batch job' -> Properties
Add `pkgbuild` user


### Grant the pkgbuild user permissions within the biocbuild user folder

Grant the `pkgbuild` user permissions within the `biocbuild` user folder
using the Users security group.

- `D:\biocbuild`

  Using File Explorer, go to `C:\Users` and right click the `biocbuild` folder
  and choose properties. Go to the Security tab:
  - Click Edit
  - Click Add
  - Enter the object names to select: Users
  - Click Check Names to validate
  - Click OK

  For Permissions choose Read & execute, List folder contents and Read.

  Click OK.

###############################################################################

NOTE (Hervé 12/04/2019): The `meat` and `NodeInfo` folders belong to the
daily builds and are automatically created/refreshed/recreated every day
by the daily builds. I'm not sure why the SPB would need to access or
even know about these folders so I suspect that the settings below
are not actually needed (in any case they shouldn't).

- `D:\biocbuild\bbs-3.12-bioc\meat`

  Using File Explorer, go to `D:\biocbuild\bbs-3.12-bioc` and right
  click the `meat` folder and choose properties. Go to the Security tab:
  - Click Edit
  - Click Add
  - Enter the object names to select: Users
  - Click Check Names to validate
  - Click OK

  For Permissions choose Read & execute, List folder contents and Read.

  Click OK.

- `D:\biocbuild\bbs-3.12-bioc\NodeInfo`

  Using File Explorer, go to `D:\biocbuild\bbs-3.12-bioc` and right
  click the `NodeInfo` folder and choose properties. Go to the Security tab:
  - Click Edit
  - Click Add
  - Enter the object names to select: Users
  - Click Check Names to validate
  - Click OK

  For Permissions choose Read & execute, List folder contents and Read.

  Click OK.

###############################################################################


### Grant the pkgbuild user permissions within the Windows\Temp folder

Grant the `pkgbuild` user permissions within the `Windows\Temp` folder using
the Users security group. This is for BiocCheck.

Using File Explorer, go to `C:\Windows` and right click the `Temp` folder
and choose properties. Go to the Security tab:

- Click Edit
- Click Add
- Enter the object names to select: Users
- Click Check Names to validate
- Click OK

For Permissions choose Full Control.

Click OK.



## 8. Add other builds to Task Scheduler


### Annotation builds

Not run on Windows at the moment.


### Experimental data builds

Not run on Windows at the moment.


### Long Tests builds

From `D:\biocbuild`:

    mkdir bbs-3.12-bioc-longtests
    cd bbs-3.12-bioc
    mkdir log

Then:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.12-bioc-longtests`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on next Saturday at 11:00 AM -
        Recur every 1 week on Saturday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.12\bioc-longtests\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.12-bioc-longtests\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.12\bioc-longtests\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild` password)

