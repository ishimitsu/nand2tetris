import os
import sys
import pprint

class CodeWriter:

    def __init__(self, file):
        if os.path.isfile(file):
            self.fp = open(file)
        return 

    def setFileName(self, FileName):
        return

    def writeArithmetic(self, command):
        return

    def writePushPop(self, command, segment, index):
        return

    def close(self, fp):
        self.fp.close()
        return
