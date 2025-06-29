@echo off
for %%i in (*.ui) do (
    pyuic5 -o "%%~ni.py" "%%i"
)
pause