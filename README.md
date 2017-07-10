
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
      * [What machines are used in which builds?](#what-machines-are-used-in-which-builds)
        * [Devel (Bioconductor 3\.2)](#devel-bioconductor-32)
        * [Release (Bioconductor 3\.1)](#release-bioconductor-31)
        * [Next devel (Bioconductor 3\.3)](#next-devel-bioconductor-33)
        * [A note about time zones\.](#a-note-about-time-zones)
    * [How the build system works](#how-the-build-system-works)
      * [More post\-build steps (run as <em>biocadmin</em>)](#more-post-build-steps-run-as-biocadmin)
    * [Care and Feeding of the Build System](#care-and-feeding-of-the-build-system)
      * [Example workflow](#example-workflow)
        * [Investigating](#investigating)
        * [Taking a deeper look](#taking-a-deeper-look)
      * [Looking at logs](#looking-at-logs)
      * [Interpreting log output](#interpreting-log-output)
      * [Running the build report without a given node](#running-the-build-report-without-a-given-node)


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

The canonical location of the code is in GitHub:

[https://github.com/Bioconductor/BBS](https://github.com/Bioconductor/BBS)

## Human resources

If you have a question not covered here:

* Dan Tenenbaum should be the first person to ask.
* Herv&eacute; Pag&egrave;s should be the next person to ask.
  He has not been completely in the loop regarding the move
  to the cloud but Dan (and this document) will try and catch him up.
* If neither of those two are available, Martin Morgan may know.

## General overview of BBS

In general, there are four *builds* that run during any given week:

1. Release *software* builds. (*bioc* is the name for our
  software package repository). These builds run nightly on
  all release build machines.
2. Release *experiment package* builds (*data-experiment* is the
   name for our experiment package repository). These builds
   run twice a week, on Wednesdays and Saturdays, on the 
   Linux, Windows, and MacOS build machines
   for release. *
3. Devel *software* builds. These builds run nightly on 
   all devel build machines.
4. Devel *experiment package* builds. These builds run
   twice a week, on Wednesdays and Saturdays, on the
   Linux, Windows, and MacOS build machines for devel.

## What builds where

We are in the process of moving as much of the build system as
possible into the cloud. 

As of 14 September 2015, the devel builds are in the cloud
and the Linux and Windows portions of the "next devel" (BioC 3.3)
builds are there as well. The current release (BioC 3.1) builds happen
entirely at FHCRC with physical machines.

"In the cloud" refers to 
[Amazon Web Services](https://aws.amazon.com/).
The exception to "in the cloud" in the above is that all 
Mac build machines are currently located at FHCRC.

This is because Apple's licensing agreements make it impossible
to virtualize OS X on anything but OS X hardware therefore
there are not a lot of affordable cloud providers for Mac.
It is possible/probable that the Macs will be shipped out of FHCRC
at some point,
either to Roswell Park or to a third-party hosting provider.
We should not need physical access to the Macs (as long as there is a
person we can call to reboot them if we cannot access them
via ssh or Screen Sharing).

### About the build machines.

There are four build machines each for release and devel.

This is for the four platforms that we build for:

* Linux (Ubuntu 14.04 LTS)
* Windows (Server 2008 or Server 2012)
* Mac OX X 10.9.5 (Mavericks)

Any build machine that has "bioconductor.org" in its
name is in the cloud. Any machine without a fully qualified
domain name is (at this point) at FHCRC in Seattle.

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
[config.yaml](http://master.bioconductor.org/config.yaml
) file for the web site (requires your svn credentials).
The *active_devel_builders* and *active_release_builders*
section will tell you what is being used, and that
should be current.

However, just to give you an idea, here is what is 
in use as of today, September 14 2015.

#### Devel (Bioconductor 3.2)

* Linux: linux1.bioconductor.org
* Windows: windows1.bioconductor.org
* Mac Mavericks: oaxaca

#### Release (Bioconductor 3.1)

* Linux: zin2
* Windows: moscato2
* Mac Mavericks: morelia

#### Next devel (Bioconductor 3.3)

* Linux: linux2.bioconductor.org
* Windows: windows2.bioconductor.org
 
Normally I would not start these builds until the current
release builds had been stopped 
(see [the prerelease checklist](Doc/prerelease_and_release_checklist.txt)) but it makes more sense to start the new devel
builds in the cloud than to move the current release builds.

#### A note about time zones.

The builds have been moved back to FHCRC in October 2015
and all build machines are on west coast time.

## How the build system works

As described above, on each build machine, the build system
code is checked out. **At present, each machine's working
copy is checked out to the branch `feature/migrate_back_to_hutch`.**

On each build machine there is a cron job (or Scheduled Task
on Windows) that kicks off the builds.

On all build machines, the build system runs as the *biocbuild* 
user. 

I highly recommend looking at the crontab for the *biocbuild*
user on one of the Linux build machines (a/k/a master build nodes).

Among other things, you'll see the following (from the BioC 3.2
master build node):

    # bbs-3.2-bioc
    24 19 * * * cd /home/biocbuild/BBS/3.2/bioc/linux1.bioconductor.org && ./prerun.sh >>/home/biocbuild/bbs-3.2-bioc/log/linux1.bioconductor.org.log 2>&1

The *prerun* step happens only on the master build node.
I recommend looking to see what happens in that prerun.sh
script which can be found in SVN at
[https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/3.2/bioc/zin1/prerun.sh](https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS/3.2/bioc/zin1/prerun.sh).
If you look there, you will see that it is essentially just sourcing
a shell script called config.sh and then running a python script.

(Note the script above is for zin1, a machine that will soon
no longer be used; but there is not yet an equivalent directory
in svn for linux1.bioconductor.org, as that code only exists
in a [github branch](https://github.com/Bioconductor/BBS/blob/start-linux1/3.2/bioc/linux1.bioconductor.org/prerun.sh)).

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
So the fact that this script runs at 19:24 means that's effectively
the deadline for changes for the day. Any changes made
after that time won't be picked up until the following day's build.

Let's look at the next line in the crontab entry:

    00 20  * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/3.2/bioc/linux1.bioconductor.org && ./run.sh >>/home/biocbuild/bbs-3.2-bioc/log/linux1.bioconductor.org.log 2>&1'

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
    10 13 * * * cd /home/biocbuild/BBS/3.2/bioc/linux1.bioconductor.org && ./postrun.sh >>/home/biocbuild/bbs-3.2-bioc/log/linux1.bioconductor.org.log 2>&1

So we started running the main build script at 20:00 and now it is
13:10 the next afternoon. We hope (as the comment indicates)
that all the builders have finished by now, otherwise there
will be (as there often is) some manual steps to do at this point
(see the ["Care and Feeding"](#care-and-feeding-of-the-build-system) section below).

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
    40 13 * * * cd /home/biocadmin/manage-BioC-repos/3.2 && (./updateReposPkgs-bioc.sh && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh) >>/home/biocadmin/cron.log/3.2/updateRepos-bioc.log 2>&1

First of all, notice the time. This starts at 13:40. This is 
hopefully enough time for the postrun.sh script (above) to have
finished; otherwise you'll have to re-run some things
manually (see [care and feeding](#care-and-feeding-of-the-build-system), below).

These steps have to do with managing our *internal
package repositories*. These repositories live on
the linux build nodes, in *biocadmin*'s home directory
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
our internal repository. If a package has been updated,
with an appropriate version bump, the older version
is removed from the repository.

The *prepare* script populates other parts of our
internal repository which will later be moved to the 
web site. Most importantly this includes the package
indexes (`PACKAGES` and `PACKAGES.gz`) which tell 
install.packages() and biocLite() and friends which packages
can be installed. There's also a `VIEWS` file which is
used to build parts of our web site (especially the 
package landing pages). From each built package we 
also extract vignettes (built documents, source documents,
and Stangled R source), `README`s, `INSTALL` and `LICENSE`
files, reference manuals, and other material that
we want to link to on the package landing page.

Finally the *push* script uses *rsync* to copy
the internal repository to our web site, which
is where users go when they install a package
via `biocLite()`.


## Care and Feeding of the Build System

Ideally the build system should *just work* every day
so you wouldn't have to pay much attention to it.
Often it does.

But should still check up on it daily to make sure
it is doing what is is supposed to do. (*You* in this context
basically means Brian, or anyone else who is taking over
this duty in his absence).

(People who are not FHCRC employees are exempt from
care and feeding of the 3.1 builds which requires 
access to the internal FHCRC network. Dan/Hervé will
do this for the time being and these builds will
stop on 10/8/2015).

For 3.2 and newer, for issues with any of the Mac
build machines at FHCRC, you will need to pass those
off to Dan or Hervé, who can log into those machines
and see what is going on. Bear in mind, some clues
may be available on the master builder.) Jim Hester
also has access to these machines.

Regarding causes for failed builds: There are a few things
that keep cropping up and we hope to work on long term
solutions for these. (`We` might mean you in these cases!)


### Example workflow

This is an example that looks at the current devel 
(BioC 3.2) builds. The exact commands/urls shown
here may not be valid for subsequent builds but
this should give you the idea of what you need to do.

From looking at *biocbuild*'s crontab on 
*linux1.bioconductor.org* we know that the *postrun* job
is supposed to run at 13:10 (that's Buffalo time).

(Note that all times in crontab files are subject to change,
so don't take this as gospel.)

The postrun script takes about 30 minutes tops, so 
by 13:40 you should see today's date near the top
of 

[http://master.bioconductor.org/checkResults/devel/bioc-LATEST/](http://master.bioconductor.org/checkResults/devel/bioc-LATEST/)

...then you should investigate. In fact, you don't even
have to wait till 13:40, it's always a good idea to check
the status of the builds.

Note that url has `master` in it. Content copied to the web 
site should immediately be visible in urls that start with
master.bioconductor.org. If you omit the master or replace it
with `www`, it might take a while longer for the content
to propagate because you are looking at an
[Amazon CloudFront](https://aws.amazon.com/cloudfront/)
distribution.

#### Investigating

There are other ways, but my preferred way to 
investigate is to ssh to the build machine
(in this case `linux1.bioconductor.org`) as the `biocbuild`
user and issue the command:

    ls -l ~/public_html/BBS/3.2/bioc/nodes/*|less

This should show some output for each node, for example
here's the part for `linux1.bioconductor.org`:

    public_html/BBS/3.2/bioc/nodes/linux1.bioconductor.org:
    total 368
    -rw-rw-r--    1 biocbuild biocbuild    458 Sep  8 09:39 BBS_EndOfRun.txt
    drwxr-xr-x    2 biocbuild biocbuild 172032 Sep  8 01:06 buildsrc
    drwxr-xr-x 1057 biocbuild biocbuild 147456 Sep  8 09:39 checksrc
    drwxr-xr-x    2 biocbuild biocbuild  36864 Sep  7 20:24 install
    drwxr-xr-x    2 biocbuild biocbuild   4096 Sep  7 20:24 NodeInfo

Here's what you are looking for:

* There should be a section for each node in the build.
* Each node should have a `BBS_EndOfRun.txt` file.
* The timestamp on that file should be **before** the 
  postrun.sh script runs in crontab (i.e. before 13:10 in
  this example).

If any of these conditions are not met, those offer you clues
to what has gone wrong. The respective possibilities are:

* Somehow the build node did not start, or failed before
  it could get very far. You need to go to that node 
  and check the logs. (More on this below.)
* The builds are still running. Knowing that the build phases
  are indicated here as `install`, `buildsrc`, `checksrc`,
  and `buildbin`, and occur in that order, look at the 
  timestamp on the directory representing the latest
  build phase. If the time is pretty recent, it probably
  means the build on that machine is still chugging along
  on that phase. If the time was hours ago, likely the
  build failed on that node and you will need to go
  to the node to figure out why.
* If all nodes have `BBS_EndOfRun.txt` files but the timestamp
  on one or more of them is later than the postrun script,
  you will need to run the postrun.sh script by hand (
  and then afterwards you will need to run the 
  update/prepare/push scripts on biocadmin by hand).

#### Taking a deeper look

If a build phase is not complete on a node, you can see where it
is without having to connect to that node, with a command like the
following. Let's say that the `checksrc` phase on node `perceval`
is not complete. Do a command like this:

    watch 'ls -l public_html/BBS/3.2/bioc/nodes/perceval/checksrc/ ' | tail -4

This will show you the last 4 files that were pushed
to the master node from perceval. The display will 
refresh every few seconds. New filenames will show up
in alphabetical order (and not case-sensitive). So
if you are in the Y's, then you're near the end.

### Looking at logs

If a build appears to have stopped on a node, you will need to
go to that node and look at its log. 

To go to the node, connect to it as the `biocbuild` user via
ssh, or Remote Desktop for windows nodes.

On Unix nodes (Linux or Mac), you can find the logs in
`~/bbs-X.Y-bioc/logs` where `X.Y` is the version of Bioconductor 
being built. (Substitute `data-experiment` for `bioc` if you
are troubleshooting the experiment data builds).

On these nodes the log information is appended to 
a file with the name of the node, for example
`perceval.log`. These files can get quite large
and should be manually rotated once in a while
(do that by archiving the old log with `gzip` and re-creating
the new one with `touch`), so likely the information you
are looking for is at the end of the log. 

On Windows nodes, the logs are in
`c:\biocbld\bbs-X.Y-bioc\log`. 

On windows, the logs are a bit different and each build
has its own datestamped log file. For example, the 
log file for the build that started on 9/7/2015 is called
`windows1.bioconductor.org-run-20150907.log`.

On all types of nodes, examine the end of the log file
with the command 

    tail -200 LOG_FILE_NAME

### Interpreting log output

There are several categories of common problems which
will be discussed TBA. For now, contact Dan and share your
findings with him.

Possible problems:

* On windows: A process is holding onto files

If you go to the windows node (using rdesktop, logging in 
as the biocbuild user with the password from the Google doc about
credentials), you can then open a command window and navigate
to `c:\biocbld\bbs-3.2-bioc\log` (the number may be different
depending on the version of Bioconductor being built), you can
look at the most recent log file which will have a name like
`windows1.bioconductor.org-run-20150926.log`. If you run
`tail` on this file you may see something like this:

  rsync: delete_file: unlink(XBSeq.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync: delete_file: unlink(SEPA.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync: delete_file: unlink(Prize.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync: delete_file: unlink(PGA.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync: delete_file: unlink(INSPEcT.buildsrc-out.txt) failed: Device or resourcebusy (16)
  rsync: delete_file: unlink(ELMER.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync: delete_file: unlink(CNVPanelizer.buildsrc-out.txt) failed: Device or resource busy (16)
  rsync error: some files/attrs were not transferred (see previous errors) (code 23) at main.c(1637) [generator=3.1.1]
  ] = 8.97 seconds / retcode = 23 / ERROR!
  3 failed attempts => EXIT.

This means that some process is holding on to those files and rsync was unable to delete them.

A crude fix for this is to reboot (provided that no other builds,
software or experiment, are running). Less crude is to double-
click the `procexp` desktop shortcut (or click Start and type
`procexp` and press Enter.) Then inside Process Explorer,
click `Find/Find Handle Or DLL...` and type in the partial
name of one of the files referenced in the log above, for example
`XBSeq`. Double-click on any matching process, then right-click the 
process and choose `Kill Process Tree`. Repeat this until there
are no processes running that are holding onto any of the
files mentioned in the log (it's probably the same process or
process tree that is holding on to all the files mentioned in
the log).




### Running the build report without a given node

Sometimes a build node failed. A common reason for this is
that there was an error or timeout when attempting to 
rsync build products from the node to the master builder.
This seems to happen most often on the Mac machines
at FHCRC. We need to investigate and fix this. 
(Maybe adjusting timeouts?)

If nothing is done, the postrun script will fail because
it can't find the build products from all build nodes.
Then, the steps that propagate the build products to
our web site (the steps that are run as biocadmin) will
fail to propagate them.

However, we still want a build report every day and
we want the build products from the successful nodes
to propagate.

So, if we can get to it well before the daily deadline
(when the prerun script is run) we should do the following:

Temporarily edit the `config.sh` script for the master builder.
Assuming the affected build is Bioconductor 3.2 and the master
builder is `linux1.bioconductor.org`, we would do:

```
ssh biocbuild@linux1.bioconductor.org
cd BBS/3.2/bioc/linux1.biocondutor.org
```

We now want to edit the file `config.sh` in the current directory.

The lines we want to edit are the lines defining the
`BBS_OUTGOING_MAP` and `BBS_REPORT_NODES` variables.
Here's what those lines look like:

```
biocbuild@linux1:-~/BBS/3.2/bioc/linux1.bioconductor.org (start-linux1)$ egrep "BBS_OUTGOING_MAP|BBS_REPORT_NODES" config.sh
export BBS_OUTGOING_MAP="source:linux1.bioconductor.org/buildsrc win.binary:windows1.bioconductor.org/buildbin mac.binary:perceval/buildbin mac.binary.mavericks:oaxaca/buildbin"
export BBS_REPORT_NODES="linux1.bioconductor.org windows1.bioconductor.org:bin perceval:bin oaxaca:bin"
```

Let's assume the node that did not complete was `oaxaca`; we want 
to remove reference to that node from both lines.

We'll make the following change:

```
biocbuild@linux1:-~/BBS/3.2/bioc/linux1.bioconductor.org (start-linux1)$ git diff config.sh
index b7a14b5..490f8b4 100644
--- a/3.2/bioc/linux1.bioconductor.org/config.sh
+++ b/3.2/bioc/linux1.bioconductor.org/config.sh
@@ -51,14 +51,14 @@ cd "$wd0"
 # packages to propagate and to later not be replaced by the bi-arch when
 # the dropped node is back.
 
-export BBS_OUTGOING_MAP="source:linux1.bioconductor.org/buildsrc win.binary:windows1.bioconductor.org/buildbin mac.binary:perceval/buildbin mac.binary.mavericks:oaxaca/buildbin"
+export BBS_OUTGOING_MAP="source:linux1.bioconductor.org/buildsrc win.binary:windows1.bioconductor.org/buildbin mac.binary:perceval/buildbin"
 # Needed only on the node performing stage7a (BBS-make-STATUS_DB.py) and
 # stage8 (BBS-report.py)
 #
 # IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
 # must be run on the BBS_CENTRAL_RHOST machine.
 
-export BBS_REPORT_NODES="linux1.bioconductor.org windows1.bioconductor.org:bin perceval:bin oaxaca:bin"
+export BBS_REPORT_NODES="linux1.bioconductor.org windows1.bioconductor.org:bin perceval:bin"
 #export BBS_SVNCHANGELOG_URL="http://fgc.lsi.umich.edu/cgi-bin/blosxom.cgi"
 export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
 export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
```

So, to explain a little bit more. `BBS_OUTGOING_MAP` 
is a space-separated list of items, each separated into

```
buildtype:nodename/product_to_propagate
```

So for oaxaca we have:


```
mac.binary.mavericks:oaxaca/buildbin
```

The first segment (before the colon) is the package
type (according to `install.packages()`) that
is produced by this build node. Then comes the node name,
then the build phase for which we propagate the build
products. For all nodes except Linux nodes this 
is `buildbin`, and for Linux nodes it's `buildsrc`.

`BBS_REPORT_NODES` governs which nodes are mentioned
in the build report and is a space-separated list
of items, each of which is the node name
followed by `:bin` if the node is not a Linux 
node.

Removing oaxaca's entry from both variables will allow
the build report to be built. 

If the postrun.sh script has not yet been run by
crontab, it will now run successfully. If the time
for it to run has already passed, you can run it
manually.

**Important**: Be sure to revert the config.sh file
to the state it was in before you made the change.
Otherwise (in this case) oaxaca will be excluded from
the subsequent builds even if it did not fail.

The way I typically do this is to start running

`./postrun.sh`

The first thing that script does is source `config.sh`.
So if you press Control-Z right after starting 
`postrun.sh` you can then revert config.sh to its original state.
Currently ~/BBS is a git working copy so you can do this with:

```
git checkout config.sh
```

Then type

```
fg
```

To bring postrun.sh back to the foreground and let it finish.
The reason I do it this way is that I then do not have to
remember after postrun.sh is done to revert it.

Alternatively you can use `tmux`; it's a good idea to use
it for any long-running script. You can then detach from 
the tmux session and revert config.sh, then reattach 
to the session to monitor the script's progress.

Now, if the biocadmin scripts have not yet been run by
crontab, you don't have to do anything more.

But if that has already happened, you need to do the following:

```
ssh biocadmin@linux1.bioconductor.org
# or ssh ubuntu@linux1.bioconductor.org and then
# sudo su - biocadmin
cd manage-BioC-repos/3.2
 ./updateReposPkgs-bioc.sh  && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh 
```

**If the builds took too long**: Sometimes no build node failed, but
the builds took longer than the time allotted.
In this case you do not need to edit `config.sh` but
you will need to manually run `postrun.sh` and the
biocadmin update/prepare/push scripts, after all build nodes
have finished. You can determine if all build nodes have finished by
running this command (again assuming you are working
with the 3.2 build on `linux1.bioconductor.org`):

```
biocbuild@linux1:-~$ ls -l ~/public_html/BBS/3.2/bioc/nodes/*
```

When that command shows a file `BBS_EndOfRun.txt` for
each node, you will know the build is complete.

If this starts happening a lot you will need to look
at the underlying root causes. It could just be
natural growth of the project. Or a particular machine
could be too slow. Maybe we need to increase the
number of cores on the instance (and we need to
set `BBS_NB_CPU` accordingly in the relevant config file to
explicitly set the number of cores used by the build
system--this should **not** be the full number of
cores on the machine, see relevant comments).
Sometimes some rogue processes start that slow
down the build nodes. There shouldn't be any
R script that runs for many hours.


