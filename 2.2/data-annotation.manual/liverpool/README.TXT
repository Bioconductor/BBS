How to build the "2.2-data-annotation" binary packages
======================================================

1. Change to this dir:

     CD E:\biocbld\bbs-2.2-data-annotation

2. Get the "2.2-data-annotation" source packages from lamb1:

     get-src-pkgs.bat

3. Build the "2.2-data-annotation" binary packages:

     build-bin-pkgs.bat

4. Do some basic checkings:
     - Compare the number of binary packages (.zip files in bin-pkgs/)
       vs the number of source packages (.tar.gz files in src-pkgs/).
     - Make sure size of binary packages is not zero (ls -alS bin-pkgs).

5. Fix "2.2-data-annotation" binary packages permissions:

     chmod 644 bin-pkgs/*.zip -c

6. Put the "2.2-data-annotation" binary packages on lamb1:

     put-bin-pkgs.bat
     
7. From the biocadmin account on lamb1:

     prepareRepos-2.2-data-annotation.sh && pushRepos-2.2-data-annotation.sh


Questions/help: hpages@fhcrc.org (ext. 5791)
Last modified: 2007-04-18
