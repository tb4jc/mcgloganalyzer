'''
Created on 29.05.2020

@author: tburri
'''
import re
import sys
import time
import calendar
import traceback
from pathlib import Path


class BtclLogParser:
    """
    classdocs
    """

    def __init__(self, filename):
        """
        Constructor
        """
        self.btclLogFilePath = filename
        self.lineNumber = 0
        self.nextLine = ""
        self.fileOk = Path(filename).exists()
        if self.fileOk:
            self.btclLogFile = open(self.btclLogFilePath)
            # read in first line
            self.nextLine = self.btclLogFile.readline()[:-1]
        else:
            print("File not found %s" % (filename))

    def isOk(self):
        return self.fileOk

    def getNextLine(self):
        if not self.fileOk:
            return 0xFFFFFFFF, ""

        nextLine = self.nextLine
        hitLine = False
        timeInSecs = 0xFFFFFFFF
        msgString = ""
        strTimeStamp = ""
        while not nextLine == '' and not hitLine:
            # take apart line
            # lineItemList = re.findall(r"[\w.:\[\]_\-\(\)/]+", nextLine[:105])
            lineItemList = list(map(str.strip, re.split(r"\[|\]| - ", nextLine)))
            try:
                if (len(lineItemList) < 8) or lineItemList[5] not in ['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'] or "****" in lineItemList[7]:
                    # ignored message -> read next
                    nextLine = self.btclLogFile.readline()[:-1]
                    self.lineNumber += 1
                else:
                    # skip DEBUG messages
                    if lineItemList[5] in ['FATAL', 'ERROR', 'WARN', 'INFO']:
                        lineTimestamp = time.strptime(lineItemList[1], "%m-%d-%y %H:%M:%S")
                        timeInSecs = int(calendar.timegm(lineTimestamp))
                        strTimeStamp = time.strftime("%d.%m.%Y %H:%M:%S", lineTimestamp)
                        hitLine = True

                        if lineItemList[3] not in ["main", "BTCLclient"]:
                            msgHeader = "BTCL-%s: " % lineItemList[3][17:]

                            if "Getting BTCL server ip" in lineItemList[7]:
                                msgBody = "DNS failure;"
                            elif "timeout" in lineItemList[7]:
                                msgBody = "timeout;"
                            elif "cbul" in lineItemList[7]:
                                msgBody = "cbul;"
                            elif "connecting" in lineItemList[7]:
                                msgBody = "connecting;"
                            elif "connected" in lineItemList[7]:
                                msgBody = "connected;"
                            else:
                                msgBody = "other;"
                        else:
                            msgHeader = "BTCL: "
                            msgBody = "info;"

                        msgString = msgHeader + msgBody + lineItemList[7]

                        self.nextLine = self.btclLogFile.readline()[:-1]
                        self.lineNumber += 1
                    else:
                        nextLine = self.btclLogFile.readline()[:-1]
                        self.lineNumber += 1
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(exc_type)
                print(exc_value)
                traceback.print_tb(exc_traceback)
                timeInSecs = 0xFFFFFFFF
                strTimeStamp = ""
                nextLine = ""

        return timeInSecs, strTimeStamp, msgString


if __name__ == '__main__':
    import os
    import tkinter as tk
    from tkinter import filedialog
    from mcgLogCombiner.mcgLogGlobalVariables import BTCL_LOG_ALL_FILENAME

    root = tk.Tk()
    root.withdraw()
    workingDirectory = filedialog.askdirectory(initialdir="C:/workspace/TWCS/___issues",
                                               title="Choose a Issue Archive Directory.")
    if workingDirectory == "":
        print("No directory selected!")
    else:
        parser = BtclLogParser(os.path.join(workingDirectory, BTCL_LOG_ALL_FILENAME))
        if parser.isOk():
            parsingOk = parser.getNextLine()
            while parsingOk[0] < 0xFFFFFFFF:
                print("timestamp: %d / msg : %s" % (int(parsingOk[0]), parsingOk[2]))
                parsingOk = parser.getNextLine()
