$Package = "IRanges"
$Version = "2.29.1"
$Rexe = "D:\biocbuild\bbs-3.15-bioc\R\bin\R.exe"

mkdir tmp
cd tmp

git clone https://git.bioconductor.org/packages/$Package

Measure-Command {
  & $Rexe CMD INSTALL $Package | Out-Default
}
# TotalSeconds      : 56.39

Measure-Command {
  & $Rexe CMD build --keep-empty-dirs --no-resave-data $Package | Out-Default
}
# TotalSeconds      : 71.58

Measure-Command {
  & $Rexe CMD check --no-install --no-multiarch --no-vignettes "${Package}_${Version}.tar.gz" | Out-Default
}
# TotalSeconds      : 

Measure-Command {
  C:\cygwin\bin\rm -rf "$Package.buildbin-libdir"
  mkdir "$Package.buildbin-libdir"
  & $Rexe CMD INSTALL --build --library="$Package.buildbin-libdir" "${Package}_${Version}.tar.gz" | Out-Default
}
# TotalSeconds      : 54.54

