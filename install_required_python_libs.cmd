@echo off

set CWD=%~dp0

if not exist %CWD%set_python_path.cmd (
    color 47
    echo.
    echo "Create file 'set_python_path.cmd' that sets environment variable PYTHON_PATH!"
    pause
    exit /b
)

call %CWD%set_python_path.cmd

%PYTHON_PATH%\python.exe -m pip install -r requirements.txt

timeout 5
