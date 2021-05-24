
[![Build Status](https://travis-ci.org/Bioconductor/BBS.svg?branch=feature%2Fstatic-analysis)](https://travis-ci.org/Bioconductor/BBS)

Table of Contents
=================

  * [Bioconductor Build System Overview](#bioconductor-build-system-overview)
    * [What is BBS?](#what-is-bbs)
    * [What is BBS <strong>not</strong>?](#what-is-bbs-not)
    * [Where is the code?](#where-is-the-code)
    * [Human resources](#human-resources)
    * [General overview of BBS](#general-overview-of-bbs)
    * [What builds where](#what-builds-where)
      * [About the build machines\.](#about-the-build-machines)
      * [How the build machines are organized\.](#how-the-build-machines-are-organized)
      * [DNS resolution and https specifics](#dns-resolution-and-https-specifics)
        * [Address and canonical DNS records](#address-and-cononical-dns-records)
        * [Traffic routing within the RPCI DMZ](#traffic-routing-within-the-rpci-dmz)
        * [Mac builders and the RPCI DMZ](#mac-builders-and-the-rpci-dmz)
      * [What machines are used in which builds?](#what-machines-are-used-in-which-builds)
        * [A note about time zones\.](#a-note-about-time-zones)
    * [How the build system works](#how-the-build-system-works)
      * [Builds](#builds)
        * [prerun](#prerun)
        * [run](#run)
        * [postrun](#postrun)
      * [Propagation Pipeline](#propagation-pipeline)
        * [update](#update)
        * [prepare](#prepare)
        * [push](#push)


Bioconductor Build System Overview
==================================

This is the main README for the Bioconductor Build System (BBS).

Further documentation on specific tasks is in the [Doc](Doc/) directory.

## What is BBS?

* A **nightly** build system, not incremental or continuous
  integration. Maybe it can be replaced by those things
  in the future.
* Home-grown. The system was written originally by
  Herv&eacute; Pag&egrave;s and is now maintained
  Herv&eacute; and Lori.
* Written in a mix of shell scripting (bash shell,
  Windows batch files), Python, and R.

## What is BBS **not**?

BBS is different from the Single Package Builder,
which is triggered when a tarball is submitted
to the new package tracker. Though there is some
common code.

## Where is the code?

The canonical location of the code is in GitHub:

[https://github.com/Bioconductor/BBS](https://github.com/Bioconductor/BBS)

## Human resources

If you have a question not covered here:

* Ask Herv&eacute; Pag&egrave;s or Lori Shepherd.
* If neither of those two are available, Martin Morgan may know.

## General overview of BBS

Build start times for release and devel builders are summarized in the
[Build Machines Daily Schedule](https://docs.google.com/document/d/1Ubp7Tcxr1I1HQ8Xrp9f73P40YQ0qhWQ_hSmHs05Ln_M/edit#heading=h.r7sorafgdpnf).

In general, there are four *builds* that run during any given week:

1. Release *software* builds. (*bioc* is the name for our
   software package repository). These builds run nightly on
   all release build machines.
2. Release *experiment package* builds (*data-experiment* is the
   name for our experiment package repository). These builds run
   nightly on the release Linux master builder only.
3. Devel *software* builds. These builds run nightly on
   all devel build machines.
4. Devel *experiment package* builds. These builds run
   nightly on the devel Linux master builder only.

## What builds where

As of December 2017, the Linux and Windows builders are in the
Roswell Park DMZ and the Mac builders are in MacStadium.

There are plans to purchase new Mac hardware in the next 6 months
and bring the Mac builders to the in-house DMZ.

### About the build machines.

There are three build machines each for release and devel.

* Linux (Ubuntu 16.04 LTS)
* Windows Server 2012
* Mac OX X 10.16.6 (El Capitan)

### How the build machines are organized.

Each build has a *master builder* which is the Linux build machine.

The *master builder* is where all build machines send their build products (via
rsync and ssh). Build products are not just package archives (.tar.gz, .tgz,
and .zip files for source packages, Mac packages, and Windows packages
respectively) but also the output of each build phase and other information
about the build, enough to construct the build report.

### DNS resolution and https specifics

In Stage 2, the Windows and Mac builders get packages to build from the *master
builder*. Historically this was done via http and has recently been
transitioned to https.

#### Address and canonical DNS records

Each machine in the RPCI DMZ has both a public and private IP. These are the
A (address) record DNS entries and they resolve to the public IPs:

malbec1.roswellpark.org
malbec2.roswellpark.org
tokay1.roswellpark.org
tokay2.roswellpark.org

In AWS Route 53 we have CNAME (canonical) record DNS entries that point names
with the .bioconductor.org extension to names with the .roswellpark.org
extension.

https://console.aws.amazon.com/route53/home?region=us-east-1#resource-record-sets:Z2LMJH3A2CQNZZ

#### Traffic routing within the RPCI DMZ

When http was used to communicate between the Windows and Linux
builders the private IP was used instead of the hostname. This resulted in direct communication
between private IPs within the DMZ and traffic was not routed to
the public IP in the firewall.

The direct IP approach doesn't work with https because the SSL certificate must
be validated and it's registered to the .bioconductor.org name (not the IP).

We tried using the .bioconductor.org name with https but there was a problem
with the routing of traffic in the DMZ. The key issue was that the outgoing
request path was different from the return response path. The
return response was coming from a different IP than the outgoing request
was sent to. Evidently certain protocols don't like this inconsistency and
https is one of them.

Outgoing traffic must use https://hostname.bioconductor.org which maps to
the public IP in the firewall. The return traffic was not forced to use
.bioconductor.org so it instead used the internal route table to lookup
the private IP of the originating machine which is also in the DMZ.

Example of tokay1 trying to talk to malbec1:

Outgoing request:
tokay1 -> firewall (public IP) -> malbec1

Return response:
malbec1 -> tokay1

There were several attempts to modify firewall rules to make https work via the
normal channels. These were unsuccessful and the alternative solution was to
modify the `/etc/hosts` file on the DMZ builders. The modification overrides the
DNS lookup (for this machine) such that .bioconductor.org now maps to the
private IP instead of the public IP. As a result, traffic no longer goes
through the firewall but instead occurs directly between the two machines which
means the outgoing and return IP addresses are the same.

#### Mac builders and the RPCI DMZ

The Mac builders are located outside the RPCI DMZ. When they https
to the *master builder*, e.g., malbec1.bioconductor.org, they are
directed to the public IP which redirects to the private IP. The
outgoing and return routes are the same. This works fine, no problems here.

### What machines are used in which builds?

This changes with every release. The *active_devel_builders* and
*active_release_builders* sections of
[config.yaml](http://bioconductor.org/config.yaml) list the current
builders.

#### A note about time zones.

The builds are on Eastern Standard Time.

## How the build system works

The build system has 2 distinct parts: building and propagation. The first
is managed by the *biocbuild* user and the second by the *biocpush* user.

### Builds

The BBS code is checked out on all build machines. Each builder has a cron job
(or Scheduled Task on Windows) that kicks off the builds. On all build
machines, the build system runs as *biocbuild*.

The crontab for the *biocbuild* user on one of the Linux build machines
(a/k/a master build nodes) lists all tasks involved in the builds. A
visual summary of these same tasks (with Windows and Mac added) is in the
[Build Machines Daily Schedule](https://docs.google.com/document/d/1Ubp7Tcxr1I1HQ8Xrp9f73P40YQ0qhWQ_hSmHs05Ln_M/edit#heading=h.r7sorafgdpnf).

#### prerun

The first line in the crontab on the master Linux builder is the start of
the prerun script:

    # prerun
    00 17 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.6/bioc/`hostname` && ./prerun.sh >>/home/biocbuild/bbs-3.6-bioc/log/`hostname`-`date +\%Y\%m\%d`-prerun.log 2>&1'

The *prerun* step happens only on the master build node. `prerun.sh`
sources `config.sh` and then calls python script `BBS-prerun.py`.

##### config.sh

The sourcing of `config.sh` sets up environment variables used during the
build. First, variables specific to this build machine are set up. Then, inside
`config.sh`, another `config.sh` script one level up is sourced. This sets up all
environment variables specific to all Unix (Linux and Mac) nodes involved in
this *software* build. Inside this `config.sh`, the `config.sh` one level up is
also sourced. That script sets up more environment variables common to all
builds (software and experiment data) for this version of Bioconductor.

It's important to understand this pattern because it occurs in several places
in BBS. Shell scripts (or batch files on windows) are essentially used to
ensure that configuration is correct, but most of the actual build work is done
by python scripts.

After `prerun.sh` sets up all the environment variables, it runs python
script `BBS-prerun.py`.

`BBS-prerun.py` runs the following stages:

* STAGE1: [on Linux only] Make a local copy of all packages to be built from
          the version control location (i.e., git, svn etc.).

The start time of this script is the deadline for changes for the day. Any
changes made after that time won't be picked up until the following day's
build.

#### run

The next line in the crontab starts the `run.sh` script:

    # run:
    55 17 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.6/bioc/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.6-bioc/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'

At the time of this writing, prerun takes about 55 min so the run script
must start after that time.

This script sources config files in the same way as `prerun.sh`. It also
sets up Xvfb (the virtual frame buffer for X11; this makes sure
that packages which need access to X11 can have it).

After loading environment variables, the main python build script, `BBS-run.py`, is run.

This script runs the following stages:

* STAGE2: Preinstall all package dependencies
          (INSTALL column on the build report)

* STAGE3: Run `R CMD build` on all BioC packages
          (BUILD column on the build report)

* STAGE4: Run `R CMD check` on all package source tarballs produced by STAGE2
          (CHECK column on the build report)

* STAGE5: [Windows and Mac only] Make binary packages
          (BUILD BIN column on the build report)

Each stage is run in parallel. The system does not move from one stage to the
next until all jobs in the current stage are completed.


#### postrun

At this point the builds should have finished on all nodes. The next line
in the crontab starts the posrun script. This must not start until the
`run.sh` job has finished on all nodes.

    # postrun:
    45 13 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.6/bioc/`hostname` && ./postrun.sh >>/home/biocbuild/bbs-3.6-bioc/log/`hostname`-`date +\%Y\%m\%d`-postrun.log 2>&1'

The prerun build script started at 17:00 and now it is 13:45 the following
afternoon. We hope that all builders have finished by now, otherwise there will
be (as there often is) some manual steps to do at this point.

The build system will now run `postrun.sh` which initializes environment
variables as described above and then runs the following 3 python scripts:

##### BBS-make-BUILD_STATUS_DB.py

This script performs stage6a:

* stage6a: [Linux only] Create `BUILD_STATUS_DB.txt` file which records the status of
           STAGES 2-5 on all platforms.

    biocbuild@malbec1:~/public_html/BBS/3.6/bioc$ head BUILD_STATUS_DB.txt
    a4#malbec1#install: NotNeeded
    a4#malbec1#buildsrc: OK
    a4#malbec1#checksrc: OK
    a4#tokay1#install: NotNeeded

##### BBS-make-OUTGOING.py

This script performs stage6b:

* stage6b: [Linux only] Copy build products to OUTGOING folder for later
           transfer to the website by *biocpush*.

##### BBS-make-PROPAGATION_STATUS_DB.py

This script calls `BBS/utils/makePropagationStatusDb.R` which
creates the `PROPAGATION_STATUS_DB.txt` file.
This file identifies which packages and what format, e.g., source or binary,
will be pushed to the website.

    biocbuild@malbec1:~/public_html/BBS/3.6/bioc$ head PROPAGATION_STATUS_DB.txt
    a4#source#propagate: UNNEEDED, same version is already published
    a4#win.binary#propagate: UNNEEDED, same version is already published
    a4#mac.binary.el-capitan#propagate: UNNEEDED, same version is already published
    a4Base#source#propagate: UNNEEDED, same version is already published

##### BBS-report.py

This script performs stage6c:

* stage6c: [Linux only] Generate and publish HTML report to the website.


The crontab contains essentially the same entries for the
experiment data builds though they run at different times.

### Propagation Pipeline

The steps discussed so far complete the `Run` portion of the builds. All
nodes have finished building and build products have been deposited on the
Linux master builder. The build report was created and posted on the website.

The second part of this process is called the "propagation pipe" and involves
moving build products from the master builder to the website. The products are
the package tarballs and binaries that will become available via
`BiocManager::install()`
as well as information used to build the landing pages. These steps are
performed by the *biocpush* user and involve the master builder only.

Looking at *biocpush*'s crontab, we see:

    35 14 * * * cd /home/biocpush/propagation/3.6 && (./updateReposPkgs-bioc.sh && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh) >>/home/biocpush/cron.log/3.6/updateRepos-bioc-`date +\%Y\%m\%d`.log 2>&1

Notice the job starts at 14:35. This is hopefully enough time for
the `postrun.sh` script (above) to have finished; otherwise we'll have to
re-run some things manually.

The `cron` job above runs three scripts, to *update*, *prepare*, and *push*.

#### update

The *update* script moves the build products that can be propagated from
`/home/biobuild/public_html/BBS/X.Y/REPO/OUTGOING/` into
`/home/biocpush/PACKAGES/X.Y/REPO/` where `X.Y` is the version of
Bioconductor and `REPO` is the type of package, e.g., bioc or data.

If a package has been updated, with an appropriate version bump, the older
version is either moved to the 'Archive' folder (in release) or removed from
the repository (in devel).

#### prepare

The *prepare* script does not move files around but just populates other parts
of our internal repository which will later be moved to the web site. Most
importantly this includes the package indexes (`PACKAGES` and `PACKAGES.gz`)
which tell install.packages() and BiocManager::install() and friends which packages can be
installed.  There's also a `VIEWS` file which is used to build parts of our web
site (especially the package landing pages). From each built package we also
extract vignettes (built documents, source documents, and Stangled R source),
`README`s, `INSTALL` and `LICENSE` files, reference manuals, and other material
that we want to link to on the package landing page.

#### push

Finally the *push* script uses *rsync* to copy the internal repository to our
web site, which is where users go when they install a package via
`BiocManager::install()`.
