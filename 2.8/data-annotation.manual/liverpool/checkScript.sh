ls src-pkgs > srcs
ls bin-pkgs > bins
sed -i "s/\.tar\.gz//" srcs
sed -i "s/\.zip//" bins
diff srcs bins 
