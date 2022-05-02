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

R Windows binary:

  http://cran.r-project.org/bin/windows/base/

R Mac binary:

  http://cran.r-project.org/bin/macosx/

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

- Start building annotations (update R on the annotation EC2 instance)

- Update AnnotationForge and GenomeInfoDbData data files in preparation for nonstandard
  orgdb generation

- db0 packages posted to the devel repo

- Draft release schedule.

- Divide package ranges

- Start contacting maintainers about errors including bad NEWS files

- Create slack channel on dev-team slack

- Announce new package submission deadline

- Announce release schedule

- OrgDb and TxDb packages posted to the devel repo

- After OrgDb and TxDb are in devel repo, add to annotationhub

<a name="fourweeks"></a>
## Four weeks before the release:

- Announce deprecated / defunct packages

- Announce contributed annotation deadline

- Update GenmeInfoDb mapping table between UCSC and ensembl

<a name="threeweeks"></a>
## Three weeks before the release:

- The day before we stop the release builds, update remove-packages.md in the
  current release, e.g., 3.5.

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

- Install latest biocViews on biocpush account on to-be-release master builder.

- Create the manifest files for new devel and remove the deprecated packages
  BEFORE the first build.

- Remove packages from package.conf that have been defunct and removed from
  last release

- Start setting up new devel builders and repositories.

  Make sure that the R that runs as biocpush is current, has the
  most current biocViews and that 'knitcitations' is installed.

  Note about Simlinks to old devel:

  Until the next devel builds are running, we want symlinks pointing to the old
  devel builds so that the BiocManager package will work. This includes the
  software, data/annotation, and data/experiment repositories.  Remove these
  symlinks when the builds start running.

- Add links to checkResults page for new devel builds

- Confirm build report for new devel builds is intact

- Think about chaning BiocManager and the /developers/howto/useDevel web
  page. Modify any R/BioC versions if necessary.

- Update AMI and docker for the release being frozen, e.g., 3.5. Do this
  before we branch so r-release is still pointing at 3.5 instead of 3.6.

- Update NEWS files

<a name="oneweek"></a>
## One week before the release:

- Packages and workflows clean of errors and warnings
- Check master has enough room for release and create archieve on S3 if necessary
   See  [S3_website](https://github.com/Bioconductor/AWS_management/blob/master/docs/S3_website.md)

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

- BiocManager: Update R version dependency in devel version of BiocVersion.

- Run the builds ...

- Run a script to generate recent NEWS for all packages, to be included
  in the release announcement. (biocViews:::getPackageNEWS.R()).
  Verify that there are no <NA>s in output. Collate package descriptions
  with biocViews:::getPackageDescriptions().

<a name="d"></a>
## Release day (D):

- bioconductor.org/config.yaml

  Update config.yaml in the root of the bioconductor.org working copy and
  change values as indicated in the comments. This will (among other things),
  automatically update the website symlinks ("release" and "devel") under
  /packages. NOTE: If there is no annotation branch, that line under
  'devel_repos' must be commented out; if any of annotation, experiment data or
  software are not available (and a simlink makes them unavailable) the script
  will break and landing pages will not be generated. If using symlinks, mark as
  unavailable or else will destroy symlinked directory!

  After a release you should let the no-longer-release version build one last
  time so package landing pages won't say "release version".

- rsync on master

  UPDATE the /etc/rsyncd.conf on master.bioconductor.org and
  restart rsync.

      sudo systemctl restart rsync

  Test rsync is still working as expected with commands from:
  http://www.bioconductor.org/about/mirrors/mirror-how-to/.

- mirrors/enable archiving for bioc in apache config

  The mirror instructions on the website will be updated
  automatically when config.yaml is updated.

  The apache config files need to updated by hand. Add a new
  (copy-paste) section at the top for the new release number in
  these 2 files:

    /etc/apache2/sites-available/000-default.conf
    /etc/apache2/sites-available/default-ssl.conf

  Note: couldn't hurt to restart apache server
  
      sudo service apache2 restart 

  Test the mirrors with commands from:
  http://www.bioconductor.org/about/mirrors/mirror-how-to/.
  In a test directory the following should produce correct results
    `rsync -zrtlv --delete master.bioconductor.org::devel/bioc .` 
    `rsync -zrtlv --delete master.bioconductor.org::release/bioc .` 


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

  -- Add "Disallow: /packages/XX/" to the web site's robots.txt file
     where XX is the new devel version (one higher than the version)
     that was just released.  (on master)

  -- Update http://bioconductor.org/install/ for BiocManager

- BiocManager::install() sanity check

  Was BiocManager installed / updated properly? With a fresh R devel and
  release

      install.packages("BiocManager")

- Finalize release announcement

  -- compare number of packages in announcement with manifest file

- Once the build report posts and products are pushed to master
  confirm landing pages have updated versions

- Announce the release

- Tweet a link to the release announcement

- Update Wikipedia page for Bioconductor

- Go for a beer.

<a name="d+"></a>
## Week after the Release (D+):

- Confirm Archive/ folder is working for new release.
  The relevant script is BBS/utils/list.old.packages.R
  which depends on BiocManager to determine if
  archiving should happen. Example location to look
  `biocpush@nebbiolo1:~$ ls PACKAGES/3.15/bioc/src/contrib/Archive/`

- Build AMIs for new release and devel

- Build dockers for new release and devel

- Update chef recipes

- Update SPB and clean sqlite file

- ID packages for deprecation

- Update static data in Bioconductor packages GenomeInfoDB and UniProt.ws
  Update GenomeInfoDB/inst/extdata/dataFiles/genomeMappingTbl.csv mapping table
  for any new ensembl or UCSC entries.
  https://genome.ucsc.edu/FAQ/FAQreleases.html
  http://useast.ensembl.org/info/website/archives/assembly.html
  Update UniProt.ws/inst/extdata/  keytypes.txt and speclist.txt
  Will need to checkout github branch remove_static_files branch for code to
  generate these files (in  R/ code).

- reach out to packages with malformated NEWS files for correction

- Update Bioconductor GitHub repositories

  Push packages with "core-package tag from git.bioconductor.org to github.
  Check if any packages have commits to just github (not sure how to fix?). If
  all looks ok, sync from git.bioconductor.org to github.
