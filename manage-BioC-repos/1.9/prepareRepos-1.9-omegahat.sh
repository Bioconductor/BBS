#!/bin/sh

REPOS_NAME="Bioconductor 1.9 Packages - Omegahat mirror"
REPOS_ROOT="$HOME/PACKAGES/1.9/omegahat"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.4', mac.binary='bin/macosx/universal/contrib/2.4')"

R="$HOME/bin/R-2.4"

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
