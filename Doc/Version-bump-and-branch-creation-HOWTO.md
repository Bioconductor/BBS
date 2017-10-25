# Version-bump-and-branch-creation-HOWTO


## Introduction

On the day prior to the release, we need to make and push the following
changes to all the packages in the release, **in this order**:

* **First version bump**: bump x.y.z version to even **in the `master` branch**
* **Branch creation**: create the release branch
* **Second version bump**: bump x.y.z version to odd y **in the `master` branch**

For example, for the BioC 3.6 release, we need to do this for all the
packages listed in the `software.txt` and `data-experiment.txt` files
of the `RELEASE_3_6` branch of the `manifest` repo.

This needs to be done **before** the BioC 3.6 software builds start for
the software packages, and **before** the BioC 3.6 data-experiment builds
start for the data-experiment packages.

Look for the prerun jobs in the crontab for the `biocbuild` user on the
main BioC 3.6 builder to get the times the software and data-experiment
builds get kicked off. According to this crontab, the last software and
data-experiment builds preceding the official release will get kicked off
on Mon Oct 30 at 17:00 EST and on Tue Oct 31 at 9:35 am EST, respectively.
Make sure to check this again a couple of days before the release as we
sometimes make small adjustments to the crontabs on the build machines.
Also be sure to translate to your local time if you are not on the East
Coast.


## A. Preliminary steps

These steps should be performed typically a couple of days before B. and C.

* Update this document to reflect the BioC version to be released (i.e.
  by replacing all occurences of `3.6` and `RELEASE_3_6` with appropriate
  version). This will avoid potentially disastrous mistakes when
  copying/pasting/executing commands from this file.

* Choose a machine with enough disk space to clone all the software and
  experiment packages (total size of all the clones is about 90G as of
  Oct 24, 2017). Also make sure to pick up a machine that has fast and
  reliable internet access.

* Make sure to enable forwarding of the authentication agent connection when
  you login to the machine (`-A` option) e.g.

      ssh -A hpages@malbec1.bioconductor.org

* Clone (or update) the BBS git repo:

      # clone
      git clone https://github.com/Bioconductor/BBS
      # update
      cd ~/BBS
      git pull

* Create the `git.bioconductor.org` folder:

      mkdir git.bioconductor.org

  and populate it with clones of the `manifest` and all packages repos:

      # This takes 2h or more so is worth doing in advance e.g. 2 days before
      # the release. It will save time when doing B. and C. below on the day
      # prior to the release.
      cd ~/git.bioconductor.org
      export BBS_HOME="$HOME/BBS"
      export PYTHONPATH="$BBS_HOME/bbs"
      $BBS_HOME/utils/update_bioc_git_repos.py manifest RELEASE_3_6
      $BBS_HOME/utils/update_bioc_git_repos.py software master  # approx. 70 min
      $BBS_HOME/utils/update_bioc_git_repos.py data-experiment master

* Finally make sure you can push changes to the BioC git server (at
  git.bioconductor.org):

      git config --global push.default matching
      cd ~/git.bioconductor.org/software/affy
      git push  # should display 'Everything up-to-date'


## B. Version bumps and branch creation for software packages

Perform these steps on the day prior to the release. They must be completed
before the software builds get kicked off (see **Introduction**). The full
procedure should take less than 2 hours. Make sure to reserve enough time.

### 1. Ask people to stop comitting/pushing changes to the BioC git server

Before you start announce or ask a team member to announce on the
bioc-devel mailing list that people should stop comitting/pushing
changes to the BioC git server (git.bioconductor.org) for the next couple
of hours.

### 2. Login to the machine where you've performed the preliminary steps

For example:

    # Use -A option to enable forwarding of the authentication agent connection
    ssh -A hpages@malbec1.bioconductor.org

See **A. Preliminary steps** above for the details.

### 3. Checkout/update the `RELEASE_3_6` branch of the `manifest` repo

    cd ~/git.bioconductor.org/manifest
    git checkout RELEASE_3_6
    git pull
    git branch
    git status

### 4. Set the `MANIFEST_FILE` environment variable

Set it to the manifest file for software packages. This must be the file
from the `RELEASE_3_6` branch of the `manifest` repo:

    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/software.txt"

### 5. Go to the `~/git.bioconductor.org/software/` folder

    cd ~/git.bioconductor.org/software

Steps 6-12 below must be performed from this folder

### 6. Make sure all package git clones are up-to-date

The `~/git.bioconductor.org/software` folder should already contain the git
clones of all the software packages that are listed in the `RELEASE_3_6`
manifest (see **A. Preliminary steps** above). Note that all the git clones
should be on the **master** branch!

Update the git clones of all the packages listed in `$MANIFEST_FILE` with:

    export BBS_HOME="$HOME/BBS"
    export PYTHONPATH="$BBS_HOME/bbs"
    $BBS_HOME/utils/update_bioc_git_repos.py

### 7. First version bump (to even y)

    ~/BBS/utils/bump_pkg_versions.sh bad
    ~/BBS/utils/bump_pkg_versions.sh test even
    ~/BBS/utils/bump_pkg_versions.sh even

### 8. Commit first version bump

    commit_msg="bump x.y.z versions to even y prior to creation of RELEASE_3_6 branch"
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # Stage DESCRIPTION for commit
    for pkg in $pkgs_in_manifest; do
      echo "'git add DESCRIPTION' for package $pkg"
      git -C $pkg add DESCRIPTION
    done

    # Dry-run commit
    for pkg in $pkgs_in_manifest; do
      echo "commit version bump for package $pkg (dry-run)"
      git -C $pkg --dry-run commit -m "$commit_msg"
    done

    # If everything looks good
    for pkg in $pkgs_in_manifest; do
      echo "commit version bump for package $pkg"
      git -C $pkg commit -m "$commit_msg"
    done

### 9. Branch creation

    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # Create the RELEASE_3_6 branch and change back to master
    for pkg in $pkgs_in_manifest; do
      echo "create RELEASE_3_6 branch for package $pkg"
      git -C $pkg checkout -b RELEASE_3_6
      git -C $pkg checkout master
    done

### 10. Second version bump (to odd y)

    ~/BBS/utils/bump_pkg_versions.sh test odd
    ~/BBS/utils/bump_pkg_versions.sh odd

### 11. Commit second version bump

Same as step 8 above EXCEPT that commit message now is:

    commit_msg="bump x.y.z versions to odd y after creation of RELEASE_3_6 branch"

### 12. Push all the changes

    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # Dry-run push
    for pkg in $pkgs_in_manifest; do
      echo "push all changes for package $pkg (dry-run)"
      git -C $pkg --dry-run push
    done

    # If everything looks good
    for pkg in $pkgs_in_manifest; do
      echo "push all changes for package $pkg"
      git -C $pkg push
    done

### 13. Tell people that comitting/pushing to the BioC git server can resume

Announce or ask a team member to announce on the bioc-devel mailing list
that comitting/pushing changes to the BioC git server (git.bioconductor.org)
can resume.

### 14. Switch `BBS_BIOC_GIT_BRANCH` from `master` to `RELEASE_3_6` on main BioC 3.6 builder

DON'T FORGET THIS STEP! Its purpose is to make the BioC 3.6 builds grab the
`RELEASE_3_6` branch of all packages instead of their `master` branch.

Login to the main BioC 3.6 builder as biocbuild and replace

    export BBS_BIOC_GIT_BRANCH="master"

with

    export BBS_BIOC_GIT_BRANCH="RELEASE_3_6"

in `~biocbuild/BBS/3.6/config.sh`

Also replace

    set BBS_BIOC_GIT_BRANCH=master

with

    set BBS_BIOC_GIT_BRANCH=RELEASE_3_6

in `~biocbuild/BBS/3.6/config.bat`


## C. Version bumps and branch creation for data-experiment packages


