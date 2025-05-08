@echo off
setlocal

REM ==============================================
REM CMD script to call PowerShell deploy script
REM Ensures parameters are passed correctly
REM SSRS is assumed to run on port 8082
REM ==============================================

REM === CONFIGURATION ===
set REPORT_NAME=GeneratedReport
set RDL_PATH=C:\AIProjects\nlp_aw_web\GeneratedReport.rdl
set FOLDER=/BI Reports with AI
set REPORT_SERVER=http://localhost:8082/ReportServer/ReportService2010.asmx

REM === Execute PowerShell script to deploy the report ===
powershell -ExecutionPolicy Bypass -File "%~dp0deploy_rdl.ps1" ^
    -ReportName "%REPORT_NAME%" ^
    -RdlPath "%RDL_PATH%" ^
    -Folder "%FOLDER%" ^
    -ReportServer "%REPORT_SERVER%"

REM === Cleanup ===
endlocal
