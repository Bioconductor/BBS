# How to set up a Windows Server 2022 system for the daily builds



This document describes the process of setting up a Windows Server 2022
machine to run the Bioconductor daily builds. It's been used to configure
palomino, an Azure VM running Windows Server 2022 Datacenter Azure Edition.



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

Always from the Admin account or from a _personal administrator account_
(see below about this):

- Go to Settings -> System -> About.

- Click on "Advanced system settings" at the bottom of the right pane. This
  opens the "System Properties" window.

- In the "System Properties" window, click on Environment Variables...

Always go to *System variables* (at the bottom) to add new variables or edit
existing variables. Do not add or edit user variables (at the top).



## 1. Initial setup (from the Administrator account)


Everything in this section must be done **from the Administrator account**.
For an Azure VM, an account with the same username as the name of the VM
should already exist and have admin privileges.

On a freshly installed Windows OS, the first time you'll log on to the
Administrator account, you'll be asked if you want this PC to be discoverable
by other PCs and devices on this network. Answer "No".


### 1.1 Install all pending Windows Updates

In Settings, go to Update & Security.

If updates are available, click on Install now. When installation is over,
restart the machine if necessary.

Then check for updates again as new updates could become available after a reboot,
and repeat the above if necessary.

Also install "Optional quality update" if they are available.


### 1.2 Check the disks

A lot of disk space is required to run the builds. Make sure that the machine
has at least 768GB of available space on one of its disks (`C:`, `D:`, `E:`,
or `F:`). On an Azure VM, we use a dedicated data disk for the builds. Note
that this disk needs to be created as an additional resource (e.g.
`palomino_DataDisk_0`) and it typically shows up as "Local Disk E:". If the
disk is attached but not visible, it's probably because it was not initialized
yet.

See https://docs.microsoft.com/en-us/azure/virtual-machines/windows/attach-managed-disk-portal for how to initialize the disk.


### 1.3 Check time and time zone

In Settings, go to Time & Language and make sure date, time, and time zone
are correct. Note that using the same time zone for all the build machines
makes things easier, less confusing, and less error-prone for everybody. All
our build machines use the "(UTC-05:00) Eastern Time (US & Canada)" time zone
at the moment.


### 1.4 Check the size of the paging file (virtual memory)

Azure VMs tend to use a very small paging file by default. For example, on
a VM of size F16s\_v2 (32 Gb of RAM), the paging file is only 16 Gb, which
will likely cause the builds to fail with the following error:

    The paging file is too small for this operation to complete

To check the paging size:

- Go to Settings -> System -> About.

- Click on "Advanced system settings" at the bottom of the right pane. This
  opens the "System Properties" window.

- In the "System Properties" window, click on the Settings button located
  in the Performance box. This opens the "Performance Options" window.

- In the "Performance Options" window, go to the Advanced tab and check
  the Total paging file size for all drives. This should be set to _at least_
  1.5 times the amount of RAM. For example on a F16s\_v2 VM, this should be
  set to 48 Gb.

To increase the paging size:

- Click on Change (in the Advanced tab of the "Performance Options" window,
  see above for how to get there).

- Click on the drive that says System managed.

- Select Custom size, then enter the Initial and Maximum sizes in MB e.g.
  50000 and 100000 for a F16s\_v2 VM.

- Click on Set, then on OK.

- Restart the computer.


### 1.5 Install a decent web browser (for all users)

E.g. Google Chrome or Firefox.

Known problem: There are some "file association" problems observed on some
versions of Windows Server when running `R CMD check` on packages that contain
calls to `browseURL()` in their examples. For example running `R CMD check` on
BiocDockerManager or tRNAdbImport produces:

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


### 1.6 Install Visual Studio Community 2022

Provides the `editbin` command, plus some DLLs apparently needed by the
most recent versions of the `tensorflow` Python module.

**From the Administrator account**:

- Download Visual Studio Community 2022 from
  https://visualstudio.microsoft.com/ (it's a free download)

- Start the installer:

  - On the first screen, go to "Individual components" and select the
    latest "MSVC v143 - VS 2022 C++ x64/x86 build tools" in the "Compilers,
    build tools, and runtimes" section.
    Total space required (bottom right) should go up from 1.39GB to 3.49GB.
    Click Install. When asked "Do you want to continue without workloads?",
    click on "Continue".

  - At the end of the installation, skip the "Sign in" step.

  - Then click on Start Visual Studio, click on Continue without code,
    and Exit.

  - Close the Visual Studio Installer.


### 1.7 Install Python 3 (for all users)

**From the Administrator account**:

Download the Latest Python 3 Release from
https://www.python.org/downloads/windows/

Choose the "Windows installer (64-bit)".

When running the installer:
- Select "Add Python 3.9 to PATH" then click on "Customize installation".
- In the "Optional Features" screen, everything should be selected. Click
  Next without changing anything.
- In "Advanced Options" choose "Install for all users" and change install
  location from `C:\Program Files\Python39` to `C:\Python39`, then click
  on "Install".

ALSO: You might need to explicitly associate `.py` files with Python. To
test whether the association works, go to `C:\Python39\Tools\demo` in the
File Explorer, and double click on `hanoi`. If the program starts, then all
is fine. If not:
- A popup window will ask you: How do you want to open this type of file
  (`.py`)? Make sure the "Always use this app to open .py files" box is
  checked. Click on "More apps".
- Scroll all the way down and click on "Look for another app on this PC".
  This opens the File Explorer.
- In the File Explorer find the python file in `C:\Python39` and
  double-click on it.


### 1.8 Upgrade to the latest pip

**From the Administrator account** in a PowerShell window:

    python -m pip install --upgrade pip


### 1.9 Install Python 3 modules

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

No longer needed (looks like Bioconductor package rhdf5client no longer needs
this):

    #pip install h5pyd

No longer needed (as of Oct. 2021):

    #pip install nbconvert

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

- `h5pyd` is needed by Bioconductor package rhdf5client. UPDATE (2021/12/10):
  Looks like it's no longer the case.

- `nbconvert` is needed by CRAN package nbconvertR which is itself used by
  Bioconductor package destiny. UPDATE (2021/12/06): destiny got deprecated
  in BioC 3.14 and removed from BioC 3.15 so we no longer need the `nbconvert`
  module on the builds machines.

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

then please refer to the _Install Visual Studio Community 2022_ section above
in this document for how to fix this.


### 1.10 Create personal administrator accounts

Go in Computer Management
      -> System Tools
         -> Local Users and Groups
            -> Users

Then in the Actions panel (on the right):
      -> Users
         -> More Actions
            -> New User

- Username: hpages / Full name: Hervé Pagès

- Username: jwokaty / Full name: Jennifer Wokaty

- Username: lshepherd / Full name: Lori Shepherd

- Username: stvjc / Full name: Vince Carey

If you create an account for yourself:
- Set your real password.
- Choose the following settings:
  - [ ] User must change password at next logon
  - [ ] User cannot change password
  - [x] Password never expires
  - [ ] Account is disabled

If you create an account for someone else:
- Set a temporary password.
- Choose the following settings:
  - [x] User must change password at next logon
  - [ ] User cannot change password
  - [ ] Password never expires
  - [ ] Account is disabled

All these real users should be made members of the `Administrators` group.

TESTING: Try to access your new account via a remote desktop client (e.g.
rdesktop or Remmina on Linux).


### 1.11 Create the `biocbuild` account

Username: `biocbuild`

For this account:
- [ ] User must change password at next logon
- [x] User cannot change password
- [x] Password never expires
- [ ] Account is disabled

By default, the home folder will be `C:\Users\biocbuild`. If space on `C:` is
limited this might need to be changed to something else (e.g. `E:\biocbuild`).
To do this: double-click on the `biocbuild` user and make the change in the
Profile tab. Note that the `C:\Users\biocbuild` folder will still be created
and populated at first logon.

Then make the `biocbuild` user a member of the `Remote Desktop Users` group.
This is needed to allow RDP access to the `biocbuild` account. Note that the
personal administrator accounts created earlier don't need this because members
of the `Administrators` group are automatically allow RDP access.


### 1.12 Grant the `biocbuild` user "Log on as batch job" rights

(This is needed in order to define scheduled tasks run by the `biocbuild`
user.)

Go in Local Security Policy -> Local Policies -> User Rights Assignment

In the right pane, right-click on 'Log on as a batch job' -> Properties

Add `biocbuild` user.


### 1.13 Install 32-bit Cygwin (for all users)

Cygwin is needed for `ssh`, `rsync`, `curl`, and `vim`.

Go to https://www.cygwin.com/, click on Install Cygwin, then download
and run `setup-x86.exe` to install or update Cygwin. IMPORTANT: Do NOT
install the 64-bit version!

In the installer:
- Install for all users.
- In the Editors category: make sure package `vim` is selected.
- In the Net category: make sure packages `curl`, `openssh`, and `rsync` are
  selected.
- Note that the Cygwin 32-bit DLL will automatically be installed.
- Don't Create icon on Desktop.

Finally **prepend** `C:\cygwin\bin` to `Path` (see _Edit an environment
variable_ in the _Managing environment variables_ section at the top of
this document for how to do this). At this point `C:\cygwin\bin` should
be first in `Path`, right before `C:\Python39\Scripts\` and `C:\Python39\`.

TESTING: Open a PowerShell window and try to run `ssh`, `rsync`, or `curl`
in it. Do this by just typing the name of the command followed by <Enter>.
If `Path` was set correctly, the command should be found (the Cygwin
executables are in `C:\cygwin\bin`).

IMPORTANT NOTE: We usually don't need the Cygwin terminal. Generally speaking,
the PowerShell window is the preferred command line environment when working
interactively on a Windows build machine.


### 1.14 Install git client for Windows

Available at https://git-scm.com/download/win

Keep all the default settings on all the screens (there are many) when
running the installer.

TESTING: Open a PowerShell window and try to run `git --version`


### 1.15 Install MiKTeX

If this is a reinstallation of MiKTeX, make sure to uninstall it (from
the Administrator account) before reinstalling.

Go to https://miktex.org/download and download the latest Basic MiKTeX
64-bit Installer (`basic-miktex-21.12-x64.exe` as of Dec. 2021).

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


### 1.16 Install Perl

Required by MiKTeX command `pdfcrop.exe` and some Bioconductor packages
like LowMACA.

We use Strawberry Perl available at https://strawberryperl.com.

Download installer for Windows 64-bit (`strawberry-perl-5.32.1.1-64bit.msi`
as of Dec. 2021).

When running the installer, keep all the default settings.


### 1.17 Sign out from the Administrator account

**From now on, all administrative tasks must be performed from one of the
_personal administrator accounts_ instead of the Administrator account.**



## 2. From a personal administrator account


Most actions in this section must be done **from a personal administrator
account**.


### 2.1 In `biocbuild`'s home: clone BBS git and create log folder

**From the `biocbuild` account** in a PowerShell window:

    cd E:\biocbuild
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
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task At startup

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `C:\Python39\python.exe`
      - Add arguments: `E:\biocbuild\BBS\utils\do_nothing_forever.py`
      - Start in: `E:\biocbuild\log`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)

Before the task can be started, the `E:\biocbuild\log` folder should
be created from the `biocbuild` account. The first time the task will be
started, the `E:\biocbuild\log\loggon_biocbuild_at_startup.log` file
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
        configurable on Windows Server 2022 -- was probably a bug in
        previous versions anyways because there is no SYSTEM user)
      - Run with highest privileges
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
    - In Settings:
        Weekly - At 2:00 PM - Recur every 1 week on each day of the week
                              except on Saturday
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
      nothing should be checked (except maybe "Allow task to be run on demand"
      if you want to be able to reboot the machine by running this task
      manually)

  - Then click OK on bottom right


### 2.4 Schedule installation of system updates before daily reboot

This is not mandatory but RECOMMENDED.

NOTE: Instructions below are for Windows Server 2012. TODO: Update them
for Windows Server 2022.

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

In Dec. 2021, CRAN has switched to a new toolchain to build R and R
packages.

**From a personal administrator account**:

- Go to https://www.r-project.org/nosvn/winutf8/ucrt3/

- Download Rtools42 for Windows 64-bit: `rtools42-4960-4926.exe`

- Run the installer and keep all the defaults. This will install Rtools42
  in `C:\rtools42`.

- Do **NOT** follow the "Putting Rtools on the PATH" instructions given
  on Rtools webpage as they put Rtools on the PATH only in the context of
  running R. We want Rtools to **always** be on the PATH, not just in the
  context of an R session.

- **Prepend** `C:\rtools42\usr\bin` and `C:\rtools42\x86_64-w64-mingw32.static.posix\bin`
  to `Path` (see _Edit an environment variable_ in the _Managing environment variables_
  section at the top of this document for how to do this).

  IMPORTANT: On a Windows build machine, `C:\rtools42\usr\bin` and
  `C:\rtools42\mingw64\bin` should **always be first** in the `Path`.

- Finally, rename the `perl.exe` file located in `C:\rtools42\usr\bin` to
  avoid any conflict with Strawberry Perl (we will install this later).
  E.g. rename to `perl_DO_NOT_USE.exe`.

TESTING: Log out and on again so that the changes to `Path` take effect. Then
in a PowerShell window:

    which which     # /usr/bin/which (provided by rtools42)
    which ssh       # /c/cygwin/bin/ssh
    which rsync     # /usr/bin/rsync, because rsync from rtools42 should be
                    # before rsync from Cygwin in Path
    which curl      # /usr/bin/curl, because curl from rtools42 should be
                    # before curl from Cygwin in Path
    which vi        # /c/cygwin/bin/vi
    rsync           # Will crash if 64-bit Cygwin was installed instead
                    # of 32-bit Cygwin!
    which make      # /usr/bin/make (provided by rtools42)
    make --version  # GNU Make 4.3
    which gcc       # /x86_64-w64-mingw32.static.posix/bin/gcc (provided by rtools42)
    gcc --version   # gcc.exe (Built by Jeroen for the R-project) 10.3.0
    which chmod     # /usr/bin/chmod (provided by rtools42)
    which perl      # /c/Strawberry/perl/bin/perl (NOT /usr/bin/perl)

### 2.8 Create and populate C:\extsoft

**From a personal administrator account**:

Download `local323.zip`, `spatial324.zip`, and `curl-7.40.0.zip` from
https://www.stats.ox.ac.uk/pub/Rtools/goodies/multilib/ and unzip them
**in that order** in `C:\extsoft`.


### 2.9 Install Pandoc

**From a personal administrator account**:

Available at: https://pandoc.org/installing.html#windows

Do NOT download the latest installer for Windows x86\_64
(`pandoc-2.11.1.1-windows-x86_64.msi` as of Nov. 2020). See
IMPORTANT NOTE below. Instead pick the installer for version
2.7.3 (`pandoc-2.7.3-windows-x86_64.msi`, available at
https://github.com/jgm/pandoc/releases/tag/2.7.3) and run it.

Direct link to the Pandoc 2.7.3 installer:

  https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-windows-x86_64.msi

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

    cd E:\biocbuild\bbs-3.15-bioc\meat
    ..\R\bin\R CMD build dagLogo
    ..\R\bin\R CMD build Harman



## 3. Set up the Bioconductor software builds


### 3.1 Check connectivity with central builder

All the steps described in this section must be performed in a PowerShell
window and from the `biocbuild` account.

#### Check that you can ssh to the central builder

Create the `E:\biocbuild\.ssh` folder and populate it with:
- biocbuild's private RSA key (copy the `id_rsa` file from another builder).
- an SSH config the you copy and adapt from another Windows builder.

Then:

    ssh -F /cygdrive/e/biocbuild/.ssh/config biocbuild@nebbiolo1

#### Check that you can send HTTP requests to the central builder

    curl http://155.52.207.165


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
locations to something else e.g. to `E:\biocbuild\AnnotationHub_cache`
and `E:\biocbuild\ExperimentHub_cache`. The location of the caches can
be controlled via environment variables `ANNOTATION_HUB_CACHE`
and `EXPERIMENT_HUB_CACHE`, which you can set permanently by using
the `setx.exe` command in a PowerShell window e.g.:

    setx ANNOTATION_HUB_CACHE "E:\biocbuild\AnnotationHub_cache"
    setx EXPERIMENT_HUB_CACHE "E:\biocbuild\ExperimentHub_cache"

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

    cd E:\biocbuild
    mkdir bbs-3.15-bioc
    cd bbs-3.15-bioc
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
Then go in the File Explorer and remove `E:\biocbuild\bbs-3.15-bioc\R`.

When running the installer:
- Ignore warning about the current user not being an admin
- Select destination location `E:\biocbuild\bbs-3.15-bioc\R`
- Don't create a Start Menu Folder
- Don't create a desktop or Quick Launch shortcut

#### Install BiocManager

In a PowerShell window, go to `E:\biocbuild\bbs-3.15-bioc` and start R:

    cd E:\biocbuild\bbs-3.15-bioc
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

`LOCAL_SOFT` needs to be set to `C:/extsoft` in `R\etc\x64\Makeconf`:

From `E:\biocbuild\bbs-3.15-bioc`:

    cd R\etc\x64
    C:\rtools42\usr\bin\cp.exe -i Makeconf Makeconf.original
    vi Makeconf

In `Makeconf`, replace line

    LOCAL_SOFT ?=

with

    LOCAL_SOFT = C:/extsoft

Make sure to use a forward slash (`/`) and to not introduce a trailing space!

Save and quit `vi`.

Check your change with:

    C:\rtools42\usr\bin\diff.exe Makeconf Makeconf.original

TESTING:

- Make sure that the edited file can be accessed from the `pkgbuild`
  account. From the `pkgbuild` account in a PowerShell window:
    ```
    C:\rtools42\usr\bin\cat E:\biocbuild\bbs-3.15-bioc\R\etc\x64\Makeconf
    ```

- Try to compile a package that uses libcurl (provided by `C:\extsoft`) e.g.
  open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
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
    - Name: `bbs-3.15-bioc`
    - In Security options:
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - At 3:00 PM - Recur every 1 week on each day of the week
                              except on Saturday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `E:\biocbuild\BBS\3.15\bioc\palomino\run.bat`
      - Add arguments: `>>E:\biocbuild\bbs-3.15-bioc\log\palomino.log 2>&1`
      - Start in: `E:\biocbuild\BBS\3.15\bioc\palomino`

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
(`jdk-17_windows-x64_bin.exe` as of Dec. 2021). Direct link:

  https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe

Use the default settings when running the installer.

Make sure that `C:\rtools42\usr\bin` and `C:\rtools42\mingw64\bin`
are still first in the `Path`. In case the JDK installer prepended
something like `C:\Program Files\Common Files\Oracle\Java\javapath`
to `Path`, then move it towards the end of `Path` (e.g. anywhere after
`C:\Program Files\Git\cmd`). See _Edit an environment variable_ in
the _Managing environment variables_ section at the top of this document
for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this
account if you were already logged on) try to load the rJava package
(this package will be automatically installed after the 1st build run
but it cannot be loaded if Java is not found on the system).
To do this: open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc`,
start R (with `R\bin\R`), then:

    library(rJava)
    .jinit()
    .jcall("java/lang/System", "S", "getProperty", "java.runtime.version")

Note that `library(rJava)` should fail in 32-bit R (e.g. in an R session
started with `R\bin\R --arch i386`).


### 4.2 Install libxml2

This is needed in order to compile the NetPathMiner package.

Download libxml2 (`libxml2.zip`) the binary for Windows from

  https://rglab.github.io/binaries/

Extract all the files to `C:\libxml2` and to `C:\protobuf` respectively.
Note that if, after extraction, the libxml2 files end up being extracted
in `C:\libxml2\libxml2` rather than in `C:\libxml2`, then you need to get
rid of that extra level of nesting. Same with the Google protocol buffer
files.

Set environment variables `LIB_XML2` and `LIB_PROTOBUF` to `C:/libxml2`
and `C:/protobuf`, respectively (see _Edit an environment variable_
in the _Managing environment variables_ section at the top of this document
for how to do this). Make sure to use `/` instead of `\` as the directory
delimiter.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the NetPathMiner package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL NetPathMiner


### 4.3 Install JAGS

This is needed by CRAN package rjags that various Bioconductor packages
depend on (CNVrd2, MADSEQ, infercnv).

Go to https://www.sourceforge.net/projects/mcmc-jags/files and click
on "Download Latest Version" (`JAGS-4.3.0.exe` as of Dec. 2021). If
you are using RTools42 + R UCRT, then download `JAGS-4.3.0.exe` from
https://www.r-project.org/nosvn/winutf8/ucrt3/extra/jags/ instead.

Use the default settings when running the installer. Make sure that all
the components to install are checked.

Set environment variable `JAGS_HOME` to `C:\Program Files\JAGS\JAGS-4.3.0`
(see _Edit an environment variable_ in the _Managing environment variables_
section at the top of this document for how to do this).
Note that setting `JAGS_HOME` is only needed on Windows and for rjags >= 4-12.
Unfortunately in rjags 4-12 the code used by the `.onLoad()` hook to find
JAGS on the machine changed from

    readRegistry("SOFTWARE\\JAGS", hive="HLM", maxdepth=2, view="32-bit")

to

    readRegistry("SOFTWARE\\JAGS", hive="HLM", maxdepth=2, view="64-bit")

but for some reason the latter fails with an error on our Windows builders.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to load the rjags package e.g. open a
PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc`, start R (with
`R\bin\R`), then:

    library(rjags)
    # Loading required package: coda
    # Linked to JAGS 4.3.0
    # Loaded modules: basemod,bugs


### 4.4 Install Ghostscript

Available at https://www.ghostscript.com/releases/

Choose Ghostscript AGPL Release for 64-bit Windows (`gs9550w64.exe` as
of Dec. 2021).

Use the default settings when running the installer.

Append `C:\Program Files\gs\gs9.55.0\bin` to `Path` (see _Edit an environment
variable_ in the _Managing environment variables_ section at the top of this
document for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on):

    which gswin64  # /c/Program Files/gs/gs9.53.3/bin/gswin64

Then try to build a package that uses Ghostscript for its vignette e.g. open
a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat` (this folder
will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build clustComp
    ..\R\bin\R CMD build MANOR
    ..\R\bin\R CMD build OrderedList
    ..\R\bin\R CMD build twilight
    ..\R\bin\R CMD check RnBeads_<X.Y.Z>.tar.gz


### 4.5 Install libSBML

Download `64-bit/libSBML-5.18.0-win-x64.exe` from
https://sourceforge.net/projects/sbml/files/libsbml/5.18.0/stable/Windows/

Use the default settings when running the installer.

Create `C:\libsbml` folder and copy
`C:\Program Files\SBML\libSBML-5.18.0-libxml2-x64\win64` to it.

Rename `C:\libsbml\win64` -> `C:\libsbml\x64`.

Set environment variable `LIBSBML_PATH` to `C:/libsbml` (use slash,
not backslash). See _Edit an environment variable_ in the _Managing
environment variables_ section at the top of this document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the rsbml package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL rsbml


### 4.6 Install Open Babel 3

This is needed in order to compile the ChemmineOB package.

Depending on whether the Girke lab provides pre-compiled Windows binaries
for Open Babel 3 or not, you'll need to follow one of the two methods below.

Note: As of December 2021, the 3.0.0 pre-compiled Windows binary does not
appear to work with the Rtools42, so you must compile Open Babel 3 from
source at http://openbabel.org/wiki/Category:Installation.

#### Method 1: Install Open Babel 3 pre-compiled Windows binaries

This is the easiest method.

Download the pre-compiled Windows binaries (`openbabel3-build.zip`)
from https://github.com/girke-lab/ChemmineOB/releases/tag/3.0.0

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
`ChemmineOB/INSTALL` needs to access stuff located in `R_HOME\library\zlibbioc`.

#### Testing

From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the ChemmineOB package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL ChemmineOB


### 4.7 Install Clustal Omega

Available at http://www.clustal.org/omega/ (this site does not support HTTPS)

Download Windows 64-bit zip file (`clustal-omega-1.2.2-win64.zip` as
of Dec. 2021).

Extract all the files in `C:\ClustalO` (last letter is the letter O, not
the number zero!). Make sure that the files get extracted in `C:\ClustalO\`
and not in a subdirectory (e.g. in `C:\ClustalO\clustal-omega-1.2.2-win64\`).

Append `C:\ClustalO` to `Path` (see _Edit an environment variable_
in the _Managing environment variables_ section at the top of this
document for how to do this).

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build a package that uses Clustal Omega
e.g. open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build LowMACA

(Note that this package also needs Perl.)


### 4.8 Install ImmuneSpace credentials

Set environment variable `ISR_login` and `ISR_pwd` to `bioc@immunespace.org`
and `1notCRAN`, respectively. See _Edit an environment variable_
in the _Managing environment variables_ section at the top of this
document for how to do this.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to build the ImmuneSpaceR package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD build ImmuneSpaceR


### 4.9 Install Dokan

This is needed by the Travel package.

Download `DokanSetup.exe` from https://dokan-dev.github.io/

Run the installer.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the Travel package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
(this folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL Travel


### 4.10 Install .NET 5.0 Runtime

This is needed by the rmspc package.

Download the Windows x64 Installer for .NET 5.0 Runtime (file
`dotnet-runtime-5.0.13-win-x64.exe` as of Dec. 2021) from
https://dotnet.microsoft.com/download/dotnet/5.0

Run the Installer.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on), in a PowerShell window:

    which dotnet    # /c/Program Files/dotnet/dotnet


### 4.11 Install protocol buffer

OCT 2021: THIS IS NO LONGER NEEDED! It seems that recent versions of
Bioconductor packages RProtoBufLib and flowWorkspace can be compiled
without this.

This is needed in order to compile the RProtoBufLib and flowWorkspace
packages.

Extract all the files to to `C:\protobuf`. Note that if, after extraction,
the protobuf files end up being extracted in `C:\protobuf\protobuf` rather
than in `C:\protobuf`, then you need to get rid of that extra level of nesting.

Set environment variables `LIB_PROTOBUF` to `C:/protobuf`
(see _Edit an environment variable_ in the _Managing environment variables_
section at the top of this document for how to do this). Make sure to use `/`
instead of `\` as the directory
delimiter.

TESTING: From the `biocbuild` account (log out and on again from this account
if you were already logged on) try to compile the flowWorkspace package e.g.
open a PowerShell window, `cd` to `E:\biocbuild\bbs-3.15-bioc\meat`
s folder will be automatically created after the 1st build run), then:

    ..\R\bin\R CMD INSTALL RProtoBufLib
    ..\R\bin\R CMD INSTALL flowWorkspace



## 5. Known issues


### 5.1 LaTeX package xcolor error

Already reported [here](https://github.com/latex3/xcolor/issues/10)
by Tomas on 2021-12-06. Affects a number of vignettes on CRAN.

The following Bioconductor packages are currently affected:
ASpediaFI, CNVrd2, gcatest, hierinf, LACE, lfa, lpsymphony, missRows,
monocle, MOSim, netbiov, OncoScore, SIMLR SparseSignatures, TNBC.CMS,
TRONCO, VERSO.



## 6. Set up other builds


### 6.1 Annotation builds

Not run on Windows at the moment.


### 6.2 Experimental data builds

In a PowerShell window from the `biocbuild` account:

    cd E:\biocbuild
    mkdir bbs-3.15-data-experiment
    mkdir bbs-3.15-data-experiment\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.15-data-experiment`
    - In Security options:
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 10:00 AM -
        Recur every 1 week on Tuesday and Thursday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `E:\biocbuild\BBS\3.15\data-experiment\palomino\run.bat`
      - Add arguments: `>>E:\biocbuild\bbs-3.15-data-experiment\log\palomino.log 2>&1`
      - Start in: `E:\biocbuild\BBS\3.15\data-experiment\palomino`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.3 Worflows builds

In a PowerShell window from the `biocbuild` account:

    cd E:\biocbuild
    mkdir bbs-3.15-workflows
    mkdir bbs-3.15-workflows\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.15-workflows`
    - In Security options:
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 8:00 AM -
        Recur every 1 week on Tuesday and Friday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `E:\biocbuild\BBS\3.15\workflows\palomino\run.bat`
      - Add arguments: `>>E:\biocbuild\bbs-3.15-workflows\log\palomino.log 2>&1`
      - Start in: `E:\biocbuild\BBS\3.15\workflows\palomino`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.4 Books builds

In a PowerShell window from the `biocbuild` account:

    cd E:\biocbuild
    mkdir bbs-3.15-books
    mkdir bbs-3.15-books\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.15-books`
    - In Security options:
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 7:00 AM -
        Recur every 1 week on Monday, Wednesday, and Friday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `E:\biocbuild\BBS\3.15\books\palomino\run.bat`
      - Add arguments: `>>E:\biocbuild\bbs-3.15-books\log\palomino.log 2>&1`
      - Start in: `E:\biocbuild\BBS\3.15\books\palomino`

  - Tab Conditions:
      nothing to do (keep all the defaults)

  - Tab Settings:
      nothing should be checked except 'Allow task to be run on demand' and
      'If the running task does not end when requested force it to stop'

  - Then click OK on bottom right (requires `biocbuild`'s password)


### 6.5 Long Tests builds

In a PowerShell window from the `biocbuild` account:

    cd E:\biocbuild
    mkdir bbs-3.15-bioc-longtests
    mkdir bbs-3.15-bioc-longtests\log

Then **from a personal administrator account** configure the task as follow:

- Open Task Scheduler

- Right-click on the `BBS` folder -> choose Create Task

  - Tab General:
    - Name: `bbs-3.15-bioc-longtests`
    - In Security options:
      - Use `PALOMINO\biocbuild` account to run the task
      - Run whether user is logged on or not
    - Configure for Windows Server 2022

  - Tab Triggers:
    - New Trigger
    - Begin the task On a schedule
      - In Settings:
        Weekly - Start on <leave current date> at 8:00 AM -
        Recur every 1 week on Saturday
    - In Advanced Settings:
        nothing should be checked except 'Enabled'

  - Tab Actions:
    - New Action
    - Action: Start a program
    - In Settings:
      - Program/script: `E:\biocbuild\BBS\3.15\bioc-longtests\palomino\run.bat`
      - Add arguments: `>>E:\biocbuild\bbs-3.15-bioc-longtests\log\palomino.log 2>&1`
      - Start in: `E:\biocbuild\BBS\3.15\bioc-longtests\palomino`

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
limited this might need to be changed to something else (e.g. `E:\pkgbuild`).
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

- `E:\biocbuild`

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

- `E:\biocbuild\bbs-3.12-bioc\meat`

  Using File Explorer, go to `E:\biocbuild\bbs-3.12-bioc` and right
  click the `meat` folder and choose properties. Go to the Security tab:
  - Click Edit
  - Click Add
  - Enter the object names to select: Users
  - Click Check Names to validate
  - Click OK

  For Permissions choose Read & execute, List folder contents and Read.

  Click OK.

- `E:\biocbuild\bbs-3.12-bioc\NodeInfo`

  Using File Explorer, go to `E:\biocbuild\bbs-3.12-bioc` and right
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

