#!/bin/sh

REPOS_NAME="Bioconductor 2.1 Packages - Extra"
REPOS_ROOT="$HOME/PACKAGES/2.1/extra"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.6', mac.binary='bin/macosx/universal/contrib/2.6')"
#CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.6')"

## We delibarately use R-2.7 to work around the following problem with graph/biocViews
## in BioC 2.1:
##   Error in if (object@edgemode == "undirected" && length(objEdges) > 0) { :
##     missing value where TRUE/FALSE needed
##   Calls: getBiocSubViews ... anyStrings -> identical -> validityMethod -> validGraph
##   Execution halted
R="$HOME/bin/R-2.7"

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; reposUrl <- paste('file://', reposRoot, sep='')"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos crontrol files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; writeRepositoryHtml(reposRoot, '$REPOS_NAME')"
##R_SCRIPT="$R_SCRIPT; data(biocViewsVocab)"
##R_SCRIPT="$R_SCRIPT; biocViews <- getBiocViews(reposUrl, biocViewsVocab, local=TRUE)"
##R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
##R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=reposRoot)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
