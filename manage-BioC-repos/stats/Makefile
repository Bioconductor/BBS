# WARNING: THIS Makefile IS *NOT* READY YET!

logfile = /home/biocadmin/cron.log/stats/stats.log

pkgdownloads_db.sqlite:
	./make_db.sh >>$(logfile) 2>&1

bioc: pkgdownloads_db.sqlite
	./mkDownloadStats-for-bioc.sh >>$(logfile) 2>&1

data-annotation: pkgdownloads_db.sqlite
	./mkDownloadStats-for-data-annotation.sh >>$(logfile) 2>&1

all: bioc data-annotation

