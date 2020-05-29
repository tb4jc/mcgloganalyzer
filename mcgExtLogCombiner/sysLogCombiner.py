'''
Created on 09.02.2016

@author: tburri
'''
from pathlib import Path
import shutil
import tarfile
import os, sys, traceback

from mcgExtLogGlobalVariables import SYS_LOG_ALL_FILENAME,ARCHIVE_TYPE_EXTENDED,ARCHIVE_TYPE_NORMAL

class SysLogCombiner():
    '''
    classdocs
    '''
    def __init__(self, archiveType, issueArchiveDir):
        '''
        Constructor
        '''
        issueArchivePath = Path(issueArchiveDir)
        if issueArchivePath.exists():
            try:
                sysLogAllPath = issueArchivePath / SYS_LOG_ALL_FILENAME
                if sysLogAllPath.exists():
                    sysLogAllPath.unlink()
                sysLogAllFile = sysLogAllPath.open(mode='a', newline='')
                tmpFilePath= issueArchivePath / "tmp/messages"
                mcgLogPath = issueArchivePath / "usr" / "local" / "data" / "log"
                mcgExtLogPath = mcgLogPath/ "mcg_ext_log"
                if archiveType == ARCHIVE_TYPE_EXTENDED:
                    unpackPath = issueArchivePath / "unpackTmp"
                    if unpackPath.exists():
                        shutil.rmtree(str(unpackPath), True)
                    unpackPath.mkdir()
                    lastLogSize = 10240000
                    lastFilePathStr = ""
                    fileList = sorted(mcgExtLogPath.glob("syslog*.tar.gz"), key=str, reverse=False)
                    for file in fileList:
                        filePath = str(file)
                        tar = tarfile.open(filePath, 'r')
                        filesInTar = tar.getnames()
                        oldSyslogTar = "messages" in filesInTar
                        curFileSize = os.stat(str(file)).st_size
                        if not oldSyslogTar:
                            if lastFilePathStr != "":
                                print("syslog file %s" % (lastFilePathStr))
                                tar2 = tarfile.open(lastFilePathStr, 'r')
                                lastFilePathStr = ""
                                for item in tar2:
                                    tar2.extract(item, str(unpackPath))
                
                                unpackFilePath = unpackPath / "messages"
                                if not unpackFilePath.exists():
                                    unpackFilePath = unpackPath / "messages.0"
                                    if not unpackFilePath.exists():
                                        unpackFilePath = unpackPath / "messages.1"
                                with unpackFilePath.open(mode='r') as infile:
                                    for line in infile:
                                        sysLogAllFile.write(line)
                                    infile.close()

                            print("syslog file %s" % (filePath))
                            for item in tar:
                                tar.extract(item, str(unpackPath))
            
                            unpackFilePath = unpackPath / "messages.0"
                            if not unpackFilePath.exists():
                                unpackFilePath = unpackPath / "messages.1"
                            with unpackFilePath.open(mode='r') as infile:
                                for line in infile:
                                    sysLogAllFile.write(line)
                                infile.close()
                        else:
                            if (lastFilePathStr != "") and (curFileSize < lastLogSize):
                                print("syslog file %s" % (lastFilePathStr))
                                tar = tarfile.open(lastFilePathStr, 'r')
                                for item in tar:
                                    tar.extract(item, str(unpackPath))
                
                                unpackFilePath = unpackPath / "messages"
                                with unpackFilePath.open(mode='r') as infile:
                                    for line in infile:
                                        sysLogAllFile.write(line)
                                    infile.close()
                            lastLogSize = curFileSize
                            lastFilePathStr = str(file)
                else:
                    # iterate over syslog backups and concatenate messages files
                    dirList = sorted(mcgLogPath.glob("syslog_*"), key=str, reverse=False)
                    for aDir in dirList:
                        if aDir.is_dir():
                            msgFile = aDir / "messages"
                            print("syslog_backup file %s" % (str(msgFile)))
                            with msgFile.open(mode='r') as infile:
                                for line in infile:
                                    sysLogAllFile.write(line)
                                infile.close()
                    tmpPath = issueArchivePath / "tmp"
                    fileList = sorted(tmpPath.glob("messages.*"), key=str, reverse=True)
                    for file in fileList:
                        print("syslog file %s" % (str(file)))
                        with file.open(mode='r') as infile:
                            for line in infile:
                                sysLogAllFile.write(line)
                            infile.close()
        
                # if current syslog file exists in /tmp -> take it to merge
                # else use syslog_last.tar.gz from extended logger if it exists
                tmpFilePath= issueArchivePath / "tmp/messages"
                lastFilePath = mcgExtLogPath / "syslog_last.tar.gz"                
                if tmpFilePath.exists():
                    print("syslog file %s" % (str(tmpFilePath)))
                    with tmpFilePath.open(mode='r') as infile:
                        for line in infile:
                            sysLogAllFile.write(line)
                        infile.close()
                elif lastFilePath.exists():
                    tar = tarfile.open(str(lastFilePath), 'r')
                    for item in tar:
                        tar.extract(item, str(unpackPath))
    
                    unpackFilePath = unpackPath / "messages.0"
                    if not unpackFilePath.exists():
                        unpackFilePath = unpackPath / "messages.1"
                    with unpackFilePath.open(mode='r') as infile:
                        for line in infile:
                            sysLogAllFile.write(line)
                        infile.close()
                    
                sysLogAllFile.close()
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)

if __name__ == "__main__":
    syslogCombiner = SysLogCombiner(ARCHIVE_TYPE_EXTENDED, "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_009.z50009.NAT_1455092253")
    syslogCombiner = SysLogCombiner(ARCHIVE_TYPE_NORMAL, "c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_129.z50129.NAT_1454659406")
    