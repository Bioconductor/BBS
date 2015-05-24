The "manage-BioC-repos" folder
==============================

This folder contains the shell scripts used internally at the Gentleman Lab
to manage the BioC repositories.

These scripts must be run under (and should be checked out by) a different user
than the user running the builds on the main build node.

At the Gentleman Lab:

  - The daily builds are running from the 'biocbuild' account.

  - The updateReposPkgs-*.sh, prepareRepos-*.sh and pushRepos-*.sh scripts in
    each subfolder of the manage-BioC-repos/ folder are daily cron jobs running
    from the 'biocadmin' account.
    Those cron jobs automatically propagate the source and binary packages
    produced by the daily builds to http://bioconductor.org/packages/
    See the CRONTAB.TXT file in each subfolder (e.g. 2.1/CRONTAB.TXT or
    2.2/CRONTAB.TXT) for the crontabs that are/were used for this.

Questions/help: hpages@fhcrc.org (ext. 5791)

