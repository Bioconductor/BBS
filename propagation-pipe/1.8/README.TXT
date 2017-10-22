IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT!

  Some scripts in this folder (manage-BioC-repos/1.8) are currently broken
  because they point to stuff that is in the $HOME/bin/ folder.
  On Feb 2008, the $HOME/bin/ folder for the 'admin' user has been
  reorganized on lamb1 so now all the scripts in the manage-BioC-repos/1.8/
  folder should point to stuff that is in the same folder (except for
  the call to $HOME/bin/R-2.3).
  This has been fixed for the scripts in the manage-BioC-repos/2.0,
  manage-BioC-repos/2.1 and manage-BioC-repos/2.2 folders but not for the
  scripts in this folder. In the unlikely eventuality that you need to run
  a script in this folder, YOU WILL NEED TO FIX IT FIRST!
  This is very easy: for example look at what has been done for the
  prepareRepos-*.sh and pushRepos-*.sh scripts in the manage-BioC-repos/2.2
  folder.

IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT! IMPORTANT!

