1. Install Python module matplotlib:

   - On Ubuntu:

       apt-get install python-matplotlib

   - From source:

       a. Get the source tarball from http://matplotlib.sourceforge.net/
       b. Extract
       c. cd matplotlib-x.y.z
       d. python setup.py build
       e. sudo python setup.py install
       f. Test by starting python and trying: import pylab

2. Add the following jobs to the crontab for biocadmin on wilson2:

    30 00 * * 2,5 cd /home/biocadmin/manage-BioC-repos/stats && (./rsync_all_logs2.sh && ./make_db.sh) >>/home/biocadmin/cron.log/stats/make_db.log 2>&1
    00 07 * * 2,5 cd /home/biocadmin/manage-BioC-repos/stats && ./mkDownloadStats-for-bioc.sh >>/home/biocadmin/cron.log/stats/bioc.log 2>&1
    30 09 * * 2,5 cd /home/biocadmin/manage-BioC-repos/stats && ./mkDownloadStats-for-data-annotation.sh >>/home/biocadmin/cron.log/stats/data-annotation.log 2>&1
    00 12 * * 2,5 cd /home/biocadmin/manage-BioC-repos/stats && ./mkDownloadStats-for-data-experiment.sh >>/home/biocadmin/cron.log/stats/data-experiment.log 2>&1

   This will update the online report

     http://bioconductor.org/packages/stats/

   every Tuesday and Friday morning.

