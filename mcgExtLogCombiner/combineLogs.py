"""
Created on 09.02.2016

@author: Thomas
"""
from pathlib import Path

from mcgExtLogCombiner.mcgExtLogGlobalVariables import ARCHIVE_TYPE_EXTENDED, ARCHIVE_TYPE_NORMAL, MCG_EXT_LOG_DIR
from mcgExtLogCombiner.comLogCombiner import ComLogCombiner
from mcgExtLogCombiner.mcgLogCombiner import McgLogCombiner
from mcgExtLogCombiner.btclLogCombiner import BtclLogCombiner
from mcgExtLogCombiner.statusLogCombiner import StatusLogCombiner
from mcgExtLogCombiner.sysInfoCombiner import SysInfoCombiner
from mcgExtLogCombiner.sysLogCombiner import SysLogCombiner


class CombineLogs(object):
    """
    classdocs
    """

    def __init__(self, issueArchiveDir, overwrite=False):
        """
        Constructor
        """
        self.issueArchiveDir = issueArchiveDir

        # check if extended logger issue archive
        mcgExtLogPath = Path(issueArchiveDir) / MCG_EXT_LOG_DIR
        if not mcgExtLogPath.exists():
            self.archiveType = ARCHIVE_TYPE_NORMAL
            print("'%s' is a NORMAL MCG Issue Archvie ..." % (issueArchiveDir,))
        else:
            self.archiveType = ARCHIVE_TYPE_EXTENDED
            print("'%s' is an EXTENDED MCG Issue Archvie ..." % (issueArchiveDir,))
            # sysInfo log only available with MCG Extended Logger
            self.sysInfo = SysInfoCombiner(self.issueArchiveDir)

        self.statLog = StatusLogCombiner(self.archiveType, issueArchiveDir)
        self._statusLogType = self.statLog.getStatusLogType()
        self._statusLogHeader = self.statLog.getStatusLogHeader()

        self.comLog = ComLogCombiner(self.archiveType, self.issueArchiveDir)
        self.mcgLog = McgLogCombiner(self.issueArchiveDir)
        self.btclLog = BtclLogCombiner(self.issueArchiveDir)
        self.sysLog = SysLogCombiner(self.archiveType, self.issueArchiveDir)

    def getArchiveType(self):
        return self.archiveType

    def getStatusLogHeader(self):
        if self.archiveType == ARCHIVE_TYPE_EXTENDED:
            return self._statusLogHeader
        else:
            return "TIMESTAMP"

    def getStatusLogType(self):
        return self._statusLogType


if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    workingDirectory = filedialog.askdirectory(initialdir="C:/workspace/TWCS/___issues",
                                               title="Choose a Issue Archive Directory.")
    if not workingDirectory == "":
        combineLog = CombineLogs(workingDirectory)
    else:
        print("No directory selected!")
