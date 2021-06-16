# Branch annotations

The document describes how to branch the annotation repository for a 
new release. This can be done the day of the release or several days after.

Before branching, Check and make sure there is enough room on master for the 
annotations.  If there isn't enough room follow the guidelines for moving
old [Bioconductor releases into S3](https://github.com/Bioconductor/AWS_management/blob/master/docs/S3_website.md)
As of release 3.13 Annotations are around 113G. 

These instructions use BioC 3.14 as the new devel version and nebbiolo2
as the devel master builder.

As of 3.14, the linux builders have moved to DFCI in Boston. Personal accounts
and the jump account should be set up for access.

A. Set up nebbiolo2

1. Create new annotation repo on devel master builder (nebbiolo2) 

    ssh to nebbiolo2 as biocpush user
    cd ~/PACKAGES/3.14/data
    mkdir annotation

2. rsync annotations from current release

Because 3.13 used RPCI mablec2 and 3.14 used DFCI nebbiolo2, we could only rsync
in one direction because of firewalls. It should work on either machine, in
either direction in the future if under the same firewall.

Dry run first.
NOTE the trailing slash and dot '.'.

    From malbec2 to nebbiolo2 (logged into malbec2):
    cd ~/PACKAGES/3.13/data/annotation
    rsync --dry-run -ave ssh . biocpush@nebbiolo2:PACKAGES/3.14/data/annotation/

Live Run if all looks correct

    rsync -ave ssh . biocpush@nebbiolo2:PACKAGES/3.14/data/annotation/


3. Remove symlinks for old R versions for windows and mac

There may be symlinks in the windows and macosx folders. These will only be
present when the new version of BioC uses a new version of R which happens
every other version of BioC. If they are present, they will look something like
this:

    ~/PACKAGES/3.7/data/annotation/bin/windows/contrib/3.5 -> 3.4
    ~/PACKAGES/3.7/data/annotation/bin/macosx/contrib/3.5 -> 3.4

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

    ssh ubuntu@master.biocondcutor.org
    sudo su - webadmin
    cd /extra/www/bioc/packages/3.14/data/annotation

Products are sent to master from both nebbiolo2 and staging.bioconductor.org.
Because of this, the rsync from nebbiolo2 to master is not from the top level;
we want to leave the products deposited by staging.bioconductor.org untouched.

2. Remove symlink and create empty annotation folder

There will likely be a simlink at 

    /extra/www/bioc/packages/3.14/data/annotation -> ../../3.13/data/annotation

pointing to the current release annotation repo. In recent years, the symlinks
have appeared underneath an already created annotation repostiory. The point is
to start with a non-linked empty annotation folder.  Remove annotation and recreate:

    rm annotation

Create a new annotation folder

    mkdir annotation


C. Back to nebbiolo2 to run the propagation scripts

1. Remove any deprecated packages from the 3.13 annotation repo that should not
be included in the devel 3.14 repo.

2. Update and run cronjob by hand (should be commented out). 

  Symlink must be gone on master before running this!!

  Run the crontab entry by hand. Monitor ~/cron.log/3.14/propagate-data-annotation-* log
  file.

3. Test BiocManager::install() to see if it finds the new repo. Try installing a
package that should be found and try installing a removed package that should
fail.

D. Update bioconductor.org/config.yaml to build landing pages for 3.14.
   Uncomment 'data/annotation':

    devel_repos:
    - "bioc"
    - "data/experiment"
    - "data/annotation"
