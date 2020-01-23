import os
import sys
import glob
import pprint

from Compiler_JackTokenizer     import JackTokenizer
from Compiler_CompilationEngine import CompilationEngine

class JackAnalyzer:
    def __init__(self):
        return

    def openFileorDir(self, path, in_ext=".jack", out_ext=".xml", out_dir="output"):
        in_flist = []
        out_flist = []        
        if os.path.isfile(path):
            in_file  = path
            out_file = os.path.split(in_file)[0] + "/../" + out_dir + '/' + os.path.basename(in_file).split('.', 1)[0] + out_ext
            in_flist.append(in_file)
            out_flist.append(out_file)              
        elif os.path.isdir(path):
           in_flist = glob.glob(path + "/*" + in_ext)
           for i in range(len(in_flist)):
               out_file = os.path.split(in_flist[i])[0] + "/../" + out_dir + '/' + os.path.basename(in_flist[i]).split('.', 1)[0] + out_ext
               out_flist.append(out_file)
               
        return in_flist, out_flist
    
    def Tokenizer2CompilationEngine(self, jack_flist, xml_flist):
        for i in range(len(jack_flist)):
            jack_file = jack_flist[i]
            xml_file  = xml_flist[i]            
            jt  = JackTokenizer(jack_file)
            # ce  = CompilationEngine(xml_file)
            
            while jt.hasMoreTokens():
                jt.advance()
                token_type = jt.tokenType()
                # if token_type != "NOT_TOKEN":
                
        return

    
if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        path = args[1]
        ja   = JackAnalyzer()
        in_flist, out_flist = ja.openFileorDir(path, ".jack", ".xml")
        print(in_flist)
        print(out_flist)
        ja.Tokenizer2CompilationEngine(in_flist, out_flist)
    else:
        print("Invalid Args! Enter path of jackfile for directory has jackfiles! ");
    
    sys.exit()
    
