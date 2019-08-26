@echo off

REM Configure auto dumps for a specific application

:: test admin
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo must be admin!
    goto END
)

if [%1] neq [] goto ARGS_OK
echo USAGE: %~n0 app.exe [remvoe]
goto END

:ARGS_OK
:: Configure that crashes of this app will generate (full) dumps
set app_name=%1
set dump_folder="%userprofile%\desktop\dumps_%app_name%"
set dump_count=30& REM note that iis creates about 5 dumps per crash, so if you want 2 iis crashes, set to 10

echo running for %app_name%


set root="HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\%app_name%"

:: if removing
if [%2] equ [remove] goto REMOVE

:: test if already configured
set already_exists=0
reg query "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\%app_name%" >nul 2>&1
if %ERRORLEVEL% equ 0 set already_exists=1

if %already_exists% equ 0 goto CONFIGURE
choice /c yn /m "Already configured. Continue? (y/n)"
if %errorlevel% neq 1 goto END

:CONFIGURE
echo Configuring...
reg add %root% /f
reg add %root% /v DumpFolder /t REG_EXPAND_SZ /d %dump_folder% /f
reg add %root% /v DumpCount  /t REG_DWORD     /d %dump_count%  /f
reg add %root% /v DumpType   /t REG_DWORD     /d 2             /f
goto END

:REMOVE
echo Removing...
reg delete %root% /f
goto END

:END
