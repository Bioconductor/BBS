How to build the "2.8-data-annotation" binary packages
======================================================
0. I using biocbuild account:

     E:\biocbld>cd BBS\2.8\bioc\liverpool
     E:\biocbld\BBS\2.8\bioc\liverpool>call config.bat

1. Change to this dir:

     CD E:\biocbld\bbs-2.8-data-annotation


1.5. Optional (use CAREFULLY and only when the system is NOT building!)
	
      Launch R : ..\bbs-2.8-bioc\R\bin\R

      #run the following:
      source("http://bioconductor.org/biocLite.R")
      biocLite(type="source")    
      biocLite(c("BSgenome", "lumi", "pdInfoBuilder", "PAnnBuilder"),type="source") 
      biocLite(c("org.Hs.eg.db", "org.Mm.eg.db", "org.At.tair.db", "org.Bt.eg.db","org.Cf.eg.db", "org.Gg.eg.db", "org.Dm.eg.db", "org.Rn.eg.db", "org.Ce.eg.db", "org.Xl.eg.db", "org.Sc.sgd.db", "org.Dr.eg.db"),type="source")

1.7. You might need to clean out the temp library from the build script  (if the version has changed for example)

      ## The following DOES NOT work you have to go there and rm it.
      ## rm -rf E:\biocbld\bbs-2.8-data-annotation\Rlib\*

2. Get the "2.8-data-annotation" source packages from lamb1:

     get-src-pkgs.bat

3. Build the "2.8-data-annotation" binary packages:

     build-bin-pkgs.bat

4. Do some basic checkings:
     - Compare the number of binary packages (.zip files in bin-pkgs/)
       vs the number of source packages (.tar.gz files in src-pkgs/).
     - Make sure size of binary packages is not zero (ls -alS bin-pkgs).

5. Fix "2.8-data-annotation" binary packages permissions:

     chmod 644 bin-pkgs/*.zip -c

6. Put the "2.8-data-annotation" binary packages on lamb1:

     put-bin-pkgs.bat
     
7. From the biocadmin account on Wilson1:

     prepareRepos-2.8-data-annotation.sh && pushRepos-2.8-data-annotation.sh


Questions/help: hpages@fhcrc.org (ext. 5791)
Last modified: 2007-04-18
