import os
import sys
import glob
import pprint

class CompilationEngine:

    tag_terminal_symbol = {
        "KEYWORD"     : "keyword",
        "SYMBOL"      : "symbol",
        "INT_CONST"   : "integerConstant",
        "STRING_CONST": "stringConstant",
        "IDENTIFIER"  : "identifier"
    }
    tag_non_terminal_symbol = {
        "class", "classVarDec", "subroutineDec", "parameterList", "subroutineBody", "varDec",
        "statements", "whileStatement", "ifStatement", "returnStatement", "letStatement", "doStatement",
        "expression", "term", "expressionList"}
    
    def __init__(self, file, tokenizer):
        # self.fp = open(file, mode='w')
        self.tokenizer    = tokenizer
        self.indent_level = 0
        return

    def writeFile(self, code):
        # TODO: add TAB for indent        
        # self.fp.write(code + '\n')
        for i in range(self.indent_level):
            print("  ", end="")
        print(code) # debug
        return

    def writeTerminal(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        else:
            print("There is No tokens.")        
            return
        token      = self.tokenizer.cur_token                
        token_type = self.tokenizer.tokenType()        
        if not token_type in ["KEYWORD", "SYMBOL", "INT_CONST", "STRING_CONST", "IDENTIFIER"]:
            print("Ignored Invalid keyword token [", token, "]!")
            return

        tag    = self.tag_terminal_symbol.get(token_type, "")
        markup = "<"  + tag + "> " + token + " </" + tag + ">"  
        self.writeFile(markup)        
        return

    def writeNonTerminal(self, token):
        self.writeFile(token)        
        return
    def writeNonTerminalTagStart(self, tag):
        markup = "<" + tag + ">"
        self.writeFile(markup)        
        return
    def writeNonTerminalTagEnd(self, tag):
        markup = "</" + tag + ">"
        self.writeFile(markup)        
        return
    
    def close(self):
        # self.fp.close()
        return
    
    def compileClass(self):
        '''
        'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.writeNonTerminalTagStart("class")
        self.writeTerminal() # 'class'
        self.writeTerminal() # className
        self.writeTerminal() # {
        
        self.writeNonTerminalTagStart("classVarDec")
        self.writeNonTerminal("HogeHoge")        
        self.writeNonTerminalTagEnd("classVarDec")        

        self.writeNonTerminalTagStart("subroutineDec")
        self.writeNonTerminal("HogeHoge")
        self.writeNonTerminalTagEnd("subroutineDec")        

        # self.writeTerminal() # }
        self.writeNonTerminalTagEnd("class")        
        return 

    def compileClassVarDec(self):
        return 

    def compileSubroutine(self):
        return 

    def compileParameterList(self):
        return 

    def compileVarDec(self):
        return 

    def compileStatements(self):
        return 

    def compileDo(self):
        return 

    def compileLet(self):
        return 

    def compileWhile(self):
        return 

    def compileReturn(self):
        return 

    def compileIf(self):
        return 

    def compileExpression(self):
        # need look ahead
        return 

    def compileTerm(self):
        return 

    def compileExpressionList(self):
        return 
    
