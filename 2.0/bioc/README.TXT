"2.0/bioc" BUILDS
=================


This is the top directory containing the set of scripts used to run
the "2.0/bioc" builds. These scripts allow to run a complete BioC 2.0
build (i.e. build + check of all the software packages in Bioconductor 2.0)
on the following nodes:

  Hostname    OS                   Arch (*)
  --------    -------------------  --------
  lamb1       Linux (SUSE 10.1)    x86_64
  wellington  Linux (SUSE 9.2)     i686
  churchill   Solaris 2.9          sparc
  lemming     Windows Server 2003  x86_64
  liverpool   Windows Server 2003  NA
  derby       MacOS X              i386

  (*) as reported by 'uname -p' (not 'arch'), except on Windows

Follow the instructions below to setup the "2.0/bioc" builds with 1 run per day.

NOTES:

  - You need to have at least 4GB of free space on the BBS_WORK_TOPDIR dir
    partition (refer to the config.sh or config.bat files in each node subdir
    for the value of BBS_WORK_TOPDIR and other node specific variables).

  - On each node, don't forget to create the 'log' and 'NodeInfo' subdirs under
    the BBS_WORK_TOPDIR dir! Also, make sure that the 'NodeInfo' subdir has
    mode 755 (having 744 is not enough to have it readable by anybody
    when it's going to be pushed to a Linux/Unix system).

  - On the Windows nodes, in addition to the 'log' and 'NodeInfo' mentioned
    above, don't forget to create the 'tmp' and 'tmpdir' subdirs under the
    BBS_WORK_TOPDIR dir!

  - On the Windows nodes: make sure that the user BBS is running as is a
    member of the "Power Users" group. If it's not the case then (1) the
    pdflatex command (from MikTeX) will not be able to download and install
    missing MikTeX extensions:
        pdflatex.EXE: Windows API error 5: Access is denied.
    and (2) 'R CMD check' will fail on all packages for some obscure reason:
        LaTeX errors when creating DVI version.

  - On the Windows nodes, make sure that the user BBS is running as has
    MAKE=make defined in its environment (this allows packages that have
    an inst/doc/Makefile to have their vignette to build properly).

  - On the Unix nodes, the bash --login option used in the crontabs below
    ensures that "run.sh" will "see" eactly the same environment than if
    started by hand.


On lamb1 (main node)
--------------------

IMPORTANT: On all other nodes, the "run.sh" job must
start AFTER the "stage1.sh" job has finished on the main node,
and finish BEFORE the "postrun.sh" job is started on the main node.

  Put the following lines in the 'biocbuild' crontab:

# bbs-2.0-bioc
01 00 * * * cd /home/biocbuild/BBS/2.0/bioc/lamb1 && ./stage1.sh >>/home/biocbuild/bbs-2.0-bioc/log/lamb1.log 2>&1
55 00 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/2.0/bioc/lamb1 && ./run.sh >>/home/biocbuild/bbs-2.0-bioc/log/lamb1.log 2>&1'
# IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "run.sh" job on ALL other nodes!
51 09 * * * cd /home/biocbuild/BBS/2.0/bioc/lamb1 && ./postrun.sh >>/home/biocbuild/bbs-2.0-bioc/log/lamb1.log 2>&1

  If you want to automatically update the http://bioconductor.org/packages/2.0/bioc
  repo with the packages produced by the last "2.0/bioc" builds, then add the following
  line in the 'biocadmin' crontab (note that this is not part of the Build System,
  see the scripts in biocadmin@lamb1:bin for more information):

# Update http://bioconductor.org/packages/2.0/bioc repo with packages produced by last "2.0/bioc" builds
# IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "postrun.sh" job!
41 12 * * * cd /home/biocadmin/bin && (./updateReposPkgs-2.0-bioc.sh && ./prepareRepos-2.0-bioc.sh && ./pushRepos-2.0-bioc.sh) >>/home/biocadmin/cron.log/updateRepos-2.0-bioc.log 2>&1


On wellington
-------------

  Put the following line in the 'biocbuild' crontab:

# bbs-2.0-bioc
53 00 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/2.0/bioc/wellington && ./run.sh >>/loc/biocbuild/bbs-2.0-bioc/log/wellington.log 2>&1'


On churchill
------------

  Put the following line in the 'biocbuild' crontab:

# bbs-2.0-bioc
51 00 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/2.0/bioc/churchill && ./run.sh >>/loc/biocbuild/bbs-2.0-bioc/log/churchill.log 2>&1'


On lemming
----------

  Put the following command in the Task Scheduler:

D:\biocbld\BBS\2.0\bioc\lemming\run.bat >>D:\biocbld\bbs-2.0-bioc\log\lemming.log 2>&1

  This MUST be started in:

D:\biocbld\BBS\2.0\bioc\lemming

by the 'LEMMING\biocbuild' user ("Run as:" field).

  Other settings:
    - Schedule Task: Daily
    - Start time: 12:50 AM
    - Stop the task if it runs for 20 hours

IMPORTANT:
  - There is an issue with batch jobs on Windows Server 2003: if you want
    the batch job to be started even when the 'biocbuild' user is not logged on,
    then have a look at
        http://support.microsoft.com/?kbid=867466
    for how to achieve this.
    (Many thanks to Joe Aprile from PHS Helpdesk for the link, Joe can also
    help with fixing this pb.)


On liverpool
------------

  Put the following command in the Task Scheduler:

E:\biocbld\BBS\2.0\bioc\liverpool\run.bat >>E:\biocbld\bbs-2.0-bioc\log\liverpool.log 2>&1

  This MUST be started in:

E:\biocbld\BBS\2.0\bioc\liverpool

by the 'LIVERPOOL\biocbuild' user ("Run as:" field).

  Other settings:
    - Schedule Task: Daily
    - Start time: 12:54 AM
    - Stop the task if it runs for 20 hours

IMPORTANT:
  - There is an issue with batch jobs on Windows Server 2003: if you want
    the batch job to be started even when the 'biocbuild' user is not logged on,
    then have a look at
        http://support.microsoft.com/?kbid=867466
    for how to achieve this.
    (Many thanks to Joe Aprile from PHS Helpdesk for the link, Joe can also
    help with fixing this pb.)


On derby
--------

  Put the following line in the 'biocbuild' crontab:

# bbs-2.0-bioc
52 00 * * * /bin/bash --login -c 'cd /Users/biocbuild/BBS/2.0/bioc/derby && ./run.sh >>/Users/biocbuild/bbs-2.0-bioc/log/derby.log 2>&1'

