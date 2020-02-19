import os
import sys
import glob
import pprint

from Compiler_JackTokenizer     import JackTokenizer
from Compiler_CompilationEngine import CompilationEngine
from Compiler_VMWriter          import VMWriter

class JackAnalyzer:
    def __init__(self):
        return

    def openFileorDir(self, path, in_ext=".jack", out_ext=".vm"):
        in_flist  = []
        out_flist = []
        
        # if os.path.isfile(path):
        #     in_file  = path
        #     out_file = os.path.split(path)[0] + '/' + os.path.basename(in_file).split('.', 1)[0] + out_ext
        #     in_flist.append(in_file)
        # elif os.path.isdir(path):
        #    in_flist = glob.glob(path + "/*" + in_ext)
        #    out_file = path + '/' + os.path.basename(path) + out_ext

        # if os.path.exists(out_file):
        #     os.remove(out_file)
        
        if os.path.isfile(path):
            in_file  = path
            out_file = out_dirpath + os.path.basename(in_file).split('.', 1)[0] + out_ext
            in_flist.append(in_file)
            out_flist.append(out_file)              
        elif os.path.isdir(path):
           in_flist = glob.glob(path + "/*" + in_ext)
           out_dirpath = path + "/"
           for i in range(len(in_flist)):
               out_file = out_dirpath + os.path.basename(in_flist[i]).split('.', 1)[0] + out_ext
               out_flist.append(out_file)
        
        return in_flist, out_flist
    
    def Tokenizer2CompilationEngine(self, jack_flist, vm_file):
        for i in range(len(jack_flist)):
            jack_file = jack_flist[i]
            vmwriter  = VMWriter(vm_flist[i])            
            tokenizer = JackTokenizer(jack_file)
            compiler  = CompilationEngine(tokenizer, vmwriter)
            compiler.compileClass()
            compiler.close()

        vmwriter.close()
        return

    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        path = args[1]
        ja   = JackAnalyzer()
        jack_flist, vm_flist = ja.openFileorDir(path, ".jack", ".vm")
        print(jack_flist)
        print(vm_flist)
        ja.Tokenizer2CompilationEngine(jack_flist, vm_flist)
    else:
        print("Invalid Args! Enter path of jackfile for directory has jackfiles! ");
    
    sys.exit()
    
