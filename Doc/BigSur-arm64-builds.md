## 1. Details about the machine


### Specs

- Hostname: taxco
- OS: Big Sur arm64
- 8 cores - 16 GB of RAM - 1 TB SSD drive


### What is installed on the system

#### Xcode

I downloaded and installed `Xcode_12.4_Release_Candidate.xip` (includes
Python 3):

    clang -v
    # Apple clang version 12.0.0 (clang-1200.0.32.29)
    # Target: arm64-apple-darwin20.1.0
    # Thread model: posix
    # InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin

    python3 --version
    # Python 3.8.2

#### A bunch of stuff provided by Simon

This is all available at https://mac.r-project.org/libs-arm64/

- Fortran compiler:

  Install with:
    ```
    sudo tar fvxz gfortran-f51f1da0-darwin20.0-arm64.tar.gz -C /
    ```
  Then add `export PATH="/opt/R/arm64/bin:$PATH"` to `/etc/profile`.
  Logout and login again for the change to take effect.

  Test with:
    ```
    which gfortran  # /opt/R/arm64/bin/gfortran
    gfortran -v
    ```

- Tcl/Tk:

  Install with:
    ```
    sudo tar fvxz tcltk-8.6-b810c941-arm64-fw.tar.gz -C /
    ```

  WARNING: Unfortunately, this Tcl/Tk seems to hang R forever when trying
  to load the tcltk package with `library(tcltk)` so I removed it for now.
  At least now `library(tcltk)` fails quickly instead of hanging forever.

- cairo (and all its deps):

  Note that cairo also needs zlib-system-stub.tar.gz (for `zlib.pc`) which
  is available at https://mac.r-project.org/libs-4/

  Install with:
    ```
    sudo tar fvxz pkgconfig-0.28-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz zlib-system-stub.tar.gz -C /
    sudo tar fvxz xml2-2.9.10-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz pixman-0.38.4-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz freetype-2.10.0-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz fontconfig-2.13.1-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz cairo-1.14.12-darwin.20-arm64.tar.gz -C /
    ```
  Create symlink to `zlib.pc` with:
    ```
    cd /opt/R/arm64/lib/pkgconfig
    sudo ln -s /usr/local/lib/pkgconfig/zlib.pc
    ```
  Test with:
    ```
    pkg-config cairo --cflags
    pkg-config cairo --libs
    ```

- JPEG, TIFF, WebP, and PNG libs:

  Install with:
    ```
    sudo tar fvxz jpeg-9d-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz tiff-4.1.0-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz libwebp-1.1.0-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz libpng-1.6.37-darwin.20-arm64.tar.gz -C /
    ```

- gmp and mpfr libs:

  Install with:
    ```
    sudo tar fvxz gmp-6.2.1-darwin.20-arm64.tar.gz -C /
    sudo tar fvxz mpfr-4.1.0-darwin.20-arm64.tar.gz -C /
    ```

- XZ utils (include lzma lib required by Rhtslib):

  Install with::
    ```
    sudo tar fvxz xz-5.2.4-darwin.20-arm64.tar.gz -C /
    ```


### What is NOT installed on the system

- NO Tcl/tk yet! (see above)

- NO XQuartz for arm64 yet! (see https://xquartz.macosforge.org/)

- NO JDK for arm64-based macOS yet! (see https://jdk.java.net/)

- NO MacTeX for arm64 yet! (see https://www.tug.org/mactex/)
  This means that we won't be able to build many many Bioconductor vignettes.

- System libraries NetCDF, FFTW, GSL, UDUNITS, SBML, and Open Babel.



## 2. How R was installed


I downloaded Simon's latest R-devel binary for Big Sur arm64 (2021-01-14
r79827) from https://mac.r-project.org/

No installer image (`.pkg` file) is available at the moment (Jan 23, 2021)
so I grabbed the tarball. Unlike the installer image, the tarball does NOT
contain Tcl/Tk so it's important to install it separetely. Unfortunately,
the Tcl/tk currently provided by Simon is causing problems (see above) so
no Tcl/Tk for now.

Install with:

    tar fvxz R-devel.tar.gz -C /

Create symlink to `R` executable with:

    cd /opt/R/arm64/bin
    ln -s /Library/Frameworks/R.framework/Resources/bin/R

Test with:

    which R

    ## Then from R:

    which(!capabilities())  # no X11, no long double!
    library(tcltk)          # fails (no working Tcl/Tk for now, see above)



## 3. Preliminary testing


Before setting up BBS and running the builds, I tried to install
a few R packages manually to get a taste of how bad things are.


### CRAN packages

CRAN provides no Mac binaries at all (no `x86_64` and no `arm64`) for R devel
so all CRAN packages must be installed **from source**.

    Cairo           ok
    jpeg            ok
    tiff            ok but only after adding -lwebp to PKG_LIBS in
                       the package's Makevars
    png             ok
    qpdf            ok
    gmp             ok
    Rmpfr           ok
    Rcpp            ok
    RcppParallel    NO! compilation error (ld error)
    minqa           ok (contains Fortran code)
    openssl         ok
    ggplot2         ok
    tidyverse       ok
    httpuv          ok
    RSQLite         ok
    matrixStats     ok
    RUnit           ok
    RcppGSL         NO! requires the GSL
    ncdf4           NO! requires the NetCDF library
    tiledb          NO! configure error
    
    BiocManager     ok


### Bioconductor packages

    zlibbioc        ok
    Biobase         ok
    biocViews       ok
    BiocCheck       ok
    S4Vectors       ok
    Biostrings      ok
    BiocParallel    ok
    Rhtslib         ok
    Rsamtools       ok
    rtracklayer     ok
    Rhdf5lib        ok
    beachmat        ok
    scRNAseq        ok
    mzR             NO! (depends on ncdf4 which requires the NetCDF library)
    RProtoBufLib    ok
    cytolib         NO! (depends on RcppParallel)



## 4. Running the Bioconductor builds (BBS)


We run the devel software builds (1938 packages as of Jan 24, 2021), and
we only perform the INSTALL stage (STAGE2) for now. No MacTeX means that
we wouldn't be able to build a lot of vignettes if we decided to also run
the BUILD stage (STAGE3).

The builds are scheduled to run daily. A report will soon be published
[here](https://bioconductor.org/checkResults/3.13/taxco/bioc-LATEST/)
and will get updated automatically every day.


### Some numbers for the record

- 1st run (`BBS_NB_CPU` set to 6):
    ```
    BBS> STAGE2 SUMMARY:
    BBS>   o Working dir: /Users/biocbuild/bbs-3.13-bioc/meat
    BBS>   o 3811 pkg dir(s) queued and processed
    BBS>   o 3568 pkg(s) to (re-)install: 2874 successes / 694 failures
    BBS>   o Total time: 6800.46 seconds
    ```

- 2nd BBS run (`BBS_NB_CPU` set to 8):
    ```
    BBS> STAGE2 SUMMARY:
    BBS>   o Working dir: /Users/biocbuild/bbs-3.13-bioc/meat
    BBS>   o 3811 pkg dir(s) queued and processed
    BBS>   o 2077 pkg(s) to (re-)install: 1635 successes / 442 failures
    BBS>   o Total time: 3172.16 seconds
    ```

- 3rd BBS run (`BBS_NB_CPU` set to 8):
    ```
    BBS> STAGE2 SUMMARY:
    BBS>   o Working dir: /Users/biocbuild/bbs-3.13-bioc/meat
    BBS>   o 3811 pkg dir(s) queued and processed
    BBS>   o 2043 pkg(s) to (re-)install: 1678 successes / 365 failures
    BBS>   o Total time: 3254.15 seconds
    ```

Comparison with other builders:

                                              BBS_NB_CPU  Time of
    Machine    OS                              / nb cpus   STAGE2
    ---------  -----------------------------  ----------  -------
    malbec2    Ubuntu 20.04                        11/20    97min
    rex3       Ubuntu 20.04                        40/80    32min
    tokay2     Windows Server 2012 R2              16/40  4h16min
    riesling1  Windows Server 2019                 36/80  1h29min
    machv2     macOS 10.14.6 Mojave (x86_64)       14/24  1h36min
    taxco      macOS 11.0.1 Big Sur (arm64)          8/8    54min

Looks good but the comparison is not really fair since on taxco, unlike
on the other builders, hundreds of packages are currently failing to
install because of another package that they depend on could not be
installed e.g.

    taxco:meat biocbuild$ time R CMD INSTALL cytolib
    * installing to library ‘/Library/Frameworks/R.framework/Versions/4.1-arm64/Resources/library’
    ERROR: dependency ‘RcppParallel’ is not available for package ‘cytolib’
    * removing ‘/Library/Frameworks/R.framework/Versions/4.1-arm64/Resources/library/cytolib’
    
    real	0m0.147s
    user	0m0.103s
    sys	0m0.032s


### Failures in our court

This is the list of Bioconductor software packages that we've identified
so far that fail to compile on taxco, despite having all their requirements
satisfied, and that compile sucessfully on all the other build machines.
In other words, the native code in these packages compiles fine with the
compilers included in Ubuntu 20.04 and in Rtools40, but not with the
compilers shipped with Xcode 12.4 RC (Apple clang version 12.0.0,
target `arm64-apple-darwin20.1.0`).

Last updated on Jan 25, 2021.

                                  Nb of      Nb of
                     Native    rev deps   rev deps
    Package          code       in BioC    on CRAN
    --------------   -------   --------   --------
    affxparser       C++             16          0   https://bioconductor.org/checkResults/3.13/taxco/bioc-LATEST/affxparser/taxco-install.html
    bridge           C                0         14
    CancerInSilico   C++              0          0
    CNORode          C                1          1
    CoGAPS           C++              1          0
    DeMixT           C                0          0
    gmapR            C                2          0
    iBBiG            C                1          1
    LEA              C                0          0
    msa              C                2          0
    muscle           C++              0          1
    NetPathMiner     C++              0          0
    Rbowtie2         C++              2          0
    Rhisat2          C++              1          0
    rGADEM           C                0          0
    seqbias          C                1          0


### Failures due to a missing dependency (CRAN and/or system lib)

Most installation failures we see on the
[taxco build report](https://bioconductor.org/checkResults/3.13/taxco/bioc-LATEST/)
are due to dependencies missing on taxco.

Here we summarize those installation failures that are due to missing
CRAN packages or system libraries.

Last updated on Jan 25, 2021.

#### Packages that depend directly or indirectly on RcppParallel

See [RcppParallel installation error log](https://www.stats.ox.ac.uk/pub/bdr/M1mac/RcppParallel.log) on CRAN.
The unavaibility of RcppParallel for Big Sur arm64 currently blocks the
installation of 65 Bioconductor software packages:

  banocc, CATALYST, censcyt, cmapR, CONFESS, cydar, CytoDx, cytofast,
  cytofWorkflow, cytolib, CytoML, CytoTree, dada2, ddPCRclust, diffcyt,
  diffuStats, flowAI, flowBeads, flowBin, flowCHIC, flowClean, flowClust,
  flowCore, flowCut, flowDensity, flowFP, flowMatch, flowMeans, flowMerge,
  flowPloidy, FlowSOM, flowSpecs, flowStats, flowTime, flowTrans, flowUtils,
  flowViz, flowWorkspace, GateFinder, genphen, ggcyto, HDCytoData,
  healthyFlowData, HIBAG, highthroughputassays, IgGeneUsage, ILoReg,
  ImmuneSpaceR, immunoClust, infinityFlow, MetaCyto, mina, ncdfFlow,
  netboost, oneSENSE, openCyto, oposSOM, optimalFlow, SAIGEgds, scClassify,
  scDataviz, scGPS, Sconify, simplifyEnrichment, ttgsea

#### Packages that depend directly or indirectly on NetCDF

The unavaibility of NetCDF on taxco currently blocks the
installation of 48 Bioconductor software packages:

  adductomicsR, Autotuner, CAMERA, cliqueMS, CluMSID, cosmiq,
  DAPAR, DAPARdata, DEP, DIAlignR, faahKO, flagme, IPO, LOBSTAHS,
  MAIT, Metab, metaMS, MetCirc, MSGFgui, msmsEDA, msmsTests,
  MSnbase, MSnID, msPurity, MSstatsQC, MSstatsQCgui, mzR, ncGTW,
  peakPantheR, POMA, PrInCE, pRoloc, pRolocdata, pRolocGUI, Prostar,
  ProteomicsAnnotationHubData, PtH2O2lipids, qPLEXanalyzer, qPLEXdata,
  RforProteomics, Risa, RMassBank, SIMAT, TargetSearch, topdownr,
  topdownrdata, xcms, yamss

What we're going to do about it: Not much for now, just hope
that an NetCDF binary for the arm64 arch will become available
[here](https://mac.r-project.org/libs-arm64/) at some point like
it's been available for years [here](https://mac.r-project.org/libs-4/)
for the x86_64 arch. ("Let the experts do the hard work" strategy.)

#### Packages that depend directly or indirectly on Tcl/Tk

The unavaibility of Tcl/Tk on taxco currently blocks the
installation of 39 Bioconductor software packages:

  ABAEnrichment, ABarray, affylmGUI, BioMM, CAFE, canceR, clustComp,
  compcodeR, CONFESS, cycle, DAPAR, fdrame, flowMeans, flowMerge, GEM,
  genArise, GOfuncR, IsoCorrectoRGUI, IsoGeneGUI, LedPred, limmaGUI,
  MBCB, Mfuzz, MoonlightR, OLINgui, OpenStats, optimalFlow,
  PharmacoGx, Pi, Prostar, RadioGx, scTensor, scTGIF, TimiRGeN, tkWidgets,
  tscR, uSORT, widgetTools, Xeva

#### Packages that depend directly or indirectly on Java/rJava

See [rJava installation error log](https://www.stats.ox.ac.uk/pub/bdr/M1mac/rJava.log) on CRAN.
The unavaibility of Java/rJava for Big Sur arm64 currently blocks the
installation of 21 Bioconductor software packages:

  ArrayExpressHTS, BioMM, BridgeDbR, CHRONOS, DaMiRseq, debCAM, esATAC,
  gaggle, GARS, IsoGeneGUI, miRSM, MSGFgui, OnassisJavaLibs, paxtoolsr,
  Rcpi, ReQON, RGMQL, RMassBank, rmelting, sarks, SELEX

#### Packages that depend directly or indirectly on the FFTW lib

The unavaibility of the FFTW lib on taxco currently blocks the
installation of 18 Bioconductor software packages:

  bnbc, Cardinal, CardinalWorkflows, CONFESS, CRImage, cytomapper,
  DonaPLLP2013, EBImage, FISHalyseR, flowcatchR, flowCHIC, furrowSeg,
  HD2013SGI, heatmaps, imageHTS, qusage, sojourner, yamss

What we're going to do about it: "Let the experts do the hard work" like
for NetCDF (see above).

#### Packages that depend directly or indirectly on the GSL

The unavaibility of the GSL on taxco currently blocks the
installation of 14 Bioconductor software packages:

  ADaCGH2, AMOUNTAIN, covEB, DirichletMultinomial, flowPeaks, GLAD, ITALICS,
  MANOR, powerTCR, RJMCMCNucleosomes, scBFA, scRepertoire, seqCNA, snapCGH

What we're going to do about it: "Let the experts do the hard work" like
for NetCDF (see above).

#### Packages that depend directly or indirectly on the UDUNITS lib

The unavaibility of the UDUNITS lib on taxco currently blocks the
installation of 4 Bioconductor software packages: schex, scTensor, scTGIF,
spicyR

What we're going to do about it: "Let the experts do the hard work" like
for NetCDF (see above).

#### Packages that depend directly or indirectly on SBML lib

The unavaibility of the SBML lib on taxco currently blocks the
installation of 3 Bioconductor software packages: rsbml, SBMLR, BiGGR

What we're going to do about it: rsbml is alreay officially no longer
supported on Mac anyways (the SBML maintainers have failed to provide
a working brew formula for years). We just forgot to mark SBMLR and BiGGR
also as unsupported on Mac.

#### Packages that depend directly or indirectly on Open Babel

The unavaibility of Open Babel on taxco currently blocks the
installation of Bioconductor software package ChemmineOB.

What we're going to do about it: Nothing for now. Last time we
installed OpenBabel on a Mac builder with brew
[was a nightmare](https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-macOS-Mojave-HOWTO.md#48-install-open-babel) (it broke many
things on the system and it took a while to figure out what exactly
and how to repair everything). So trying this on taxco will be delayed
as much as it can be.

#### Packages that depend directly or indirectly on tiledb

See [tiledb installation error log](https://www.stats.ox.ac.uk/pub/bdr/M1mac/tiledb.out) on CRAN.
The unavaibility of tiledb for Big Sur arm64 currently blocks the
installation of Bioconductor software package TileDBArray.

