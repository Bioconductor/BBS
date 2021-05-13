#!/bin/sh

## Example config variables
##    SUBVIEW="ExperimentData"
##    REPOS_NAME="Bioconductor 3.14 Packages - Experiment"
##    VIEW_ROOT="$HOME/PACKAGES/3.14"
##    REPOS_ROOT="$VIEW_ROOT/data/experiment"
##    CONTRIB_PATHS="c(source='src/contrib', win.binary='bin/windows/contrib/4.1')"
##    HTML_DIR="data/experiment/html"

rm -r "$REPOS_ROOT"/html "$REPOS_ROOT"/index.html "$REPOS_ROOT"/REPOSITORY "$REPOS_ROOT"/repository-detail.css "$REPOS_ROOT"/VIEWS "$REPOS_ROOT"/vignettes

R_EXPR="library(biocViews)"
R_EXPR="$R_EXPR; if (!requireNamespace('BiocManager', quietly=TRUE)) install.packages('BiocManager', repos='https://cran.rstudio.com')"
R_EXPR="$R_EXPR; subview <- '$SUBVIEW'"
R_EXPR="$R_EXPR; htmlDir <- '$HTML_DIR'"
R_EXPR="$R_EXPR; reposName <- '$REPOS_NAME'"
R_EXPR="$R_EXPR; reposRoot <- '$REPOS_ROOT'"
R_EXPR="$R_EXPR; reposUrl <- '$REPOS_URL'"
R_EXPR="$R_EXPR; viewRoot <- '$VIEW_ROOT'"
R_EXPR="$R_EXPR; viewUrl <- '$VIEW_URL'"
R_EXPR="$R_EXPR; manifestFile <- '$MANIFEST_FILE'"
R_EXPR="$R_EXPR; meatPath <- '$MEAT0_PATH'"
R_EXPR="$R_EXPR; contribPaths <- $CONTRIB_PATHS"
R_EXPR="$R_EXPR; statsUrl <- '$STATS_URL'"
R_EXPR="$R_EXPR; logUrl <- '$LOG_URL'"
R_EXPR="$R_EXPR; setwd(reposRoot)"
R_EXPR="$R_EXPR; extractVignettes(reposRoot, contribPaths)"
R_EXPR="$R_EXPR; if ($EXTRACT_MANUALS) extractManuals(reposRoot, contribPaths)"
R_EXPR="$R_EXPR; genReposControlFiles(reposRoot, contribPaths, manifestFile, meatPath)"
R_EXPR="$R_EXPR; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'readmes', 'README')"
R_EXPR="$R_EXPR; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'install', 'INSTALL')"
R_EXPR="$R_EXPR; extractTopLevelFiles(reposRoot, contribPaths['source'][1], 'licenses', 'LICENSE')"
R_EXPR="$R_EXPR; extractNEWS(reposRoot, contribPaths['source'][1])"
R_EXPR="$R_EXPR; extractCitations(reposRoot, contribPaths['source'][1], 'citations')"

$Rscript -e "$R_EXPR"

chmod +r "$REPOS_ROOT" -Rc

echo "DONE."
