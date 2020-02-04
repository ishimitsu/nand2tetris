import os
import sys
import glob
import pprint

from Compiler_JackTokenizer     import JackTokenizer
from Compiler_CompilationEngine import CompilationEngine

class JackAnalyzer:
    def __init__(self):
        return

    def openFileorDir(self, path, in_ext=".jack", out_ext=".vm"):
        in_flist = []
        out_file = ""
        
        if os.path.isfile(path):
            in_file  = path
            out_file = os.path.split(path)[0] + '/' + os.path.basename(in_file).split('.', 1)[0] + out_ext
            in_flist.append(in_file)
        elif os.path.isdir(path):
           in_flist = glob.glob(path + "/*" + in_ext)
           out_file = path + '/' + os.path.basename(path) + out_ext
               
        return in_flist, out_file
    
    def Tokenizer2CompilationEngine(self, jack_flist, vm_file):
        for i in range(len(jack_flist)):
            jack_file = jack_flist[i]
            jt  = JackTokenizer(jack_file)
            
            ce  = CompilationEngine(vm_file, jt)
            ce.compileClass()
            ce.close()
        return

    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        path = args[1]
        ja   = JackAnalyzer()
        jack_flist, vm_file = ja.openFileorDir(path, ".jack", ".vm")
        print(jack_flist)
        print(vm_file)
        ja.Tokenizer2CompilationEngine(jack_flist, vm_file)
    else:
        print("Invalid Args! Enter path of jackfile for directory has jackfiles! ");
    
    sys.exit()
    
