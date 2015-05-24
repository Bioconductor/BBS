#!/bin/sh

REPOS_NAME="Bioconductor 2.5 Packages - Extra"
REPOS_ROOT="$HOME/PACKAGES/2.5/extra"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.10', mac.binary.universal='bin/macosx/universal/contrib/2.10', mac.binary.leopard='bin/macosx/leopard/contrib/2.10')"

R="$HOME/bin/R-2.10"

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; reposUrl <- paste('file://', reposRoot, sep='')"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos control files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; writeRepositoryHtml(reposRoot, '$REPOS_NAME')"
##R_SCRIPT="$R_SCRIPT; data(biocViewsVocab)"
##R_SCRIPT="$R_SCRIPT; biocViews <- getBiocViews(reposUrl, biocViewsVocab, local=TRUE)"
##R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
##R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=reposRoot)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
