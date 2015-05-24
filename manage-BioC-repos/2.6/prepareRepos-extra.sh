#!/bin/sh

REPOS_NAME="Bioconductor 2.6 Packages - Extra"
REPOS_ROOT="$HOME/PACKAGES/2.6/extra"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.11', win64.binary='bin/windows64/contrib/2.11', mac.binary.leopard='bin/macosx/leopard/contrib/2.11')"
HTML_DIR="extra/html"

R="$HOME/bin/R-2.11"

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; htmlDir <- '$HTML_DIR'"

R_SCRIPT="$R_SCRIPT; reposUrl <- paste('file://', reposRoot, sep='')"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos control files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"

## Continue to generate HTML, so that mirrors won't break
R_SCRIPT="$R_SCRIPT; writeRepositoryHtml(reposRoot, '$REPOS_NAME')"
R_SCRIPT="$R_SCRIPT; data(biocViewsVocab)"
R_SCRIPT="$R_SCRIPT; biocViews <- getBiocViews(reposUrl, biocViewsVocab, local=TRUE, htmlDir=htmlDir)"
R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=reposRoot)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
