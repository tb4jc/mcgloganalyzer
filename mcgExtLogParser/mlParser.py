"""
Created on 10.02.2016

@author: tburri
"""
import re
import sys
import time
import traceback
from pathlib import Path


class McgLogParser:
    """
    classdocs
    """

    def __init__(self, filename):
        """
        Constructor
        """
        self.mcgLogFilePath = filename
        self.lineNumber = 0
        self.nextLine = ""
        self.fileOk = Path(filename).exists()
        if self.fileOk:
            self.mcgLogFile = open(self.mcgLogFilePath)
            # read in first line
            self.nextLine = self.mcgLogFile.readline()[:-1]
        else:
            print("File not found %s" % (filename))

    def isOk(self):
        return self.fileOk

    def getNextLine(self):
        if not self.fileOk:
            return (0xFFFFFFFF, "")

        nextLine = self.nextLine
        hitLine = False
        timeInSecs = 0xFFFFFFFF
        msgString = ""
        strTimeStamp = ""
        while not nextLine == '' and not hitLine:
            # take apart line
            lineItemList = re.findall(r"[\w.:\[\]_\-\(\)/]+", nextLine[:105])
            msgString = nextLine[105:]
            try:
                if (len(lineItemList) < 7) or lineItemList[6] not in ['ERROR', 'WARN', 'INFO', 'EINFO', 'INT1', 'INT2',
                                                                      'DEBUG']:
                    # linefeed in message -> read next
                    nextLine = self.mcgLogFile.readline()[:-1]
                    self.lineNumber += 1
                else:
                    # search ERROR level
                    if lineItemList[6] == "ERROR":
                        lineTimestamp = time.strptime(lineItemList[5], "%Y-%m-%d/%H:%M:%S")
                        timeInSecs = time.mktime(lineTimestamp)
                        strTimeStamp = time.strftime("%d.%m.%Y %H:%M:%S", lineTimestamp)
                        hitLine = True
                        self.nextLine = self.mcgLogFile.readline()[:-1]
                        self.lineNumber += 1
                        nextLineItemList = re.findall(r"[\w.:\[\]_\-\(\)/]+", self.nextLine[:105])
                        if (len(nextLineItemList) < 7) or nextLineItemList[6] not in ['ERROR', 'WARN', 'INFO', 'EINFO',
                                                                                      'INT1', 'INT2', 'DEBUG']:
                            # found linefeed line -> read in next for next call of getNextLine
                            msgString += self.nextLine
                            self.nextLine = self.mcgLogFile.readline()[:-1]
                            self.lineNumber += 1
                    else:
                        nextLine = self.mcgLogFile.readline()[:-1]
                        self.lineNumber += 1
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(exc_type)
                print(exc_value)
                traceback.print_tb(exc_traceback)
                timeInSecs = 0xFFFFFFFF
                strTimeStamp = ""
                nextLine = ""

        return (timeInSecs, strTimeStamp, msgString)


if __name__ == '__main__':
    import os
    import tkinter as tk
    from tkinter import filedialog
    from mcgExtLogCombiner.mcgExtLogGlobalVariables import MCG_LOG_ALL_FILENAME

    root = tk.Tk()
    root.withdraw()
    workingDirectory = filedialog.askdirectory(initialdir="C:/workspace/TWCS/___issues",
                                               title="Choose a Issue Archive Directory.")
    if workingDirectory == "":
        print("No directory selected!")
    else:
        parser = McgLogParser(os.path.join(workingDirectory, MCG_LOG_ALL_FILENAME))
        if parser.isOk():
            parsingOk = parser.getNextLine()
            while parsingOk[0] < 0xFFFFFFFF:
                print("timestamp: %d / msg : %s" % (int(parsingOk[0]), str(parsingOk[1])))
                parsingOk = parser.getNextLine()
