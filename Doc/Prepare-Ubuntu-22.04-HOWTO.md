# How to set up an Ubuntu 22.04 system for the daily builds

Note: A machine running Ubuntu can be configured for the BBS with
https://github.com/Bioconductor/bioconductor_salt.

## 1. Initial setup (from a sudoer account)


Everything in this section must be done **from a sudoer account**.


### 1.1 Standalone vs non-standalone builder

A build machine can be set up either as a _standalone builder_ or as
a _non-standalone builder_.

A _non-standalone builder_ is a build node that participates to builds that
are run by a group of build machines. For example, 3 machines participated
to the BioC 3.11 software builds:
https://bioconductor.org/checkResults/3.11/bioc-LATEST/

When part of a group of build machines, one machine must be set up as the
_central builder_ (a.k.a. _primary node_) e.g. malbec2 in the case of the
BioC 3.11 software builds. The other machines, called _satellite nodes_,
only need to be set up as _non-standalone builders_, which is a
lighter/simpler set up.

There are 2 kinds of _non-standalone builders_:
- builders managed by the BioC core team called _internal build nodes_
- builders managed by an external group called _external build nodes_

An _internal build node_ must be able to communicate with the _central builder_
via HTTP/S and SSH. Note that this communication can generate some fair amount
of data transfer back and forth between each _satellite node_ and the _central
builder_ (> 5GB every day on normal days).

An _external build node_ must be able to communicate with the _central
builder_ via HTTP/S only. Additionally, the machine needs to be set up
in a way that allows the _central builder_ to retrieve the content of
`~/bbs-X.Y-bioc/products-out/` on a daily basis, typically via rsync.


### 1.2 Check hardware requirements

These are the requirements for running the BioC software builds.

For a _central builder_:

- At least 800GB of disk space

- At least 32 logical cores

- At least 48GB of RAM

For a _satellite node_ or _standalone builder_:

- At least 400GB of disk space

- At least 20 logical cores

- At least 32GB of RAM

These requirements are _very_ approximate and tend to increase over time (as
Bioconductor grows). The above numbers reflect the current state of affairs
as of Aug 2020.


### 1.3 Check `/etc/hostname` and `/etc/hosts`

This applies to all build machines, _standalone_ or _non-standalone_.

- `/etc/hostname` should contain the short name of the build
  machine as it will appear on the build report (e.g. `nebbiolo2`).
  Note that you will need to make sure to set `BBS_NODE_HOSTNAME`
  to the same value when you configure BBS (see for example
  `3.16/bioc/nebbiolo2/config.sh` in BBS git tree).

- Check `/etc/hosts` and make sure that it contains an entry that maps
  the name in `/etc/hostname` to 127.0.1.1 or to the permanent IP address
  of the machine.

TESTING: You should be able to ping yourself with e.g.:

    ping nebbiolo2

Note that not having this set properly will cause Bioconductor
package **RGMQL** to fail. So if you already have R and **RGMQL** installed
on the machine (which would be the case if the software builds are
already set up), you can start R and try:

    library(RGMQL)
    init_gmql()  # will fail if the short name of the machine
                 # does not resolve to itself


### 1.4 Apply any pending system updates and reboot

This applies to all build machines, _standalone_ or _non-standalone_.

#### Quick way:

    sudo apt-get update && sudo apt-get --with-new-pkgs upgrade && sudo apt autoremove
    sudo reboot

#### Not so quick way:

This "not so quick way" might require up to 5 calls to `sudo apt-get upgrade`!

- Let's start with the basic commands:
    ```
    sudo apt-get update
    sudo apt-get upgrade  # 1st time
    ```

- Then try `sudo apt-get upgrade` again (2nd time) to see if more actions are
  needed. It should display something like:
    ```
    0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
    ```
  But if it displays something like:
    ```
    ...
    The following packages have been kept back:
      base-files linux-headers-generic netplan.io ubuntu-server
    0 upgraded, 0 newly installed, 0 to remove and 4 not upgraded.
    ```
  then upgrade again with:
    ```
    sudo apt-get --with-new-pkgs upgrade  # 3rd time
    ```

- Then try `sudo apt-get upgrade` again (4th time). Now there shouldn't be
  any "kept back packages" anymore. However you could still see some "no
  longer required" packages:
    ```
    ...
    The following packages were automatically installed and are no longer required:
      linux-headers-4.15.0-136 linux-headers-4.15.0-136-generic
    Use 'sudo apt autoremove' to remove them.
    0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
    ```
  in which case just use the suggested command:
    ```
    sudo apt autoremove
    ```

- Then try `sudo apt-get upgrade` for the last time (5th time) and you should
  see something like this:
    ```
    Reading package lists... Done
    Building dependency tree
    Reading state information... Done
    Calculating upgrade... Done
    0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
    ```
  which indicates that everything is up-to-date.

- Finally you can reboot with:
    ```
    sudo reboot
    ```

IMPORTANT: The OS versions present on the build machines are listed
in the `BBS/nodes/nodespecs.py` file and the OS versions displayed on
the build reports are extracted from this file. So it's important to
keep this file in sync with the actual versions present on the builders.


### 1.5 Check locales

This applies to all build machines, _standalone_ or _non-standalone_.

The following command:

    cat /etc/default/locale

should display:

    #  File generated by update-locale
    LANG="en_US.UTF-8"

Note that with the above setting (`LANG="en_US.UTF-8"`), and if the `LC_TIME`
variable is not defined in the `/etc/default/locale` file, the `date` command
prints the time in AM/PM format on Ubuntu 22.04:

    date
    # Tue Apr 20 04:25:04 PM EDT 2021

To change this to 24-hour format (which is highly recommended), set `LC_TIME`
to `en_GB` like this:

    sudo locale-gen "en_GB"
    sudo update-locale LC_TIME="en_GB"

Then logout and login again for the change to take effect, and try:

    date
    # Tue 20 Apr 16:26:10 EDT 2021


### 1.6 Set up the `biocbuild` and `pkgbuild` accounts

This only applies to build machines managed by the BioC core team.
On an _external build node_, the builds can be run from any account.

#### Create the `biocbuild` account

    sudo adduser biocbuild

This should be set up as a regular account. In particular it should NOT have
sudo privileges. Ask a core team member what password to use for `biocbuild`.

#### Install RSA keys

Login as `biocbuild` and install the following RSA keys (in
the `~biocbuild/.ssh/` folder):
- `biocbuild` RSA private and public keys (`id_rsa` and `id_rsa.pub` files)
- core team member public keys (in `authorized_keys` file)

Easiest way to do this is to copy the keys from another build machine.

Then `chmod 400 ~/.ssh/id_rsa` so permissions look like this:

    biocbuild@nebbiolo2:~$ ls -l .ssh/id_rsa
    -r-------- 1 biocbuild biocbuild 1679 Apr 30 15:20 .ssh/id_rsa

#### (Optional) Set up the pkgbuild account

If the machine will also run the single package builder then you
should create the `pkgbuild` account. The process is the same as
the `biocbuild` account, including the password. The group of public
keys may differ, so ask if you are not sure who should have access.

#### Testing

- Logout and try to login again as `biocbuild`. If your public key was
  added to `~biocbuild/.ssh/authorized_keys` then you should no longer
  need to enter the `biocbuild` password or your passphrase.

- You should be able to ssh to master from the `biocbuild` account. Try:
    ```
    ssh -A webadmin@master.bioconductor.org
    ```
  It's important to make sure that this works otherwise the build system
  won't be able to push the daily build reports to master.

Then logout completely (i.e. first from the webadmin account on master, then
from the `biocbuild` account on the Linux builder) and go back to your personal
account on the machine (sudoer account).

TIP: Rather than using `sudo su -` to access the `biocbuild` account, it's
strongly recommended that you always use the following method to access
the `biocbuild` account, where `username` is replaced by your username and
`nebbiolo2` is replaced by its address:

    ssh -A -J username@ada.dfci.harvard.edu biocbuild@nebbiolo2

Otherwise, you may have issues when attempting subsequent configurations.


### 1.7 Run Xvfb as a service

This applies to all build machines, _standalone_ or _non-standalone_.

Some Bioconductor packages like **adSplit** or **lmdme**, contain examples that
need access to an X11 display. However, when running `R CMD check` in the
context of the daily builds, no X11 display is available. This will cause the
above packages to fail on the build report.  Here is the full list of packages
affected by this (as of April 2023): **adSplit**, **clippda**, **DaMiRseq**,
**fCI**, **GARS**, **lmdme**, **NormqPCR**, **OMICsPCA**, and **TTMap**.
Note that for some packages we will only see a warning but for some others
it will be an ERROR (either during the BUILD or CHECK stage).

If R is already installed on the machine, an easy way to reproduce the
problem is with:

    /path/to/Rscript -e 'png("fig2.png", type="Xlib")'
    #Error in .External2(C_X11, paste0("png::", filename), g$width, g$height,  :
    #  unable to start device PNG
    #Calls: png
    #In addition: Warning message:
    #In png("fig2.png", type = "Xlib") :
    #  unable to open connection to X11 display ''
    #Execution halted

If the software builds are already set up, you can access the `Rscript`
command by **going to the `biocbuild` account** and do:

    cd ~/bbs-3.19-bioc/
    R/bin/Rscript -e 'png("fig2.png", type="Xlib")'

Running Xvfb (X virtual framebuffer) as a service addresses this problem.

#### Install Xvfb

    sudo apt-get install xvfb

#### Create `/etc/init.d/xvfb`

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

#### Set `DISPLAY` in `/etc/profile.d/xvfb.sh`

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

#### Testing

**From the `biocbuild` account**:

    service xvfb status  # should be up and running
    echo $DISPLAY        # :1.0
    cd ~/bbs-3.19-bioc/
    R/bin/Rscript -e 'png("fig2.png", type="Xlib")'  # no more error!


### 1.8 Install Ubuntu/deb packages

This applies to all build machines, _standalone_ or _non-standalone_.

The packages needed on a Linux build machine running Ubuntu are in the files
under `BBS/Ubuntu-files/22.04/`. They can be installed with:

    sudo apt-get install <pkg1> <pkg2> <pkg3> ...

They can also be installed with the following code where `BBS_UBUNTU_PATH`
is the path to `BBS/Ubuntu-files/22.04` and `BBS_PACKAGES_FILE` is the
name of the text file containing the list of packages:

    BBS_UBUNTU_PATH=
    BBS_PACKAGES_FILE=
    sudo apt install $(cat $BBS_UBUNTU_PATH/$BBS_PACKAGES_FILE | awk '/^[^#]/ {print $1}')

#### Always nice to have

[apt_nice_to_have.txt](../Ubuntu-files/22.04/apt_nice_to_have.txt)

#### Packages required by the build system itself (BBS)

[apt_required_build.txt](../Ubuntu-files/22.04/apt_required_build.txt)

#### Packages for compiling R

[apt_required_compile_R.txt](../Ubuntu-files/22.04/apt_required_compile_R.txt) are
required to compile R.

[apt_optional_compile_R.txt](../Ubuntu-files/22.04/apt_optional_compile_R.txt)
are optional;  however, some capabilities will be missing.

#### Packages needed to build vignettes and reference manuals

[apt_vignettes_reference_manuals.txt](../Ubuntu-files/22.04/apt_vignettes_reference_manuals.txt)

#### Packages needed to support extra fonts (e.g. Helvetica)

Some R code can fail with errors like:

    Error in grid.Call(C_stringMetric, as.graphicsAnnot(x$label)) :
      X11 font -adobe-helvetica-%s-%s-*-*-%d-*-*-*-*-*-*-*, face 1 at size 11 could not be loaded

This can be solved by installing the packages in
[apt_extra_fonts.txt](../Ubuntu-files/22.04/apt_extra_fonts.txt)

Note that a reboot is required to make the fix effective.

#### Packages needed by some CRAN and/or BioC packages

For CRAN packages, install [apt_cran.txt](../Ubuntu-files/22.04/apt_cran.txt).

For BioC packages, install [apt_bioc.txt](../Ubuntu-files/22.04/apt_bioc.txt).

#### IMPORTANT NOTES

The list of things that need to be installed on a Linux builder is in
constant evolution as new or existing Biocondutor packages introduce
new system requirements. System requirements should preferably be installed
with `sudo apt-get install` whenever possible, which is the standard
installation method on Ubuntu. This has the following advantages:

1. It guarantees a clean _system-wide_ installation. More precisely, it
   guarantees that things get installed in standard locations that are
   available _for all the users_ on the machine.

2. It's safe. Even though we're using `sudo`, we can trust that
   `sudo apt-get install` won't mess up the system. There's no such
   guarantee with the specific installation methods used by individual
   software.

3. It makes things a lot easier to uninstall and thus tends to make it
   easier to keep the machine in a clean state in the long run. Things
   that have been installed via other installation mechanisms are sometimes
   hard to uninstall and it can be tricky to bring the machine back to
   its previous state.

4. It keeps the setup of the machine simple, easy to document, and easy
   to replicate. For example, to keep track of new system requirements,
   we just need to add the names of the required Ubuntu/Debian packages
   to `BBS/Ubuntu-files/22.04/apt_bioc.txt` or other appropriate file
   under `BBS/Ubuntu-files/22.04/`. This makes it easy to automate
   installation across machines including Docker images.

However, there's actually one important exception to the "install with
apt-get install first" rule: Python modules. These should preferably be
installed via `pip3`. See next section below.


### 1.9 Check Python 3 and install Python 3 modules

This applies to all build machines, _standalone_ or _non-standalone_.

#### Check Python 3

Check that Python 3 is available and in the `PATH` with:

    which python3

The above command should return the path to a system-wide Python interpreter
e.g. `/usr/bin/python3`.

Also check Python 3 version with:

    python3 --version

The version should be relatively recent e.g. >= 3.8.

#### Set `RETICULATE_PYTHON` in `/etc/profile`

We need to make sure that, by default, the **reticulate** package will
use the system-wide Python interpreter that is in the `PATH`.

In `/etc/profile` add:

    export RETICULATE_PYTHON="/usr/bin/python3"  # same as 'which python3'

Logout and login again for the changes to `/etc/profile` to take effect.

TESTING: **From the `biocbuild` account**. If R is already installed on the
machine, start it, and do:

    if (!require(reticulate))
        install.packages("reticulate", repos="https://cran.r-project.org")
    ## py_config() should display the path to the system-wide Python
    ## interpreter returned by the 'which python3' command above.
    ## It should also display this note:
    ##   NOTE: Python version was forced by RETICULATE_PYTHON
    py_config()

#### Install Python 3 modules needed by Single Package Builder

`virtualenv` is used by the Single Package Builder. Despite python3 shipping
with `venv`, `venv` is not sufficient. The SPB must use `virtualenv`.

    sudo -H pip3 install -r $BBS_UBUNTU_PATH/pip_spb.txt

#### Install Python 3 modules needed by CRAN/Bioconductor packages

Some CRAN/Bioconductor packages interact with Python 3 and Python modules.

CRAN packages do this via the **reticulate** package, and they are expected
to list their Python requirements in `SystemRequirements`. For those packages,
we need to install the required Python modules on the builders.

Bioconductor packages are supposed to do this via the **basilisk** package,
which will automatically handle their Python requirements. So for those
packages, we don't need to install any Python modules on the builders, and the
packages don't need to list their Python requirements in `SystemRequirements`.
Note however that not all Bioconductor packages use **basilisk** to handle
their Python requirements. Those that do not should be treated as CRAN packages
w.r.t. those requirements.

IMPORTANT NOTE: We deliberately install Python modules _system wide_
(with `sudo -H pip3 install <module>`) on the builders. This will make them
available to _all the builds_, independently of which account they will run
from (e.g. `biocbuild` for BBS or `pkgbuild` for the Single Package Builder).
Since we only install _trusted_ modules, this should not be a security
concern. See
https://askubuntu.com/questions/802544/is-sudo-pip-install-still-a-broken-practice)

    sudo -H pip3 install -r $BBS_UBUNTU_PATH/pip_pkgs.txt

Notes:

- `scipy` is needed by Bioconductor package **MOFA2** but also by
  the `scikit-learn` module (when `scikit-learn` is imported and `scipy` is not present,
  the former breaks). However, for some reason, `sudo -H pip3 install scikit-learn`
  does not install `scipy` and completes successfully even if `scipy` is
  not installed.

- `numpy`, `scikit-learn`, `h5py`, and `pandas` are needed by Bioconductor packages
  **BiocSklearn**, **MOFA2**, and `numpy` is also needed by Bioconductor
  package **DChIPRep**.

- `mofapy2` is needed by Bioconductor package **MOFA2**.

- `tensorflow` is needed by Bioconductor packages **DeepPINCS**. Note that trying
  to load the module in a Python 3 session, previous versions have raised the
  following error:
    ```
    >>> import tensorflow
    2020-08-08 16:52:56.617223: W tensorflow/stream_executor/platform/default/dso_loader.cc:59] Could not load dynamic library 'libcudart.so.10.1'; dlerror: libcudart.so.10.1: cannot open shared object file: No such file or directory
    2020-08-08 16:52:56.617255: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
    ```
  Even though the message says that the error can be ignored, you can get rid
  of it by installing the `libcudart` package. The most recent version of the
  package is `libcudart11.0:
    ```
    sudo apt-get install libcudart11.0
    ```

- `h5pyd` is needed by Bioconductor package **rhdf5client**.

- `nbconvert` and `jupyter` are needed by CRAN package **nbconvertR**
  which is itself used by Bioconductor package **destiny**.
  Note that `jupyter --version` should display something like this
  (as of Jan. 2021):
    ```
    hpages@nebbiolo2:~$ jupyter --version
    jupyter core     : 4.7.1
    jupyter-notebook : 6.3.0
    qtconsole        : 5.1.0
    ipython          : 7.23.0
    ipykernel        : 5.5.3
    jupyter client   : 6.1.12
    jupyter lab      : not installed
    nbconvert        : 6.0.7
    ipywidgets       : 7.6.3
    nbformat         : 5.1.3
    traitlets        : 5.0.5
    ```
  It's ok if jupyter lab is not installed but everything else should be.

- `matplotlib` and `phate` are needed by CRAN package **phateR** which is
  itself used by Bioconductor package **phemd**.

TESTING: From Python (start it with `python3`), check `tensorflow` version
with:

    import tensorflow
    tensorflow.version.VERSION  # should be 2.x.y


### 1.10 Run Apache server as a service

This is only required for a _standalone builder_ or _central builder_.

Install Apache server:

    sudo apt-get install apache2

Start it:

    sudo service apache2 start

Check its status:

    service apache2 status

Service will automatically restart after each reboot.


### 1.11 Logout and login again as `biocbuild`

This applies to all build machines, _standalone_ or _non-standalone_.

For an _external build node_, replace `biocbuild` with the name of the
account from which the builds will be run.

Almost everything in the next section must be done from the `biocbuild`
account.



## 2. Set up the Bioconductor software builds


### 2.1 Set Apache server DocumentRoot

This is only required for a _standalone builder_ or _central builder_.

Create `/home/biocbuild/public_html/BBS` from the `biocbuild` account:

    cd
    mkdir -p public_html/BBS

Then edit `/etc/apache2/sites-enabled/000-default.conf` **from a sudoer
account**. First make a copy of the original file:

    cd /etc/apache2/sites-enabled/
    sudo cp -i 000-default.conf 000-default.conf.original

and make the following changes:

- Set `DocumentRoot` to `/home/biocbuild/public_html`

- Add the following lines at the bottom of the `VirtualHost` section:
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

    # Should print index of /home/biocbuild/public_html/BBS in HTML form:
    curl http://localhost/BBS/



### 2.2 Check connectivity with central builder

This is needed only for a _non-standalone builder_.

#### 2.2.1 For an _internal build node_

Make sure to perform these checks from the `biocbuild` account.

##### Check that you can ping the central builder

Depending on whether the node you're ping'ing from is within RPCI's DMZ
or not, use the _central builder_'s short or long (i.e. hostname+domain)
hostname. For example:

    ping malbec2                                   # from within RPCI's DMZ
    ping malbec2.bioconductor.org                  # from anywhere else

##### Check that you can ssh to the central builder

    ssh malbec2                   # from within RPCI's DMZ
    ssh malbec2.bioconductor.org  # from anywhere else

If this is blocked by RPCI's firewall, after a while you'll get:

    ssh: connect to host malbec2.bioconductor.org port 22: Connection timed out

Contact the IT folks at RPCI if that's the case:

    Radomski, Matthew <Matthew.Radomski@RoswellPark.org>
    Landsiedel, Timothy <tjlandsi@RoswellPark.org>

##### Check that you can send HTTPS requests to the central builder

    curl https://nebbiolo2                           # from within DFCI
    curl https://nebbiolo2.bioconductor.org          # from anywhere else

More details on https implementation in `BBS/README.md`.

#### 2.2.2 For an _external build node_

Make sure to perform this check from the account from which the builds will
be run.

Check that you can send HTTP requests to the _central builder_:

    curl http://155.52.207.165   # if central builder is nebbiolo1
    curl http://155.52.207.166   # if central builder is nebbiolo2


### 2.3 Clone BBS git tree and create bbs-X.Y-bioc directory structure

This applies to all build machines, _standalone_ or _non-standalone_.

It must be done from the `biocbuild` account for an _internal build node_, or
from the account from which the builds will be run for an _external build node_.

#### Clone BBS git tree

    cd
    git clone https://github.com/bioconductor/BBS

#### Temporarily disable propagation (central builder only)

Propagation is documented in a separate document: Set-up-propagation-HOWTO.md

Until we've set it up, we need to comment out the `export BBS_OUTGOING_MAP=...`
line in `~/BBS/3.19/bioc/nebbiolo2/config.sh`.

We also need to add the build type to the list in `BBS/BBSreportutils.py`:

    ### Whether to display the package propagation status led or not for the
    ### given buildtype.
    def display_propagation_status(buildtype):
        return buildtype not in ["bioc-longtests", "bioc-testing", "cran"] # Add to list

One visible effect of doing this is that the daily build reports generated
by the `postrun.sh` script won't have the little LEDs in the rightmost column
indicating propagation status.

Note that the change is only temporary (don't commit it!), until we've set up
propagation of the 3.19 software packages.

#### Edit non_target_repos.txt (no longer needed)

Only if we are a few weeks before the next Bioconductor release (Spring or
Fall) and you are setting up the **future devel builds**.

In this case you are setting up builds for a version of Bioconductor
that doesn't exist yet. This means that the public package repositories
for this version of Bioconductor (i.e. the package repos under
https://bioconductor.org/packages/X.Y) don't exist yet either. Or maybe
some of them exist (e.g. software) but others are still missing (e.g.
data-experiment).

NOTE: The procedure described below is no longer needed. A better, simpler way
to handle this is by creating "fake X.Y repositories". See _Create fake X.Y
repositories_ section in the Set-up-propagation-HOWTO.md document for how to
do this.

Kept only for the record:

If we are in the situation described above (i.e. no X.Y repositories yet),
then `~/BBS/X.Y/bioc/non_target_repos.txt` needs to be temporarily modified
to point to the current devel repositories.

For example, if we are a few weeks before the BioC 3.19 release,
and you are setting up the future BioC 3.19 builds, then you need to
make the following change to `~/BBS/3.19/bioc/non_target_repos.txt`:
**replace every occurences of `BBS_BIOC_VERSION` with 3.19**.

The modified file should look like this:

    https://bioconductor.org/packages/3.19/data/annotation
    https://bioconductor.org/packages/3.19/data/experiment
    https://bioconductor.org/packages/3.19/workflows
    https://bioconductor.org/packages/3.19/books

The reason we need to do this is for the build system to be able to find and
install all the dependencies of the software packages (BBS doesn't and cannot
use `BiocManager::install()` for that).

Note that the change is only temporary (don't commit it!), until the 3.19
public repos exist and get populated.

#### Create bbs-X.Y-bioc directory structure

This applies to all build machines, _standalone_ or _non-standalone_.

For example, for the BioC 3.19 software builds:

    cd
    mkdir bbs-3.19-bioc
    cd bbs-3.19-bioc/
    mkdir rdownloads log


### 2.4 Install R

This applies to all build machines, _standalone_ or _non-standalone_.

It must be done from the `biocbuild` account for an _internal build node_, or
from the account from which the builds will be run for an _external build node_.

Note that we always build R **from source** on a Linux builder. We do not
install a package from a Linux distribution (i.e. we don't use `apt-get`
on Ubuntu).

#### Get R source tarball from CRAN

Move to the directory where we're going to download and extract the R source
tarball from CRAN:

    cd ~/bbs-3.19-bioc/rdownloads/

The exact tarball to download depends on whether we're configuring builds
for BioC release or devel. Remember that each version of Bioconductor is
tied to a given version of R e.g. BioC 3.11 & BioC 3.12 are tied to R 4.0,
BioC 3.13 & BioC 3.14 will be tied to R 4.1, etc... The reason two consecutive
versions of Bioconductor are tied to the same version of R is because R has
one major release per year (every Spring) and Bioconductor has two (one in
Spring and one in Fall). This is key to understand the following:

- The latest BioC release always uses the latest release of R. The source
  tarball for the latest release of R is normally available on the CRAN home
  page at: https://cran.r-project.org/
  So if you are installing/updating R for the release builds, use that.

- For BioC devel, it depends:
  * The BioC devel cycle that runs from Spring to Fall uses the same R
    as the current BioC release.
  * The BioC devel cycle that runs from Fall to Spring uses R devel.
    So in this case you need to pick up the latest daily snapshot of
    R devel [available here](https://stat.ethz.ch/R/daily/), or,
    if we're close to the release of the next major version of R,
    pick up the latest daily snapshot of R alpha/beta/RC
    [available here](https://cran.r-project.org/src/base-prerelease/).

IMPORTANT NOTE: If we are only a few weeks before the Spring release of
Bioconductor and you are setting up the **future devel builds** (i.e.
builds for the upcoming Spring-to-Fall devel cycle), then you need to pick
up the same R that you would pick up for the devel builds. For example, if
we are a few weeks before the BioC 3.13 release, and you are setting up
the future BioC 3.14 builds, then you need to pick up the latest daily
snapshot of R alpha/beta/RC.

Note that the source tarball you download should have a unique and descriptive
name, including a version and/or a date, such as `R-3.2.r67960.tar.gz`,
`R-3.2-2015-10-26.tar.gz`, or `R-alpha_2021-04-28_r80240.tar.gz`. If it does
not have such a name (e.g. it's just called `R-devel.tar.gz`) please rename
it after downloading and before extracting.

#### Extract the source tarball

    tar zxvf R-alpha_2021-04-28_r80240.tar.gz

If the directory created by untarring is called something like `R-devel`
or `R-alpha`, we should rename it to a unique and descriptive name that
contains an svn revision number or a date e.g. to something like `R-4.1.r80240`
or `R-4.1-2021-04-28`.

Check version and revision with:

    cat R-alpha/VERSION
    cat R-alpha/SVN-REVISION

#### Configure and compile R

Create the `<R_HOME>` folder, and `cd` to it:

    cd ~/bbs-3.19-bioc/
    
    ## If we are updating R, let's keep the previous R/ subfolder around,
    ## just in case:
    rm -rf R.old
    mv R R.old
    
    ## Start with a new empty R/ subfolder:
    mkdir R
    cd R/

Run `configure` and `make`:

    ../rdownloads/R-4.1.r80240/configure --enable-R-shlib
    make -j10       # or 'make -j' to use all cores

Note: Using the `-j` option allows `make` to run in parallel. The nb following
the option specifies the nb of jobs to run simultaneously. See `man make` for
the details. Don't try to use a nb of jobs that is more than the nb of logical
cores available on the machine. It might still work but it won't be optimal (it
might actually slow things down). To get the nb of logical cores on a Linux
system:

    cat /proc/cpuinfo | grep processor | wc -l

#### After compilation

- Do NOT run `make install`!

- Create the `site-library/` subfolder inside the `<R_HOME>` folder:
    ```
    mkdir site-library
    ```
  This will automatically point `.Library.site` to this location
  (`<R_HOME>/site-library`) when we start R (see **Basic testing** below).
  The reason we do this is to avoid installing any additional package in
  `.Library` (which is pointing to `<R_HOME>/library`). This will allow
  `_R_CHECK_SUGGESTS_ONLY_=true` to work properly when we run `R CMD check`
  on Bioconductor packages.

- Run the `R-fix-flags.sh` script to modify the compiler flags that will be
  used during package compilation. The script will modify `R/etc/Makeconf`.
  It's important to run this from the `~/bbs-3.19-bioc/R/etc/` directory and
  not one level up. Both locations contain `Makeconf` files but we only want
  to modify the `Makeconf` file located in `~/bbs-3.19-bioc/R/etc/`:
    ```
    cd etc/
    ~/BBS/utils/R-fix-flags.sh
    ```
  The script adds the `-Wall` flag to the compilation commands that will be
  used to compile package native code (i.e. C/C++/Fortran code). The flag
  tells the compiler to display additional warnings that can help package
  maintainers find potential problems in their code. These warnings will be
  included in the HTML report that gets generated at the end of the builds.

#### Basic testing

Start R:

    cd ~/bbs-3.19-bioc/
    R/bin/R         # check version displayed by startup message

Then from R:

    # --- check capabilities ---
    
    capabilities()  # all should be TRUE except aqua and profmem
    X11()           # nothing visible should happen
    dev.off()
    
    # --- check .Library and .Library.site ---
    
    .Library        # <R_HOME>/library
    .Library.site   # <R_HOME>/site-library
    
    # --- install a few CRAN packages ---
    
    # with C++ code:
    install.packages("Rcpp", repos="https://cran.r-project.org")
    # with Fortran code:
    install.packages("minqa", repos="https://cran.r-project.org")
    # a possibly difficult package:
    install.packages("rJava", repos="https://cran.r-project.org")

#### Install BiocManager + BiocCheck

From R:

    install.packages("BiocManager", repos="https://cran.r-project.org")

    library(BiocManager)    # This displays the version of Bioconductor
                            # that BiocManager is pointing at.
    BiocManager::install()  # This installs the BiocVersion package. Make
                            # sure its version matches Bioconductor version.

    ## IMPORTANT: Do this ONLY if BiocManager is pointing at the wrong version
    ## of Bioconductor. This will happen if you are installing R for the devel
    ## builds during the devel cycle that runs from Spring to Fall (these
    ## builds use the same version of R as the release builds).
    BiocManager::install(version="devel")  # see IMPORTANT note above!

    BiocManager::install("BiocCheck")  # required by SPB

#### [OPTIONAL] More testing

From R:

    # always good to have:
    install.packages("devtools", repos="https://cran.r-project.org")
    BiocManager::install("BiocStyle")

    BiocManager::install("rtracklayer")
    BiocManager::install("VariantAnnotation")
    BiocManager::install("rhdf5")

#### [OPTIONAL] Flush the data caches

When R is updated, it's a good time to flush the cache for AnnotationHub,
ExperimentHub, and BiocFileCache. This is done by removing the corresponding
folders present in `~/.cache/`.

Removing these folders means all packages using these resources will have
to re-download the files. This ensures that resources are still available.
However it also contributes to an increased runtime for the builds.

Should we also remove package specific caches?


### 2.5 Add software builds to biocbuild's crontab

This applies to all build machines, _standalone_ or _non-standalone_.

It must be done from the `biocbuild` account for an _internal build node_, or
from the account from which the builds will be run for an _external build node_.

First make sure to have the following lines at the top of the crontab:

    USER=biocbuild
    
    # By default, PATH is set to /usr/bin:/bin only. We need /usr/local/bin
    # for things that we install locally (e.g. new versions of pandoc).
    # It must be placed **before** /usr/bin.
    PATH=/usr/local/bin:/usr/bin:/bin

Then add the following entries to the crontab (all times are EST times,
please adjust if your _satellite node_ is in a different time zone):

#### Central builder:

    # BIOC 3.19 SOFTWARE BUILDS
    # -------------------------
    
    # prerun:
    55 13 * * 0-5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-bioc/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run:
    00 15 * * 0-5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-bioc/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # NEXT DAY
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    00 11 * * 1-6 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-bioc/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

#### Satellite node (i.e. non-standalone builder):

IMPORTANT: All times above are EST times! Please adjust the entry below to make sure
that your _satellite node_ starts `run.sh` at 3:00 pm EST if it's located in a different
time zone.

    # BIOC 3.19 SOFTWARE BUILDS
    # -------------------------
    
    # run:
    00 15 * * 0-5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-bioc/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'


### 2.6 First build report

#### Central builder:

On the day after adding the software builds to `biocbuild`'s crontab, you
should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/bioc-LATEST/

Some red on the report is to be expected (the purpose of the next section is
to reduce the amount of red as much as possible) but if you are happy with
the result so far and want to show it to the world, link the report from this
page:

  https://master.bioconductor.org/checkResults/

To do this, go on master (`ssh -A webadmin@master.bioconductor.org` from the
`biocbuild` account) and edit `/extra/www/bioc/checkResults/index.html` (backup
the file first).

Also note that the builds will automatically create and populate the
`~/bbs-3.19-bioc/meat/` folder, which we will refer to and use in the
next section.

#### Satellite node (i.e. non-standalone builder):

If you are running an _external build node_, please make arrangements
with the BioC core team so that they can retrieve the content of
the `~/bbs-X.Y-bioc/products-out/` folder. They'll typically set a cron
job on the central builder to do this every day, from Monday to Saturday,
between 10:30am and 11:00am EST.

Once this is in place, the results for the new _satellite node_ should
appear on the daily report at:

  https://bioconductor.org/checkResults/3.19/bioc-LATEST/

Some red on the report is to be expected. The purpose of the next section
is to reduce the amount of red as much as possible.



## 3. Install additional stuff for Bioconductor packages with special needs


Everything in this section must be done **from a sudoer account**.


### 3.1 Install Quarto

Required by CRAN package **quarto**.

Download latest `quarto-X.Y.ZZZ-linux-amd64.deb` package from https://quarto.org/docs/download/ (`quarto-1.3.450-linux-amd64.deb` as of Sep 15, 2023).

Install with `sudo dpkg -i quarto-X.Y.ZZZ-linux-amd64.deb`.


### 3.2 Install BibTeX style humannat.bst

Required by Bioconductor package **destiny**.

Used to be part of earlier Ubuntu versions (in texlive-bibtex-extra) but
doesn't seem to be here anymore in Ubuntu 22.04.

Install with:

    cd /usr/share/texlive/texmf-dist/bibtex/bst/
    sudo mkdir beebe
    cd beebe/
    sudo wget https://ctan.org/tex-archive/biblio/bibtex/contrib/misc/humannat.bst
    sudo texhash


### 3.3 Install ensembl-vep

Required by Bioconductor packages **ensemblVEP** and **MMAPPR2**.

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
    sudo cpan install IO::String
    sudo cpan install Bio::SeqFeature::Lite  # takes a while...

Install `libhts-dev` and create some symlinks (needed for Tabix Perl module):

    sudo apt-get install libhts-dev
    cd /usr/lib/
    sudo ln -s x86_64-linux-gnu/libhts.so
    sudo ln -s x86_64-linux-gnu/libhts.a

Then:

    sudo cpan install Bio::DB::HTS::Tabix

#### Install ensembl-vep

    cd /usr/local/
    sudo git clone https://github.com/Ensembl/ensembl-vep.git
    cd ensembl-vep/
    #sudo git checkout release/100  # select desired branch

    # Avoid the hassle of getting HTSlib to compile because ensemblVEP and
    # MMAPPR2 pass 'R CMD build' and 'R CMD check' without that and that's
    # all we care about.
    sudo perl INSTALL.pl --NO_HTSLIB
    # When asked if you want to install any cache files - say no
    # When asked if you want to install any FASTA files - say no
    # When asked if you want to install any plugins - say no

#### Edit `/etc/profile`

In `/etc/profile` append `/usr/local/ensembl-vep` to `PATH`.
Note that the `/etc/profile` file has read-only permissions (factory
settings). To save changes you will need to force save, e.g., in the
`vi` editor this is `w!`.

Logout and login again for the changes to `/etc/profile` to take effect.

#### Testing

From the `biocbuild` account, try to build and check the **ensemblVEP**
and **MMAPPR2** packages:

    cd ~/bbs-3.19-bioc/meat/

    ## Takes about 4 min. to build and 8 min. to check:
    ../R/bin/R CMD build ensemblVEP
    ../R/bin/R CMD check --no-vignettes ensemblVEP_X.Y.Z.tar.gz

    ## Takes about 2 min. to build and 4 min. to check:
    ../R/bin/R CMD build MMAPPR2
    ../R/bin/R CMD check --no-vignettes MMAPPR2_X.Y.Z.tar.gz


### 3.4 Set LIBSBML_CFLAGS and LIBSBML_LIBS

Required by Bioconductor package **rsbml**.

Unfortunately `libsbml5-dev` doesn't include a pkg-config file (`libsbml.pc`)
so we need to define environment variables LIBSBML_CFLAGS and LIBSBML_LIBS
in order for rsbml to compile.

#### Edit `/etc/profile`

In `/etc/profile` add:

    export LIBSBML_CFLAGS="-I/usr/include"
    export LIBSBML_LIBS="-lsbml"

Logout and login again for the changes to `/etc/profile` to take effect.

#### Testing

From the `biocbuild` account:

    echo $LIBSBML_CFLAGS
    # -I/usr/include
    echo $LIBSBML_CFLAGS
    # -lsbml
    # Check libsbml5-dev is installed
    dpkg-query -s libsbml5-dev
    cd ~/bbs-3.19-bioc/meat/
    ../R/bin/R CMD INSTALL rsbml


### 3.5 Install ImmuneSpace credentials

Required by Bioconductor package **ImmuneSpaceR**. Get credentials from
Bitwarden.

#### Edit `/etc/profile`

In `/etc/profile` add:

    export ISR_login=*****
    export ISR_pwd=****

Logout and login again for the changes to `/etc/profile` to take effect.

#### Testing

From the `biocbuild` account:

    cd ~/bbs-3.19-bioc/meat/
    ../R/bin/R CMD build ImmuneSpaceR


### 3.6 Install Perl module XML::Simple

Required by Bioconductor package **LowMACA**.

#### Install

    sudo cpan install XML::Simple

#### Testing

From the `biocbuild` account:

    cd ~/bbs-3.19-bioc/meat/
    ../R/bin/R CMD build LowMACA


### 3.7 Install .NET runtime

Required by Bioconductor package **rmspc**.

For more about installing .NET, see https://docs.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#2204-.

#### Install the Microsoft signing key

    wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    rm packages-microsoft-prod.deb

#### Install the runtime

    sudo apt-get update && sudo apt-get install -y aspnetcore-runtime-6.0

#### Testing

From the `biocbuild` account, try to build and check the **rmspc** package:

    cd ~/bbs-3.19-bioc/meat/
    ../R/bin/R CMD build rmspc
    ../R/bin/R CMD check --no-vignettes rmspc_X.Y.Z.tar.gz



## 4. Set up other builds


### 4.1 Annotation builds

From the `biocbuild` account:

    mkdir -p ~/bbs-3.19-data-annotation/log

Then add the following entries to `biocbuild`'s crontab:

    # BIOC 3.19 DATA ANNOTATION BUILDS
    # --------------------------------
    # run on Wednesday
    
    # prerun:
    30 02 * * 3 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-annotation/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-data-annotation/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run:
    00 03 * * 3 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-annotation/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-data-annotation/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    00 06 * * 3 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-annotation/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-data-annotation/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

After the builds complete, you should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/data-annotation-LATEST/

If you're happy with the result, link the report from this page:

  https://master.bioconductor.org/checkResults/


### 4.2 Experimental data builds

From the `biocbuild` account:

    mkdir -p ~/bbs-3.19-data-experiment/log

Then add the following entries to `biocbuild`'s crontab:

    # BIOC 3.19 DATA EXPERIMENT BUILDS
    # --------------------------------
    # run on Tuesdays and Thursdays
    
    # prerun:
    30 08 * * 2,4 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-experiment/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-data-experiment/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run:
    00 10 * * 2,4 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-experiment/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-data-experiment/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    45 14 * * 2,4 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/data-experiment/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-data-experiment/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

After the builds complete, you should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/data-experiment-LATEST/

If you're happy with the result, link the report from this page:

  https://master.bioconductor.org/checkResults/


### 4.3 Workflows builds

From the `biocbuild` account:

    mkdir -p ~/bbs-3.19-workflows/log

Then add the following entries to `biocbuild`'s crontab:

    # BIOC 3.19 WORKFLOWS BUILDS
    # --------------------------
    # run on Tuesdays and Fridays
    
    # prerun:
    45 07 * * 2,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/workflows/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-workflows/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run (start after the books builds to avoid concurrent INSTALLs and
    # competing for resources):
    00 08 * * 2,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/workflows/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-workflows/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    00 14 * * 2,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/workflows/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-workflows/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

After the builds complete, you should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/workflows-LATEST/

If you're happy with the result, link the report from this page:

  https://master.bioconductor.org/checkResults/


### 4.4 Books builds

From the `biocbuild` account:

    mkdir -p ~/bbs-3.19-books/log

Then add the following entries to `biocbuild`'s crontab:

    # BIOC 3.19 BOOKS BUILDS
    # ----------------------
    # run on Mondays, Wednesdays, and Fridays
    
    # prerun:
    45 06 * * 1,3,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/books/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-books/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run (start before the workflows builds to avoid concurrent INSTALLs and
    # competing for resources):
    00 07 * * 1,3,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/books/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-books/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    00 14 * * 1,3,5 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/books/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-books/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

After the builds complete, you should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/books-LATEST/

If you're happy with the result, link the report from this page:

  https://master.bioconductor.org/checkResults/


### 4.5 Long Tests builds

From the `biocbuild` account:

    mkdir -p ~/bbs-3.19-bioc-longtests/log

Then add the following entries to `biocbuild`'s crontab:

    # BIOC 3.19 SOFTWARE LONGTESTS BUILDS
    # -----------------------------------
    # run every Saturday
    
    # prerun:
    55 06 * * 6 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc-longtests/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.19-bioc-longtests/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'
    
    # run:
    00 08 * * 6 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc-longtests/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.19-bioc-longtests/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'
    
    # postrun (must start after 'run.sh' has finished on all participating nodes):
    00 21 * * 6 /bin/bash --login -c 'cd /home/biocbuild/BBS/3.19/bioc-longtests/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.19-bioc-longtests/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

After the builds complete, you should get the first build report at:

  https://master.bioconductor.org/checkResults/3.19/bioc-longtests-LATEST/

If you're happy with the result, link the report from this page:

  https://master.bioconductor.org/checkResults/


## 5 Store the last 7 reports

Save the 7 most recent software reports in `/home/biocbuild/archives`. Create the
directory with `mkdir /home/biocbuild/archives` then add the following to
the crontab:

    # Archive reports
    35 12 * * 1-6 cp /home/biocbuild/public_html/BBS/3.19/bioc/report/report.tgz /home/biocbuild/archives/bioc-report-`date +\%Y\%m\%d`.tgz

    # Remove reports older than 1 week
    40 12 * * 1-6 find /home/biocbuild/archives/bioc-report*.tgz -maxdepth 1 -mtime +7 -type f -delete



## 6 Miscellaneous

### 6.1 Disk space invisibly used on zfs partitions

Zfs is a volume manager and a filesystem with a snapshot feature that can reduce
the visible space of a partition using it when inspecting with `df`. Nebbiolo1
has a 1.7T zfs partition at `data`; however, the visible space can appear
smaller, possibly after an update or upgrade, when a snapshot is automatically
taken. This can also potentially lead to a `No space left on device` error when
attempting to write to disk.

#### Diagnosis

Check the partition size with `df`:

    $ df -Th /home
    Filesystem      Size  Used Avail Use% Mounted on
    data/home      zfs    946G  818G  128G  87% /home          # Should be 1.7T

List any existing snapshots. (None should exist.)

    # A snapshot exists
    $ zfs list -t snap
    NAME                   USED  AVAIL     REFER  MOUNTPOINT
    data/home@01-03-2023   782G      -      815G  -

#### Fix

Remove the snapshot to release the space with `zfs destroy <name of snapshot>`:

    $ sudo zfs destroy data/home@01-03-2023
    sudo zfs destroy data/home@01-03-2023

    $ df -Th /home
    Filesystem      Size  Used Avail Use% Mounted on
    data/home      zfs    1.7T  818G  822G  50% /home          # Correct size
