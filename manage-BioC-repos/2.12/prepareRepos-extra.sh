#!/bin/sh

cd "$HOME/manage-BioC-repos/2.12"

. ./config.sh

REPOS_NAME="Bioconductor $BIOC_VERSION Packages - Extra"
REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/extra"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/$R_VERSION', win64.binary='bin/windows64/contrib/$R_VERSION', mac.binary='bin/macosx/contrib/$R_VERSION', mac.binary='bin/macosx/contrib/$R_VERSION')"
HTML_DIR="extra/html"

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
R_SCRIPT="$R_SCRIPT; biocViews <- getBiocViews(reposUrl, biocViewsVocab, local=TRUE, htmlDir=htmlDir, defaultView = 'No View Supplied')"
R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=reposRoot)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
