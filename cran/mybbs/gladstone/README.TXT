Last updated: 2007-05-02

gladstone users can use BBS (the BioC Build System) to build and check
CRAN packages with the version of R of their choice.


Instructions
============

  1. Get a working copy of the BBS sources:

       svn co https://hedgehog.fhcrc.org/bioconductor/trunk/bioC/admin/build/BBS BBSwc

     Make sure that you are actually reading the last version of this README.TXT
     file. It's here:

       BBSwc/cran/mybbs/gladstone/README.TXT

  2. Create your personal public_html directory (this is where the
     Build System results will be written):

       mkdir -p ~/public_html/BBS

     Check perms of your ~, ~/public_html and ~/public_html/BBS dirs:
     you need to make them readable and executable by anybody (755) so that
     the Apache server running on gladstone can access them.

     Now you should be able to open a browser in http://gladstone/~$USER/BBS/
     from anywhere behind the Hutch's firewall.

  3. Each running instance of BBS needs write access to its own
     dedicated directory (BBS_WORK_TOPDIR) and to its own
     dedicated R installation. For example if you plan to check
     all the CRAN packages with 2 different installations of R,
     then you need to setup 2 instances of BBS e.g. "mybbs1" and "mybbs2".
     Here is how you can do this:
       a. Create the ~/mybbs1 and ~/mybbs2 dirs.
       b. Create a 'NodeInfo' subdir under ~/mybbs1 and ~/mybbs2.
          (check that ~/mybbs1/NodeInfo and ~/mybbs2/NodeInfo have
          mode 755).
       c. Create a 'log' subdir under ~/mybbs1 and ~/mybbs2.
     
  4. In each BBS_WORK_TOPDIR dir created in 2., create the bbs.sh
     script containing the following:

       #!/bin/bash
       # This is the ~/mybbs1/bbs.sh script

       export BBS_HOME=<abs_path_to_BBSwc> # e.g. ~/BBSwc
       export BBS_WORK_TOPDIR=~/mybbs1
       export BBS_BUILD_LABEL="mybbs1" # No space or slash!
       export BBS_R_HOME=<abs_path_to_R_installation>

       cd $BBS_HOME/cran/mybbs/gladstone && \
          (./prerun.sh && ./run.sh && ./postrun.sh) 2>&1 \
            >> $BBS_WORK_TOPDIR/log/$BBS_BUILD_LABEL.log

     Don't forget to chmod +x bbs.sh

  5. Start the "mybbs1" builds with:
       ~/mybbs1/bbs.sh

This will run STAGE2 (install all dependencies) + STAGE3 (the BUILD stage)
+ STAGE4 (the CHECK stage) on the 1000 CRAN packages.

You can see the progress by looking at the log file in BBS_WORK_TOPDIR/log.

When it's done (after about 12h30), a report will be published here:
    http://gladstone/~$USER/BBS/$BBS_BUILD_LABEL/report/

If you want to go faster, add
    export BBS_NB_CPU=2
or
    export BBS_NB_CPU=3
in your bbs.sh script. This will parallelize STAGE3 and STAGE4 by running
simultaneously BBS_NB_CPU 'R CMD build' or 'R CMD check' commands.
STAGE2 is not parallelized.

If bbs.sh has terminated normally, you can rerun it by simply doing
    ~/mybbs1/bbs.sh
again. You might want to 'svn up' the BBS sources first and/or
change some of the env. var. values defined in bbs.sh (you can
change any of them, except BBS_WORK_TOPDIR).

Some infos to come soon on how to skip certain stages (you might want to
skip STAGE2 which is not very usefull for CRAN packages and takes forever).

Some known issues:

  - bbs.sh starts by removing any 00LOCK dir that it finds in BBS_R_HOME/library.
    This is because this 00LOCK file might have been left behind by a previous
    run of bbs.sh that has been interrupted (by hand or because of an error).
 
  - When bbs.sh has finished (or if you interrupt it with CTRL+C), it's possible
    that some R processes started by BBS are still running. If this is the case,
    then you need to kill them by hand.
    BBS for BioC (the daily builds) runs under a dedicated user "biocbuild"
    and therefore can safely do a 'kill -9 -1' at the end of a run. If you don't
    want to do this (this will kill all your processes and kick you out of
    gladstone), then you'll have to figure out if there are such remaining
    processes and to kill them one by one.

  - You'll probably find more...


FYI, there are 3 different places under which BBS will put things during a run:
  - Under $BBS_WORK_TOPDIR/
  - Under http://gladstone/~$USER/BBS/$BBS_BUILD_LABEL/
  - Under $BBS_R_HOME/library. This can be overwritten by defining the
    R_LIBS env. var.

Please let me know in case of problems.

H.

