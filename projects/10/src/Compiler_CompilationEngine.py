import os
import sys
import glob
import pprint
import re

class CompilationEngine:

    tag_terminal = {
        "KEYWORD"     : "keyword",
        "SYMBOL"      : "symbol",
        "INT_CONST"   : "integerConstant",
        "STRING_CONST": "stringConstant",
        "IDENTIFIER"  : "identifier"
    }
    # terminal_keyWord = {
    #     "class"       : "CLASS",
    #     "method"      : "METHOD",
    #     "function"    : "FUNCTION",
    #     "constructor" : "CONSTRUCTOR",
    #     "int"         : "INT",
    #     "boolean"     : "BOOLEAN",
    #     "char"        : "CHAR",
    #     "void"        : "VOID",
    #     "var"         : "VAR",
    #     "static"      : "STATIC",
    #     "field"       : "FIELD",
    #     "let"         : "LET",
    #     "do"          : "DO",
    #     "if"          : "IF",
    #     "else"        : "ELSE",
    #     "while"       : "WHILE",
    #     "return"      : "RETURN",
    #     "true"        : "TRUE",
    #     "false"       : "FALSE",
    #     "null"        : "NULL",
    #     "this"        : "THIS"
    # }
    
    # tag_non_terminal_symbol = {
    #    "class", "classVarDec", "subroutineDec", "parameterList", "subroutineBody", "varDec",
    #    "statements", "whileStatement", "ifStatement", "returnStatement", "letStatement", "doStatement",
    #    "expression", "term", "expressionList"}
    
    def __init__(self, file, tokenizer):
        # self.fp = open(file, mode='w')
        self.tokenizer    = tokenizer
        self.indent_level = 0
        return

    def writeFile(self, code):
        indent = "  " * self.indent_level        
        # self.fp.write(indent + code + '\n')
        print(indent + code) # debug
        return

    def writeTerminal(self, expect_type, expect_term=""):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        else:
            print("There is No more tokens.")
            return
        token       = self.tokenizer.cur_token                                                          
        token_type  = self.tokenizer.tokenType()
        writeMarkup = False
        markup      = ""
        tag         =  self.tag_terminal.get(expect_type, "")
    
        if expect_type == "KEYWORD" and token_type == "KEYWORD":
            keyWord = self.tokenizer.keyWord()
            keyWord = keyWord.lower()    # change lower case letters
            if not re.fullmatch(expect_term, keyWord) == "None":
                markup = "<" + tag + "> " + keyWord + " </" + tag + ">"   
        elif expect_type == "SYMBOL" and token_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            if not re.fullmatch(expect_term, symbol) == "None":
                markup = "<" + tag + "> " + symbol + " </" + tag + ">" 
        elif expect_type == "INT_CONST" and token_type == "INT_CONST":
            int_const = self.tokenizer.intVal()
            markup = "<" + tag + "> " + int_const + " </" + tag + ">"             
        elif expect_type == "STRING_CONST" and token_type == "STRING_CONST":
            str_const = self.tokenizer.stringVal()            
            markup = "<" + tag + "> " + str_const + " </" + tag + ">"                             
        elif expect_type == "IDENTIFIER" and token_type == "IDENTIFIER":
            identifier = self.tokenizer.identifier()
            markup = "<" + tag + "> " + identifier + " </" + tag + ">"
            
        if len(markup) > 0:
            self.writeFile(markup)
        else:
            print("Error: Current token[",  token, "]/type[", token_type, "] doesn't match expect_term[", expect_term, "]/type[", expect_type, "]")
            
        return
    
    def writeNonTerminal(self, token):
        self.writeFile(token)        
        return
    def writeNonTerminalTagStart(self, tag):
        markup = "<" + tag + ">"
        self.writeFile(markup)
        self.indent_level += 1
        return
    def writeNonTerminalTagEnd(self, tag):
        self.indent_level -= 1        
        markup = "</" + tag + ">"
        self.writeFile(markup)
        return
    
    def close(self):
        # self.fp.close()
        return
    
    def compileClass(self):
        '''  'class' className '{' classVarDec* subroutineDec* '}'  '''
        self.writeNonTerminalTagStart("class")
        self.writeTerminal("KEYWORD", "class")
        self.writeTerminal("IDENTIFIER")   # className
        self.writeTerminal("SYMBOL", "{")
        self.compileClassVarDec()
        self.compileSubroutine()    
        self.writeTerminal("SYMBOL", "}")
        self.writeNonTerminalTagEnd("class")        
        return 
    
    def compileClassVarDec(self):
        '''  ('static' | 'field') type varName (',' varName)* ';'  '''
        self.writeNonTerminalTagStart("classVarDec")
        self.writeTerminal("KEYWORD", "static | field")
        self.compileType()
        self.writeTerminal("IDENTIFIER") # varName
        
        # TODO: (',' varName)*
        
        self.writeTerminal("SYMBOL", ";")
        self.writeNonTerminalTagEnd("classVarDec")        
        return 

    def compileType(self):
        '''  'int' | 'char' | 'boolean' | className  '''
        self.writeTerminal("KEYWORD", "int | char | boolean")
        # TODO: className
        return
        
    def compileSubroutine(self):
        '''
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName 
        '(' parameterList ')' subroutineBody
        '''        
        self.writeNonTerminalTagStart("subroutineDec")

        
        self.writeNonTerminalTagEnd("subroutineDec")        
        return 

    def compileParameterList(self):
        '''
        '''        
        self.writeNonTerminalTagStart("parameterList")
        self.writeNonTerminalTagEnd("parameterList")        
        return 

    def compileVarDec(self):
        '''
        '''        
        self.writeNonTerminalTagStart("varDec")
        self.writeNonTerminalTagEnd("varDec")               
        return 

    def compileStatements(self):
        '''
        '''        
        self.writeNonTerminalTagStart("statements")
        self.writeNonTerminalTagEnd("statements")         
        return 

    def compileDo(self):
        '''
        '''        
        self.writeNonTerminalTagStart("doStatement")
        self.writeNonTerminalTagEnd("doStatement")        
        return 

    def compileLet(self):
        '''
        '''        
        self.writeNonTerminalTagStart("letStatement")
        self.writeNonTerminalTagEnd("letStatement")  
        return 

    def compileWhile(self):
        '''
        '''        
        self.writeNonTerminalTagStart("whileStatement")
        self.writeNonTerminalTagEnd("whileStatement")                
        return 

    def compileReturn(self):
        '''
        '''        
        self.writeNonTerminalTagStart("returnStatement")
        self.writeNonTerminalTagEnd("returnStatement")      
        return 

    def compileIf(self):
        '''
        '''        
        self.writeNonTerminalTagStart("ifStatement")
        self.writeNonTerminalTagEnd("ifStatement")         
        return 

    def compileExpression(self):
        '''
        '''        
        self.writeNonTerminalTagStart("expression")
        # need look ahead        
        self.writeNonTerminalTagEnd("expression")   

        return 

    def compileTerm(self):
        '''
        '''        
        self.writeNonTerminalTagStart("term")
        self.writeNonTerminalTagEnd("term")                
        return 
    
    def compileExpressionList(self):
        '''
        '''        
        self.writeNonTerminalTagStart("expressionList")
        self.writeNonTerminalTagEnd("expressionList")        
        return 
    
