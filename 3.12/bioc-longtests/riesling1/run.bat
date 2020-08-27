echo OFF
echo ========================================================
echo STARTING %cd%\run.bat on %date% at %time%
echo --------------------------------------------------------
echo ON

call config.bat

call %BBS_HOME%\utils\clean-before-run.bat

set YYYYMMDD=%date:~10,4%%date:~4,2%%date:~7,2%
set LOG_FILE=%BBS_WORK_TOPDIR%\log\%BBS_NODE_HOSTNAME%-run-%YYYYMMDD%.log

%BBS_PYTHON_CMD% %BBS_HOME%\BBS-run.py STAGE3 >>%LOG_FILE% 2>&1
%BBS_PYTHON_CMD% %BBS_HOME%\BBS-run.py STAGE4 >>%LOG_FILE% 2>&1

echo OFF
echo --------------------------------------------------------
echo %cd%\run.bat DONE on %date% at %time%
echo ========================================================
echo ON
