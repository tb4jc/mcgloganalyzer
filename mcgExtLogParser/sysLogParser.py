"""
Created on 10.02.2016

@author: tburri
"""
from pathlib import Path
import sys, time, re, traceback


class SysLogParser:
    """
    classdocs
    """
    NONE = 0
    GSM_ENGINE_UP = 1
    GSM_ENGINE_DOWN = 2
    PPP_FAILED = 3
    GSM_RESET = 4
    WLAN_ENGINE_UP = 5
    WLAN_ENGINE_DOWN = 6

    def __init__(self, filename):
        """
        Constructor
        """
        self.sysLogFilePath = filename
        self.fileOk = Path(filename).exists()
        if self.fileOk:
            self.sysLogFile = open(self.sysLogFilePath)
        else:
            print("File not found %s" % (filename))
        self.connectTimeFound = False
        self.uLastGsmUpTime = 0

    def isOk(self):
        return self.fileOk

    def getNextLine(self):
        if not self.fileOk:
            return (0xFFFFFFFF, 0, "")

        nextLine = self.sysLogFile.readline()[:-1]
        hitLine = False
        timeInSecs = 0xFFFFFFFF
        resultType = SysLogParser.NONE
        timeStamp = ""
        result = ""
        lastUpTimeToReset = ""
        try:
            while not nextLine == '' and not hitLine:
                # search for
                #     ppp/lte up/down
                #     ppp drops -> report connect time
                #     gsm engine resets

                # split line with reg ex
                lineSplit = re.findall(r"[\w.:\[\]]+", nextLine)
                if "Connect time" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.GSM_ENGINE_DOWN
                    self.connectTimeFound = True
                    result = "GSM down after " + lineSplit[6]
                elif "LTE now up" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.GSM_ENGINE_UP
                    result = "LTE up"
                elif "LTE now down" in nextLine:
                        hitLine = True
                        resultType = SysLogParser.GSM_ENGINE_DOWN
                        self.connectTimeFound = True
                        result = "LTE down"
                elif "Hangup (SIGHUP)" in nextLine:
                    # filter out last drop with 'Connect time'
                    if not self.connectTimeFound:
                        hitLine = True
                        resultType = SysLogParser.PPP_FAILED
                        result = "GSM connect failed"
                    else:
                        self.connectTimeFound = False
                elif "max number (10)" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.GSM_RESET
                    result = "GSM engine reset"
                elif "PPP now up" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.GSM_ENGINE_UP
                    result = "GSM up (%s/%s)" % (lineSplit[10], lineSplit[11])
                elif "WLAN now up" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.WLAN_ENGINE_UP
                    result = "WLAN up"
                elif "WLAN now down" in nextLine:
                    hitLine = True
                    resultType = SysLogParser.WLAN_ENGINE_DOWN
                    result = "WLAN down"

                if hitLine:
                    strTimeStamp = nextLine[:15]
                    lineTimestamp = time.strptime(time.strftime("%Y ") + strTimeStamp, "%Y %b %d %H:%M:%S")
                    timeInSecs = time.mktime(lineTimestamp)
                    timeStamp = time.strftime("%d.%m.%Y %H:%M:%S", lineTimestamp)
                    if resultType == SysLogParser.GSM_ENGINE_UP:
                        self.uLastGsmUpTime = timeInSecs
                    elif resultType in [SysLogParser.GSM_RESET, SysLogParser.GSM_ENGINE_DOWN]:
                        diff = timeInSecs - self.uLastGsmUpTime
                        sDiff = time.gmtime(diff)
                        lastUpTimeToReset = time.strftime("%H:%M:%S", sDiff)
                else:
                    nextLine = self.sysLogFile.readline()[:-1]
        except BaseException:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(exc_type)
            print(exc_value)
            traceback.print_tb(exc_traceback)
            timeInSecs = 0xFFFFFFFF
            timeStamp = ""
            resultType = SysLogParser.NONE
            result = ""

        return timeInSecs, timeStamp, resultType, result, lastUpTimeToReset


if __name__ == '__main__':
    parser = SysLogParser('sysLog_all.log')
    if parser.isOk():
        parsingOk = parser.getNextLine()
        timeInSecs = parsingOk[0]
        while timeInSecs > 0:
            resultType = parsingOk[1]
            result = parsingOk[2]
            if resultType == SysLogParser.PPP_CONNECT_TIME:
                print("timestamp: %d / PPP Connection Time = %s minutes" % (timeInSecs, result))
            elif resultType == SysLogParser.PPP_FAILED:
                print("timestamp: %d / %s" % (timeInSecs, result))
            elif resultType == SysLogParser.PPP_RESET:
                print("timestamp: %d / %s" % (timeInSecs, result))
            else:
                print("timestamp: %d / unsupported resultType %d" % (timeInSecs, resultType))
            parsingOk = parser.getNextLine()
            timeInSecs = parsingOk[0]
    else:
        print("parser not ok")
