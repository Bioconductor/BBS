Table of Contents
=================

* [Troubleshooting the Builds](#care-and-feeding-of-the-build-system)
  * [Example workflow](#example-workflow)
    * [Investigating](#investigating)
    * [Taking a deeper look](#taking-a-deeper-look)
  * [Looking at logs](#looking-at-logs)
  * [Interpreting log output](#interpreting-log-output)
  * [Running the build report without a given node](#running-the-build-report-without-a-given-node)
* [Extras](#extras)
  * [Monitor dcf files](#monitor-dcf-files)
  * [Broken DESCRIPTION files](#broken-description-files)
  * [Daily Tasks](#daily-tasks)

This content used to be called "Care and Feeding of the Build
System" and was included in the BBS/README.md. That document got too big
so troubleshooting was broken out here.


## Troubleshooting the Builds 

Ideally the build system should *just work* every day
so you wouldn't have to pay much attention to it.
Often it does.

But it should still be checked on daily to make sure
it is doing what is is supposed to do.

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
  update/prepare/push scripts on biocpush by hand).

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

There are several categories of common problems which will be discussed TBA.
For now, contact Hervé or Lori and share your findings with them.

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
our web site (the steps that are run as biocpush) will
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
 # The variables below control postrun.sh so only need to be defined on the
 # central node

 # Control propagation:
-export BBS_OUTGOING_MAP="source:linux1.bioconductor.org/buildsrc win.binary:windows1.bioconductor.org/buildbin mac.binary:perceval/buildbin mac.binary.mavericks:oaxaca/buildbin"
+export BBS_OUTGOING_MAP="source:linux1.bioconductor.org/buildsrc win.binary:windows1.bioconductor.org/buildbin mac.binary:perceval/buildbin"

 # Control generation of the report: 
-export BBS_REPORT_NODES="linux1.bioconductor.org windows1.bioconductor.org:bin perceval:bin oaxaca:bin"
+export BBS_REPORT_NODES="linux1.bioconductor.org windows1.bioconductor.org:bin perceval:bin"
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

Now, if the biocpush scripts have not yet been run by
crontab, you don't have to do anything more.

But if that has already happened, you need to do the following:

```
ssh biocpush@linux1.bioconductor.org
# or ssh ubuntu@linux1.bioconductor.org and then
# sudo su - biocpush
cd propagation/3.2
 ./updateReposPkgs-bioc.sh  && ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh 
```

**If the builds took too long**: Sometimes no build node failed, but
the builds took longer than the time allotted.
In this case you do not need to edit `config.sh` but
you will need to manually run `postrun.sh` and the
biocpush update/prepare/push scripts, after all build nodes
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

# Extras

These should be organized at some point - for now they are captured here.

## Monitor dcf files 

To watch the incoming summary.dcf files in real time on the main node,
e.g. on lamb2, do:

    cd ~biocbuild/public_html/BBS/2.7/bioc/nodes
    watch -d 'ls -ltr */*/*-summary.dcf | tail'

## Broken DESCRIPTION files

The BBS doesn't like it when a DESCRIPTION file is broken and excludes the
package from the builds during the prerun step:

    biocbuild@malbec1:~/bbs-3.6-bioc/log$ grep -i skip malbec1-20171204-prerun.log
    BBS>   Bad DESCRIPTION file in pkg dir '/home/biocbuild/bbs-3.6-bioc/MEAT0/sampleClassifier'. Skip it!

## Daily Tasks

Each morning, the build system must be inspected (manually<sup>1</sup>).  The expected results of the nigthly build are described below.  To begin, ssh to the Linux build box : 

```
ssh ubuntu@linux1.bioconductor.org
```

Next, switch to the `biocbuild` user:

```
ubuntu@linux1:~$ sudo su - biocbuild
```

From there, navigate to the `nodes` directory, which contains useful information about each build server: 
```
cd /home/biocbuild/public_html/BBS/3.2/bioc/nodes
```
Note the current time ...
```
biocbuild@linux1:-~/public_html/BBS/3.2/bioc/nodes$ date
Mon Oct  5 12:32:47 EDT 2015
```
... and compare that against the timestamps of directories and files related to the build : 
```
biocbuild@linux1:-~/public_html/BBS/3.2/bioc/nodes$ ls -l *
linux1.bioconductor.org:
total 368
-rw-rw-r--    1 biocbuild biocbuild    458 Oct  5 09:05 BBS_EndOfRun.txt
drwxrwxr-x    2 biocbuild biocbuild 172032 Oct  5 00:45 buildsrc
drwxrwxr-x 1077 biocbuild biocbuild 147456 Oct  5 09:05 checksrc
drwxrwxr-x    2 biocbuild biocbuild  36864 Oct  4 20:21 install
drwxr-xr-x    2 biocbuild biocbuild   4096 Oct  4 20:21 NodeInfo

oaxaca:
# Output omitted for brevity

perceval:
total 428
drwxrwxr-x    2 biocbuild biocbuild  73728 Oct  5 12:33 buildbin
drwxrwxr-x    2 biocbuild biocbuild 167936 Oct  5 02:01 buildsrc
drwxrwxr-x 1055 biocbuild biocbuild 143360 Oct  5 11:40 checksrc
drwxrwxr-x    2 biocbuild biocbuild  36864 Oct  4 20:26 install
drwxr-xr-x    2 biocbuild biocbuild   4096 Oct  4 20:27 NodeInfo

windows1.bioconductor.org:
# Output omitted for brevity

```
Notice, there is a directory for each build box (***linux1.bioconductor.org***,  ***oaxaca***,  ***perceval***,  ***windows1.bioconductor.org***).  Inside, there are various sub-directories and files.  We expect that these directories and files will be updated each day.

When the build has completely finished on a given build box, a `BBS_EndOfRun.txt` file will be created.  Notice, above there is one for the linux1.bioconductor.org server.  It is often after 1p.m. (Eastern) that the build on perceval is complete<sup>3</sup>, however Linux, Windows and the other Mac build server (oaxaca) are often finished by 11a.m. (Eastern).

To determine which nodes are finished, execute the following command: 
```
find /home/biocbuild/public_html/BBS/3.2/bioc/nodes -maxdepth 2 -type f -name "BBS_EndOfRun.txt" -exec ls -1 {} \;
```
Which will result in output like : 
```
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/windows1.bioconductor.org/BBS_EndOfRun.txt
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/linux1.bioconductor.org/BBS_EndOfRun.txt
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/oaxaca/BBS_EndOfRun.txt
```

*If the directories and files do not apear updated when running `ls -l *` in the `nodes` directory, investigate the build server that appears to have a fault.*  Information on investigating build servers can be found in the document [InvestigatingBuildServers.md](InvestigatingBuildServers.md).

<hr/>
<sub>
1) This manual process of inspecting the build system should be automated.  The GH issue to track this problem is: https://github.com/Bioconductor/BBS/issues/11 .
<br/>2) For the purpose of automation, we should enumerate exactly which conditions must be met (e.g. requiring an exact time of day that specific files have been updated).
<br/>3) The perceval build server has been known to be slow.  We should create a ticket to investigate and resolve this issue.
</sub>
