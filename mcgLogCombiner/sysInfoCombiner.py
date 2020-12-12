'''
Created on 09.02.2016

@author: tburri
'''
from pathlib import Path
import shutil
import tarfile
import sys, traceback

from mcgLogGlobalVariables import SYS_INFO_ALL_FILENAME

class SysInfoCombiner():
    '''
    classdocs
    '''
    def __init__(self, issueArchiveDir):
        '''
        Constructor
        '''
        issueArchivePath = Path(issueArchiveDir)
        if issueArchivePath.exists():
            try:
                sysInfoAllPath = issueArchivePath / SYS_INFO_ALL_FILENAME
                if sysInfoAllPath.exists():
                    sysInfoAllPath.unlink()
                sysInfoAllFile = sysInfoAllPath.open(mode='a', newline='')
                mcgLogPath = issueArchivePath / "usr" / "local" / "data" / "log" / "mcg_ext_log"
                unpackPath = issueArchivePath / "unpackTmp"
                if unpackPath.exists():
                    shutil.rmtree(str(unpackPath), True)
                unpackPath.mkdir()
                fileList = sorted(mcgLogPath.glob("sysinfo*.tar.gz"), key=str, reverse=False)
                for file in fileList:
                    print("sysInfo file %s" % (str(file)))
                    tar = tarfile.open(str(file), 'r')
                    for item in tar:
                        tar.extract(item, str(unpackPath))
                    with (unpackPath / "sysinfo.log").open(mode='r') as infile:
                        for line in infile:
                            sysInfoAllFile.write(line)
                        infile.close()
                tmpFilePath= issueArchivePath / "tmp/sysinfo.log"
                with tmpFilePath.open(mode='r') as infile:
                    for line in infile:
                        sysInfoAllFile.write(line)
                    infile.close()
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)

if __name__ == "__main__":
    sysInfoCombiner = SysInfoCombiner("c:\\workspace\\TWCS\\___issues\\mcg_ext_log_mcg-issue-archive_mcg.zz_502_355.z50355.NAT_1454932014")
        