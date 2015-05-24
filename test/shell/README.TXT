BioC_builder was my first "quick and dirty" attempt to rewrite 
parts of the BioC Build System. The top scripts were shell scripts.
From these scripts I was trying to call as much of the old stuff
(mostly Python scripts belonging to the old Build System) as I could.

I kept it here because of the locking feature I implemented
(may be one day we want to use that kind of feature for BBS).

The BioC_builder scripts have been used temporarly on gopher5
as part of the process to build/check packages for BioC 1.7.
We used to have the following in the 'biocbuild' crontab:

# bioc-1.7 builds
# ---------------
# STAGE1 for bioc-1.7
18 12 * * * $HOME/BioC_builder/scripts/BioC_builder.sh STAGE1 1.7 >>$HOME/BioC_builder/log/history.log 2>&1
# STAGE2 for bioc-1.7
25 12 * * * $HOME/BioC_builder/scripts/BioC_builder.sh STAGE2 1.7 >>$HOME/BioC_builder/log/history.log 2>&1
# STAGE3 for bioc-1.7
35 12 * * * $HOME/BioC_builder/scripts/BioC_builder.sh STAGE3 1.7 >>$HOME/BioC_builder/log/history.log 2>&1
# STAGE4 for bioc-1.7
01 18 * * * $HOME/BioC_builder/scripts/BioC_builder.sh STAGE4 1.7 >>$HOME/BioC_builder/log/history.log 2>&1

Warning: STAGE1, STAGE2, STAGE3 and STAGE4 don't match the current
stage1, STAGE2, STAGE3 and STAGE4 of BBS!
