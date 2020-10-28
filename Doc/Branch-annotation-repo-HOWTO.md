# Branch annotations

The document describes how to branch the annotation repository for a 
new release. This can be done the day of the release or several days after.

Before branching, Check and make sure there is enough room on master for the 
annotations.  If there isn't enough room follow the guidelines for moving
old [Bioconductor releases into S3](https://github.com/Bioconductor/AWS_management/blob/master/docs/S3_website.md)
As of release 3.11 Annotations are around 83G. 

These instructions use BioC 3.7 as the new devel version and malbec2
as the devel master builder.

A. Set up malbec2

1. Create new annotation repo on devel master builder (malbec2) 

    ssh biocadmin@malbec2.bioconductor.org
    cd ~/PACKAGES/3.7/data
    mkdir annotation

2. rsync annotations from current release

Dry run first.
NOTE the trailing slash and dot '.'.

    From malbec1 to malbec2 (logged into malbec2):
    cd ~/PACKAGES/3.7/data/annotation
    rsync --dry-run -ave ssh biocadmin@malbec1:PACKAGES/3.6/data/annotation/ .

    From malbec1 to malbec2 (logged into malbec1):
    cd ~/PACKAGES/3.7/data/annotation
    rsync --dry-run -ave ssh ~/PACKAGES/3.6/data/annotation
    biocadmin@malbec2:PACKAGES/3.7/data/annotation/

3. Remove symlinks for old R versions for windows and mac

There may be symlinks in the windows and macosx folders. These will only be
present when the new version of BioC uses a new version of R which happens
every other version of BioC. If they are present, they will look something like
this:

    ~/PACKAGES/3.7/data/annotation/bin/windows/contrib/3.5 -> 3.4
    ~/PACKAGES/3.7/data/annotation/bin/macosx/el-capitan/contrib/3.5 -> 3.4

Remove the symlinks and rename the folder with content to the version of 
R being used by devel e.g., 

    rm ~/PACKAGES/3.7/data/annotation/bin/windows/contrib/3.5 -> 3.4
    mv 3.4 3.5

The PACKAGES and PACKAGES.gz files are empty. They are needed for
install.packages() even though we don't have binaries for annotations.

* Rerun rsync

    rsync --dry-run -ave ssh biocadmin@malbec1:PACKAGES/3.6/data/annotation/ .

A rerun of the rsync command should only show changes in the files we
just edited.

B. Set up master.bioconductor.org

1. Log on master as webadmin

    ssh webadmin@master.biocondcutor.org
    cd /extra/www/bioc/packages/3.7/data/annotation

Products are sent to master from both malbec2 and staging.bioconductor.org.
Because of this, the rsync from malbec2 to master is not from the top level;
we want to leave the products deposited by staging.bioconductor.org untouched.

2. Remove symlink and create empty annotation folder

There will likely be a simlink at 

    /extra/www/bioc/packages/3.7/data/annotation

pointing to the 3.6 annotation repo. Remove the symlink:

    rm annotation

Create a new annotation folder

    mkdir annotation

C. Back to malbec2 to run the scripts

1. Remove any deprecated packages from the 3.6 annotation repo.

2. Update and run cronjob by hand (should be commented out). 

  Symlink must be gone on master before running this!

  Run the crontab entry by hand. Monitor ~/cron.log/3.7/propagate-data-annotation-* log
  file.

3. Test BiocManager::install() to see if it finds the new repo.

D. Update bioconductor.org/config.yaml to build landing pages for 3.7.
   Uncomment 'data/annotation':

    devel_repos:
    - "bioc"
    - "data/experiment"
    - "data/annotation"
