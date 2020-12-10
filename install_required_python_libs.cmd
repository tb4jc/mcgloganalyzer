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

%PYTHON_PATH%\python.exe -m pip install --upgrade pip
%PYTHON_PATH%\Scripts\pip install --upgrade setuptools
%PYTHON_PATH%\Scripts\pip install --upgrade XlsxWriter

timeout 5
