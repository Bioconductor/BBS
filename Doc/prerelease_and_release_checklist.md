# Pre-release Activities 

## Table of Contents
- [Testing R versions](#rversions)
- [Six weeks before the release](#sixweeks)
- [Four weeks before the release](#fourweeks)
- [Three weeks before the release](#threeweeks)
- [Two weeks before the release](#twoweeks)
- [One week before the release](#oneweek)
- [Day before we branch](#d-2)
- [Day we branch](#d-1)
- [Release day](#d)
- [Week after the Release](#d+)

<a name="rversions"></a>
## R versions

Prior to the release we should be testing the latest binary packages with
the upcoming release with R RC or R PRERELEASE on a clean Windows and Mac machine.
It's important to use these binary R installations:

Windows:

  http://cran.fhcrc.org/bin/windows/base/

Mac:

  http://cran.fhcrc.org/bin/macosx/

A "clean" machine means, on Windows, no Rtools, LaTeX, etc.
On Mac it means no Xcode and do not use Simon U's builds, use the one above.

We should test with both the GUI and command-line versions of R.
One specific thing to test is that the impute, DNAcopy, and NuPoP
packages can be loaded on a Mac in the R GUI. If they can't, the
links in the .so files are not being fixed properly.

During this process, we want to watch every day for new R versions
(RC, prerelease,etc) and install them on our devel build systems.


Some important operations that need to happen before a BioC release,
in _this_ order

<a name="sixweeks"></a>
## Six weeks before the release:

- Draft release schedule.

- Divide package ranges

- Start contacting maintainers about errors

<a name="fourweeks"></a>
## Four weeks before the release:

- Announce release schedule

- Announce deprecated / defunct packages

- Announce contributed annotation deadline

- Start building workflows on devel

- Start building annotations

<a name="threeweeks"></a>
## Three weeks before the release:

- The day before we stop the release builds, update remove-packages.md in the 
  current release, e.g., 3.5.

- db0 packages posted to the devel repo

- Deadline for new package submissions

<a name="twoweeks"></a>
## Two weeks before the release:

- Disable commits to old release branch

- After the last build report for old relase is online, stop the old release builds.

  HISTORICAL NOTE: After stopping release builds, on all Mac build machines, point
  the "Current" symlink in /Library/Frameworks/R.framework/Versions to the
  new DEVEL version of R. Otherwise we will be producing broken binaries!
  (Not applicable if only one build is running on each Mac machine, as should
  be the case from BioC 2.9 onward; but we do want to make sure that there is
  only ever one version of R installed on these Mac build machines.)

- Update https://bioconductor.org/checkResults/ by moving the old release to
  the top of the "Archived results for past release" section.

- Feature freeze for the to-be-release version. No API changes, no new
  packages added to the roster.

- All contributed annotation packages added to the to-be-release repo.

- Install latest biocViews on biocadmin account on to-be-release master builder.

- Create the software and experimental data manifest files for new devel

- Start setting up new devel builders and repositories.

  Make sure that the R that runs as biocadmin has the 'knitcitations' package
  installed.

  Note about Simlinks to old devel:

  Until the next devel builds are running, we want symlinks pointing to the old
  devel builds so that the BiocInstaller package will work. This includes the
  software, data/annotation, and data/experiment repositories.  Remove these
  symlinks when the builds start running.

- Add links to checkResults page for new devel builds

- Confirm build report for new devel builds is intact

- Think about chaning BiocInstaller and the /developers/howto/useDevel web
  page. Modify any R/BioC versions if necessary.

- Update AMI and docker for the release being frozen, e.g., 3.5. Do this
  before we branch so r-release is still pointing at 3.5 instead of 3.6.

- OrgDb and TxDb packages posted to the devel repo

- Update NEWS files

<a name="oneweek"></a>
## One week before the release:

- Deprecated packages

  Remove from the manifest of the to-be-released version of BioC all packages
  which were deprecated in a previous release cycle 
  (grep -i deprecated */R/zzz.R).

- Add OrgDb and TxDb packages to AnnotationHub

- Deadline for NEWS files to be updated

- Packages and workflows clean of errors and warnings

<a name="d-2"></a>
## Day before we branch (D-2):

- Manifest file for the release branch

  Create the manifest file for the release branch, e.g., "RELEASE_3_6".
  Up to this point and until we branch tomorrow, both 3.6 and the new devel 
  should be using the "master" manifest.

  NOTE: Branch creation must be done after all packages for 3.6 have been 
  added to the manifest.

  NOTE: As part of the bump and branch process tomorrow, the
  BBS_BIOC_MANIFEST_GIT_BRANCH variable on the release builder will be
  modified to point to the correct manifest.
  This variable is defined in the config.sh and config.bat files located in the
  ~biocbuild/BBS/3.6/bioc/ and ~biocbuild/BBS/3.6/data-experiment/ folders.
  For now, packages must still be built off their master branch so do NOT 
  touch the BBS_BIOC_GIT_BRANCH variable!

- Modify the /about/removed-packages/. Link to the last good landing page
  of each package.

<a name="d-1"></a>
## Day we branch (D-1):

- Send mail to bioc-devel to ask people to stop commits until
  further notice so we can create the 3.6 branches (software and data
  experiment). The bump and branch took about 2 hours.

- Bump versions and create BioC 3.6 release branch
  https://github.com/Bioconductor/BBS/blob/master/Doc/Version-bump-and-branch-creation-HOWTO.md

- Confirm MEAT0 is pointed at the correct manifest for the
  3.6 and 3.7 builds.

- Update gitolite authorization files to give maintainers R/W
  access to their package in the new branch.

- Confirm new branch can be checkout from a location other than
  the machine used to create the branch (i.e., your local system).

- Announce the creation of the 3.6 branch and that commits can
  resume. Clarify the difference between the new branch and master.

- Confirm defunct packages have been removed from the 3.7 manifest.

- BiocInstaller

  -- If a new R is released today, modify the biocLite.R script (which lives 
     in the BiocInstaller package in inst/scripts)to make sure the next devel 
     version of R is properly identified.

  -- Change R/zzz.R of the BiocInstaller package to indicate new 
     BioC version number.

  -- Change DESCRIPTION file of BiocInstaller to depend on latest devel
     version of R (if that is appropriate).

  -- Modify inst/scripts/BiocInstaller.dcf to change relavant variables.

  OLD NOTE: Make sure that the BiocInstaller package is manually pushed out
  to the new devel repos. It has to be manually pushed out because
  otherwise it will fail its unit test because it is testing to make
  sure that BiocInstaller is in the devel repos. A chicken-and-egg situation.

  NEW NOTE: I'm not sure the unit test refered to above still exits.
  Reguardless, the key idea is that the correct version of BiocInstaller MUST 
  be on master by the time the release is announced. If this is not the case, 
  users tying to biocLite() with the new devel will not get the correct 
  packages. BiocInstaller can get to master by successfully completing a
  build cycle or by manually droping the tarball in 
  /home/biocadmin/PACKAGES/3.7/bioc/src/contrib.
  The permissions on the tarball must be correct and there can only be one 
  version of the tarball in the repository.

- Run the builds ...

- Run a script to generate recent NEWS for all packages, to be included
  in the release announcement. (biocViews:::getPackageNEWS.R()).
  Verify that there are no <NA>s in output. Collate package descriptions
  with biocViews:::getPackageDescriptions().

- Edit inst/scripts/BiocInstaller.dcf in BiocInstaller to change
  relevant variables. This will automatically push soon after being
  committed.


<a name="d"></a>
## Release day (D):

- bioconductor.org/config.yaml

  Update config.yaml in the root of the bioconductor.org working copy and
  change values as indicated in the comments. This will (among other things),
  automatically update the website symlinks ("release" and "devel") under
  /packages. NOTE: If there is no annotation branch, that line under
  'devel_repos' must be commented out; if any of annotation, experiment data or
  software are not available (and a simlink makes them unavailable) the script
  will break and landing pages will not be generated.
 
  After a release you should let the no-longer-release version build one last
  time so package landing pages won't say "release version" (and also so the
  BiocInstaller landing page will reflect the version of the package that you
  will push out manually--see the "Modify BiocInstaller..." step below).

- rsync on master

  UPDATE the /etc/rsyncd.conf on master.bioconductor.org. 
  Test rsync is still working as expected with commands from:
  http://www.bioconductor.org/about/mirrors/mirror-how-to/.

- mirrors

  The mirror instructions on the website will be updated 
  automatically when config.yaml is updated.
 
  Test the mirrors with commands from:
  http://www.bioconductor.org/about/mirrors/mirror-how-to/.

- Update checkResults page and symlinks ("release" and "devel") under
  checkResults/.

- Website updates:
  -- Update build report index page and symlinks; remove "devel"
     background image from report.css (if there is one).

  -- Put release announcement on web and add to pages which contain
     links to all release announcements (/about/release-announcements
     and **/layouts/_release_announcements.html**). Put today's
     date at the top of the web version of the release
     announcement.
 
  -- Add the last release version to the list of 'Previous Versions'
     (layouts/_bioc_older_packages.html). **DON'T FORGET THIS!**

  -- Update link to release announcement on main index page

  -- Update number of packages on main index page

  -- Update symlinks ("release" and "devel") under /checkReports

  -- Add "Disallow: /packages/XX/" to the web site's robots.txt file
     where XX is the new devel version (one higher than the version)
     that was just released.

- biocLite() sanity check

  Was biocLite.R updated properly? With a fresh R devel (make sure
  BiocInstaller is not installed), source biocLite.R and make sure the
  appropriate version is installed. Of course, do the same with release.  **
  really do this! with R-devel too if appropriate! **

- Finalize release announcement

  -- compare number of packages in announcement with manifest file

- Once the build report posts and products are pushed to master
  confirm landing pages have updated versions 

- Announce the release

- Tweet a link to the release announcement

- Update Wikipedia page for Bioconductor

- Update RSS feed

- Go for a beer.

<a name="d+"></a>
## Week after the Release (D+):

- Branch annotations

- Confirm Archive/ folder is working for new release

- Build AMIs for new release and devel

- Build dockers for new release and devel

- Update chef recipes

- Update SPB and clean sqlite file

- ID packages for deprecation in BioC 3.7

- Update R for biocadmin on both master Linux builders

- Update Bioconductor GitHub repositories

  Push packages with "core-package tag from git.bioconductor.org to github.
  Check if any packages have commits to just github (not sure how to fix?). If
  all looks ok, sync from git.bioconductor.org to github.
