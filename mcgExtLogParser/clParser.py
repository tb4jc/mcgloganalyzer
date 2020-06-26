"""
Created on 09.02.2016

@author: tburri
"""
import re
import time
import calendar
from pathlib import Path


class ComLogParser:
    """
    classdocs
    """

    def __init__(self, filename):
        """
        Constructor
        """
        self.idDict = []
        self.destLines = 0
        self.failedLines = 0
        self.transferredLines = 0
        self.comLogFilePath = filename
        self.fileOk = Path(filename).exists()
        if self.fileOk:
            self.comLogFile = open(self.comLogFilePath)
        else:
            print("File not found %s" % (filename))

    def isOk(self):
        return self.fileOk

    def printStats(self):
        print("dest lines = %d" % (self.destLines))
        print("failed lines = %d" % (self.failedLines))
        print("transferred lines = %d" % (self.transferredLines))

    def getNextLine(self):
        if not self.fileOk:
            return (0xFFFFFFFF, False, False)

        nextLine = self.comLogFile.readline()[:-1]
        hitLine = False
        timeInSecs = 0xFFFFFFFF
        ftpResult = False
        restartResult = False
        timeStamp = ""
        while not nextLine == '' and not hitLine:
            restartResult = False
            ftpResult = False
            lineSplit = re.findall(r"[\w.:\[\]_\-\(\)]+", nextLine)
            if not "++++++++++++++++++++" in nextLine:
                # no mcg startup
                # search for starting wayside FTP transaction
                if (len(lineSplit) == 10) and lineSplit[8] == "destination" and not lineSplit[9] == "127.0.0.1":
                    transactionID = lineSplit[5]
                    self.idDict.append(transactionID)
                    self.destLines += 1
                # search failed line containing '4 failed' with existing transactionID
                elif "4 failed" in nextLine:
                    transactionID = lineSplit[5]
                    if transactionID in self.idDict:
                        self.idDict.remove(transactionID)
                        hitLine = True
                        self.failedLines += 1
                # search success line containing 'transferred' with existing transactionID
                elif "transferred" in nextLine:
                    transactionID = lineSplit[5]
                    if transactionID in self.idDict:
                        hitLine = True
                        ftpResult = True
                        self.idDict.remove(transactionID)
                        self.transferredLines += 1

            else:
                hitLine = True
                restartResult = True

            if hitLine:
                strDate = lineSplit[0]
                strTime = lineSplit[1]
                lineTimestamp = time.strptime(strDate + " " + strTime, "%Y-%m-%d %H:%M:%S")
                timeInSecs = int(calendar.timegm(lineTimestamp))
                timeStamp = time.strftime("%d.%m.%Y %H:%M:%S", lineTimestamp)

            nextLine = self.comLogFile.readline()[:-1]

        return (timeInSecs, timeStamp, ftpResult, restartResult)


if __name__ == '__main__':
    parser = ComLogParser('comLog_all.log')
    if parser.isOk():
        lines = 0
        parsingOk = parser.getNextLine()
        while parsingOk[0] != -1:
            if parsingOk[2]:
                print("MCG restart")
            else:
                lines += 1
                print("timestamp: %d ftpResult: %s" % (int(parsingOk[0]), str(parsingOk[1])))
            parsingOk = parser.getNextLine()

        print("lines = %d" % (lines))
        parser.printStats()
