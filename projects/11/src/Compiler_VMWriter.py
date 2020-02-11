import os
import sys
import glob
import pprint
import re  # for re.split

class VMWriter:
    SegmentList = {"argument", "local", "constant", "this", "that", "pointer", "temp"}
    Arithmetic = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
    
    def __init__(self, vm_file):
        self.fname = vm_file        
        self.fp = open(vm_file, mode='w')
        return 

    def close(self):
        self.fp.close()
        return
    
    def write(self, code):
        self.fp.write(code + '\n')
        return

    def writePush(self, segment, index):
        if not segment in self.SegmentList:
            print("Invalid Segment [", segment, " ", index, "! so Ignored.")
            return
        
        code = "push " + segment + " " + str(index)
        self.write(code)
        return

    def writePop(self, segment, index):
        if not segment in self.SegmentList:
            print("Invalid Segment [", segment, " ", index, "! so Ignored.")
            return
        
        code = "pop " + segment + " " + str(index)        
        self.write(code)
        return
    
    def writeArithmetic(self, command):
        if not command in self.Arithmetic:
            print("Invalid Arithmetic [", command, "! so Ignored.")
            return
        
        self.write(command)
        return
    
    def writeLabel(self, label):
        self.write("label " + label)
        return

    def writeGoto(self, label):
        self.write("goto " + label)
        return    

    def writeIf(self, label):
        self.write("if-goto " + label)
        return

    def writeCall(self, functionName, numArgs=0):
        code = "call " + functionName + " " + str(numArgs)
        self.write(code)
        return
    
    def writeFunction(self, functionName, numLocals=0):
        code = "function " + functionName + " " + str(numLocals)
        self.write(code)
        return
    
    def writeReturn(self):
        self.write("return")
        return
    
