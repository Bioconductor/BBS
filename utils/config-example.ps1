<#
Example configuration values.

Do NOT put actual config values in this file.

Copy it to config.ps1 and set the actual values there.
Do NOT check config.ps1 into version control!
Values are security-sensitive (passwords, etc.) so
be mindful of that.

DELETE config.ps1 when you are done with it!
#>

$Env:COMPUTER_NAME = "windows1"
$Env:BIOCBUILD_PASSWORD="secret!!!"
$Env:BIOC_VERSION="3.2"
$Env:RTOOLS_VERSION="33"
$Env:R_URL="https://cran.rstudio.com/bin/windows/base/R-3.2.2beta-win.exe"
$Env:R_INSTALLER="R-3.2.2beta-win.exe"
$Env:USE_DEVEL="TRUE"
$Env:GOOGLE_API_KEY="secret!!"
$Env:POSTGRES_SUPERPASSWORD="1secretT0"

