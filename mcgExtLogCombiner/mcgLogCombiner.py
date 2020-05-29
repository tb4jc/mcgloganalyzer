"""
Created on 09.02.2016

@author: tburri
"""
import sys
import traceback
from pathlib import Path


class McgLogCombiner:
    """
    classdocs
    """
    mcgLogAllName = "mcgLog_all.log"

    def __init__(self, issueArchiveDir):
        """
        Constructor
        """
        issueArchivePath = Path(issueArchiveDir)
        if issueArchivePath.exists():
            try:
                mcgLogAllPath = issueArchivePath / McgLogCombiner.mcgLogAllName
                if mcgLogAllPath.exists():
                    mcgLogAllPath.unlink()
                mcgLogAllFile = mcgLogAllPath.open(mode='a', newline='')
                mcgExtLogPath = issueArchivePath / "usr" / "local" / "data" / "log"
                fileList = sorted(mcgExtLogPath.glob("mcgLogger.log*"), key=str, reverse=True)
                for file in fileList:
                    print("mcgLog file %s" % (str(file)))
                    with file.open(mode='r') as infile:
                        for line in infile:
                            mcgLogAllFile.write(line)
                        infile.close()
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)


if __name__ == "__main__":
    # extended issue archive
    mcgLogCombiner = McgLogCombiner("c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_009.z50009.NAT_1455092253")
    # normal issue archive
    mcgLogCombiner = McgLogCombiner("c:\\workspace\\TWCS\\___issues\\mcg-issue-archive_mcg.zz_502_129.z50129.NAT_1454659406")
