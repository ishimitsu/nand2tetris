import os
import sys
import glob
import pprint
import re  # for re.split

class VMWriter:
    Segment = {
         "const", 
         "local",
         "arg",
         "this",
         "that",
         "pointer",
         "temp"
    }
        
    Arithmetic = {
        "add", "sub",
        "neg", "eq",
        "gt",  "lt",
        "and", "or", "not"
    }
    
    def __init__(self, vm_file):
        self.fp = open(vm_file, mode='w')
        return 

    def close(self):
        self.fp.close()
        return
    
    def writeVMCode2File(self, asmcode):
        self.fp.write(asmcode + '\n')
        return

    def writePush(self, segment, index):
        return

    def writePop(self, segment, index):
        return
    
    def writeArithmetic(self, command):
        return
    
    def writeLabel(self, label):
        return

    def writeGoto(self, label):
        return

    def writeIf(self, label):
        return

    def writeCall(self, functionName, numArgs=0):
        return
    
    def writeFunction(self, functionName, numLocals=0):
        return
    
    def writeReturn(self):
        return
    
