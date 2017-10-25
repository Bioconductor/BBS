# Version-bump-and-branch-creation-HOWTO


## A. Introduction

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


## B. Preliminary steps

These steps should be performed typically a couple of days before C., D.,
and E.

* Update this document to reflect the BioC version to be released (i.e.
  by replacing all occurences of `3.6` and `RELEASE_3_6` with appropriate
  version). This will avoid potentially disastrous mistakes when
  copying/pasting/executing commands from this file.

* Choose a machine with enough disk space to clone all the software and
  experiment packages (total size of all the clones is about 90G as of
  Oct 24, 2017). Also make sure to pick up a machine that has fast and
  reliable internet access.

* Make sure to use the `-A` flag to enable forwarding of the authentication
  agent connection when you `ssh` to the machine e.g.:

      ssh -A hpages@malbec1.bioconductor.org

* Clone (or update) the BBS git repo:

      # clone
      git clone https://github.com/Bioconductor/BBS
      # update
      cd ~/BBS
      git pull

* Create the `git.bioconductor.org` folder:

      mkdir git.bioconductor.org

* Populate `git.bioconductor.org` with clones of the `manifest` and
  all packages repos. This takes about 3h so is worth doing in advance
  e.g. 2 days before the release. It will save time when doing C. and D.
  below on the day prior to the release:

      export BBS_HOME="$HOME/BBS"
      export PYTHONPATH="$BBS_HOME/bbs"
      cd ~/git.bioconductor.org

      $BBS_HOME/utils/update_bioc_git_repos.py manifest RELEASE_3_6

      # takes approx. 1h10
      $BBS_HOME/utils/update_bioc_git_repos.py software master

      # takes approx. 1h45
      $BBS_HOME/utils/update_bioc_git_repos.py data-experiment master

* Make sure you can push changes to the BioC git server (at
  git.bioconductor.org):

      # check config file
      cat ~/.gitconfig

      # make any necessary adjustment with
      git config --global user.email "you@example.com"
      git config --global user.name "Your Name"

      # also make sure to set push.default to matching      
      git config --global push.default matching

      # check config file again
      cat ~/.gitconfig

      # try to push
      cd ~/git.bioconductor.org/software/affy
      git push  # should display 'Everything up-to-date'

* Find (and fix) packages with problematic versions:

      # software packages
      cd ~/git.bioconductor.org/software
      ~/BBS/utils/bump_pkg_versions.sh bad

      # data-experiment packages
      cd ~/git.bioconductor.org/data-experiment
      ~/BBS/utils/bump_pkg_versions.sh bad


## C. Version bumps and branch creation for software packages

Perform these steps on the day prior to the release. They must be completed
before the software builds get kicked off (see **A. Introduction**). The full
procedure should take about 3 hours. Make sure to reserve enough time.

### C1. Ask people to stop committing/pushing changes to the BioC git server

Before you start announce or ask a team member to announce on the
bioc-devel mailing list that people should stop committing/pushing
changes to the BioC git server (git.bioconductor.org) for the next couple
of hours.

### C2. Login to the machine where you've performed the preliminary steps

Make sure to use the `-A` flag to enable forwarding of the authentication
agent connection e.g.:

    ssh -A hpages@malbec1.bioconductor.org

See **B. Preliminary steps** above for the details.

### C3. Checkout/update the `RELEASE_3_6` branch of the `manifest` repo

    cd ~/git.bioconductor.org/manifest
    git checkout RELEASE_3_6
    git pull
    git branch
    git status

### C4. Set the `MANIFEST_FILE` environment variable

Set it to the manifest file for software packages. This must be the file
from the `RELEASE_3_6` branch of the `manifest` repo:

    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/software.txt"

### C5. Go to the `~/git.bioconductor.org/software/` folder

    cd ~/git.bioconductor.org/software

Steps C6-C12 below must be performed from this folder

### C6. Make sure all package git clones are up-to-date

The `~/git.bioconductor.org/software` folder should already contain the git
clones of all the software packages that are listed in the `RELEASE_3_6`
manifest (see **B. Preliminary steps** above). Note that all the git clones
should be on the **`master`** branch!

Update the git clones of all the packages listed in `$MANIFEST_FILE` with:

    export BBS_HOME="$HOME/BBS"
    export PYTHONPATH="$BBS_HOME/bbs"
    cd ~/git.bioconductor.org/software

    $BBS_HOME/utils/update_bioc_git_repos.py

### C7. First version bump (to even y)

This will modify the DESCRIPTION files only. It won't commit anything.

    cd ~/git.bioconductor.org/software

    # dry-run
    ~/BBS/utils/bump_pkg_versions.sh test even

    # if everything looks good
    ~/BBS/utils/bump_pkg_versions.sh even

    # remove the DESCRIPTION.original files
    ~/BBS/utils/bump_pkg_versions.sh clean

### C8. Commit first version bump

    commit_msg="bump x.y.z versions to even y prior to creation of RELEASE_3_6 branch"
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`
    cd ~/git.bioconductor.org/software

    # stage DESCRIPTION for commit
    for pkg in $pkgs_in_manifest; do
      echo ">>> 'git add DESCRIPTION' for package $pkg"
      git -C $pkg add DESCRIPTION
    done

    # dry-run commit
    for pkg in $pkgs_in_manifest; do
      echo ">>> commit version bump for package $pkg (dry-run)"
      git -C $pkg commit --dry-run -m "$commit_msg"
    done

    # if everything looks good
    for pkg in $pkgs_in_manifest; do
      echo ">>> commit version bump for package $pkg"
      git -C $pkg commit -m "$commit_msg"
    done

    # check last commit
    for pkg in $pkgs_in_manifest; do
      echo ">>> last commit for package $pkg"
      git -C $pkg log -n 1
    done
    
### C9. Branch creation

    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`
    cd ~/git.bioconductor.org/software

    # create the RELEASE_3_6 branch and change back to master
    for pkg in $pkgs_in_manifest; do
      echo ">>> create RELEASE_3_6 branch for package $pkg"
      git -C $pkg checkout -b RELEASE_3_6
      git -C $pkg checkout master
    done

### C10. Second version bump (to odd y)

This will modify the DESCRIPTION files only. It won't commit anything.

    cd ~/git.bioconductor.org/software

    # dry-run
    ~/BBS/utils/bump_pkg_versions.sh test odd

    # if everything looks good
    ~/BBS/utils/bump_pkg_versions.sh odd

    # remove the DESCRIPTION.original files
    ~/BBS/utils/bump_pkg_versions.sh clean

### C11. Commit second version bump

Same as step C8 above EXCEPT that commit message now is:

    commit_msg="bump x.y.z versions to odd y after creation of RELEASE_3_6 branch"

### C12. Push all the changes

    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`
    cd ~/git.bioconductor.org/software

    # dry-run push
    for pkg in $pkgs_in_manifest; do
      echo ">>> push all changes for package $pkg (dry-run)"
      git -C $pkg push --all --dry-run
    done

    # if everything looks good
    for pkg in $pkgs_in_manifest; do
      echo ">>> push all changes for package $pkg"
      git -C $pkg push --all
    done


## D. Version bumps and branch creation for data-experiment packages


## E. Finishing up

### E1. Enable push access to new `RELEASE_3_6` branch

This is done by editing the `conf/packages.conf` file in the `gitolite-admin`
repo (`git clone git@git.bioconductor.org:gitolite-admin`). Ask a team member
that is familiar with gitolite (Nitesh or Martin at the moment) to help with
this.

### E2. Tell people that committing/pushing to the BioC git server can resume

Announce or ask a team member to announce on the bioc-devel mailing list
that committing/pushing changes to the BioC git server (git.bioconductor.org)
can resume.

### E3. Switch `BBS_BIOC_GIT_BRANCH` from `master` to `RELEASE_3_6` on main BioC 3.6 builder

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

