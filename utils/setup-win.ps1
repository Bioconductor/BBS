# COMPUTER_NAME should be set 
# to the name this machine should have
# (without the domain name)

# if you are going to run this as a script, you need
# to run this line in a powershell window first:
# Set-ExecutionPolicy RemoteSigned

# rename computer; this requires a reboot to take effect ;-(
Rename-Computer -NewName $Env:COMPUTER_NAME

# set domain name (hopefully the hardcoded value is ok)
[Environment]::SetEnvironmentVariable("userdnsdomain", "bioconductor.org", "Machine")

# put it into the environment right away:
$env:userdnsdomain = "bioconductor.org"

# set time zone, may want to customize this
tzutil.exe /s "US Eastern Standard Time"

$download_dir = "c:\Users\Administrator\Downloads"
cd $download_dir

$curl = "c:\cygwin64\bin\curl"

iex "$curl -LO https://github.com/msysgit/msysgit/releases/download/Git-1.9.5-preview20150319/Git-1.9.5-preview20150319.exe"

.\Git-1.9.5-preview20150319.exe /verysilent

# add git to path
$path = $Env:Path

$path += ";C:\Program Files (x86)\Git\bin"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

iex "$curl -LO https://s3.amazonaws.com/bioc-windows-setup/SlikSvn.zip"

unzip .\SlikSvn.zip -d "C:\Program Files (x86)"

$path += ";C:\Program Files (x86)\SlikSvn\bin"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

mkdir \biocbld

git clone https://github.com/Bioconductor/BBS.git c:\biocbld\BBS

cd \biocbld\BBS
# this should be temporary:
git checkout start-linux1

cd $download_dir

mkdir \biocbld\.BBS

echo "You have to manually add c:\.BBS\id_rsa!!!!"

# be sure BIOCBUILD_PASSWORD env var is set....
net user biocbuild "$Env:BIOCBUILD_PASSWORD" /ADD

# give biocbuild the right to log on 
net localgroup "Remote Desktop Users" biocbuild /add

# install python
iex "$curl -LO http://downloads.activestate.com/ActivePython/releases/2.7.8.10/Acti
vePython-2.7.8.10-win32-x86.msi"

 .\ActivePython-2.7.8.10-win32-x86.msi INSTALLDIR=c:\Python27 /qb

# add to path
$path += ";c:\Python27"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

# be sure BIOC_VERSION variable is set

#cd "c:\biocbld\BBS\$Env:BIOC_VERSION"

# no point, SET statements in bat file are ignored....

# be sure RTOOLS_VERSION is set to e.g. 33

iex "$curl -LO https://cran.rstudio.com/bin/windows/Rtools/Rtools$env:RTOOLS_VERSION.exe"

siex " .\Rtools$env:RTOOLS_VERSION.exe /verysilent"

 $path = "C:\Rtools\bin;C:\Rtools\gcc-4.6.3\bin;" + $path

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

# be sure BIOC_VERSION is set to e.g. 3.2
$bioc_basedir = "c:\biocbld\bbs-$env:BIOC_VERSION-bioc"

mkdir $bioc_basedir


# be sure R_URL is set to the URL containing the R for 
# windows installer

# be sure R_INSTALLER is set to e.g.
# R-3.2.1patched-win.exe

$r_basedir = "$bioc_basedir\R"
$r = "$r_basedir\bin\R"

iex "$curl -LO $env:R_URL"

iex ".\$env:R_INSTALLER /DIR=$r_basedir /noicons /verysilent "

# biocbuild user should MANUALLY add R to their user path
# or we could try and figure out how to script it, for bonus points

