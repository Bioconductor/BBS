## 1. Introduction

Every 6 months, a couple of weeks before a new BioC release, we need to
set up the builds for _the future devel cycle_ of Bioconductor (_the future
devel cycle_ is what will become the official devel cycle immediately
after the creation of the release branch). This documents explains how
to do that.

For clarity, we're describing the scenario where BioC 3.18 is to be released
soon so is still the current devel version of Bioconductor. The 3.18 builds
have been up and running for 6 months but now it's time to set up the 3.19
builds. In our scenario, the 3.17 builds have been stopped recently so the
machines that were running them are now available for the 3.19 builds.

These machines are nebbiolo1 (Linux), tokay1 (Windows), and merida1 (Mac).

nebbiolo1 will be the _central builder_ for the 3.19 builds (like it was for
the 3.17 builds). This is where the build products from all the build nodes
will be collected. The central builder generates the build reports and
propagates packages (source tarballs and binaries) produced by the builds
to master.bioconductor.org.



## 2. Add config files and scripts to BBS source tree

Clone the BBS repository on your local machine. With HTTPS:
```
git clone https://github.com/Bioconductor/BBS
```
or with SSH:
```
git clone git@github.com:Bioconductor/BBS.git

```
Make sure you have push access to it.


### In top-level BBS folder

#### Copy `BBS/3.18` to `BBS/3.19`

```
cd BBS
cp -r 3.18 3.19
```

Don't copy the `3.17` folder! It's important to copy the latest folder to get
the latest versions of the config files and scripts.

#### From inside `BBS/3.19` folder

```
cd 3.19
```

Rename machines to reflect new names e.g. nebbiolo2 -> nebbiolo1, tokay2 -> tokay1,
machv2 -> merida1. This means renaming the directories inside `bioc/`,
`data-experiment/`, `workflows/`, and `bioc-longtests/`, and replacing
every occurence in every file except in `report.css`.

Replace every occurence of `RELEASE_3_18` with `devel` in every file.

Replace every occurence of `3.18` with `3.19` in every file.

Set new background color in `report.css`.

#### `git add` new `3.19` folder

```
cd ..
git add 3.19
```


### In `BBS/propagation/` folder

#### Copy `BBS/propagation/3.18/` to `BBS/propagation/3.19/`

```
cd propagation
cp -r 3.18 3.19
```

#### From inside `BBS/propagation/3.19` folder

```
cd 3.19
```

Replace every occurence of `3.18` with `3.19` in every file.

If the devel builds use a new R version (e.g. 4.4 instead of 4.3) then
replace every occurence of `4.3` with `4.4`.

#### `git add` new `propagation/3.19` folder

```
cd ../..
git add propagation/3.19
```


### Commit and push

```
git commit -m 'Add config files and scripts for 3.19 builds'
```



## 3. Create 3.19 destinations on master.bioconductor.org

See `3. Create https://bioconductor.org/packages/X.Y on master` in
`Set-up-propagation-HOWTO.md`.


## 4. Activate builds on central builder


The central builder should be running Linux or other Unix-like OS.

In our scenario (i.e. 3.19 builds), nebbiolo1 is the central builder.

Builds on all machines are run under dedicated user account `biocbuild`.

Connect to the `biocbuild` account on nebbiolo1:
```
ssh -A biocbuild@nebbiolo1.bioconductor.org
```

Pull latest changes to BBS:
```
cd ~/BBS
git pull --all
```

Remove `~/public_html/BBS/3.17` (this is about 160G):
```
cd ~/public_html/BBS
rm -rf 3.17
```


### Software builds

#### Preliminary steps

Remove `~/bbs-3.17-bioc` folder and create `~/bbs-3.19-bioc` folder.

In `~/bbs-3.19-bioc` create `log` and `rdownloads` folders.

Download latest R 4.4 source tarball in `~/bbs-3.19-bioc/rdownloads`
and install in `~/bbs-3.19-bioc/R` (using the usual procedure, see
Update-R-on-Linux-HOWTO.md).

In `~/BBS/3.19/bioc/nebbiolo1/config.sh` remove Windows and Mac builders
from `BBS_OUTGOING_MAP` and `BBS_REPORT_NODES` to keep only nebbiolo1.
This is a local and temporary edit (until the other nodes are added to
the software builds), so don't commit!

#### Activation

Edit crontab: replace all occurrences of 3.17 with 3.19 then uncomment
entries for software builds. Builds will start at scheduled time.
Check for build report the next day at:

    https://bioconductor.org/checkResults/3.19/bioc-LATEST/


### Data-experiment builds

#### Preliminary steps

Remove `bbs-3.17-data-experiment` folder and create `bbs-3.19-data-experiment`
folder

In `bbs-3.19-data-experiment` create `log` folder

#### Activation

Edit crontab: uncomment entries for data-experiment builds.
Builds will start at scheduled time.
Check for build report 1 or 2 days later at:

    https://bioconductor.org/checkResults/3.19/data-experiment-LATEST/


### Workflows and "long tests" builds

Repeat data-experiment instructions. _Top-level working dirs_ for these builds
are `bbs-3.19-workflows` and `bbs-3.19-bioc-longtests`.


### Summary and follow-up

In the end, the home of the `biocbuild` user should look like this:
```
biocbuild@nebbiolo1:~$ ls
BBS	       bbs-3.19-bioc-longtests	 bbs-3.19-workflows  Desktop
bbs-3.19-bioc  bbs-3.19-data-experiment  bin		     public_html
```
where the `bbs-3.19-*` folders are the _top-level working dirs_ for
the individual builds.

Monitor the builds for the next few days i.e. check the log files in
the `log` subdir of each _top-level working dir_ and make sure that
the `prerun.sh`, `run.sh`, and `postrun.sh` scripts are starting at
the expected times and that they successfully completed (check their
tail with `tail`). Their timestamps will indicate at what time they
completed or failed.

Check the build reports at:

- https://bioconductor.org/checkResults/3.19/bioc-LATEST/
- https://bioconductor.org/checkResults/3.19/data-experiment-LATEST/
- https://bioconductor.org/checkResults/3.19/workflows-LATEST/
- https://bioconductor.org/checkResults/3.19/bioc-longtests-LATEST/

The page at https://bioconductor.org/checkResults/ should have links
to them.



## 5. Activate propagation pipes


Connect to the `biocpush` account on nebbiolo1. Note that if the account
doesn't exist yet, you need to use your personal account on the machine
to create it. This should be created as a regular account, like the `biocbuild`
account. See section _Create the biocbuild account_ in
Prepare-Ubuntu-20.04-HOWTO.md for the details.

Once in the `biocpush` account, pull the latest changes to BBS (or clone BBS
git tree if you just created the `biocpush` account):
```
cd ~/BBS
git pull --all
```


### Set up internal staging package repos

Create `~/PACKAGES/3.19` and the 3 CRAN-style package repos: `bioc` (software),
`data/experiment`, and `workflows` below it. No `data/annotation` repo for
now:
```
mkdir ~/PACKAGES/3.19/bioc
mkdir -p ~/PACKAGES/3.19/data/experiment/
mkdir ~/PACKAGES/3.19/workflows
```

Each repo must have the following structure:
```
biocpush@nebbiolo1:~/PACKAGES/3.19/data/experiment$ tree
.
├── bin
│   ├── macosx
│   │   └── contrib
│   │       └── 4.4
│   │           └── PACKAGES
│   └── windows
│       └── contrib
│           └── 4.4
│               └── PACKAGES
└── src
    └── contrib
        └── PACKAGES

9 directories, 3 files
```
where `PACKAGES` are empty files.


### Install latest R

This is an R that is only used to run the propagation pipe. Must be a
version with same X.Y than the R used for the builds (so 4.4 in our case).
It doesn't have to be the same exact version though. Unlike the R we use
for the builds, we won't update it i.e. we'll keep this same installation
for the entire life of the 3.19 builds (i.e. for about 1 year).

Download latest R 4.4 source tarball in `~/rdownloads` then run `configure`
and `make` in `~/R-4.4`.

In `~/bin`, create symlink:
```
ln -s ~/R-4.4/bin/R R-4.4
```
Make sure you can start R with:
```
R-4.4
```


### Install packages needed by propagation pipe

```
cd pkgs_to_install
```
See `README` file.


### Activate propagation of software, data-experiment, and workflow packages

Create `3.19` subfolder in `~/cron.log`

Edit crontab: replace all occurrences of 3.17 with 3.19 and uncomment
entries for propagation of software, data-experiment, and workflow
packages.


### Follow-up

Monitor the propagation pipes for the next few days by checking the
log files in `~/cron.log/3.19`.

If propagation was successful, you should be able to access the following
package index files:

- https://bioconductor.org/packages/3.19/bioc/src/contrib/PACKAGES
- https://bioconductor.org/packages/3.19/data/experiment/src/contrib/PACKAGES
- https://bioconductor.org/packages/3.19/workflows/src/contrib/PACKAGES



## 6. Activate builds on the other builders


Traditionally the Windows and Mac builders only run the software builds.


### On Windows

In our scenario (i.e. 3.19 builds), tokay1 will run the Windows software
builds.

#### From the `biocbuild` account on tokay1

Use rdesktop to connect to the `biocbuild` account on tokay1:

In a PowerShell Window, pull latest changes to BBS:
```
cd C:\Users\biocbuild\BBS
git pull --all
```

Follow the steps described in the "Create and populate the
bbs-3.yy-bioc folder" and "Install R in bbs-3.yy-bioc" sections of
the [`Prepare-Windows-Server-2012-HOWTO.TXT`](https://github.com/Bioconductor/BBS/blob/devel/Doc/Prepare-Windows-Server-2012-HOWTO.TXT) document.
Make sure to replace all occurences of 3.17 with 3.19.

Remove `C:\Users\biocbuild\bbs-3.17-bioc`.

#### From a personal administrator account on tokay1

Use rdesktop to connect to your personal account on tokay1:

Follow the steps described in the "Add nightly builds to Task Scheduler"
section of the `Prepare-Windows-Server-2012-HOWTO.TXT` document.
Make sure to replace all occurences of 3.17 with 3.19.

Builds will start at scheduled time.

Remove the old task schedule job for previous version.

#### From the `biocbuild` account on the central builder

In our scenario (i.e. 3.19 builds), nebbiolo1 is the central builder.

Connect to the `biocbuild` account on nebbiolo1:
```
ssh -A biocbuild@nebbiolo1.bioconductor.org
```

Make sure tokay1 will be included in the next build report:
```
cd ~/BBS/3.19/bioc/nebbiolo1/
git diff config.sh
vi config.sh  # tokay1 should be in BBS_OUTGOING_MAP and BBS_REPORT_NODES
```

Next day: Check build report at:

    https://bioconductor.org/checkResults/3.19/bioc-LATEST/


### On Mac

In our scenario (i.e. 3.19 builds), merida1 will run the Mac software
builds.

#### From the `biocbuild` account on merida1

Connect to the `biocbuild` account on merida1:
```
ssh -A biocbuild@merida1.bioconductor.org
```

Pull latest changes to BBS:
```
cd ~/BBS
git pull --all
```

Create `~/bbs-3.19-bioc` folder and `log` subfolder.

Install R by following instructions in section "E. Install R" of
the [`Prepare-MacOSX-El-Capitan-HOWTO.TXT`](https://github.com/Bioconductor/BBS/blob/devel/Doc/Prepare-MacOSX-El-Capitan-HOWTO.TXT) document (in our scenario,
`R-devel-el-capitan-signed.pkg` needs to be installed).

Edit crontab: replace all occurrences of 3.17 with 3.19 then uncomment
entry for software builds. Builds will start at scheduled time.

Remove `~/bbs-3.17-bioc` folder.

#### From the `biocbuild` account on the central builder

In our scenario (i.e. 3.19 builds), nebbiolo1 is the central builder.

Connect to the `biocbuild` account on nebbiolo1:
```
ssh -A biocbuild@nebbiolo1.bioconductor.org
```

Make sure merida1 will be included in the next build report:
```
cd ~/BBS/3.19/bioc/nebbiolo1/
git diff config.sh  # see local edits
vi config.sh  # merida1 should be in BBS_OUTGOING_MAP and BBS_REPORT_NODES
```

Next day: Check build report at:

    https://bioconductor.org/checkResults/3.19/bioc-LATEST/

