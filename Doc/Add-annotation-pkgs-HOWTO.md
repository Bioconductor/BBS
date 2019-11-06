# How to add annotation packages to builder <a name="top"/>

This document explains how to add packages to the builder, how to run the 
crontab job, and how to check that everything worked properly. This example 
demonstrates the steps using the Bioconductor 3.10 release.

### Table of Contents
+ [What should be added](#added)
+ [Running the crontab job](#crontab)
+ [Checking](#checking)

## What should be added <a name="added"/>

In order for the package to be built, the tarball for the package should be 
located in `/home/biocadmin/PACKAGES/3.10/data/annotation/src/crontrib/`. If 
there is an older version of the package located here it should be removed. Be 
sure to only remove versions that are getting replaced with a newer version 
because once they are removed it's very difficult to recover them.

## Running the crontab job <a name="crontab"/>

Once the correct version of the package is in 
`/home/biocadmin/PACKAGES/3.10/data/annotation/src/contrib` then the crontab job 
must be run so that the VIEWS are updated. This can be done doing the following 
steps.

**1. View the crontab job**

```sh
crontab -l
```

This command will give you a visual of the crontab job. The last line of the job 
should be commented out. This is the line to be edited.

**2. Edit and run the crontab job**

To open the crontab job so it can be edited can be done as such,

```sh
crontab -e
```

Then the last line should be uncommented and the next run time should be entered. 
It is important to remember the time format is in military time. For example, 
if it is currently 10:16, change the time to 10:18 just to be sure the time 
isn't going to change just as you are saving and closing the document.

After making the necessary time change, save and close the crontab job. Then 
when it turns to the time put in for the job, it will get run. 

**3. Check to be sure it's running**

To be sure the job is running, you can use the command

```sh
tail /home/biocadmin/crontab.log/3.10/propagate-data-annotation-20191028.log
```

where the date should be changed to the day that it is being run. 

**4. Comment crontab job**

Once the job is running it's important add back the comment that was removed. 
So use 

```sh
crontab -e

crontab -l
```

to edit the file and then to make sure the line is commented out.

## Checking <a name="checking"/> 

The job can take almost 3 hours to run but after it's finished there are a few 
ways to check to be sure everything worked properly.

* Immediately after, check the VIEWS file and/or try to install the new package.
* 30 minutes after, check the landing page of the new package.
* The day after, check the impact of the new annotation on the build report.

When checking a package that is being updated, the version number should be the 
newest version. When checking a new package, be sure that the package is 
available and can be installed.
