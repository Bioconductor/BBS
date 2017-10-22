#!/bin/sh

CONFIG="$1"
. $CONFIG

## Example config variables
##    SUBVIEW="ExperimentData"
##    REPOS_NAME="Bioconductor 1.8 Packages - Experiment"
##    VIEW_ROOT="$HOME/PACKAGES/1.8"
##    REPOS_ROOT="$VIEW_ROOT/data/experiment"
##    CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/2.3')"

rm -rf "$REPOS_ROOT/html $REPOS_ROOT/index.html $REPOS_ROOT/REPOSITORY $REPOS_ROOT/repository-detail.css $REPOS_ROOT/SYMBOLS $REPOS_ROOT/VIEWS $REPOS_ROOT/vignettes"

R="$HOME/bin/R-2.5"

R_SCRIPT="library('biocViews')"
R_SCRIPT="$R_SCRIPT; reposRoot <- '$REPOS_ROOT'"
R_SCRIPT="$R_SCRIPT; viewRoot <- '$VIEW_ROOT'"
R_SCRIPT="$R_SCRIPT; reposUrl <- '$REPOS_URL'"
R_SCRIPT="$R_SCRIPT; contribPaths <- $CONTRIB_PATHS"
R_SCRIPT="$R_SCRIPT; extractVignettes(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; print('Generating repos crontrol files...')"
R_SCRIPT="$R_SCRIPT; genReposControlFiles(reposRoot, contribPaths)"
R_SCRIPT="$R_SCRIPT; writeRepositoryHtml(reposRoot, '$REPOS_NAME', viewUrl='$VIEW_URL')"
R_SCRIPT="$R_SCRIPT; data(biocViewsVocab)"
R_SCRIPT="$R_SCRIPT; biocViews <- getBiocSubViews(reposUrl, biocViewsVocab, topTerm='$SUBVIEW', local=FALSE)"
R_SCRIPT="$R_SCRIPT; print('Writing BiocViews...')"
R_SCRIPT="$R_SCRIPT; writeBiocViews(biocViews, dir=viewRoot)"
R_SCRIPT="$R_SCRIPT; writeTopLevelView('$VIEW_ROOT', biocViewsVocab)"

echo "$R_SCRIPT" | $R --slave

chmod +r $REPOS_ROOT -Rc

echo "DONE."

