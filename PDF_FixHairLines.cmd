@echo off
REM Drag and drop one or more files onto this .bat to process it.

py -3 PDF_Fix.py %*
echo.
REM if errorlevel 1 pause

pause