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
        self.tokenizer      = tokenizer
        self.indent_level   = 0
        self.compile_result = True
        self.nextToken() # get first token
        return

    def writeFile(self, code):
        indent = "  " * self.indent_level        
        # self.fp.write(indent + code + '\n')
        print(indent + code) # debug
        return

    def nextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            return True
        else:
            print("There is No more tokens.")
            
        return False

    def isTerminal(self, expect_type, expect_term=""):
        token_type = self.tokenizer.tokenType()
        ret        = False
        if expect_type == "KEYWORD" and token_type == "KEYWORD":
            keyWord = self.tokenizer.keyWord()
            keyWord = keyWord.lower()    # change lower case letters
            if not re.fullmatch(expect_term, keyWord) == None:
                ret = True
        elif expect_type == "SYMBOL" and token_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            if not re.fullmatch(expect_term, symbol) == None:
                ret = True
        elif expect_type == "INT_CONST" and token_type == "INT_CONST":
            ret = True                         
        elif expect_type == "STRING_CONST" and token_type == "STRING_CONST":
            ret = True             
        elif expect_type == "IDENTIFIER" and token_type == "IDENTIFIER":
            ret = True                         
        else:
            token = self.tokenizer.cur_token                                                          
            # print("Error: token[", token, "]/type[", token_type, "] doesn't match term[", expect_term, "]/type[", expect_type, "]")
            self.compile_result = False
            
        return ret
            
    def getTerminalMarkup(self, term_type):
        markup = ""
        tag    = self.tag_terminal.get(term_type, "")
        
        if term_type == "KEYWORD":
            keyWord = self.tokenizer.keyWord()
            markup = "<" + tag + "> " + keyWord.lower() + " </" + tag + ">"   # change lower case letters
        elif term_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            markup = "<" + tag + "> " + symbol + " </" + tag + ">" 
        elif term_type == "INT_CONST":
            int_const = self.tokenizer.intVal()
            markup = "<" + tag + "> " + int_const + " </" + tag + ">"             
        elif term_type == "STRING_CONST":
            str_const = self.tokenizer.stringVal()            
            markup = "<" + tag + "> " + str_const + " </" + tag + ">"                             
        elif term_type == "IDENTIFIER":
            identifier = self.tokenizer.identifier()
            markup = "<" + tag + "> " + identifier + " </" + tag + ">"

        return markup

    def writeTerminal(self, expect_type, expect_term=""):
        if self.isTerminal(expect_type, expect_term) == True:
            markup = self.getTerminalMarkup(expect_type)  
            self.writeFile(markup)
            self.nextToken() # after write, refer next token
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
        self.writeTerminal("KEYWORD", "class")
        self.writeTerminal("IDENTIFIER")   # className
        self.writeTerminal("SYMBOL", "{")

        # classVarDec*
        while self.isTerminal("KEYWORD", "static|field") == True:
            self.compileClassVarDec()
        # subroutineDec*        
        while self.isTerminal("KEYWORD", "constructor|function|method") == True:     
            self.compileSubroutine()  
        
        self.writeTerminal("SYMBOL", "}")
        self.writeNonTerminalTagEnd("class")        
        return 
    
    def compileClassVarDec(self):
        '''  
        ('static' | 'field') type varName (',' varName)* ';'  
        '''
        self.writeNonTerminalTagStart("classVarDec")
        self.writeTerminal("KEYWORD", "static|field")
        self.compileType()
        self.writeTerminal("IDENTIFIER") # varName
        
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ",") == True:
            self.writeTerminal("SYMBOL", ",")
            self.writeTerminal("IDENTIFIER") # varName
                
        self.writeTerminal("SYMBOL", ";")
        self.writeNonTerminalTagEnd("classVarDec")
        return 

    def compileType(self):
        '''  
        'int' | 'char' | 'boolean' | className  
        '''
        if self.isTerminal("KEYWORD", "int|char|boolean"):
            self.writeTerminal("KEYWORD", "int|char|boolean")
        elif self.isTerminal("IDENTIFIER"):
            self.writeTerminal("IDENTIFIER") # className

        return
        
    def compileSubroutine(self):
        '''
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName 
        '(' parameterList ')' subroutineBody
        '''        
        self.writeNonTerminalTagStart("subroutineDec")
        self.writeTerminal("KEYWORD", "constructor|function|method")

        # ('void' | type)
        if self.isTerminal("KEYWORD", "void"):
            self.writeTerminal("KEYWORD", "void")
        else:
            self.compileType()
            
        self.writeTerminal("IDENTIFIER") # subroutineName
        self.compileParameterList()
        self.compileSubroutineBody() 
        self.writeNonTerminalTagEnd("subroutineDec")        
        return 

    def compileParameterList(self):
        '''  
        ((type varName) (',' type varName)*)?  
        '''        
        self.writeNonTerminalTagStart("parameterList")
        if self.isTerminal("SYMBOL", "\("):
            self.nextToken() # ignore "("
            
        self.compileType()
        self.writeTerminal("IDENTIFIER") # varName
        
        # (',' type varName)*
        while self.isTerminal("SYMBOL", ",") == True:
            self.writeTerminal("SYMBOL", ",")
            self.compileType()
            self.writeTerminal("IDENTIFIER") # varName

        if self.isTerminal("SYMBOL", "\)"):
            self.nextToken() # ignore ")"

        self.writeNonTerminalTagEnd("parameterList")        
        return 

    def compileSubroutineBody(self):
        '''  '{' varDec* statements '}'  '''        
        self.writeNonTerminalTagStart("subroutineBody")
        # TODO        
        self.writeNonTerminalTagEnd("subroutineBody")        
        return 
    
    def compileVarDec(self):
        '''  
        'var' type varName (',' varName)* ';'  
        '''        
        self.writeNonTerminalTagStart("varDec")
        # TODO        
        self.writeNonTerminalTagEnd("varDec")               
        return 

    def compileStatements(self):
        '''  statement*  '''        
        self.writeNonTerminalTagStart("statements")
        # TODO        
        self.writeNonTerminalTagEnd("statements")         
        return 

    def compileStatement(self):
        '''  
        letStatement | ifStatement | whileStatement | doStatement | returnStatement  
        '''        
        self.writeNonTerminalTagStart("statements")
        # TODO        
        self.writeNonTerminalTagEnd("statements")         
        return
    
    def compileDo(self):
        '''  
        'do' subroutineCall ';'  
        '''        
        self.writeNonTerminalTagStart("doStatement")
        # TODO        
        self.writeNonTerminalTagEnd("doStatement")        
        return 

    def compileLet(self):
        '''  
        'let' varName ('[' expression ']')? '=' expression ';'  
        '''        
        self.writeNonTerminalTagStart("letStatement")
        # TODO        
        self.writeNonTerminalTagEnd("letStatement")  
        return 

    def compileWhile(self):
        '''  
        'while' '(' expression ')' '{' statements '}'
        '''        
        self.writeNonTerminalTagStart("whileStatement")
        # TODO        
        self.writeNonTerminalTagEnd("whileStatement")                
        return 

    def compileReturn(self):
        '''
        'return' expression? ';'
        '''        
        self.writeNonTerminalTagStart("returnStatement")
        # TODO        
        self.writeNonTerminalTagEnd("returnStatement")      
        return 

    def compileIf(self):
        '''
        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        '''        
        self.writeNonTerminalTagStart("ifStatement")
        # TODO        
        self.writeNonTerminalTagEnd("ifStatement")         
        return 

    def compileExpression(self):
        '''
        term (op term)*  
        '''        
        self.writeNonTerminalTagStart("expression")
        # need look ahead
        # TODO        
        self.writeNonTerminalTagEnd("expression")   

        return 

    def compileTerm(self):
        '''
        integerConstant | stringConstant | keywordConstant | varName | 
        varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        '''        
        self.writeNonTerminalTagStart("term")
        # TODO                
        self.writeNonTerminalTagEnd("term")                
        return 
    
    def compileExpressionList(self):
        '''
        (expression (',' expression)* )?
        '''        
        self.writeNonTerminalTagStart("expressionList")
        # TODO                        
        self.writeNonTerminalTagEnd("expressionList")        
        return 
    
