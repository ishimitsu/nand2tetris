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

    def keyWord2Compiler(self, keyWord, Tokenizer, Compiler):
        keyWordType = jt.keyWord()

        # check .jack starts with "class"
        if Tokenizer.t_idx == 0 and not keyWordType == "CLASS":
            print("This Jack File is Invalid because it doesn't start with CLASS, so exit Analyzer!")
            sys.exit()
        
        if keyWordType   == "CLASS":
            Compiler.compileClass()
        elif keyWordType in ["STATIC", "FIELD"]:
            Compiler.compileClassVarDec()
        # elif keyWordType in ["INT", "CHAR", "BOOLEN"]:
        #     type
        elif keyWordType in ["METHOD", "FUNCTION", "CUNSTRUCTOR", "VOID"]:
            Compiler.compileSubroutine()
            # Compiler.compileParameterlist()
        elif keyWordType == "VAR":
            Compiler.compileVarDec()
        elif keyWordType == "DO":
            Compiler.compileDo()
        elif keyWordType == "LET":
            Compiler.compileLet()            
        elif keyWordType == "WHILE":
            Compiler.compileWhile()
        elif keyWordType == "RETURN":
            Compiler.compileReturn()
        elif keyWordType in ["IF", "ELSE"]:
            Compiler.compileIf()
        # elif keyWordType in ["TRUE", "FALSE", "NULL", "THIS"]:
        #     keyWordConstant
        else:
            print("Ignored Invalid keyWord token: ", Tokenizer.cur_token)
        
        return
    
    def Tokenizer2CompilationEngine(self, jack_flist, xml_flist):
        for i in range(len(jack_flist)):
            jack_file = jack_flist[i]
            jt  = JackTokenizer(jack_file)
            
            xml_file  = xml_flist[i]                        
            ce  = CompilationEngine(xml_file, jt)
            ce.compileClass()
            
            # while jt.hasMoreTokens():
            #     jt.advance()
            #     token_type = jt.tokenType()
            #     # print(jt.cur_token, "\t =>\t", token_type, end="\n")  
            #     if token_type   == "KEYWORD":
            #         self.keyWord2Compiler(jt, ce)
            #     elif token_type == "SYMBOL":
            #         symbol  = jt.symbol()
            #         # ce.compileExpression
            #     elif token_type == "INT_CONST":
            #         intval  = jt.intVal()
            #         # ce.compileExpression                    
            #     elif token_type == "STRING_CONST":
            #         strval  = jt.stringVal()
            #         # ce.compileExpression
            #     elif token_type == "IDENTIFIER":
            #         idt     = jt.identifier()
            #         # ce.compileTerm
            #     else :
            #         print("Ignored Invalid token: ", jt.cur_token)

            ce.close()
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
    
