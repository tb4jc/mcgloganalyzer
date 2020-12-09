"""
Created on 09.02.2016

@author: Thomas
"""
import argparse
import csv
import shutil
import stat
import tarfile
import time
import tkinter as tk
import traceback
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from tkinter import Frame, LEFT, RIGHT, Y, TOP, END
from tkinter import Text
from tkinter import Scrollbar

from mcgExtLogCombiner import *
from mcgExtLogWriter import *
from mcgExtLogParser import *

cmdLineRun = True
cIssueArchiveDir = ""
workingDir = ""
scrollTxt = None
startTime = time.process_time()


class scrollTxtArea:
    def __init__(self, root):
        frame = Frame(root)
        frame.pack()
        self.text = None
        self.textPad(frame)
        return

    def textPad(self, frame):
        # add a frame and put a text area into it
        textPad = Frame(frame)
        self.text = Text(textPad, height=25, width=90)

        # add a vertical scroll bar to the text area
        scroll = Scrollbar(textPad)
        self.text.configure(yscrollcommand=scroll.set)

        # pack everything
        self.text.pack(side=LEFT)
        scroll.pack(side=RIGHT, fill=Y)
        textPad.pack(side=TOP)
        return

    def insertText(self, txt):
        self.text.insert(END, txt)
        return


def printTxt(txt, e='\n', f=False):
    global cmdLineRun
    if cmdLineRun:
        print(txt, end=e, flush=f)
    else:
        global scrollTxt
        scrollTxt.insertText(txt + e)


def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    try:
        os.remove(name)
    except BaseException:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)


def timestampConverter(time_string, string_type='timestamp'):
    if string_type == 'timestamp':
        d = datetime.utcfromtimestamp(int(time_string))
        return d.strftime("%Y-%m-%d_%H.%M.%S")
    elif string_type == 'date-hour':
        d = datetime.strptime(time_string + "+0000", "%Y-%m-%d %H.%M.%S%z")
        return int(d.timestamp())


def handleFileOrDir(issueArchiveDirPath):
    global args
    global startTime
    isTarFile = issueArchiveDirPath.is_file()
    # if tar file -> first extract it ...
    if isTarFile:
        printTxt("Unpacking and evaluating MCG Issue Archive '%s' ..." % issueArchiveDirPath, e='', f=True)
        fileBase = issueArchiveDirPath.stem[:-4]  # removes .tar from file basename (file name without extension)
        fileBase_parts = fileBase.split('_')
        len_fileBase_parts = len(fileBase_parts)
        # check if it is an issue archive from automated test bench - starts with test case prefix
        if fileBase.startswith("TC-", 0, 3):
            mcgFQDN = '_'.join(fileBase_parts[3:4])
            len_fileBase_parts -= 2
        else:
            mcgFQDN = '_'.join(fileBase_parts[1:-1])

        workingDirPath = issueArchiveDirPath.parent
        if len_fileBase_parts == 3:
            str_timestamp = timestampConverter(fileBase_parts[-1])
            archiveDirPath = workingDirPath / (fileBase + '_' + str_timestamp)
        elif len_fileBase_parts == 4:
            str_timestamp = timestampConverter(' '.join(fileBase_parts[-2:]), "date-hour")
            archiveDirPath = workingDirPath / ('_'.join(fileBase_parts[0:-2]) + "_" + str(str_timestamp) + "_" + '_'.join(fileBase_parts[-2:]))

        if archiveDirPath.exists():
            shutil.rmtree(str(archiveDirPath), onerror=del_rw)
        archiveDirPath.mkdir(parents=True)
        tar = tarfile.open(str(issueArchiveDirPath), 'r')
        for item in tar:
            tar.extract(item, str(archiveDirPath))
        printTxt("done.", f=True)
        issueArchiveDir = str(archiveDirPath)
    else:
        printTxt("Evaluating MCG Issue Archive Directory '%s' ..." % issueArchiveDirPath, e='', f=True)
        filename_parts = issueArchiveDirPath.parts[-1].split('_')
        mcgFQDN = '_'.join(filename_parts[1:-3])
        issueArchiveDir = str(issueArchiveDirPath)

    fqdnLabels = mcgFQDN.split('.')
    deviceLabel = fqdnLabels[0]
    carLabel = fqdnLabels[1]
    consistLabel = fqdnLabels[2]
    fleetLabel = fqdnLabels[3]

    fileNamePrefix = fleetLabel + "_" + consistLabel + "_" + carLabel + "_" + deviceLabel

    # combine all files
    overWriteFlag = isTarFile or not args.skip_combine
    combiner = CombineLogs(issueArchiveDir, overWriteFlag)

    try:
        combinedCsvLogPath = Path(issueArchiveDir) / (fileNamePrefix + "_combinedCsvLogFile.csv")
        combinedExcelLogPath = Path(issueArchiveDir) / (fileNamePrefix + "_combinedCsvLogFile.xlsx")
        combinedExcelLogPath2 = Path(issueArchiveDir) / (fileNamePrefix + "_combinedCsvLogFile2.xlsx")
        combinedCsvLogFile = combinedCsvLogPath.open(mode='w', newline='')
        startTime = time.process_time()
        excelWriter = ExcelWriter(str(combinedExcelLogPath))

        newHeader = combiner.getStatusLogHeader()
        newHeader += ";Additional_Info;TimeToFail / AddInfo2\n"
        combinedCsvLogFile.write(newHeader)
        excelWriter.addHeaders(newHeader.split(';'))

        comLogParserInst = ComLogParser(str(Path(issueArchiveDir) / COM_LOG_ALL_FILENAME))
        sysLogParserInst = SysLogParser(str(Path(issueArchiveDir) / SYS_LOG_ALL_FILENAME))
        mcgLogParser = McgLogParser(str(Path(issueArchiveDir) / MCG_LOG_ALL_FILENAME))
        btclLogParserInst = BtclLogParser(str(Path(issueArchiveDir) / BTCL_LOG_ALL_FILENAME))

        if combiner.getArchiveType() == ARCHIVE_TYPE_EXTENDED:
            statLogFile = str(Path(issueArchiveDir) / STAT_LOG_ALL_FILENAME)
            statLogParserInst = StatLogParser(statLogFile, type)
            if comLogParserInst.isOk() and statLogParserInst.isOk() and sysLogParserInst.isOk() and btclLogParserInst.isOk():
                rssiResultMapPath = Path(issueArchiveDir) / (fileNamePrefix + "_rssiResultMap.csv")
                rssiResultMapFile = rssiResultMapPath.open(mode='w', newline='')
                rssiResultMapCsv = csv.DictWriter(rssiResultMapFile, delimiter=";", fieldnames=["rssi", "FTP Result"])
                rssiResultMapCsv.writeheader()
                comDropKmlWriter = KmlWriter(str(Path(issueArchiveDir) / (fileNamePrefix + "_ComDrops.kml")))
                kmlWriter = KmlWriter(str(Path(issueArchiveDir) / (fileNamePrefix + "_ComResults.kml")))

                writtenLines = 0
                statisticsTotal = 0
                statisticsSuccess = 0
                lastGsmUp = 0
                statusLogLine = statLogParserInst.getNextLine()
                comLogLine = comLogParserInst.getNextLine()
                lastFtpOkTimestamp = None
                sysLogLine = sysLogParserInst.getNextLine()
                btclLogLine = btclLogParserInst.getNextLine()
                try:
                    # skip all till first statusLogLine
                    while comLogLine[0] < statusLogLine[0]:
                        comLogLine = comLogParserInst.getNextLine()
                    while sysLogLine[0] < statusLogLine[0]:
                        sysLogLine = sysLogParserInst.getNextLine()
                    while btclLogLine[0] < statusLogLine[0]:
                        btclLogLine = btclLogParserInst.getNextLine()

                    lastStatusLogLine = statusLogLine
                    # loop over status all log file
                    while statusLogLine[0] < 0xFFFFFFFF:
                        if (statusLogLine[0] <= comLogLine[0]) and (statusLogLine[0] <= sysLogLine[0]) and (statusLogLine[0] <= btclLogLine[0]):
                            if True:
                                newLine = "%s;%s;;\n" % (statusLogLine[1], statusLogLine[2])
                                combinedCsvLogFile.write(newLine)
                                excelWriter.addRow(newLine.split(';')[:-1])
                            lastStatusLogLine = statusLogLine
                            statusLogLine = statLogParserInst.getNextLine()

                        elif (comLogLine[0] <= statusLogLine[0]) and (comLogLine[0] <= sysLogLine[0]) and (comLogLine[0] <= btclLogLine[0]):
                            # check which statusLogLine is nearer and use this values
                            diff1 = statusLogLine[0] - comLogLine[0]
                            diff2 = comLogLine[0] - lastStatusLogLine[0]
                            if diff1 < diff2:
                                statusLine = statusLogLine[2]
                            else:
                                statusLine = lastStatusLogLine[2]

                            # restart
                            if comLogLine[3]:
                                newLine = "%s;%s;%s;\n" % (comLogLine[1], statusLine, "Restart")
                            else:
                                # FTP event
                                statisticsTotal += 1
                                if comLogLine[2]:
                                    statisticsSuccess += 1
                                    lastFtpOkTimestamp = comLogLine
                                newLine = "%s;%s;%s;\n" % (
                                    comLogLine[1], statusLine, "FTP OK" if comLogLine[2] else "FTP Failed")
                                kmlWriter.addPlacemark(newLine, "FTP", comLogLine[2])
                                rssiResultMapCsv.writerow(
                                    {'rssi': newLine.split(';')[8], 'FTP Result': str(comLogLine[2])})
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            # fetch next comLog FTP result
                            comLogLine = comLogParserInst.getNextLine()
                        elif (sysLogLine[0] <= statusLogLine[0]) and (sysLogLine[0] <= comLogLine[0]) and (sysLogLine[0] <= btclLogLine[0]):
                            # check which statusLogLine is nearer and use this values
                            diff1 = statusLogLine[0] - sysLogLine[0]
                            diff2 = sysLogLine[0] - lastStatusLogLine[0]
                            if diff1 < diff2:
                                statusLine = statusLogLine[2]
                            else:
                                statusLine = lastStatusLogLine[2]

                            strTimeToFailColumn = sysLogLine[4]
                            if sysLogLine[2] == sysLogParserInst.GSM_RESET and lastFtpOkTimestamp is not None:
                                sDiff = sysLogLine[0] - lastFtpOkTimestamp[0]
                                strDiffTimestamp = time.strftime("%H:%M:%S", time.gmtime(sDiff))
                                strTimeToFailColumn = strTimeToFailColumn + ";" + strDiffTimestamp
                            newLine = "%s;%s;%s;%s\n" % (sysLogLine[1], statusLine, sysLogLine[3], strTimeToFailColumn)
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            kmlWriter.addPlacemarkPpp(newLine, sysLogLine[2], sysLogLine[3])
                            if not sysLogLine[2] == SysLogParser.GSM_ENGINE_UP:
                                comDropKmlWriter.addPlacemarkPpp(newLine, sysLogLine[2], sysLogLine[3])

                            # fetch next sysLog result
                            sysLogLine = sysLogParserInst.getNextLine()
                        elif (btclLogLine[0] <= statusLogLine[0]) and (btclLogLine[0] <= comLogLine[0]) and (btclLogLine[0] <= sysLogLine[0]):
                            # check which statusLogLine is nearer and use this values
                            diff1 = statusLogLine[0] - btclLogLine[0]
                            diff2 = btclLogLine[0] - lastStatusLogLine[0]
                            if diff1 < diff2:
                                statusLine = statusLogLine[2]
                            else:
                                statusLine = lastStatusLogLine[2]

                            newLine = "%s;%s;%s;\n" % (btclLogLine[1], statusLine, btclLogLine[2])
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))

                            # fetch next sysLog result
                            btclLogLine = btclLogParserInst.getNextLine()
                        else:
                            raise BaseException("Failure during parsing merged log files!")

                        writtenLines += 1

                except BaseException:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print(exc_type)
                    print(exc_value)
                    traceback.print_tb(exc_traceback)
                rssiResultMapFile.close()
                kmlWriter.finishFile()
                comDropKmlWriter.finishFile()
            else:
                print("Not all parser are not ok!")
        else:
            if comLogParserInst.isOk() and mcgLogParser.isOk() and sysLogParserInst.isOk() and btclLogParserInst.isOk():
                writtenLines = 0
                statisticsTotal = 0
                statisticsSuccess = 0
                comLogLine = comLogParserInst.getNextLine()
                mcgLogLine = mcgLogParser.getNextLine()
                sysLogLine = sysLogParserInst.getNextLine()
                btclLogLine = btclLogParserInst.getNextLine()
                lastFtpOkTimestamp = None
                try:
                    # iterate over files as long as any parser returns valid timestamp
                    while (sysLogLine[0] < 0xFFFFFFFF) or (comLogLine[0] < 0xFFFFFFFF) or (mcgLogLine[0] < 0xFFFFFFFF) or (btclLogLine[0] < 0xFFFFFFFF):
                        if (sysLogLine[0] <= comLogLine[0]) and (sysLogLine[0] <= mcgLogLine[0]) and (sysLogLine[0] <= btclLogLine[0]):
                            strTimeToFailColumn = sysLogLine[4]
                            if sysLogLine[2] == sysLogParserInst.GSM_RESET and lastFtpOkTimestamp is not None:
                                sDiff = sysLogLine[0] - lastFtpOkTimestamp[0]
                                strDiffTimestamp = time.strftime("%H:%M:%S", time.gmtime(sDiff))
                                strTimeToFailColumn = strTimeToFailColumn + ";" + strDiffTimestamp
                            newLine = "%s;%s;%s\n" % (sysLogLine[1], sysLogLine[3], strTimeToFailColumn)
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            # fetch next sysLog result
                            sysLogLine = sysLogParserInst.getNextLine()

                        elif (comLogLine[0] <= sysLogLine[0]) and (comLogLine[0] <= mcgLogLine[0]) and (comLogLine[0] <= btclLogLine[0]):
                            if comLogLine[3]:
                                newLine = "%s;%s;%s\n" % (comLogLine[1], "Restart", "")
                            else:
                                statisticsTotal += 1
                                if comLogLine[2]:
                                    statisticsSuccess += 1
                                    lastFtpOkTimestamp = comLogLine
                                newLine = "%s;%s;%s\n" % (
                                    comLogLine[1], "FTP OK" if comLogLine[2] else "FTP Failed", "")
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            # fetch next comLog FTP result
                            comLogLine = comLogParserInst.getNextLine()

                        elif (mcgLogLine[0] <= sysLogLine[0]) and (mcgLogLine[0] <= comLogLine[0]) and (mcgLogLine[0] <= btclLogLine[0]):
                            newLine = "%s;%s;%s\n" % (mcgLogLine[1], mcgLogLine[2], "")
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            # fetch next mcgLog result
                            mcgLogLine = mcgLogParser.getNextLine()
                        elif (btclLogLine[0] <= sysLogLine[0]) and (btclLogLine[0] <= comLogLine[0]) and (btclLogLine[0] <= mcgLogLine[0]):
                            newLine = "%s;%s;\n" % (btclLogLine[1], btclLogLine[2])
                            combinedCsvLogFile.write(newLine)
                            excelWriter.addRow(newLine.split(';'))
                            # fetch next mcgLog result
                            btclLogLine = mcgLogParser.getNextLine()
                        else:
                            raise BaseException("Failure during parsing merged log files!")

                        writtenLines += 1

                except BaseException:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print(exc_type)
                    print(exc_value)
                    traceback.print_tb(exc_traceback)
            else:
                print("any parser not ok")
        combinedCsvLogFile.close()
        excelWriter.finishFile()
        diffTime = time.process_time() - startTime
        print("Excel execution time is %f" % (diffTime,))

        # write statistics file
        printTxt("Written lines = %d" % (writtenLines))
        statisticsFilePath = Path(issueArchiveDir) / (fileNamePrefix + "_FTP_Statistics.txt")
        statisticsFile = statisticsFilePath.open(mode='w')
        printTxt("Statistics:")
        statisticsFile.write("Statistics:\n")
        printTxt("total FTP results = %d" % (statisticsTotal))
        statisticsFile.write("total FTP results = %d\n" % statisticsTotal)
        printTxt("total FTP success = %d" % (statisticsSuccess))
        statisticsFile.write("total FTP success = %d\n" % statisticsSuccess)
        if not statisticsTotal == 0:
            okTotalRatio = statisticsSuccess / statisticsTotal * 100
        else:
            okTotalRatio = 0.0
        printTxt("ratio %0.4f%%" % okTotalRatio)
        statisticsFile.write("Ok/Total-Ratio = %0.4f%%\n" % okTotalRatio)
        statisticsFile.close()
    except BaseException:
        print(sys.exc_info())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze a selected MCG Issue archive file or directory - with or without MGC Extended Logging')
    parser.add_argument('-s', '--skip-combine',
                        action='store_true',
                        help='If parameter is given, the program expects a MCG Issue Archive as input with already combined log files')
    parser.add_argument('fileOrDir', metavar='file/dir', nargs='?', default='none', help='archive or directory')

    args = parser.parse_args()
    if args.fileOrDir == "none":
        rootFrame = tk.Tk()
        rootFrame.withdraw()
        workingDirectory = filedialog.askdirectory(initialdir="C:/workspace/TWCS/___issues", title="Choose a Issue Archive Directory.")
        if workingDirectory == "":
            parser.print_help()
            sys.exit()
        else:
            cIssueArchiveDirPath = Path(workingDirectory)
            handleFileOrDir(cIssueArchiveDirPath)

    elif not args.fileOrDir == "none":
        cmdLineRun = True
        cIssueArchiveDirPath = Path(args.fileOrDir)
        if not cIssueArchiveDirPath.exists():
            printTxt("MCG Issue Archive file/dir '%s' doesn't exists!" % args.fileOrDir)
            sys.exit()
        handleFileOrDir(cIssueArchiveDirPath)
    else:
        rootFrame = tk.Tk()
        rootFrame.withdraw()
        cIssueArchiveDir = filedialog.askopenfilename(initialdir="C:/",
                                                      filetypes=(("MCG Issue Archives", "*.gz"), ("All Files", "*.*")),
                                                      title="Choose a file.")
        if not cIssueArchiveDir == "":
            handleFileOrDir(Path(cIssueArchiveDir))
        else:
            print("No file selected.")
