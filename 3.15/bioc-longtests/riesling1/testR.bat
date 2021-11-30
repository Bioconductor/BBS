call config.bat

%BBS_R_HOME%\bin\Rscript --vanilla -e "cat('TMPDIR=',Sys.getenv('TMPDIR'),'\n',sep='');cat('TMP=',Sys.getenv('TMP'),'\n',sep='');cat('TEMP=',Sys.getenv('TEMP'),'\n',sep='');cat('tempdir(): ',tempdir(),'\n',sep='')"

