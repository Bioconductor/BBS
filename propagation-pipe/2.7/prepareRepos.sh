#!/bin/sh

## Example config variables
##    SUBVIEW="ExperimentData"
##    REPOS_NAME="Bioconductor 2.7 Packages - Experiment"
##    VIEW_ROOT="$HOME/PACKAGES/2.7"
##    REPOS_ROOT="$VIEW_ROOT/data/experiment"
##    CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.12')"
##    HTML_DIR="data/experiment/html"

rm -rf "$REPOS_ROOT/html $REPOS_ROOT/index.html $REPOS_ROOT/REPOSITORY $REPOS_ROOT/repository-detail.css $REPOS_ROOT/SYMBOLS $REPOS_ROOT/VIEWS $REPOS_ROOT/vignettes"

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; source('http://bioconductor.org/biocLite.R')"
R_SCRIPT="$R_SCRIPT; subview <- '$SUBVIEW'"
R_SCRIPT="$R_SCRIPT; backgroundColor <- '$BACKGROUND_COLOR'"
R_SCRIPT="$R_SCRIPT; htmlDir <- '$HTML_DIR'"
R_SCRIPT="$R_SCRIPT; reposName <- '$REPOS_NAME'"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; reposUrl <- '$REPOS_URL'"
R_SCRIPT="$R_SCRIPT; viewRoot <- '$VIEW_ROOT'"
R_SCRIPT="$R_SCRIPT; viewUrl <- '$VIEW_URL'"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; statsUrl <- '$STATS_URL'"
R_SCRIPT="$R_SCRIPT; logUrl <- '$LOG_URL'"
R_SCRIPT="$R_SCRIPT; setwd(reposRoot)"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; extractManuals(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos control files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"

## Continue to generate HTML, so that mirrors won't break
##R_SCRIPT="$R_SCRIPT; writeRepositoryHtml(reposRoot, reposName, viewUrl=viewUrl, reposFullUrl=biocinstallRepos(), downloadStatsUrl=statsUrl, devHistoryUrl=logUrl, backgroundColor=backgroundColor)"
##R_SCRIPT="$R_SCRIPT; data(biocViewsVocab)"
##R_SCRIPT="$R_SCRIPT; biocViews <- getBiocSubViews(reposUrl, biocViewsVocab, topTerm=subview, local=TRUE, htmlDir=htmlDir)"
##R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
##R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=viewRoot)"
##R_SCRIPT="$R_SCRIPT; writeTopLevelView(viewUrl, biocViewsVocab)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."
