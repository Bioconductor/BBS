# Version-bump-and-branch-creation-HOWTO


## A. Introduction

On the day prior to the release, we need to make and push the following
changes to all the packages that go in the release, **in this order**:

* **First version bump**: bump x.y.z version to even y **in the `master` branch**
* **Branch creation**: create the release branch
* **Second version bump**: bump x.y.z version to odd y **in the `master` branch**

For example, for the BioC 3.9 release, we need to do this for all the
packages listed in the `software.txt`, `data-experiment.txt`, and
`workflows.txt` files of the `RELEASE_3_9` branch of the `manifest`
repo.

Note that there is one exception: the BiocVersion package (software package).
Section **C.** below provides more information about this.

This needs to be done before the BioC 3.9 builds start for software,
workflows and data-experiment packages.

Look for the prerun jobs in the crontab for the `biocbuild` user on the main
BioC 3.9 builder to get the times the software and data-experiment builds get
kicked off. Make sure to check the crontab again a couple of days before the
release as we sometimes make small adjustments to the crontabs on the build
machines.  Also be sure to translate to your local time if you are not on the
East Coast.


## B. Preliminary steps

These steps should be performed typically a couple of days before the steps
in sections **C.**, **D.**, and **E.**.

* Update this document to reflect the BioC version to be released i.e.
  replace all occurrences of `3.9` and `RELEASE_3_9` with appropriate
  version. This will avoid potentially disastrous mistakes when
  copying/pasting/executing commands from this document.

* Choose a Linux machine with enough disk space to clone all the software,
  data-experiment, and workflow packages (as of May 2, 2019, the total size
  of all the package clones is about 108G). The machine needs to have the
  `git` client and Python. The procedure described here doesn't require
  `sudo` privileges.
  Make sure to pick up a machine that has fast and reliable internet access.
  The Linux build machines are a good choice. If you want to use one of
  them, use your personal account or the `biocadmin` account. Do NOT use
  the `biocbuild` account to not interfere with the builds. Using a Mac
  server might work but was not tested.

* Make sure to use the `-A` flag to enable forwarding of the authentication
  agent connection when you `ssh` to the machine e.g.:

      ssh -A hpages@malbec1.bioconductor.org

* Clone (or update) the `BBS` git repo:

      # clone
      git clone https://github.com/Bioconductor/BBS
      # update
      cd ~/BBS
      git pull

* Create the `git.bioconductor.org` folder:

      mkdir git.bioconductor.org

* Populate `git.bioconductor.org` with git clones of the `manifest` repo
  and all the package repos (software, data-experiment, and workflows).
  This takes more than 3h so is worth doing in advance e.g. a couple of days
  before the release. It will save time when performing the steps described
  in sections **C.**, **D.**, and **E.** below on the day prior to the release.

      export BBS_HOME="$HOME/BBS"

      # clone `manifest` repo
      $BBS_HOME/utils/update_bioc_git_repos.py manifest RELEASE_3_9

      # clone software package repos (takes approx. 1h20)
      time $BBS_HOME/utils/update_bioc_git_repos.py software master RELEASE_3_9

      # clone data-experiment package repos (takes approx. 1h50)
      time $BBS_HOME/utils/update_bioc_git_repos.py data-experiment master RELEASE_3_9

      # clone workflow package repos (takes approx. 4 min)
      time $BBS_HOME/utils/update_bioc_git_repos.py workflows master RELEASE_3_9

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
      $BBS_HOME/utils/bump_pkg_versions.sh bad

      # data-experiment packages
      cd ~/git.bioconductor.org/data-experiment
      $BBS_HOME/utils/bump_pkg_versions.sh bad

      # workflow packages
      cd ~/git.bioconductor.org/workflows
      $BBS_HOME/utils/bump_pkg_versions.sh bad

* Clone (or update) the `bioc_git_transition` git repo:

      # clone
      git clone https://github.com/Bioconductor/bioc_git_transition
      # update
      cd ~/bioc_git_transition
      git pull

* Find packages with duplicate commits

    Historically the GIT-SVN mirror was the primary source of duplicate commits.
    Since the transition to git, we should not be seeing many new duplicates.
    Additionally, we've implemented a gitolite hook to prevent any new
    duplicate commits from getting through. For these reasons, this check for
    duplicates is becoming obsolete and can probably be removed at the next
    release in Spring 2019.
    ```
    # Local copy of bioc_git_transition
    export BIOC_GIT_TRANSITION="$HOME/bioc_git_transition"
    
    # software packages
    export WORKING_DIR="$HOME/git.bioconductor.org/software"
    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/software.txt"
    cd $WORKING_DIR
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # Check last 10 commits in each package
    for pkg in $pkgs_in_manifest; do
        echo ""
        echo ">>> check $pkg package for duplicate commits"
        python $BIOC_GIT_TRANSITION/misc/detect_duplicate_commits.py $pkg 10
    done > duplicatecommits.out 2>&1
    ```

* Anyone involved in the "bump and branch" procedure should temporarily
  be added to the `admin` group in `gitolite-admin/conf/gitolite.conf`.
  Membership in this group enables the creation of a new branch and
  _pushing_ to any branch regardless of inactivated (commented out) lines
  in `gitolite-admin/conf/packages.conf`.


## C. Version bumps and branch creation for software packages

Perform these steps on the day prior to the release. They must be completed
before the software builds get kicked off (see **A. Introduction**). The full
procedure should take about 2.5 hours. Make sure to reserve enough time.

NOTE: BiocVersion needs special treatment because its version must always
match the version of the branch it's in. This means that it only needs the
second bump. So it will remain at `3.9.*` in the RELEASE_3_9 branch and will
be set to `3.10.0` in the new master branch.

### C1. Ask people to stop committing/pushing changes to the BioC git server

Announce or ask a team member to announce on the bioc-devel mailing list
that people must stop committing/pushing changes to the BioC git server
(git.bioconductor.org) for the next 2.5 hours.

### C2. Modify packages.conf to block all commits

The `RELEASE_3_8` lines in `gitolite-admin/conf/packages.conf` were commented
out when the release builds were frozen. At this point, only the `master`
lines are still active. 

Deactivate all push access by commenting out the `master` lines in
`gitolite-admin/conf/packages.conf`.

NOTE: Do not change the branch from RELEASE_3_7 to RELEASE_3_8, it is
not a good solution. Maintainers now will be able to push their own
RELEASE_3_8 branch before we are able to create it at release
time. This issue reflects the issue
https://stat.ethz.ch/pipermail/bioc-devel/2019-May/015048.html.

Using vim, it is possible with a one liner,

       :g/RW master/s/^/#

Once `packages.conf` is updated, push to `gitolite-admin` on the git server
to make the changes effective.

### C3. Login to the machine where you've performed the preliminary steps

Make sure to use the `-A` flag to enable forwarding of the authentication
agent connection e.g.:

    ssh -A hpages@malbec1.bioconductor.org

See **B. Preliminary steps** above for the details.

### C4. Checkout/update the `RELEASE_3_9` branch of the `manifest` repo

    cd ~/git.bioconductor.org/manifest
    git pull --all
    git checkout RELEASE_3_9
    git branch
    git status

### C5. Set the `WORKING_DIR` and `MANIFEST_FILE` environment variables

Point `WORKING_DIR` to the folder containing the software packages:

    export WORKING_DIR="$HOME/git.bioconductor.org/software"

All the remaining steps in section **C.** must be performed from within
this folder.

Point `MANIFEST_FILE` to the manifest file for software packages. This must
be the file from the `RELEASE_3_9` branch of the `manifest` repo:

    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/software.txt"

### C6. Make sure all package git clones are up-to-date

Go to the working folder:

    cd $WORKING_DIR

This folder should already contain the git clones of all the
software packages that are listed in the `RELEASE_3_9` manifest
(see **B. Preliminary steps** above). Note that all the git clones
should be on the **`master`** branch!

Update the git clones of all the packages listed in `$MANIFEST_FILE`. This
should take 15-20 minutes:

    export BBS_HOME="$HOME/BBS"
    time $BBS_HOME/utils/update_bioc_git_repos.py

### C7. First version bump (to even y)

This will modify the DESCRIPTION files only. It won't commit anything.

    cd $WORKING_DIR

    # dry-run
    $BBS_HOME/utils/bump_pkg_versions.sh test even

    # if everything looks OK
    $BBS_HOME/utils/bump_pkg_versions.sh even

    # ** IMPORTANT **
    # Manually correct the version in the BiocVersion DESCRIPTION so it
    # remains at 3.9.0.

    # remove the DESCRIPTION.original files
    $BBS_HOME/utils/bump_pkg_versions.sh clean

    # check 'y' is even and not greater than 99
    export BIOC_GIT_TRANSITION="$HOME/bioc_git_transition"
    python $BIOC_GIT_TRANSITION/misc/detect_bad_version.py . even

### C8. Commit first version bump

    commit_msg="bump x.y.z version to even y prior to creation of RELEASE_3_9 branch"

    cd $WORKING_DIR
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # stage DESCRIPTION for commit
    time for pkg in $pkgs_in_manifest; do
      echo ""
      echo ">>> 'git add DESCRIPTION' for package $pkg"
      git -C $pkg add DESCRIPTION
    done > stage.out

    # commit
    time for pkg in $pkgs_in_manifest; do
      echo ""
      echo ">>> commit version bump for package $pkg"
      git -C $pkg commit -m "$commit_msg"
    done > commit.out

    # check last commit
    for pkg in $pkgs_in_manifest; do
      echo ""
      echo ">>> last commit for package $pkg"
      git -C $pkg log -n 1
    done
 
### C9. Branch creation

    cd $WORKING_DIR
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # create the RELEASE_3_9 branch and change back to master
    time for pkg in $pkgs_in_manifest; do
      echo ""
      echo ">>> create RELEASE_3_9 branch for package $pkg"
      git -C $pkg checkout -b RELEASE_3_9
      git -C $pkg checkout master
    done > createbranch.out 2>&1

    # check existence of the new branch
    for pkg in $pkgs_in_manifest; do
      git -C $pkg branch -a | grep RELEASE_3_9
      if [ $? -ne 0 ]; then
        echo "ERROR: No RELEASE_3_9 branch in $pkg"
        break
      fi
    done

### C10. Second version bump (to odd y)

This will modify the DESCRIPTION files only. It won't commit anything.

    cd $WORKING_DIR

    # dry-run
    $BBS_HOME/utils/bump_pkg_versions.sh test odd

    # if everything looks OK
    $BBS_HOME/utils/bump_pkg_versions.sh odd

    # ** IMPORTANT **
    # Manually set the version in the BiocVersion DESCRIPTION to 3.10.0.
    # The BiocVersion package must be 3.10.0 in the master branch.

    # remove the DESCRIPTION.original files
    $BBS_HOME/utils/bump_pkg_versions.sh clean

    # check 'y' is odd and not greater than 99
    export BIOC_GIT_TRANSITION="$HOME/bioc_git_transition"
    python $BIOC_GIT_TRANSITION/misc/detect_bad_version.py . odd 

### C11. Commit second version bump

Same as step C8 above EXCEPT that commit message now is:

    commit_msg="bump x.y.z version to odd y after creation of RELEASE_3_9 branch"

### C12. Disable hooks

Log on to git.bioconductor.org as the `git` user.

- Comment out the hook lines in `packages.conf`.

- Remove the `pre-receive.h00-pre-receive-hook-software` file from the
  `hook/` directory in each package, e.g.,
  `/home/git/repositories/packages/<PACKAGE>.git/hooks`
    ```
    rm -rf ~/repositories/packages/*.git/hooks/pre-receive.h00-pre-receive-hook-software
    ```

### C13. Push all the changes

Last sanity check before pushing:

    cd <some package>
    ## master: This should show the even bump, followed by the odd bump
    git log master -n 2
    ## RELEASE_3_9: This should show the even bump only
    git log RELEASE_3_9 -n 1

Push:

    cd $WORKING_DIR
    pkgs_in_manifest=`grep 'Package: ' $MANIFEST_FILE | sed 's/Package: //g'`

    # dry-run push (takes 20-30 min, not worth it!)
    #for pkg in $pkgs_in_manifest; do
    #  echo ""
    #  echo ">>> pushing all changes for package $pkg (dry-run)"
    #  git -C $pkg push --all --dry-run
    #done

    # if everything looks OK (takes approx. 25 min)
    time for pkg in $pkgs_in_manifest; do
      echo ""
      echo ">>> pushing all changes for package $pkg"
      git -C $pkg push --all
    done > push.out 2>&1

Open `push.out` in an editor and search for errors. A typical error is
`Error: duplicate commits` (happened for affyPLM and Rdisop first time I
tested this). Report these errors to `gitolite` experts Nitesh and Martin.


## D. Version bumps and branch creation for data-experiment packages

Repeat steps C5 to C13 above **but for C5 define the environment variables
as follows**:

    export WORKING_DIR="$HOME/git.bioconductor.org/data-experiment"
    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/data-experiment.txt"

Approx. timings (on malbec1):

* **Commit first version bump**: 21 sec for `stage DESCRIPTION`, 41 sec
  for `commit`
* **Branch creation**: 40 sec
* **Commit second version bump**: < 1 sec for `stage DESCRIPTION`, 28 sec for `commit`
* **Push all the changes**: 43 min


## E. Version bumps and branch creation for workflow packages

Repeat steps C5 to C13 above **but for C5 define the environment variables
as follows**:

    export WORKING_DIR="$HOME/git.bioconductor.org/workflows"
    export MANIFEST_FILE="$HOME/git.bioconductor.org/manifest/workflows.txt"

Approx. timings (on malbec1):

* **Commit first version bump**: < 1 min
* **Branch creation**: < 10 sec
* **Commit second version bump**: < 10 sec
* **Push all the changes**: < 2 min


## F. Finishing up

### F1. Enable push access to new `RELEASE_3_9` branch

This is done by editing the `conf/packages.conf` file in the `gitolite-admin`
repo (`git clone git@git.bioconductor.org:gitolite-admin`). 

- If not done already, replace all instances of `RELEASE_3_8` with
`RELEASE_3_9`.

- Uncomment all `RELEASE_3_9` and `master` lines.

- Run `gitolite setup` from /home/git/repositories to re-enable the hooks.

- Test that a non-super user can push access is enabled. (Nitesh can do
this currently with ni41435 account, and the dummy package
BiocGenerics_test).

Check,

	git push
	git checkout RELEASE_3_9
	git pull

### F2. Tell people that committing/pushing to the BioC git server can resume

Announce or ask a team member to announce on the bioc-devel mailing list
that committing/pushing changes to the BioC git server (git.bioconductor.org)
can resume.

### F3. Switch `BBS_BIOC_GIT_BRANCH` from `master` to `RELEASE_3_9` on main BioC 3.9 builder

DON'T FORGET THIS STEP! Its purpose is to make the BioC 3.9 builds grab the
`RELEASE_3_9` branch of all packages instead of their `master` branch.

Login to the main BioC 3.9 builder as `biocbuild` and replace

    export BBS_BIOC_GIT_BRANCH="master"

with

    export BBS_BIOC_GIT_BRANCH="RELEASE_3_9"

in `~/BBS/3.9/config.sh`

Also replace

    set BBS_BIOC_GIT_BRANCH=master

with

    set BBS_BIOC_GIT_BRANCH=RELEASE_3_9

in `~/BBS/3.9/config.bat`

Then remove the `manifest` and `MEAT0` folders from `~/bbs-3.9-bioc/`,
`~/bbs-3.9-data-experiment/`, and `~/bbs-3.9-workflows/`. They'll get
automatically re-created and re-populated when the builds start.

### F4. Update all core bioconductor packages hosted on github/Bioconductor organization

The code to update all packages is in,
https://github.com/Bioconductor/GitContribution.git, in the branch
`core_team_package_to_github`, in the script
`update_packages.R`.

You need to set up your github account credentials(API key) for this
script to run (Nitesh/Martin have this setup on their machine
already).

The API keys need to be setup as options in the ~/.Rprofile,

	options(
		git_contributions_github_user="ntu***",
		git_contributions_github_auth=readLines("~/git0Auth.txt")
	)
	
The `git0Auth.txt` file can be obtained from the github
https://github.com/settings/tokens. This will work only if the user
has admin access to the Bioconductor organization on github.

The specific function which needs to be run is

	update_all_packages()
	
which runs, the function (this essentially does all the work).Be sure
to edit the release version in the function.
	
	clone_and_push_git_repo(package, release="RELEASE_3_9")

	
This function will push the `RELEASE_3_9` branch to github and sync
the packages on github.
