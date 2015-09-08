Bioconductor Build System Overview
==================================

This is the main README for the Bioconductor Build System (BBS).

Further documentation (of varying states of out-of-date-ness)
is in the [Doc](Doc/) directory.

## What is BBS?

* A **nightly** build system, not incremental or continuous
  integration. Maybe it can be replaced by those things
  in the future.
* Home-grown. The system was written originally by 
  Herv&eacute; Pag&egrave;s and is now maintained 
  by Dan Tenenbaum. Brian Long is learning to maintain
  it as well.
* Written in a mix of shell scripting (bash shell, 
  Windows batch files), Python, and R.

## What is BBS **not**?

* BBS is different from the Single Package Builder,
  which is triggered when a tarball is submitted
  to the new package tracker. Though there is some
  common code.
* BBS is different from the workflow builder which 
  is based on jenkins and builds in response to commits.
  This builder is only used to build contents of
  directories in 
  [https://hedgehog.fhcrc.org/bioconductor/trunk/madman/workflows](https://hedgehog.fhcrc.org/bioconductor/trunk/madman/workflows
  ).

## Where is the code?

If you are reading this document, hopefully you've found it.

The canonical location of the code is in Subversion:

[https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS)

However, it's also in GitHub:

[https://github.com/Bioconductor/BBS](https://github.com/Bioconductor/BBS)

Some things to note about the Github repository:

1. It is not automatically kept in sync with the SVN repository.
   A technique like
   [this](https://github.com/Bioconductor/BiocGithubHelp/wiki/Managing-your-Bioc-code-on-hedgehog-and-github)
   is used to manually sync it.
2. Normally every build machine should have a checkout/working copy
   of the Subversion repository. However, during the transition
   to cloud-based builds we needed to fork the build code,
   so the cloud-based machines have a Git working copy.
   After the 3.2 release all machines should be using
   an SVN working copy (or at least all machines
   should be using the same version control system).
3. The cloud-based machines actually have a non-master
   branch (start-linux1) checked out. After the 
   3.2 release, this branch should be merged with
   master and master should be merged with svn.



## Human resources

If you have a question not covered here:

* Dan Tenenbaum should be the first person to ask.
* Herv&eacute; Pag&egrave;s should be the next person to ask.
  He has not been completely in the loop regarding the move
  to the cloud but Dan will try and catch him up.
* If neither of those two are available, Martin Morgan may know.

## General overview of BBS

In general, there are four *builds* that run during any given week:

1. Release *software* builds. (*bioc* is the name for our
  software package repository). These builds run nightly on
  all release build machines.
2. Release *experiment package* builds (*data-experiment* is the
   name for our experiment package repository). These builds
   run twice a week, on Wednesdays and Sundays, on the 
   Linux, Windows, and Snow Leopard build machines
   for release. *
3. Devel *software* builds. These builds run nightly on 
   all devel build machines.
4. Devel *experiment package* builds. These builds run
   twice a week, on Wednesdays and Sundays, on the
   Linux, Windows, and Snow Leopard build machines for devel.

* = **Note**: The experiment data builds currently run on 
Snow Leopard but not Mavericks. If you refer to
[the note below](#snow_leopard_note) you'll see that
this needs to change; beginning with Bioconductor 3.3
we will no longer build on Snow Leopard, so experiment
data builds must happen on Mavericks.

## What builds where

We are in the process of moving as much of the build system as
possible into the cloud. 

As of 8 September 2015, the devel builds are in the cloud
and we are working on starting the "next devel" (BioC 3.3)
builds there. The current release (BioC 3.1) builds happen
entirely at FHCRC with physical machines.

"In the cloud" refers to 
[Amazon Web Services](https://aws.amazon.com/).
The exception to "in the cloud" in the above is that all 
Mac build machines are currently located at FHCRC.

This is because Apple's licensing agreements make it impossible
to virtualize OS X on anything but OS X hardware therefore
there are not a lot of affordable cloud providers for Mac.
It is possible/probable that the Macs will be shipped out of FHCRC,
either to Roswell Park or to a third-party hosting provider.
We should not need physical access to the Macs (as long as there is a
person we can call to reboot them if we cannot access them
via ssh or Screen Sharing).

### About the build machines.

There are four build machines each for release and devel.

This is for the four platforms that we build for:

* Linux (Ubuntu 14.04 LTS)
* Windows (Server 2008 or Server 2012)
* Mac OS X 10.6.8 (Snow Leopard)
* Mac OX X 10.9.5 (Mavericks)

Any build machine that has "bioconductor.org" in its
name is in the cloud. Any machine without a fully qualified
domain name is (at this point) at FHCRC in Seattle.


<span id="snow_leopard_note"></span>

**Note about Snow Leopard**: R's support for Snow Leopard is 
being phased out with R-3.3, which will be released in the
Spring of 2016. Therefore the upcoming devel version of
Bioconductor (3.3) will not be built on Snow Leopard; nor will
future versions. Therefore we can phase out one Snow Leopard
machine after the 3.2 release (October 14, 2015), and the second
one after the 3.3 release sometime in Spring 2016.
Then we will only have two Mac Minis (morelia and oaxaca)
which we use for building on Mavericks.

### How the build machines are organized.

Each build has a *master builder* which is generally
the same as the Linux build machine.

The *master builder* is where all build machines send
their build products (via rsync and ssh). Build products are not just
package archives (.tar.gz, .tgz, and .zip files for
source packages, mac packages, and windows packages respectively)
but also the output of each build phase and other information
about the build, enough to construct the build report.

### What machines are used in which builds?

This changes with every release, so in order to avoid
writing soon-to-be obsolete information here, I will
refer you to the
[config.yaml](https://hedgehog.fhcrc.org/bioconductor/trunk/bioconductor.org/config.yaml
) file for the web site (requires your svn credentials).
The *active_devel_builders* and *active_release_builders*
section will tell you what is being used, and that
should be current.

However, just to give you an idea, here is what is 
in use as of today, September 8 2015.

#### Devel (Bioconductor 3.2)

Linux: linux1.bioconductor.org
Windows: windows1.bioconductor.org
Mac Snow Leopard: perceval
Mac Mavericks: oaxaca

#### Release (Bioconductor 3.1)

Linux: zin2
Windows: moscato2
Mac Snow Leopard: petty
Mac Mavericks: morelia

#### Next devel (Bioconductor 3.3)

*We're just going to attempt to start these beginning on
9/8/2015; these machines may not exist or be accessible
by the time you read this.*

Normally I would not start these builds until the current
release builds had been stopped 
(see [the prerelease checklist](Doc/prerelease_and_release_checklist.txt)) but it makes more sense to start the new devel
builds in the cloud than to move the current release builds.

Linux: linux2.bioconductor.org
Windows: windows2.bioconductor.org

*After the 3.2 release, we'll add:*

Mac Mavericks: morelia

We will not have a Snow Leopard build machine for the 3.3 builds
because BioC 3.3 will use R-3.3 which will no longer support
Snow Leopard.

#### A note about time zones.

All machines that are part of the BioC 3.2 builds 
are on Eastern (Buffalo) time. All machines that
are building BioC 3.1 are on Pacific (Seattle) time.

The "next devel (BioC 3.3)" builds will start with 
two machines (Linux and Windows) both on Eastern time.
After the 3.2 release, they will be joined by a
Mavericks machine which will move to Eastern time.
From this point forward, all Bioconductor build machines
will be on Eastern time.


## How the build system works

As described above, on each build machine, the build system
code is checked out.

On each build machine there is a cron job (or Scheduled Task)
on Windows that kicks off the builds.

On all build machines, the build system runs as the *biocbuild* 
user. 

I highly recommend looking at the crontab for the *biocbuild*
user on one of the Linux build machines (a/k/a master build nodes).

Among other things, you'll see the following (from the BioC 3.2
master build node):

    # bbs-3.2-bioc
    24 16 * * * cd /home/biocbuild/BBS/3.2/bioc/zin1 && ./prerun.sh >>/home/biocbuild/bbs-3.2-bioc/log/zin1.log 2>&1

The *prerun* step happens only on the master build node.
I recommend looking to see what happens in that prerun.sh
script which can be found in SVN at
[https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/3.2/bioc/zin1/prerun.sh](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/3.2/bioc/zin1/prerun.sh).
If you look there, you will see that it is essentially just sourcing
a shell script called config.sh and then running a python script.

The sourcing of the config script sets up environment variables
that will be used during the build. First, variables specific to this
build machine are set up. Then, inside config.sh, another config.sh
script one level up is sourced. This sets up all environment 
variables specific to all Unix (Linux and Mac) nodes involved
in this *software* build. Inside this config.sh, the config.sh one level up
is also sourced. That script sets up more environment variables
common to all builds (software and experiment data) for this
version of Bioconductor. 

It's important to understand this pattern because it occurs
in several places in BBS. Shell scripts (or batch files on
windows) are essentially used to
ensure that configuration is correct, but most of the actual
build work is done by python scripts.

So, after prerun.sh sets up all the environment variables,
it runs a
[python script](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/BBS-prerun.py).

This script basically makes a snapshot of the svn repository
to be built.
In the numeric stage listing used by Hervé, this is STAGE1.
(For a release build, this is a release branch;
for devel, it's trunk.)
So the fact that this script runs at 16:24 means that's effectively
the deadline for changes for the day. Any changes made
after that time won't be picked up until the following day's build.

Let's look at the next line in the crontab entry:

    00 17 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.2/bioc/zin1 && ./run.sh >>/home/biocbuild/bbs-3.2-bioc/log/zin1.log 2>&1'


So after giving the prerun script 36 minutes to run, the run.sh
script starts up.

This script sources config files in the same way. It also
sets up Xvfb (the virtual frame buffer for X11; this makes sure
that packages which need access to X11 can have it).
Then finally the main python build script,
[BBS-run.py](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/BBS-run.py),
is run. 

This script runs the following steps, along with the stage
number used by Hervé:

* STAGE2: Preinstall dependencies needed to build
* STAGE3: Build source packages (with `R CMD build`)
* STAGE4: Check source packages (with `R CMD check`)
* STAGE5: Build binary packages (not on Linux builders)

Each stage is run in parallel. The system does not move from one stage to the next until all jobs in the current stage are completed.

Moving on to the next line in the crontab:

    ##### IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "run.sh" job on ALL other nodes!
    10 10 * * * cd /home/biocbuild/BBS/3.2/bioc/zin1 && ./postrun.sh >>/home/biocbuild/bbs-3.2-bioc/log/zin1.log 2>&1

So we started running the main build script at 17:00 and now it is
10:10 the next morning. We hope (as the comment indicates)
that all the builders have finished by now, otherwise there
will be (as there often is) some manual steps to do at this point
(see the ["Care and Feeding"](#care_and_feeding) section below).

The build system will now run postrun.sh which initializes
environment variables as above and then runs 
[BBS-report.py](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/BBS-report.py).

This moves build products into a place where they are accessible
to a subsequent step, and generates the build report and
copies it to the web site.

The crontab contains pretty much the same entries for the
experiment data builds (though those only run twice 
a week, and at different times when hopefully the machines
are not too busy with the software builds), and a few
other entries, but those are the most important.

### More post-build steps (run as *biocadmin*)

There are more steps in the build process. 
These steps are run as the *biocadmin* user, and **only**
on the master (i.e. linux) build node.

Looking at *biocadmin*'s crontab, we see:

    # Update 3.2/bioc repo with packages from latest "bbs-3.2-bioc" run
    # IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "postrun.sh" job!
    30 10 * * * cd /home/biocadmin/manage-BioC-repos/3.2 && (./updateReposPkgs-bioc.sh && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh) >>/home/biocadmin/cron.log/3.2/updateRepos-bioc.log 2>&1

First of all, notice the time. This starts at 10:30. This is 
hopefully enough time for the postrun.sh script (above) to have
finished; otherwise you'll have to re-run some things
manually (see [care and feeding](#care_and_feeding), below).

These steps have to do with managing our *internal
package repositories*. These repositories live on
the linux build notes, in *biocadmin*'s home directory
under `~/PACKAGES/X.Y/REPO` where `X.Y` is the version
of Bioconductor that's being built and `REPO` are the type
of packages being built, `bioc` being software packages
and `data/experiment` being experiment data packages
(a `data/annotation` repository also exists, but
this is managed by others and you don't need to know
as much about it at this point).

So the `cron` job above runs three scripts, to *update*,
*prepare*, and *push*.

The *update* script moves the build products into
our external repository. If a package has been updated,
with an appropriate version bump, the older version
is removed from the repository.

The *prepare* script populates other parts of our
internal repository which will later be moved to the 
web site. Most importantly this includes the package
index pages (PACKAGES and PACKAGES.gz) which tell 
install.packages() and biocLite() and friends which packages
can be installed. There's also a VIEWS file which is
used to build parts of our web site (especially the 
package landing pages). From each built package we 
also extract vignettes (built documents, source documents,
and Stangled R source), READMEs, INSTALL and LICENSE
files, reference manuals, and other material that
we want to link to on the package landing page.

Finally the *push* script uses *rsync* to copy
the internal repository to our web site, which
is where users go when they install a package
via `biocLite()`.



<span id="care_and_feeding"></span>

## Care and Feeding of the Build System

Coming soon.

