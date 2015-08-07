# needs to be run as biocbuild!

cd c:\Users\biocbuild\Downloads
$curl = "c:\cygwin64\bin\curl"



iex "$curl -LO https://github.com/Ensembl/ensembl-tools/archive/release/80.zip"

unzip .\80.zip

mv .\ensembl-tools-release-80\scripts\variant_effect_predictor c:\vep

cd c:\vep

# remove or comment out call to test() inside INSTALL.pl

cat .\INSTALL.pl | sed "s/test()/#test()/" > INSTALL_notest.pl

perl INSTALL_notest.pl -a a

cd c:\Users\biocbuild\Downloads
