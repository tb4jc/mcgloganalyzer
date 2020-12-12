import os,sys

cwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cwd)

for entry in os.listdir(cwd):
    entryAbsPath = os.path.join(cwd, entry)
    if os.path.isdir(entryAbsPath):
        if entryAbsPath not in sys.path:
            sys.path.append(entryAbsPath)

from mcgLogWriter.mcgLogExcelWriter import ExcelWriter
from mcgLogWriter.mcgLogKmlWriter import KmlWriter
