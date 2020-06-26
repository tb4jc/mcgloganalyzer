"""
Created on 09.02.2016

@author: tburri
"""
import sys
import time
import calendar
import traceback
from pathlib import Path


class StatLogParser:
    """
    classdocs
    """

    def __init__(self, filename, engineType):
        """
        Constructor
        """
        self.statusFilePath = filename
        self._engType = engineType
        self.fileOk = Path(filename).exists()
        self.lineNumber = 1

        if self.fileOk:
            self.statusFile = open(self.statusFilePath)
            # skip header line
            self.statusFile.readline()

    def isOk(self):
        return self.fileOk

    def getNextLine(self):
        if not self.fileOk:
            return (0xFFFFFFFF, "")

        self.lineNumber += 1
        timeInSecs = 0xFFFFFFFF
        nextLine = self.statusFile.readline()[:-1]
        lineSplit = nextLine.split(';')
        timeStamp = ""
        if not nextLine == "":
            try:
                lineTimestamp = time.strptime(lineSplit[0], "%d.%m.%Y %H:%M:%S")
                timeInSecs = int(calendar.timegm(lineTimestamp))
                timeStamp = lineSplit[0]
                linePart = nextLine.partition(';')
                nextLine = linePart[2]
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(exc_type)
                print(exc_value)
                traceback.print_tb(exc_traceback)
                timeInSecs = 0xFFFFFFFF
                nextLine = ""

        return (timeInSecs, timeStamp, nextLine)
