"1.9/bioc" BUILDS
=================


This is the top directory containing the set of scripts used to run
the "1.9/bioc" builds. These scripts allow to run a complete BioC 1.9
build (i.e. build + check of all the software packages in Bioconductor 1.9)
on the following nodes:

  Hostname    OS                   Arch (*)
  --------    -------------------  --------
  lamb1       Linux (SUSE 10.1)    x86_64
  wellington  Linux (SUSE 9.2)     i686
  churchill   Solaris 2.9          sparc
  lemming     Windows Server 2003  x86_64

  (*) as reported by 'uname -p' (not 'arch'), except on Windows

Follow the instructions below to setup the "1.9/bioc" builds with 1 run per day.

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

# "1.9/bioc" builds (daily)
01 12 * * * cd /home/biocbuild/BBS/1.9/bioc/lamb1 && ./stage1.sh >>/home/biocbuild/bbs-1.9/log/lamb1.log 2>&1
55 12 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/1.9/bioc/lamb1 && ./run.sh >>/home/biocbuild/bbs-1.9/log/lamb1.log 2>&1'
# IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "run.sh" job on ALL other nodes!
51 21 * * * cd /home/biocbuild/BBS/1.9/bioc/lamb1 && ./postrun.sh >>/home/biocbuild/bbs-1.9/log/lamb1.log 2>&1

  If you want to automatically update the http://bioconductor.org/packages/1.9/bioc
  repo with the packages produced by the last "1.9/bioc" builds, then add the following
  line in the 'biocadmin' crontab (note that this is not part of the Build System,
  see the scripts in biocadmin@lamb1:bin for more information):

# Update http://bioconductor.org/packages/1.9/bioc repo with packages produced by last "1.9/bioc" builds
# IMPORTANT: Make sure this is started AFTER 'biocbuild' has finished its "postrun.sh" job!
41 00 * * * cd /home/biocadmin/bin && (./updateReposPkgs-1.9-bioc.sh && ./prepareRepos-1.9-bioc.sh && ./pushRepos-1.9-bioc.sh) >>/home/biocadmin/cron.log/updateRepos-1.9-bioc.log 2>&1


On wellington
-------------

  Put the following line in the 'biocbuild' crontab:

# "1.9/bioc" builds (daily)
53 12 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/1.9/bioc/wellington && ./run.sh >>/loc/biocbuild/bbs-1.9/log/wellington.log 2>&1'


On churchill
------------

  Put the following line in the 'biocbuild' crontab:

# "1.9/bioc" builds (daily)
51 12 * * * /bin/bash --login -c 'cd /home/biocbuild/BBS/1.9/bioc/churchill && ./run.sh >>/loc/biocbuild/bbs-1.9/log/churchill.log 2>&1'


On lemming
----------

  Put the following command in the Task Scheduler:

D:\biocbld\BBS\1.9\bioc\lemming\run.bat >>D:\biocbld\bbs-1.9\log\lemming.log 2>&1

  This MUST be started in:

D:\biocbld\BBS\1.9\bioc\lemming

by the 'LEMMING\biocbuild' user ("Run as:" field).

  Other settings:
    - Schedule Task: Daily
    - Start time: 12:50 PM
    - Stop the task if it runs for 20 hours

IMPORTANT:
  - There is an issue with batch jobs on Windows Server 2003: if you want
    the batch job to be started even when the 'biocbuild' user is not logged on,
    then have a look at
        http://support.microsoft.com/?kbid=867466
    for how to achieve this.
    (Many thanks to Joe Aprile from PHS Helpdesk for the link, Joe can also
    help with fixing this pb.)

