How to build the "2.9-data-annotation" binary packages
======================================================
0. I using biocbuild account:

     D:\biocbld>cd BBS\2.9\bioc\moscato1
     D:\biocbld\BBS\2.9\bioc\moscato1>call config.bat

1. Change to this dir:

     CD D:\biocbld\bbs-2.9-data-annotation


1.5. Optional (use CAREFULLY and only when the system is NOT building!)
	
      Launch R : ..\bbs-2.9-bioc\R\bin\R

      #run the following:
      source("http://bioconductor.org/biocLite.R")
      biocLite(type="source")
      biocLite(c("GenomicFeatures","BSgenome", "lumi", "pdInfoBuilder", 
      "PAnnBuilder"),type="source")
      biocLite(c("org.Hs.eg.db", "org.Mm.eg.db", "org.At.tair.db", 
      "org.Bt.eg.db", "org.Cf.eg.db", "org.Gg.eg.db", "org.Dm.eg.db", 
      "org.Rn.eg.db", "org.Ce.eg.db", "org.Xl.eg.db", "org.Sc.sgd.db", 
      "org.Ss.eg.db", "org.Dr.eg.db"),type="source")



1.7. You might need to clean out the temp library from the build script  (if the version has changed for example)

      ## The following DOES NOT work you have to go there and rm it.
      ## rm -rf D:\biocbld\bbs-2.9-data-annotation\Rlib\*

2. Get the "2.9-data-annotation" source packages from wilson2:

     get-src-pkgs.bat

3. Build the "2.9-data-annotation" binary packages:

     build-bin-pkgs.bat

4. Do some basic checkings:
     - Compare the number of binary packages (.zip files in bin-pkgs/)
       vs the number of source packages (.tar.gz files in src-pkgs/).
     - Make sure size of binary packages is not zero (ls -alS bin-pkgs).

5. Fix "2.9-data-annotation" binary packages permissions:

     chmod 644 bin-pkgs/*.zip -c

6. Put the "2.9-data-annotation" binary packages on wilson2:

     put-bin-pkgs.bat
     
7. From the biocadmin account on wilson2:

     cd ~/manage-BioC-repos/2.9
     ./prepareRepos-data-annotation.sh && ./pushRepos-data-annotation.sh


Questions/help: hpages@fhcrc.org (ext. 5791)
Last modified: 2011-07-27
