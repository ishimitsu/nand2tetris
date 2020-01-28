import os
import sys
import glob
import pprint

class CompilationEngine:

    tag_terminal = {
        "KEYWORD"     : "keyword",
        "SYMBOL"      : "symbol",
        "INT_CONST"   : "integerConstant",
        "STRING_CONST": "stringConstant",
        "IDENTIFIER"  : "identifier"
    }
    terminal_keyWord = {
        "class"       : "CLASS",
        "method"      : "METHOD",
        "function"    : "FUNCTION",
        "constructor" : "CONSTRUCTOR",
        "int"         : "INT",
        "boolean"     : "BOOLEAN",
        "char"        : "CHAR",
        "void"        : "VOID",
        "var"         : "VAR",
        "static"      : "STATIC",
        "field"       : "FIELD",
        "let"         : "LET",
        "do"          : "DO",
        "if"          : "IF",
        "else"        : "ELSE",
        "while"       : "WHILE",
        "return"      : "RETURN",
        "true"        : "TRUE",
        "false"       : "FALSE",
        "null"        : "NULL",
        "this"        : "THIS"
    }
    
    tag_non_terminal_symbol = {
        "class", "classVarDec", "subroutineDec", "parameterList", "subroutineBody", "varDec",
        "statements", "whileStatement", "ifStatement", "returnStatement", "letStatement", "doStatement",
        "expression", "term", "expressionList"}
    
    def __init__(self, file, tokenizer):
        # self.fp = open(file, mode='w')
        self.tokenizer    = tokenizer
        self.indent_level = 0
        self.indent       = ""
        return

    def writeFile(self, code):
        indent = "  " * self.indent_level        
        # self.fp.write(indent + code + '\n')
        print(indent + code) # debug
        return

    def writeTerminal(self, expect_type, expect=""):
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
            if keyWord == expect:
                markup = "<" + tag + "> " + keyWord + " </" + tag + ">"   
        elif expect_type == "SYMBOL" and token_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            if symbol == expect:
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
            print("Current token[",  token, "]/type[", token_type, "] doesn't match expect token[", expect, "]/type[", expect_type, "]")
            
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
        '''
        'class' className '{' classVarDec* subroutineDec* '}'
        '''
        self.writeNonTerminalTagStart("class")
        
        self.writeTerminal("KEYWORD", "class") # 'class'
        self.writeTerminal("IDENTIFIER")       # className    
        self.writeTerminal("SYMBOL", "{")      # {

        # classVarDec*
        self.writeNonTerminalTagStart("classVarDec")
        self.writeNonTerminal("HogeHoge")        
        self.writeNonTerminalTagEnd("classVarDec")        

        # subroutineDec*
        self.writeNonTerminalTagStart("subroutineDec")
        self.writeNonTerminal("HogeHoge")
        self.writeNonTerminalTagEnd("subroutineDec")        

        # self.writeTerminal("SYMBOL", "}") # }
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
    
