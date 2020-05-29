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
import traceback
from pathlib import Path

from mcgExtLogCombiner.mcgExtLogGlobalVariables import BTCL_LOG_ALL_FILENAME, MCG_LOG_DIR


class BtclLogCombiner:
    """
    classdocs
    """

    def __init__(self, issueArchiveDir):
        """
        Constructor
        """
        issueArchivePath = Path(issueArchiveDir)
        if issueArchivePath.exists():
            try:
                btclLogAllPath = issueArchivePath / BTCL_LOG_ALL_FILENAME
                # clean up old files
                if btclLogAllPath.exists():
                    btclLogAllPath.unlink()

                btclLogAllFile = btclLogAllPath.open(mode='w', newline='')
                logDirPath = issueArchivePath / MCG_LOG_DIR
                fileList = sorted(logDirPath.glob("btcl_client.log*"), key=str, reverse=True)
                for file in fileList:
                    print("btcl_client.log file %s" % (str(file)))
                    with file.open(mode='r') as infile:
                        for line in infile:
                            btclLogAllFile.write(line)
                        infile.close()
            except BaseException:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)


if __name__ == "__main__":
    btclLogCombiner = BtclLogCombiner("e:\\Daten\\Bombardier\\M7\\mcg-issue-archive_mcg.car75988.cst75988.M7_1590749144_2020-05-29_10.45.44")
