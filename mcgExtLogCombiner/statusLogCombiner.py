'''
Created on 09.02.2016

@author: tburri
'''
from pathlib import Path
import shutil
import tarfile
import sys, traceback

from mcgExtLogGlobalVariables import STAT_LOG_ALL_FILENAME,ARCHIVE_TYPE_EXTENDED,ARCHIVE_TYPE_NORMAL


class StatusLogCombiner():
    '''
    classdocs
    '''
    def __init__(self, archiveType, issueArchiveDir):
        '''
        Constructor
        '''
        self._statusLogHeader = ""
        self._type = "unknown"
        
        if archiveType == ARCHIVE_TYPE_EXTENDED:
            issueArchivePath = Path(issueArchiveDir)
            if issueArchivePath.exists():
                #filePart = "status_" + type
                #fileName = filePart + ".log"
                try:
                    tmpPath = issueArchivePath / "tmp"
                    tmpFileList = tmpPath.glob("status_*.log")
                    tmpFilePath = list(tmpFileList)[0]
                    #fileName = tmpFilePath.name
                    self._type = tmpFilePath.name.split('_')[1].split('.')[0]
                    statusLogAllPath = issueArchivePath / STAT_LOG_ALL_FILENAME
                    if statusLogAllPath.exists():
                        statusLogAllPath.unlink()
                    statusLogAllFile = statusLogAllPath.open(mode='a', newline='')
                    mcgExtLogPath = issueArchivePath / "usr" / "local" / "data" / "log" / "mcg_ext_log"
                    unpackPath = issueArchivePath / "unpackTmp"
                    if unpackPath.exists():
                        shutil.rmtree(str(unpackPath), True)
                    unpackPath.mkdir()
                    fileList = sorted(mcgExtLogPath.glob("status_*.tar.gz"), key=str, reverse=False)
                    firstFile = True
                    for file in fileList:
                        print("status %s file %s" % (self._type, str(file)))
                        tar = tarfile.open(str(file), 'r')
                        for item in tar:
                            tar.extract(item, str(unpackPath))
                        with (unpackPath / tmpFilePath.name).open(mode='r') as infile:
                            if firstFile:
                                firstFile = False
                            else:
                                #skip first line
                                self._statusLogHeader = infile.readline()[:-1]
                            for line in infile:
                                statusLogAllFile.write(line)
                            infile.close()
                    #tmpFilePath = issueArchivePath / "tmp" / fileName
                    with tmpFilePath.open(mode='r') as infile:
                        # skip header
                        infile.readline()
                        for line in infile:
                            statusLogAllFile.write(line)
                        infile.close()
                    statusLogAllFile.close()
                except BaseException:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback)
            else:
                self._statusLogHeader = "TIMESTAMP;EVENT"
                print("statusLogCombiner: nothing to do - is a 'normal' issue archive directory")

    def getStatusLogHeader(self):
        return self._statusLogHeader

    def getStatusLogType(self):
        return self._type

if __name__ == "__main__":

        # extended issue archive
    statusLogCombiner1 = StatusLogCombiner(ARCHIVE_TYPE_EXTENDED, "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_009.z50009.NAT_1455092253")
    print(statusLogCombiner1.getStatusLogHeader(), end='\n')
    print(statusLogCombiner1.getStatusLogType(),end='\n')

    # normal issue archive
    statusLogCombiner2 = StatusLogCombiner(ARCHIVE_TYPE_NORMAL, "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_129.z50129.NAT_1454659406")
    print(statusLogCombiner2.getStatusLogHeader(), end='\n')
    print(statusLogCombiner2.getStatusLogType(),end='\n')

