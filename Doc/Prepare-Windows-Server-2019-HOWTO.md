# How to set up a Windows Server 2019 system for the daily builds



This document describes the process of setting up a Windows Server 2019
machine to run the Bioconductor daily builds. It's been used to configure
machines running Windows Server 2019 Standard or Windows Server 2019
Datacenter.



## 0. General information and tips


### 0.1 Disconnect vs Sign out

When you're done working on a Windows builder it's important that you
properly terminate your session by _signing out_ (a.k.a. _logging off_).
Please keep in mind that using _Disconnect_ to end your rdesktop (or Remmina)
session does NOT sign you out. Also if you accidentally loose your rdesktop
(or Remmina) session, it's very likely that you're only disconnected but
that your session on the remote machine is still open, in which case you
need to reconnect and properly terminate your session.

To properly terminate your session, you can either:
- use the `logoff` command in a PowerShell window or
- sign out via the Power User Task Menu (right-click on the Windows logo
  at the very bottom-left corner of the screen, and go to "Shut down or
  sign out", then choose "Sign out").


### 0.2 How to open the Task Manager

Quick way: CTRL+Shift+Esc

Or via the Power User Task Menu: right-click on the Windows logo at the
very bottom-left corner of the screen and click on "Task Manager".


### 0.3 Managing environment variables

#### Print the value of an environment variable in a PowerShell window

Print all environment variables with:
```
Get-ChildItem Env:
```

Print a particular environment variable (e.g. `Path`) with:
```
echo $Env:Path
```

#### Edit an environment variable

Always from a _personal administrator account_ (see below about this):

Open File Explorer -> This PC -> right-click on This PC -> Properties -> Advanced system settings -> Environment Variables...

Always go to *System variables* (at the bottom) to add new variables or edit
existing variables. Do not add or edit user variables (at the top).



## 1. Initial setup (from the Administrator account)


Everything in this section must be done **from the Administrator account**.


### 1.1 Check time and time zone

In Settings, go to Time & Language and make sure date, time, and time zone
are correct. Note that using the same time zone for all the build machines
makes things easier, less confusing, and less error-prone for everybody. All
our build machines use the "(UTC-05:00) Eastern Time (US & Canada)" time zone
at the moment.


### 1.2 Install a decent web browser (for all users)

E.g. Google Chrome or Firefox.

Known problem: There are some "file association" problems on Windows Server
2019 when running `R CMD check` on packages that contain calls to browseURL()
in their examples. For example running `R CMD check` on BiocDockerManager
or tRNAdbImport produces:

    > BiocDockerManager::help()
    Error in shell.exec(url) :
      file association for 'https://hub.docker.com/r/bioconductor/bioconductor_docker' not available or invalid

or:

    > tRNAdbImport::open_tdbID("tdbD00000785")
    Error in shell.exec(url) :
      file association for 'http://trna.bioinf.uni-leipzig.de/DataOutput/Result?ID=tdbD00000785' not available or invalid

when checking the examples. Note that these errors only happen in the context
of the daily builds i.e. they can't be reproduced by running `R CMD check` on
BiocDockerManager or tRNAdbImport in an interactive session in a PowerShell
window.

The "file association" problem happens with both browsers, Google Chrome
and Firefox.

Until a solution is found it's been suggested to the maintainers of the
BiocDockerManager and tRNAdbImport packages that they put the problematic
calls in an `if (interactive()) ...` statement.


### 1.3 Install Visual Studio Community 2019

Provides the `editbin` command, plus some DLLs apparently needed by the
most recent versions of the `tensorflow` Python module.

**From the Administrator account**:

- Download Visual Studio Community 2019 from
  https://visualstudio.microsoft.com/ (it's a free download)

- Start the installer:

  - On the first screen, go to "Individual components" and select the
    latest "MSVC v142 - VS 2019 C++ x64/x86 build tools" in the "Compilers,
    build tools, and runtimes" section.
    Total space required (bottom right) should go up from 693MB to 2.46GB.
    Click Install. When asked "Do you want to continue without workloads?",
    click on "Continue".

  - At the end of the installation, skip the Sign in step.

  - Then click on Start Visual Studio, click on Continue without code,
    and Exit.

  - Close the Visual Studio Installer.


### 1.4 Install Python 3 (for all users)

**From the Administrator account**:

Download the Latest Python 3 Release from
https://www.python.org/downloads/windows/

Choose the "Windows installer (64-bit)".

When running the installer:
- Select "Add Python 3.8 to PATH" then click on "Customize installation".
- In the "Optional Features" screen, click Next without changing anything.
- In "Advanced Options" choose "Install for all users" and change install
  location from `C:\Program Files\Python38` to `C:\Python38`, then click
  on "Install".

ALSO: You might need to explicitly associate `.py` files with Python. To
test whether the association works, go to `C:\Python38\Tools\demo` in the
File Explorer, and double click on `hanoi`. If the program starts, then all
is fine. If not:
- A popup window will ask you: How do you want to open this type of file
  (`.py`)? Make sure the "Always use this app to open .py files" box is
  checked. Click on "More apps".
- Scroll all the way down and click on "Look for another app on this PC".
  This opens the File Explorer.
- In the File Explorer find the python file in `C:\Python38` and
  double-click on it.


### 1.5 Upgrade to the latest pip

**From the Administrator account** in a PowerShell window:

    python -m pip install --upgrade pip


### 1.6 Install Python 3 modules

#### Python 3 modules needed by BBS

**From the Administrator account** in a PowerShell window:

    pip install psutil

#### Python 3 modules needed by the Single Package Builder only

**From the Administrator account** in a PowerShell window:

`virtualenv` is used by the single package builder. Despite python3 shipping
with `venv`, `venv` is not sufficient. The SPB must use `virtualenv`.

    pip install virtualenv

#### Python 3 modules needed by some CRAN/Bioconductor packages

**From the Administrator account** in a PowerShell window:

    pip install numpy scipy sklearn h5py pandas mofapy mofapy2
    pip install tensorflow tensorflow_probability
    pip install h5pyd
    pip install nbconvert

No longer needed (as of Nov. 2020):

    #pip install matplotlib phate

Notes:
- `scipy` is needed by Bioconductor packages MOFA and MOFA2, but also by
  the `sklearn` module (when `sklearn` is imported and `scipy` is not present,
  the former breaks). However, for some reason, `pip install sklearn`
  does not install `scipy` and completes successfully even if `scipy` is
  not installed.

- `numpy`, `sklearn`, `h5py`, and `pandas` are needed by Bioconductor packages
  BiocSklearn, MOFA and MOFA2, and `numpy` is also needed by Bioconductor
  package DChIPRep.

- `mofapy` and `mofapy2` are needed by Bioconductor packages MOFA and MOFA2,
  respectively.

- `tensorflow` is needed by Bioconductor packages scAlign and netReg.

- `tensorflow_probability` is needed by Bioconductor package netReg.

- `h5pyd` is needed by Bioconductor package rhdf5client.

- `nbconvert` is needed by CRAN package nbconvertR which is itself used by
  Bioconductor package destiny.

- `matplotlib` and `phate` are needed by CRAN package phateR which is itself
  used by Bioconductor package phemd. UPDATE (2020/11/06): It looks like
  recent versions of phateR no longer need this.

TESTING: In a PowerShell window, start Python and try to import the
`tensorflow` module. You should see something like this:

    >>> import tensorflow
    2021-04-07 22:29:19.150396: W tensorflow/stream_executor/platform/default/dso_loader.cc:60] Could not load dynamic library 'cudart64_110.dll'; dlerror: cudart64_110.dll not found
    2021-04-07 22:29:19.158058: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
    INFO:tensorflow:Enabling eager execution
    INFO:tensorflow:Enabling v2 tensorshape
    INFO:tensorflow:Enabling resource variables
    INFO:tensorflow:Enabling tensor equality
    INFO:tensorflow:Enabling control flow v2
    >>>

If instead of the above you get an error like this:

    ImportError: Could not find the DLL(s) 'msvcp140.dll or msvcp140_1.dll'.
    TensorFlow requires that these DLLs be installed in a directory that is
    named in your %PATH% environment variable. You may install these DLLs by
    downloading "Microsoft C++ Redistributable for Visual Studio 2015, 2017
    and 2019" for your platform from this URL:
    https://support.microsoft.com/help/2977003/the-latest-supported-visual-c-downloads

then please refer to the _Install Visual Studio Community 2019_ section above
in this document for how to fix this.


### 1.7 Create personal administrator accounts

Go in Computer Management
      -> System Tools
         -> Local Users and Groups
            -> Users

Then in the Actions panel (on the right):
      -> Users
         -> More Actions
            -> New User

- Username: hpages / Full name: Hervé Pagès

- Username: lshepherd / Full name: Lori Shepherd

- Username: mtmorgan / Full name: Martin Morgan

For all these accounts:
- [x] User must change password at next logon
- [ ] User cannot change password
- [ ] Password never expires
- [ ] Account is disabled

Then make these users members of the `Administrators` group.

TESTING: Try to access these accounts via a remote desktop client (e.g.
rdesktop or Remmina on Linux).


### 1.8 Create the `biocbuild` account

Username: `biocbuild`

For this account:
- [ ] User must change password at next logon
- [x] User cannot change password
- [x] Password never expires
- [ ] Account is disabled

By default, the home folder will be `C:\Users\biocbuild`. If space on `C:` is
limited this might need to be changed to something else (e.g. `D:\biocbuild`).
To do this: double-click on the `biocbuild` user and make the change in the
Profile tab. Note that the `C:\Users\biocbuild` folder will still be created
and populated at first logon.

Then make the `biocbuild` user a member of the `Remote Desktop Users` group.
This is needed to allow RDP access to the `biocbuild` account. Note that the
personal administrator accounts created earlier don't need this because members
of the `Administrators` group automatically allow RDP.


### 1.9 Grant the `biocbuild` user "Log on as batch job" rights

(This is needed in order to define scheduled tasks run by the `biocbuild`
user.)

Go in Local Security Policy -> Local Policies -> User Rights Assignment

In the right pane, right-click on 'Log on as a batch job' -> Properties

Add `biocbuild` user.


### 1.10 Install 32-bit Cygwin (for all users)

Cygwin is needed for `ssh`, `rsync`, `curl`, and `vi`.

Go to https://www.cygwin.com/, click on Install Cygwin, then download
and run `setup-x86.exe` to install or update Cygwin. IMPORTANT: Do NOT
install the 64-bit version!

In the installer:
- Install for all users.
- Make sure packages `curl`, `openssh`, and `rsync` are selected (the 3 of
  them are in the Net category). Note that the Cygwin 32-bit DLL will
  automatically be installed.
- Don't Create icon on Desktop.

Finally **prepend** `C:\cygwin\bin` to `Path` (see _Edit an environment
variable_ in the _Managing environment variables_ section at the top of
this document for how to do this). At this point `C:\cygwin\bin` should
be first in `Path`, right before `C:\Python38\Scripts\` and `C:\Python38\`.

TESTING: Open a PowerShell window and try to run `ssh`, `rsync`, or `curl`
in it. Do this by just typing the name of the command followed by <Enter>.
If `Path` was set correctly, the command should be found (the Cygwin
executables are in `C:\cygwin\bin`).

IMPORTANT NOTE: We will never need the Cygwin terminal. Generally speaking,
the PowerShell window is the preferred command line environment when working
interactively on a Windows build machine.


### 1.11 Install git client for Windows

Available at https://git-scm.com/download/win

Keep all the default settings on all the screens (there are many) when
running the installer.

TESTING: Open a PowerShell window and try to run `git --version`


### 1.12 Install MiKTeX

If this is a reinstallation of MiKTeX, make sure to uninstall it (from
the Administrator account) before reinstalling.

Go to https://miktex.org/download and download the latest Basic MiKTeX
64-bit Installer (`basic-miktex-20.11-x64.exe` as of Nov. 2020).

When running the installer:

- Install MiKTeX for all users
- Preferred paper: Letter
- Install missing packages on-the-fly: Yes

IMPORTANT: After the installer finishes, do NOT check for updates by
unchecking the "Check for updates now" on the "Update Check" screen.
We're going to do this from the MiKTeX Console.

Open the MiKTeX Console by going to the Windows start menu:

- Switch to administrator mode
- In Settings: select "Always install missing packages on-the-fly" and make
  sure that the "For anyone who uses this computer (all users)" box is NOT
  checked (otherwise running `R CMD build` from a non-admin account like
  `biocbuild` will fail to install missing packages on-the-fly because it
  doesn't have admin privileges)
- In Updates: click on "Check for updates", and, if any updates,
  click on "Update now"

IMPORTANT: After each update, or if this is a reinstallation of MiKTeX,
make sure to manually delete `C:\Users\biocbuild\AppData\Roaming\MiKTeX\`
and `C:\Users\pkgbuild\AppData\Roaming\MiKTeX\` (better done from
the `biocbuild` and `pkgbuild` accounts, respectively).


### 1.13 Sign out from the Administrator account

**From now on, all administrative tasks must be performed from one of the
_personal administrator accounts_ instead of the Administrator account.**



## 2. From a personal administrator account


Most actions in this section must be done **from a personal administrator
account**.


### 2.1 In `biocbuild`'s home: clone BBS git and create log folder

**From the `biocbuild` account** in a PowerShell window:

    cd D:\biocbuild
    git clone https://github.com/Bioconductor/BBS
    mkdir log


### 2.2 Add `loggon_biocbuild_at_startup` task to Task Scheduler

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

**From a personal administrator account** configure the task as follow:

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

  - Then click OK on bottom right (requires `biocbuild`'s password)

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


### 2.3 Schedule daily server reboot

This is not mandatory but HIGHLY RECOMMENDED.

Leftover processes from previous builds often get in the way of the next
builds, causing catastrophic build failures. Until BBS does a better job at
killing these leftover processes (see `bbs.jobs.killProc()` function in BBS
source code), rebooting the server will do it. Blunt but efficient.
Best time for this reboot is a few minutes (e.g. 15) before the prerun script
starts on the central node. This is because if, for some reason, the builds
were still running on the Windows node, that would kill them before the
prerun script starts. Which is good because otherwise the Windows node would
still be sending build products to the "central folder" on the central node,
and the prerun script would fail to delete this folder.

**From a personal administrator account** configure the task as follow:

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
      - Run whether user is logged on or not (note that this is not
        configurable on Windows Server 2019)
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
      - Program/script: `C:\Windows\system32\shutdown.exe`
      - Add arguments: `-r -f -t 01`

  - Tab Conditions:
      nothing should be checked

  - Tab Settings:
      nothing should be checked

  - Then click OK on bottom right


### 2.4 Schedule installation of system updates before daily reboot

This is not mandatory but HIGHLY RECOMMENDED.

NOTE: Instructions below are for Windows Server 2012. TODO: Update them
for Windows Server 2019.

**From a personal administrator account**:

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


### 2.5 Install Rtools

**From a personal administrator account**:

- Go to https://CRAN.R-project.org/bin/windows/Rtools/

- Download Rtools40 for Windows 64-bit: `rtools40-x86_64.exe`

- Run the installer and keep all the defaults. This will install Rtools40
  in `C:\rtools40`.

- Do **NOT** follow the "Putting Rtools on the PATH" instructions given
  on Rtools webpage as they put Rtools on the PATH only in the context of
  running R. We want Rtools to **always** be on the PATH, not just in the
  context of an R session.

- **Prepend** `C:\rtools40\usr\bin`, `C:\rtools40\mingw32\bin`, and
  `C:\rtools40\mingw64\bin` to `Path` (see _Edit an environment variable_
  in the _Managing environment variables_ section at the top of this document
  for how to do this).

  IMPORTANT: On a Windows build machine, `C:\rtools40\usr\bin`,
  `C:\rtools40\mingw32\bin`, and `C:\rtools40\mingw64\bin` should
  **always be first** in the `Path`.

- Finally, rename the `perl.exe` file located in `C:\rtools40\usr\bin` to
  avoid any conflict with Strawberry Perl (we will install this later).
  E.g. rename to `perl_DO_NOT_USE.exe`.

TESTING: Log out and on again so that the changes to `Path` take effect. Then
in a PowerShell window:

    which which     # /usr/bin/which (provided by rtools40)
    which ssh       # /c/cygwin/bin/ssh
    which rsync     # /usr/bin/rsync, because rsync from rtools40 should be
                    # before rsync from Cygwin in Path
    which curl      # /usr/bin/curl, because curl from rtools40 should be
                    # before curl from Cygwin in Path
    which vi        # /c/cygwin/bin/vi
    rsync           # Will crash if 64-bit Cygwin was installed instead
                    # of 32-bit Cygwin!
    which make      # /usr/bin/make (provided by rtools40)
    make --version  # GNU Make 4.2.1
    which gcc       # /mingw32/bin/gcc (provided by rtools40)
    gcc --version   # gcc.exe (Built by Jeroen for the R-project) 8.3.0
    which chmod     # /usr/bin/chmod (provided by rtools40)

Oh WAIT!! You also need to perform the step below (_Allow cc1plus.exe
access to a 3GB address space_) or the mzR package won't compile in
32-bit mode!


### 2.6 Allow cc1plus.exe access to a 3GB address space

`cc1plus.exe` is a 32-bit executable shipped with Rtools. It's located
in `C:\rtools40\mingw32\lib\gcc\i686-w64-mingw32\8.3.0\`.

By default `cc1plus.exe` can only access a 2GB address space. However, in
order to be able to compile large software projects (e.g. mzR) on 32-bit
Windows, it needs to be able to access to a 3GB address space. See:
https://www.intel.com/content/www/us/en/programmable/support/support-resources/knowledge-base/embedded/2016/cc1plus-exe--out-of-memory-allocating-65536-bytes.html

But first we need to get the `editbin` command. We get this command by
installing Visual Studio Community 2019 **from the Administrator account**.
Refer to the _Install Visual Studio Community 2019_ section above
in this document for how to do this.

Then **from the Administrator account** again, in the Developer Command
Prompt for VS 2019:

    bcdedit /set IncreaseUserVa 3072
    editbin /LARGEADDRESSAWARE "C:\rtools40\mingw32\lib\gcc\i686-w64-mingw32\8.3.0\cc1plus.exe"
    # Microsoft (R) COFF/PE Editor Version 14.27.29112.0
    # Copyright (C) Microsoft Corporation.  All rights reserved.


### 2.7 Create and populate C:\extsoft

**From a personal administrator account**:

Download `local323.zip`, `spatial324.zip`, and `curl-7.40.0.zip` from
https://www.stats.ox.ac.uk/pub/Rtools/goodies/multilib/ and unzip them
**in that order** in `C:\extsoft`.

When extacting all files from `curl-7.40.0.zip`, you'll be asked if you want
to replace or skip the files with the same names (these are the `libz.a`
files located in `lib\i386\` and `lib\x64\`, respectively). Choose "Skip
these files".


### 2.8 Install Pandoc

**From a personal administrator account**:

Available at: https://pandoc.org/installing.html#windows

Do NOT download the latest installer for Windows x86\_64
(`pandoc-2.11.1.1-windows-x86_64.msi` as of Nov. 2020). See
IMPORTANT NOTE below. Instead pick the installer for version
2.7.3 (`pandoc-2.7.3-windows-x86_64.msi`, available at
https://github.com/jgm/pandoc/releases/tag/2.7.3) and run it.

IMPORTANT NOTE: Some recent versions of Pandoc are hopelessly broken/useless:

- There is a Pandoc/rmarkdown issue that was introduced in Pandoc 2.8.
  It caused build failures with the ERROR `Environment cslreferences undefined`.
  Until we know it is resolved we have downgraded Pandoc to 2.7.3.

- The more recent versions of Pandoc are even worse. As of Nov. 2020, the
  most recent versions are 2.11.1 and 2.11.1.1. They do NOT work with the
  latest rmarkdown (2.5). More precisely:

  1. They no longer include `pandoc-citeproc`, which causes rmarkdown to
     complain during `R CMD build` with the following warning:
        ```
        Warning in engine$weave(file, quiet = quiet, encoding = enc) :
          Pandoc (>= 1.12.3) and/or pandoc-citeproc not available. Falling back to R Markdown v1.
        ```
     This affects many packages.

  2. Probably related to 1., `R CMD build` fails on dozens of packages (e.g.
     ADAM, dagLogo, GRmetrics, Harman, and many more...) during creation of
     the vignettes with the following error:
        ```
        Error: processing vignette 'IntroductionToHarman.Rmd' failed with diagnostics:
        could not find function "doc_date"
        ```

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) in a PowerShell window:

    which pandoc           # /c/Program Files/Pandoc/pandoc
    which pandoc-citeproc  # /c/Program Files/Pandoc/pandoc-citeproc

Then, if you already have R installed, try to build a package that uses
Pandoc e.g.:

    cd D:\biocbuild\bbs-3.14-bioc\meat
    ..\R\bin\R CMD build dagLogo
    ..\R\bin\R CMD build Harman



## 3. Set up the Bioconductor software builds


### 3.1 Check connectivity with central builder

All the steps described in this section must be performed in a PowerShell
window and from the `biocbuild` account.

#### Check that you can ping the central builder

Depending on whether the node you're ping'ing from is within RPCI's DMZ
or not, use the central builder's short or long (i.e. hostname+domain)
hostname. For example:

    ping malbec1                                   # from within RPCI's DMZ
    ping malbec1.bioconductor.org                  # from anywhere else

#### Install `biocbuild`'s RSA private key

Create the `.BBS/id_rsa` file as follow:

    cd D:\biocbuild
    mkdir .BBS
    cd .BBS
    
    # Use vi (from Cygwin) to create the id_rsa file (copy/paste its content
    # from another builder e.g. malbec1 or tokay1).
    
    chmod 400 id_rsa

#### Check that you can ssh to the central builder

    ssh -i D:\biocbuild\.BBS\id_rsa biocbuild@malbec1 -o StrictHostKeyChecking=no

If malbec1 not in DNS, replace with 172.29.0.3

Contact the IT folks at RPCI if this is blocked by RPCI's firewall:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

#### Check that you can send HTTPS requests to the central builder

    curl https://malbec1                           # from within RPCI's DMZ
    curl https://malbec1.bioconductor.org          # from anywhere else

Contact the IT folks at RPCI if this is blocked by RPCI's firewall (see above).

More details on https implementation in `BBS/README.md`.


### 3.2 [OPTIONAL] Customize locations of AnnotationHub & ExperimentHub caches

Once the builds are up and running, they will typically download
big amount of data from the data hubs (AnnotationHub & ExperimentHub).
For example, as of March 2021, about 70GB of data gets downloaded from
ExperimentHub to the local ExperimentHub cache.

By default, the locations of the caches are

    C:\Users\biocbuild\AppData\Local\AnnotationHub\AnnotationHub\Cache

and

    C:\Users\biocbuild\AppData\Local\ExperimentHub\ExperimentHub\Cache

even if the home folder of the `biocbuild` account was explicitely set to
something other than `C:\Users\biocbuild`! (See _Create the `biocbuild`
account_ section above in this document for more information about using
a customized `biocbuild`'s home folder.)

If R is already installed, you can check this from R with:

    library(AnnotationHub)
    getAnnotationHubOption("CACHE")
    library(ExperimentHub)
    getExperimentHubOption("CACHE")

If space on `C:` is limited, you might want to consider changing these
locations to something else e.g. to `D:\biocbuild\AnnotationHub_cache`
and `D:\biocbuild\ExperimentHub_cache`. The location of the caches can
be controlled via environment variables `ANNOTATION_HUB_CACHE`
and `EXPERIMENT_HUB_CACHE`, which you can set permanently by using
the `setx.exe` command in a PowerShell window e.g.:

    setx ANNOTATION_HUB_CACHE "D:\biocbuild\AnnotationHub_cache"
    setx EXPERIMENT_HUB_CACHE "D:\biocbuild\ExperimentHub_cache"

IMPORTANT: Make sure to do this from the `biocbuild` account!

TESTING: Open **another** PowerShell window and check that the environment
variables are defined. Do this with:

    echo $Env:ANNOTATION_HUB_CACHE
    echo $Env:EXPERIMENT_HUB_CACHE

If R is already installed, you can also check this from R with:

    library(AnnotationHub)
    getAnnotationHubOption("CACHE")
    library(ExperimentHub)
    getExperimentHubOption("CACHE")


### 3.3 Create bbs-x.y-bioc directory structure

**From the `biocbuild` account** in a PowerShell window:

    cd D:\biocbuild
    mkdir bbs-3.14-bioc
    cd bbs-3.14-bioc
    mkdir log
    mkdir tmp
    mkdir tmpdir


### 3.4 Install R

**From the `biocbuild` account**:

#### Get R Windows binary from CRAN

https://cran.rstudio.com/bin/windows/base/

Choose the binary that matches the BioC version to build (see links
in "Other builds" section if you need the latest R devel binary).

If updating R, uninstall the current R before running the installer:
- Open the Control Panel
- Click on Uninstall a program
- Make sure you pick up the correct R in case there is more than one instance!
Then go in the File Explorer and remove `D:\biocbuild\bbs-3.14-bioc\R`.

When running the installer:
- Ignore warning about the current user not being an admin
- Select destination location `D:\biocbuild\bbs-3.14-bioc\R`
- Don't create a Start Menu Folder
- Don't create a desktop or Quick Launch shortcut

#### Install BiocManager

In a PowerShell window, go to `D:\biocbuild\bbs-3.14-bioc` and start R:

    cd D:\biocbuild\bbs-3.14-bioc
    R\bin\R  # check version of R displayed by startup message

Then from R:

    install.packages("BiocManager")

    ## Check that BiocManager is pointing at the correct version
    ## of Bioconductor:

    library(BiocManager)  # This displays the version of Bioconductor
                          # that BiocManager is pointing at.

    ## IMPORTANT: Switch to "devel" **ONLY** if you are installing R for
    ## the devel builds and if BioC devel uses the same version of R as
    ## BioC release!
    install(version="devel")

Quit R (do NOT save the workspace image).

TESTING: Start R and try to install/compile IRanges, Biobase, and zlibbioc
**from source** with:

    library(BiocManager)
    install("IRanges", type="source")
    install("Biobase", type="source")
    install("zlibbioc", type="source")

Quit R (do NOT save the workspace image).

#### Point R to C:/extsoft

`LOCAL_SOFT` needs to be set to `C:/extsoft` in `R\etc\{i386,x64}\Makeconf`:

- Edit `R\etc\i386\Makeconf`:

   From `D:\biocbuild\bbs-3.14-bioc`:
   ```
   cd R\etc\i386
   C:\rtools40\usr\bin\cp.exe -i Makeconf Makeconf.original
   vi Makeconf
   # Replace line
   #     LOCAL_SOFT ?=
   # with
   #     LOCAL_SOFT = C:/extsoft
   # Make sure to not introduce a trailing space!
   # Then save and quit vi.
   ```
   Check your changes with:
   ```
   C:\rtools40\usr\bin\diff.exe Makeconf Makeconf.original
   ```

- Edit `R\etc\x64\Makeconf`:

   From `D:\biocbuild\bbs-3.14-bioc`:
   ```
   cd R\etc\x64
   C:\rtools40\usr\bin\cp.exe -i Makeconf Makeconf.original
   vi Makeconf
   # Replace line
   #     LOCAL_SOFT ?=
   # with
   #     LOCAL_SOFT = C:/extsoft
   # Make sure to not introduce a trailing space!
   # Then save and quit vi.
   ```
   Check your changes with:
   ```
   C:\rtools40\usr\bin\diff.exe Makeconf Makeconf.original
   ```

TESTING:

- Make sure that the 2 edited files can be accessed from the `pkgbuild`
  account. From the `pkgbuild` account in a PowerShell window:
    ```
    C:\rtools40\usr\bin\cat D:\biocbuild\bbs-3.14-bioc\R\etc\i386\Makeconf
    C:\rtools40\usr\bin\cat D:\biocbuild\bbs-3.14-bioc\R\etc\x64\Makeconf
    ```

- Try to compile a package that uses libcurl (provided by `C:\extsoft`) e.g.
  open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
  (this folder should be automatically created after the 1st build run), then:
    ```
    ..\R\bin\R CMD INSTALL Rhtslib
    ```

- Try to compile a package that uses the GSL (also provided by `C:\extsoft`):
    ```
    ..\R\bin\R CMD INSTALL flowPeaks
    ..\R\bin\R CMD INSTALL GLAD
    ..\R\bin\R CMD INSTALL PICS
    ```

- Try to compile a package that uses netCDF (also provided by `C:\extsoft`):
    ```
    ..\R\bin\R CMD INSTALL mzR  # will take about 10-15 min!
    ```

#### Install BiocCheck

BiocCheck is needed for the Single Package Builder:

    library(BiocManager)

    ## This installs all BiocCheck deps as binaries if they are available,
    ## which is much faster than installing from source.
    install("BiocCheck")

    ## IMPORTANT: BiocCheck needs to be loaded at least once for a full
    ## installation (this will install the BiocCheck and BiocCheckGitClone
    ## scripts).
    library(BiocCheck)

#### Install Cairo

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

#### Flush the data caches

When R is updated, it can be a good time to flush the cache for AnnotationHub,
ExperimentHub, and BiocFileCache. This is done by removing the corresponding
folders present in `C:\Users\biocbuild\AppData\Local`. Note that the
location of the ExperimentHub cache can be controlled via environment
variable `EXPERIMENT_HUB_CACHE` which you can check with
`echo $Env:EXPERIMENT_HUB_CACHE` in a PowerShell window (see
_Location of ExperimentHub cache_ section above for more information).

Removing these folders means that all packages using these resources will
have to re-download the data. This is a way to check that resources are
still available. However it also contributes to an increased runtime for
the builds.

Should we also remove package specific caches?


### 3.5 Add software builds to Task Scheduler

**From a personal administrator account** configure the task as follow:

- Open Task Scheduler

- In the right pane (Actions) click on Enable All Tasks History (if not
  already done)

- In the left pane create new `BBS` folder next to Microsoft folder (if not
  already done)

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.14-bioc`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - At 4:00 PM - Recur every 1 week on each day of the week
                              except on Saturday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.14\bioc\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.14-bioc\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.14\bioc\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)



## 4. Install additional stuff for Bioconductor packages with special needs


All the installations in this section must be made **from a personal
administrator account**.


### 4.1 Install Java

You need the JDK (Java Development Kit). Available at:

  https://www.oracle.com/technetwork/java/javase/downloads/index.html

Choose "JDK Download" then download the "Windows x64 Installer"
(`jdk-15.0.1_windows-x64_bin.exe` as of Nov. 2020). Note that
Oracle no longer provides the JDK for 32-bit windows (see
https://stackoverflow.com/questions/7019912/using-the-rjava-package-on-win7-64-bit-with-r
for some details), so any Bioconductor package that depends on
rJava/Java needs to be marked as unsupported on 32-bit Windows.

Use the default settings when running the installer.

Make sure that `C:\rtools40\usr\bin`, `C:\rtools40\mingw32\bin`
and `C:\rtools40\mingw64\bin` are still first in the `Path`. In case
the installer prepended something to `Path` (e.g. something like
`C:\ProgramData\Oracle\Java\javapath`), move it towards the end of
`Path` (e.g. anywhere after `C:\Program Files\Git\cmd`). See _Edit an
environment variable_ in the _Managing environment variables_ section
at the top of this document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this
account if you were already logged on) try to load the rJava package for
the 64-bit arch (this package will be automatically installed after the
1st build run but cannot be loaded if Java is not found on the system).
To do this: open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc`,
start 64-bit R (with `R\bin\R --arch x64`, or just `R\bin\R` since x64
is the default), then:

    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")

Note that `library(rJava)` should fail in 32-bit R (e.g. in an R session
started with `R\bin\R --arch i386`).


### 4.2 Install libxml2 and google protocol buffer

This is needed in order to compile the RProtoBufLib and flowWorkspace
packages.

Download libxml2 and google protocol buffer Windows binaries from

  https://rglab.github.io/binaries/

Extract all the files to `C:\libxml2` and to `C:\protobuf` respectively.
Set environment variables `LIB_XML2` and `LIB_PROTOBUF` to `C:/libxml2`
and `C:/protobuf`, respectively (see _Edit an environment variable_
in the _Managing environment variables_ section at the top of this document
for how to do this). Make sure to use `/` instead of `\` as the directory
delimiter.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the flowWorkspace package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL RProtoBufLib
    ..\R\bin\R CMD INSTALL flowWorkspace


### 4.3 Install JAGS

Go to https://www.sourceforge.net/projects/mcmc-jags/files and click
on "Download Latest Version" (`JAGS-4.3.0.exe` as of Nov. 2020).

Use the default settings when running the installer.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to load the rjags package e.g. open a
PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc`, start R (with
`R\bin\R`), then:

    library(rjags)
    # Loading required package: coda
    # Linked to JAGS 4.3.0
    # Loaded modules: basemod,bugs


### 4.4 Install Ghostscript

Available at: https://www.ghostscript.com/download/gsdnld.html

Choose Ghostscript AGPL Release for 64-bit Windows (`gs9533w64.exe` as
of Nov. 2020).

Use the default settings when running the installer.

Append `C:\Program Files\gs\gs9.53.3\bin` to `Path` (see _Edit an environment
variable_ in the _Managing environment variables_ section at the top of this
document for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on):

    which gswin64  # /c/Program Files/gs/gs9.53.3/bin/gswin64

Then try to build a package that uses Ghostscript for its vignette e.g. open
a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat` (this folder
will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build clustComp
    ..\R\bin\R CMD build MANOR
    ..\R\bin\R CMD build OrderedList
    ..\R\bin\R CMD build twilight
    ..\R\bin\R CMD check RnBeads_<X.Y.Z>.tar.gz


### 4.5 Install libSBML

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
not backslash). See _Edit an environment variable_ in the _Managing
environment variables_ section at the top of this document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the rsbml package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL rsbml


### 4.6 Install Open Babel 3

This is needed in order to compile the ChemmineOB package.

Depending on whether the Girke lab provides pre-compiled Windows binaries
for Open Babel 3 or not, you'll need to follow one of the two methods below.

#### Method 1: Install Open Babel 3 pre-compiled Windows binaries

Download the pre-compiled Windows binaries from

  https://github.com/girke-lab/ChemmineOB/releases/tag/3.0.0

Extract all the files to `C:\openbabel3`.

Set environment variables `OPEN_BABEL_BIN` and `OPEN_BABEL_SRC` to
`c:/openbabel3/bin` and `c:/openbabel3/src`, respectively (see _Edit an
environment variable_ in the _Managing environment variables_ section
at the top of this document for how to do this). Make sure to use `/`
instead of `\` as the directory delimiter.

#### Method 2: Install Open Babel 3 from source

Hopefully you manage to install pre-compiled Windows binaries (see above)
so you don't need to do this.

Follow instructions in `ChemmineOB/INSTALL` for how to compile Open Babel 3
on Windows.

IMPORTANT: Unlike all the other things here that need to be installed from
a personal administrator account, this one needs to be installed from the
`biocbuild` account. That's because the compilation process described in
`ChemmineOB/INSTALL` needs to access stuff under

    c:/Users/biocbuild/bbs-3.14-bioc/R/library/zlibbioc/

#### Testing

From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the ChemmineOB package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL ChemmineOB


### 4.7 Install Strawberry Perl

Available at: http://strawberryperl.com (this site does not support HTTPS)

Download installer for Windows 64-bit (`strawberry-perl-5.32.0.1-64bit.msi`
as of Nov. 2020).

When running the installer, keep all the default settings.
Check that the perl executable is in `Path`:

    which perl  # /c/Strawberry/perl/bin/perl

If `which perl` returns `/usr/bin/perl` then you MUST rename the `perl.exe`
file located in `C:\rtools40\usr\bin` to avoid any conflict. See
_Install Rtools_ section above for more information.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Perl e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build LowMACA

(Note that this package also needs Clustal Omega.)


### 4.8 Install Clustal Omega

Available at: http://www.clustal.org/omega/ (this site does not support HTTPS)

Download Windows 64-bit zip file (`clustal-omega-1.2.2-win64.zip` as
of Nov. 2020).

Extract all the files in `C:\ClustalO`. Make sure that the files
get extracted in `C:\ClustalO\` and not in a subdirectory (e.g. in
`C:\ClustalO\clustal-omega-1.2.2-win64\`).

Append `C:\ClustalO` to `Path` (see _Edit an environment variable_
in the _Managing environment variables_ section at the top of this
document for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Clustal Omega
e.g. open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build LowMACA

(Note that this package also needs Perl.)


### 4.9 Install ImmuneSpace credentials

Set environment variable `ISR_login` and `ISR_pwd` to `bioc@immunespace.org`
and `1notCRAN`, respectively. See _Edit an environment variable_
in the _Managing environment variables_ section at the top of this
document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build the ImmuneSpaceR package e.g.
open a PowerShell window, `cd` to `D:\biocbuild\bbs-3.14-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build ImmuneSpaceR


### 4.10 Install gtkmm

Download `gtkmm-win64-devel-2.22.0-2.exe` from

  https://download.gnome.org/binaries/win64/gtkmm/2.22/

Run it (use default settings). This installs gtkmm in `C:\gtkmm64`

Set `GTK_PATH` to `C:\gtkmm64`

Also make sure that `C:\rtools40\usr\bin`, `C:\rtools40\mingw32\bin`
and `C:\rtools40\mingw64\bin` are still first in the `Path`. In case
the installer prepended something to `Path` (e.g. something like
`C:\gtkmm64\bin`), move it towards the end of `Path` (e.g. anywhere
after `C:\ClustalO`). See _Edit an environment variable_ in
the _Managing environment variables_ section at the top of this
document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the HilbertVisGUI package
for the x64 arch only e.g. open a PowerShell window, `cd` to
`D:\biocbuild\bbs-3.14-bioc\meat` (this folder will be automatically
created after the 1st build run), then:

    ..\R\bin\R --arch x64 CMD INSTALL --no-multiarch HilbertVisGUI

NOV. 2020: The above fails at the linking step with a bunch of "undefined
reference" errors:

    C:/rtools40/mingw64/bin/g++ -std=gnu++11 -shared -s -static-libgcc -o HilbertVisGUI.dll tmp.def R_env_prot.o R_interface.o colorizers.o display.o ruler.o window.o -LC:/gtkmm64/lib -Lc:/devel/dist/win64/libpng-1.4.3-1/lib -lgtkmm-2.4 -latkmm-1.6 -lgdkmm-2.4 -lgiomm-2.4 -lpangomm-1.4 -lgtk-win32-2.0 -lglibmm-2.4 -lcairomm-1.0 -lsigc-2.0 -lgdk-win32-2.0 -latk-1.0 -lgio-2.0 -lpangowin32-1.0 -lgdi32 -lpangocairo-1.0 -lgdk_pixbuf-2.0 -lpng14 -lpango-1.0 -lcairo -lgobject-2.0 -lgmodule-2.0 -lgthread-2.0 -lglib-2.0 -lintl -LC:/extsoft/lib/x64 -LC:/extsoft/lib -LD:/biocbuild/bbs-3.14-bioc/R/bin/x64 -lR
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: ruler.o:ruler.cc:(.text+0x119c): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: ruler.o:ruler.cc:(.text+0x12d1): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: ruler.o:ruler.cc:(.text+0x21de): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: ruler.o:ruler.cc:(.text+0x2457): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: window.o:window.cc:(.text+0x4c9): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: window.o:window.cc:(.text+0x5ac6): undefined reference to `Glib::file_test(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, Glib::FileTest)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: window.o:window.cc:(.text+0x5b31): undefined reference to `Glib::filename_display_basename(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: window.o:window.cc:(.text+0x5b70): undefined reference to `Glib::ustring::ustring(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
    C:/rtools40/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/8.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: window.o:window.cc:(.text+0x5d45): undefined reference to `Gdk::Pixbuf::save(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, Glib::ustring const&)'
    collect2.exe: error: ld returned 1 exit status
    no DLL was created

I suspect that this is because of a binary incompatibility between the
binaries provided by `gtkmm-win64-devel-2.22.0-2.exe` (which is 10 year old
and was compiled with an old version of `gcc`) and the compilers provided
by Rtools40 (`gcc` 8.3.0).



## 5. Known issues


### 5.1 file association for 'http://...' not available or invalid

Affects Bioconductor packages:

- BiocDockerManager:
    ```
    BiocDockerManager::help()
    # Error in shell.exec(url) : 
    #   file association for 'https://hub.docker.com/r/bioconductor/bioconductor_docker' not available or invalid
    ```
- GenomicFeatures:
    ```
    browseUCSCtrack("hg38", tablename="knownGene")
    # Error in shell.exec(url) : 
    #   file association for 'http://genome.ucsc.edu/cgi-bin//hgTrackUi?db=hg38&g=knownGene' not available or invalid
    ```
- hpar:
    ```
    test_check("hpar")
    # -- 1. Error: getHpa (@test_hpa.R#49)  ------------------------------------------
    # file association for 'http://www.proteinatlas.org/ENSG00000000003' not available or invalid
    ```
- miRBaseConverter:
    ```
    goTo_miRBase(Accession1)
    # Error in shell.exec(url) : 
    #   file association for 'http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=MI0000447' not available or invalid
    ```
- rWikiPathways:
    ```
    wikipathwaysAPI()
    # Error in shell.exec(url) : 
    #   file association for 'https://webservice.wikipathways.org/ui' not available or invalid
    ```



## 6. Set up other builds


### 6.1 Annotation builds

Not run on Windows at the moment.


### 6.2 Experimental data builds

In a PowerShell window from the `biocbuild` account:

    cd D:\biocbuild
    mkdir bbs-3.14-data-experiment
    mkdir bbs-3.14-data-experiment\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.14-data-experiment`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 9:25 AM -
        Recur every 1 week on Monday and Thursday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.14\data-experiment\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.14-data-experiment\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.14\data-experiment\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.3 Worflows builds

In a PowerShell window from the `biocbuild` account:

    cd D:\biocbuild
    mkdir bbs-3.14-workflows
    mkdir bbs-3.14-workflows\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.14-workflows`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 9:00 AM -
        Recur every 1 week on Tuesday and Friday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.14\workflows\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.14-workflows\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.14\workflows\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.4 Books builds

In a PowerShell window from the `biocbuild` account:

    cd D:\biocbuild
    mkdir bbs-3.14-books
    mkdir bbs-3.14-books\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.14-books`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 10:30 AM -
        Recur every 1 week on Tuesday and Friday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.14\books\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.14-books\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.14\books\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.5 Long Tests builds

In a PowerShell window from the `biocbuild` account:

    cd D:\biocbuild
    mkdir bbs-3.14-bioc-longtests
    mkdir bbs-3.14-bioc-longtests\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.14-bioc-longtests`
    - In Security options:
      - Use `RIESLING1\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2019

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 4:00 PM -
        Recur every 1 week on Saturday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `D:\biocbuild\BBS\3.14\bioc-longtests\riesling1\run.bat`
      - Add arguments: `>>D:\biocbuild\bbs-3.14-bioc-longtests\log\riesling1.log 2>&1`
      - Start in: `D:\biocbuild\BBS\3.14\bioc-longtests\riesling1`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)



## 7. Single Package Builder Requirements


### 7.1 Create the `pkgbuild` account

Username: `pkgbuild`

For this account:
- [ ] User must change password at next logon
- [x] User cannot change password
- [x] Password never expires
- [ ] Account is disabled

By default, the home folder will be `C:\Users\pkgbuild`. If space on `C:` is
limited this might need to be changed to something else (e.g. `D:\pkgbuild`).
To do this: double-click on the `pkgbuild` user and make the change in the
Profile tab. Note that the `C:\Users\pkgbuild` folder will still be created
and populated at first logon.

Make the `pkgbuild` user a member of the `Remote Desktop Users` group.


### 7.2 Grant the `pkgbuild` user "Log on as batch job" rights

(This is needed in order to define scheduled tasks run by the `pkgbuild`
user.)

Go in Local Security Policy -> Local Policies -> User Rights Assignment

In the right pane, right-click on 'Log on as a batch job' -> Properties

Add `pkgbuild` user.


### 7.3 Grant the `pkgbuild` user permissions within the `biocbuild` user folder

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


### 7.4 Grant the `pkgbuild` user permissions within the `Windows\Temp` folder

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

