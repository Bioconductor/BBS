#!/bin/sh

cd "$HOME/manage-BioC-repos/3.5"

. ./config.sh

REPOS_NAME="Bioconductor $BIOC_VERSION Packages - Extra"
REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/extra"
REPOS_URL="http://master.bioconductor.org/packages/$BIOC_VERSION/extra"
VIEW_URL="http://bioconductor.org/packages/$BIOC_VERSION"
CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/$R_VERSION', mac.binary.mavericks='bin/macosx/mavericks/contrib/$R_VERSION')"
LOG_URL=""

rm -rf "$REPOS_ROOT"/REPOSITORY "$REPOS_ROOT"/repository-detail.css "$REPOS_ROOT"/SYMBOLS "$REPOS_ROOT"/vignettes "$REPOS_ROOT"/manuals "$REPOS_ROOT"/citations "$REPOS_ROOT"/news "$REPOS_ROOT"/licenses "$REPOS_ROOT"/readmes "$REPOS_ROOT"/install

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; source('http://master.bioconductor.org/biocLite.R')"
R_SCRIPT="$R_SCRIPT; reposName <- '$REPOS_NAME'"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; reposUrl <- '$REPOS_URL'"
R_SCRIPT="$R_SCRIPT; viewUrl <- '$VIEW_URL'"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; logUrl <- '$LOG_URL'"
R_SCRIPT="$R_SCRIPT; setwd(reposRoot)"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; extractHTMLDocuments(reposRoot, contribPaths['source'][1], 'vignettes')"
R_SCRIPT="$R_SCRIPT; extractManuals(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos control files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; writeRFilesFromVignettes(reposRoot, reposName, viewUrl=viewUrl, reposFullUrl=biocinstallRepos(), devHistoryUrl=logUrl)"
R_SCRIPT="$R_SCRIPT; extractCitations(reposRoot, contribPaths['source'][1], 'citations')"
R_SCRIPT="$R_SCRIPT; extractNEWS(reposRoot, contribPaths['source'][1])"
R_SCRIPT="$R_SCRIPT; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'licenses', 'LICENSE')"
R_SCRIPT="$R_SCRIPT; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'readmes', 'README')"
R_SCRIPT="$R_SCRIPT; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'install', 'INSTALL')"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
