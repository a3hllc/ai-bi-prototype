@echo off
setlocal

REM -- Configuration
set REPORT_NAME=GeneratedReport
set RDL_PATH=C:\AIProjects\nlp_aw_web\GeneratedReport.rdl
set REPORT_FOLDER=/AIReports
set REPORT_SERVER=http://localhost/ReportServer/ReportService2005.asmx

REM -- Deploy using PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0deploy_rdl.ps1" ^
    -ReportName "%REPORT_NAME%" ^
    -RdlPath "%RDL_PATH%" ^
    -Folder "%REPORT_FOLDER%" ^
    -ReportServer "%REPORT_SERVER%"

endlocal
