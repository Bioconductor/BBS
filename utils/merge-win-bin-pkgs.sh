#!/bin/bash

set -e # Exit immediately if a simple command exits with a non-zero status.

print_usage()
{
	cat <<-EOD
	Script for merging Windows i386 and x64 binary packages into a bi-arch
	package.
	
	Usage:
	  $0 <pkgname> <version> \\
	     <baseURL-to-i386-zipfile> \\
	     <baseURL-to-x64-zipfile> \\
	     [cleanup]
	
	Example:
	  $0 IRanges 1.7.9 \\
	     http://lamb2/BBS/2.7/bioc/nodes/liverpool/buildbin \\
	     http://lamb2/BBS/2.7/bioc/nodes/gewurz/buildbin
	EOD
	exit 1
}

if [ "$1" == "" ] || [ "$2" == "" ] || [ "$3" == "" ] || [ "$4" == "" ]; then
	print_usage
	exit 1
fi

PKGNAME="$1"
VERSION="$2"
I386BASEURL="$3"
X64BASEURL="$4"

TMPDIR="$PKGNAME.tmp"
ZIPFILE="${PKGNAME}_${VERSION}.zip"
I386URL="$I386BASEURL/$ZIPFILE"
X64URL="$X64BASEURL/$ZIPFILE"
X64PKGDIR="${PKGNAME}.x64"

guess_path_type()
{
	path="$1" # Local path or URL
	tmp=`echo $path | grep -E "^http://"`
	if [ "$tmp" == "" ]; then
		echo "local"
	else
		echo "http"
	fi
}

unzip_file()
{
	dirpath="$1"
	filename="$2"
	path="$dirpath/$filename"
	path_type=`guess_path_type $dirpath`
	if [ "$path_type" == "local" ]; then
		localfile="$path"
	else
		wget --no-verbose "$path"
		localfile="$filename"
	fi
	cat <<-EOD
	  >> Unzipping file
	       $path
	EOD
	unzip -q "$localfile"
}

extract_dcf_field()
{
	key="$1"
	dcf_file="$2"
	EOK_REGEXP=":"
	DCFLINE_REGEXP="^$key$EOK_REGEXP[[:space:]]*([^[:space:]].*[^[:space:]])[[:space:]]*$"
	dcf_line=`grep -E "^$key$EOK_REGEXP" "$dcf_file"`
	echo $dcf_line | sed -r "s/$DCFLINE_REGEXP/\1/"
}

check_pkg_name_and_version()
{
	description_file="$1"
	package_string=`extract_dcf_field Package "$description_file"`
	if [ "$package_string" != "$PKGNAME" ]; then
		echo "ERROR: Unexpected package name found in $description_file (found: $package_string)"
		exit 2
	fi
	version_string=`extract_dcf_field Version "$description_file"`
	if [ "$version_string" != "$VERSION" ]; then
		echo "ERROR: Unexpected package version found in $description_file (found: $version_string)"
		exit 2
	fi
}

rm -rf "$ZIPFILE" "$TMPDIR"
mkdir "$TMPDIR"
cd "$TMPDIR"

# Extract the x64 zipfile (after downloading if remote)
x64_path_type=`guess_path_type $X64BASEURL`
unzip_file "$X64BASEURL" "$ZIPFILE"
rm -f "$ZIPFILE"
mv "$PKGNAME" "$X64PKGDIR"

# Check Package and Version fields of x64 zipfile
check_pkg_name_and_version "${X64PKGDIR}/DESCRIPTION"

# Extract the i386 zipfile (after downloading if remote)
i386_path_type=`guess_path_type $I386BASEURL`
unzip_file "$I386BASEURL" "$ZIPFILE"

# Check Package and Version fields of i386 zipfile
check_pkg_name_and_version "${PKGNAME}/DESCRIPTION"

# Check Archs fields
i386_archs_string=`extract_dcf_field Archs "${PKGNAME}/DESCRIPTION"`
x64_archs_string=`extract_dcf_field Archs "${X64PKGDIR}/DESCRIPTION"`
if [ "$i386_archs_string" == "" ]; then
	if [ "$x64_archs_string" != "" ]; then
		if [ "$i386_path_type" != "local" ]; then
			rm "$ZIPFILE"
		fi
		echo "ERROR: File $I386URL doesn't seem to contain native code (no Archs field) while $X64URL does. This is a VERY abnormal situation!"
		exit 2
	fi
	echo "  >> $PKGNAME package doesn't seem to contain native code -> nothing to do"
	if [ "$i386_path_type" == "local" ]; then
		cp "$I386URL" "../"
	else
		mv "$ZIPFILE" "../"
	fi
	if [ "$5" == "cleanup" ]; then
		cd ..
		rm -rf "$TMPDIR"
	fi
	echo "DONE."
	exit 0
fi
rm -f "$ZIPFILE"

if [ "$i386_archs_string" != "i386" ]; then
	echo "ERROR: File $I386URL doesn't look like an i386 binary (Archs found: $i386_archs_string)"
	exit 2
fi
if [ "$x64_archs_string" != "x64" ]; then
	echo "ERROR: File $X64URL doesn't look like an x64 binary (Archs found: $x64_archs_string)"
	exit 2
fi

# Copy x64 libs to i386 package
echo "  >> Copying x64 libs to i386 package"
cp -ri "${X64PKGDIR}/libs/x64" "${PKGNAME}/libs/"

# Update the Archs field in DESCRIPTION file
echo "  >> Updating Archs field in ${TMPDIR}/${PKGNAME}/DESCRIPTION"
cd "$PKGNAME"
mv DESCRIPTION DESCRIPTION.original
cat DESCRIPTION.original | sed -r "s/^Archs: i386/Archs: i386, x64/" > DESCRIPTION
rm DESCRIPTION.original

# Update the MD5 file
echo "  >> Updating ${TMPDIR}/${PKGNAME}/MD5"
checksum=`md5sum DESCRIPTION | sed -r "s/^([^[:space:]]+)  DESCRIPTION/\1/"`
mv MD5 MD5.original
cat MD5.original | sed -r "s/^[^[:space:]]+ \*DESCRIPTION/$checksum \*DESCRIPTION/" > MD5
rm MD5.original

# Zip the bi-arch package
cd ..
echo "  >> Zipping the new bi-arch package into $ZIPFILE"
zip -rq "../$ZIPFILE" "$PKGNAME"

if [ "$5" == "cleanup" ]; then
	cd ..
	rm -rf "$TMPDIR"
fi
echo "DONE."

