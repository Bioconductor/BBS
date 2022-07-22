#!/bin/bash
#
# Script for installing a source package (tarball) for a given set of Mac OS X
# architectures. Typical use:
#
#   ./macosx-inst-pkg.sh affyio_1.5.8.tar.gz
#
# Note that this scripts does NOT check the source package!
#
# Author: Hervé Pagès <hpages.on.github@gmail.com>
# Last modified: 2011-06-23

set -e  # Exit immediately if a simple command exits with a non-zero status

# Extra .so for the following archs will be installed (in addition to the
# native .so):
#TARGET_ARCHS="/ppc /x86_64 /ppc64"
TARGET_ARCHS="/x86_64"
SINGLE_ARCH=true

# Change dynamic shared library path for
LOCAL_DYLIB_DIR="/usr/local/lib"
LOCAL_FORTRAN_DYLIB_DIR="/usr/local/gfortran/lib"

if uname -a | grep -q "Version 10."; then
    # Snow Leopard builds
    DYLIB_FILES="libgcc_s.1.dylib libgfortran.2.dylib libreadline.5.2.dylib libreadline.dylib"
elif uname -a | grep -q "Version 13."; then
    # Mavericks builds
    DYLIB_FILES="libgcc_s.1.dylib libgfortran.3.dylib libreadline.5.2.dylib libreadline.dylib libquadmath.0.dylib"
elif uname -a | grep -q "Version 15."; then
    # El Capitan builds
    DYLIB_FILES="libgcc_s.1.dylib libgfortran.3.dylib libreadline.5.2.dylib libreadline.dylib libquadmath.0.dylib"
elif uname -a | grep -q "Version 18."; then
    # Mojave builds (e.g. merida1)
    DYLIB_FILES="libgcc_s.1.dylib libgfortran.5.dylib libquadmath.0.dylib"
else
    # Builds on any macOS >= Monterey with High Sierra as **target**
    DYLIB_FILES="libgcc_s.1.1.dylib libgfortran.5.dylib libquadmath.0.dylib"
fi


# -------- It is unlikely that you need to touch anything below this ---------

print_usage()
{
	cat <<-EOD
	Usage:
	  $0 <src-tarball-path> [<R_CMD> [<path-to-install-dir>]]
	EOD
	exit 1
}

if [ "x$1" == "x" ] || [ "x$4" != "x" ]; then
    print_usage
fi

srcpkg_filepath="$1"
srcpkg_filename=`echo "$srcpkg_filepath" | sed 's/.*\///'`

FILENAME_PARSER="^(.*)_([^_]+)\.tar\.gz$"
pkgname=`echo "$srcpkg_filename" | sed -E "s/$FILENAME_PARSER/\1/"`
#pkgversion=`echo "$srcpkg_filename" | sed -E "s/$FILENAME_PARSER/\2/"`

if [ "x$2" != "x" ]; then
    R_CMD="$2"
else
    R_CMD="R"
fi

if [ "x$3" != "x" ]; then
    R_LIBS="$3"
else
    R_LIBS="`$R_CMD CMD sh -c 'echo "$R_HOME"'`/library"
fi

R_xyversion=`echo 'cat(version$major,strsplit(version$minor,split=".",fixed=TRUE)[[1L]][1L],sep=".");if(version$arch=="aarch64")cat("-arm64")' | $R_CMD --no-echo`

R_lib_dir="/Library/Frameworks/R.framework/Versions/$R_xyversion/Resources/lib"

RVPATH_REGEXP="\/Library\/Frameworks\/R\.framework\/Versions\/"

fix_dylib_links()
{
    so_file="$1"
    # 1st fix: Because we use simultaneously several versions of R on the same
    # build machine, some packages end up being linked to the wrong version of
    # R. For example, they can end up being linked to
    #   /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libR.dylib
    # when they should in fact be linked to
    #   /Library/Frameworks/R.framework/Versions/2.12/Resources/lib/libR.dylib
    # The code below fixes those links.
    # NB: set +e below prevents the script from exiting if a simple command
    # in the back-quoted expression exits with a non-zero status.
    set +e
    bad_dylibs=`otool -L "$so_file" | \
                grep -E "^[[:space:]]$RVPATH_REGEXP[^\/]+\/.*" | \
                sed -E "s/^[[:space:]]([^[:space:]]+) \(.*\)$/\1/" | \
                grep -v "$R_xyversion"`
    set -e
    for old_dylib in $bad_dylibs; do
        new_dylib=`echo $old_dylib | \
                   sed -E "s/^($RVPATH_REGEXP)[^\/]+(\/.*)$/\1$R_xyversion\2/"`
        if [ ! -f "$new_dylib" ]; then
            echo "ERROR: R installation problem: File $new_dylib not found!"
            exit 1
        fi
        echo "install_name_tool -change \"$old_dylib\" \"$new_dylib\" \"$so_file\""
        install_name_tool -change "$old_dylib" "$new_dylib" "$so_file"
    done
    # 2nd fix: Replace links to local .dylib files with links to the .dylib
    # files shipped with R.
    for dylib_file in $DYLIB_FILES; do
        old_dylib="$LOCAL_DYLIB_DIR/$dylib_file"
        new_dylib="$R_lib_dir/$dylib_file"
        if [ ! -f "$new_dylib" ]; then
            echo "ERROR: R installation problem: File $new_dylib not found!"
            exit 1
        fi
        echo "install_name_tool -change \"$old_dylib\" \"$new_dylib\" \"$so_file\""
        install_name_tool -change "$old_dylib" "$new_dylib" "$so_file"
    done
    # 3rd fix: Replace links to .dylib files in LOCAL_FORTRAN_DYLIB_DIR with
    # links to the .dylib files shipped with R.
    old_dylibs=`otool -L "$so_file" | grep "$LOCAL_FORTRAN_DYLIB_DIR/.*\.dylib" | cut -d ' ' -f 1`
    pattern=`echo $LOCAL_FORTRAN_DYLIB_DIR | sed "s/\//\\\\\\\\\//g"`
    replacement1=`echo $R_lib_dir | sed "s/\//\\\\\\\\\//g"`
    replacement2=`echo "/usr/lib" | sed "s/\//\\\\\\\\\//g"`
    for old_dylib in $old_dylibs; do
        new_dylib=`echo $old_dylib | sed "s/$pattern/$replacement1/"`
        if [ ! -f "$new_dylib" ]; then
            new_dylib=`echo $old_dylib | sed "s/$pattern/$replacement2/"`
            if [ ! -f "$new_dylib" ]; then
                echo "ERROR: R installation problem: File $new_dylib not found!"
                exit 1
            fi
        fi
        echo "install_name_tool -change \"$old_dylib\" \"$new_dylib\" \"$so_file\""
        install_name_tool -change "$old_dylib" "$new_dylib" "$so_file"
    done
    ## 4th fix: Edit link to liblzma.5.dylib so that the library will also be
    ## searched in /usr/lib on the user machine at load time.
    ## In the end, this was not needed (see
    ## https://support.bioconductor.org/p/109172/#109510), and it was not
    ## solving the problem anyway because liblzma.5.dylib in /usr/lib and
    ## /usr/local/opt/xz/lib are incompatible. Keeping the code around in case
    ## we need to use this trick for another library but THE TRICK WILL WORK
    ## ONLY IF THE COMPATBILITY VERSION OF THE LIBRARY IS THE SAME AT THE
    ## VARIOUS RPATH LOCATIONS!
    #extra_rpath="/usr/lib"
    #dylib_paths=`otool -L $so_file | grep "liblzma\..*dylib" | cut -d ' ' -f 1`
    #for dylib_path in $dylib_paths; do
    #    dylib_dirname=`dirname "$dylib_path"`
    #    if [ "$dylib_dirname" != "$extra_rpath" ] && [ "$dylib_dirname" != "@rpath" ]; then
    #        dylib_rpath="@rpath/`basename \"$dylib_path\"`"
    #        echo "install_name_tool -change \"$dylib_path\" \"$dylib_rpath\" \"$so_file\""
    #        install_name_tool -change "$dylib_path" "$dylib_rpath" "$so_file"
    #        echo "install_name_tool -add_rpath \"$dylib_dirname\" \"$so_file\""
    #        install_name_tool -add_rpath "$dylib_dirname" "$so_file"
    #        echo "install_name_tool -add_rpath \"$extra_rpath\" \"$so_file\""
    #        install_name_tool -add_rpath "$extra_rpath" "$so_file"
    #    fi
    #done
}

echo ">>>>>>> "
echo -n ">>>>>>> "
echo "INSTALLATION WITH 'R CMD INSTALL --preclean --no-multiarch --library=$R_LIBS $srcpkg_filepath'"
echo ">>>>>>> "
echo ""
$R_CMD CMD INSTALL --preclean --no-multiarch --library="$R_LIBS" "$srcpkg_filepath"
echo ""
echo ""

so_path="$R_LIBS/$pkgname/libs"
if [ -d "$so_path" ]; then
    for arch in $TARGET_ARCHS; do
        # Packages that don't have a configure script should already have
        # their .so installed out-of-the-box for all the target archs by
        # the standard R CMD INSTALL command above. But not any more!

        if $SINGLE_ARCH ; then
            arch=""
        fi
        arch_so_path="${so_path}${arch}"
        if [ ! -d "$arch_so_path" ]; then
            # The package has a configure script.
            echo ">>>>>>> "
            echo -n ">>>>>>> "
            echo "INSTALLATION OF $arch LIBS WITH 'R_ARCH=$arch R CMD INSTALL --preclean --no-multiarch --no-test-load --library=$R_LIBS --libs-only $srcpkg_filepath'"
            echo ">>>>>>> "
            echo ""
            R_ARCH=$arch $R_CMD CMD INSTALL --preclean --no-multiarch --no-test-load --library="$R_LIBS" --libs-only "$srcpkg_filepath"
            echo ""
            echo ""
        fi
        for so_file in $arch_so_path/*.so; do
            if [ -e "$so_file" ]; then
                echo ">>>>>>> "
                echo -n ">>>>>>> "
                echo "FIXING LINKS FOR $so_file"
                echo ">>>>>>> "
                echo ""
                fix_dylib_links "$so_file"
                echo ""
                echo ""
            fi
        done
    done
fi

