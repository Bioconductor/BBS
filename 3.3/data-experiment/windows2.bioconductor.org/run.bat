echo OFF
echo ========================================================
echo STARTING %cd%\run.bat on %date% at %time%
echo --------------------------------------------------------
echo ON

call config.bat

call %BBS_HOME%\utils\clean-before-run.bat

set YYYYMMDD=%datc:~10,4%%datc:~4,2%%datc:~7,2%
set LOG_FILE=%BBS_WORK_TOPDIR%\log\%BBS_NODE_HOSTNAME%-run-%YYYYMMDD%.log

%BBS_HOME%\BBS-run.py >>%LOG_FILE% 2>&1

echo OFF
echo --------------------------------------------------------
echo %cd%\run.bat DONE on %date% at %time%
echo ========================================================
echo ON
