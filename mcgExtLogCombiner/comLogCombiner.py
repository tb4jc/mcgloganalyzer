"""
Created on 09.02.2016

@author: tburri
"""
import os
import re
import shutil
import sys
import tarfile
import time
import calendar
import traceback
from pathlib import Path

from mcgExtLogCombiner.mcgExtLogGlobalVariables import ARCHIVE_TYPE_EXTENDED, ARCHIVE_TYPE_NORMAL, \
    COM_LOG_ALL_FILENAME, MCG_LOG_DIR, EXT_ARCHIVE_TYPE_FILENAME, NORMAL_ARCHIVE_TYPE_FILENAME


class ComLogCombiner:
    """
    classdocs
    """

    def __init__(self, archiveType, issueArchiveDir):
        """
        Constructor
        """
        issueArchivePath = Path(issueArchiveDir)
        if issueArchivePath.exists():
            try:
                comLogAllPath = issueArchivePath / COM_LOG_ALL_FILENAME
                # clean up old files
                if comLogAllPath.exists():
                    comLogAllPath.unlink()

                comLogAllFile = comLogAllPath.open(mode='a', newline='')
                logDirPath = issueArchivePath / MCG_LOG_DIR
                if archiveType == ARCHIVE_TYPE_EXTENDED:
                    archiveTypeFile = Path(issueArchivePath / EXT_ARCHIVE_TYPE_FILENAME).open(mode='w', newline='')
                    archiveTypeFile.write("extended archive file")
                    archiveTypeFile.close()
                    mcgExtLogPath = logDirPath / "mcg_ext_log"
                    unpackPath = issueArchivePath / "unpackTmp"
                    if unpackPath.exists():
                        shutil.rmtree(str(unpackPath), True)
                    unpackPath.mkdir()
                    fileList = sorted(mcgExtLogPath.glob("comLog*.tar.gz"), key=str, reverse=False)
                    lastFirstTimeStamp = 0
                    for file in fileList:
                        curFileSize = os.stat(str(file)).st_size
                        print("comLog file %s" % (str(file)))
                        tar = tarfile.open(str(file), 'r')
                        for item in tar:
                            tar.extract(item, str(unpackPath))
                        with (unpackPath / MCG_LOG_DIR / "comLogger.log.0").open(mode='r') as infile:
                            firstLine = True
                            for line in infile:
                                if firstLine:
                                    lineSplit = re.findall(r"[\w.:\[\]_\-\(\)]+", line)
                                    strDate = lineSplit[0]
                                    strTime = lineSplit[1]
                                    lineTimestamp = time.strptime(strDate + " " + strTime, "%Y-%m-%d %H:%M:%S")
                                    timeInSecs = int(calendar.timegm(lineTimestamp))
                                    if timeInSecs <= lastFirstTimeStamp:
                                        break
                                    else:
                                        lastFirstTimeStamp = timeInSecs
                                    firstLine = False
                                comLogAllFile.write(line)
                else:
                    archiveTypeFile = Path(issueArchivePath / NORMAL_ARCHIVE_TYPE_FILENAME).open(mode='w', newline='')
                    archiveTypeFile.write("normal archive file")
                    archiveTypeFile.close()
                    fileList = sorted(logDirPath.glob("comLogger.log.*"), key=str, reverse=False)
                    for file in fileList:
                        curFileSize = os.stat(str(file)).st_size
                        print("comLog file %s, size %d" % (str(file), curFileSize))
                        with file.open(mode='r') as infile:
                            for line in infile:
                                comLogAllFile.write(line)

                logFilePath = logDirPath / "comLogger.log"
                if logFilePath.exists():
                    print("comLog file %s" % (str(logFilePath)))
                    with logFilePath.open(mode='r') as infile:
                        for line in infile:
                            comLogAllFile.write(line)
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)


if __name__ == "__main__":
    comLogCombiner = ComLogCombiner(ARCHIVE_TYPE_EXTENDED,
                                    "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_183.z50183.NAT_1454929024")
    comLogCombiner = ComLogCombiner(ARCHIVE_TYPE_NORMAL,
                                    "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_129.z50129.NAT_1454659406")
