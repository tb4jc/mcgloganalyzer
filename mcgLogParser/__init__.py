import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from mcgLogParser.clParser import ComLogParser
from mcgLogParser.statLogParser import StatLogParser
from mcgLogParser.sysLogParser import SysLogParser
from mcgLogParser.mlParser import McgLogParser
from mcgLogParser.btclLogParser import BtclLogParser

