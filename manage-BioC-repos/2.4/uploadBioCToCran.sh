#!/bin/sh

PKGS_TO_UPLOAD="pkgsToUpload"
BIOC_REPOS="http://bioconductor.org/packages/2.4/bioc"
CRAN_REPOS="http://cran.fhcrc.org"

rm -rf $PKGS_TO_UPLOAD
mkdir $PKGS_TO_UPLOAD

R="$HOME/bin/R-2.9"

R_SCRIPT="uploadDir <- '$PKGS_TO_UPLOAD'"
R_SCRIPT="$R_SCRIPT; biocRepos <- '$BIOC_REPOS'"
R_SCRIPT="$R_SCRIPT; cranRepos <- '$CRAN_REPOS'"
R_SCRIPT="$R_SCRIPT; biocPkgs <- row.names(available.packages(contrib.url(biocRepos)))"
R_SCRIPT="$R_SCRIPT; cranPkgs <- row.names(available.packages(contrib.url(cranRepos)))"
R_SCRIPT="$R_SCRIPT; pkgsToUpload <- intersect(biocPkgs, cranPkgs)"
R_SCRIPT="$R_SCRIPT; download.packages(pkgsToUpload, uploadDir, repos = biocRepos, type = 'source')"
R_SCRIPT="$R_SCRIPT; sink('uploadedPkgs.txt')"
R_SCRIPT="$R_SCRIPT; cat(paste('The following', length(pkgsToUpload), 'dual-hosted CRAN/BioC packages have been uploaded:\n\n'))"
R_SCRIPT="$R_SCRIPT; cat(paste(pkgsToUpload, collapse = '\n'))"
R_SCRIPT="$R_SCRIPT; sink()"

echo "$R_SCRIPT" | $R --slave

ftp -i -n ftp://CRAN.R-project.org/incoming/ <<END_SCRIPT
quote USER anonymous
quote PASS paboyoun@fhcrc.org
binary
lcd $PKGS_TO_UPLOAD
mput *.tar.gz
quit
END_SCRIPT

mail "CRAN@R-project.org" -s "Upload of dual-hosted CRAN/BioC packages" -S replyto=paboyoun@fhcrc.org < uploadedPkgs.txt
