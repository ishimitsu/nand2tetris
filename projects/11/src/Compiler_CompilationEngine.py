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
    
    def __init__(self, file, tokenizer):
        self.fp = open(file, mode='a')
        self.fname          = file
        self.tokenizer      = tokenizer
        self.indent_level   = 0
        self.compile_result = True
        self.nextToken() # get first token
        return

    def writeFile(self, code):
        indent = "  " * self.indent_level        
        self.fp.write(indent + code + '\n')
        # print(indent + code) # debug
        return
    
    def close(self):
        self.fp.write('\n')        
        self.fp.close()
        if self.tokenizer.hasMoreTokens():        
            print("[", self.fname, "] Compile failed! There are some tokens aren't compiled yet.")
            print("rest token :", self.tokenizer.cur_token)
            self.compile_result = False
        else:
            print("[", self.fname, "] All tokens Compile finished.")            
        return
    
    def nextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            return True
            
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
        elif (expect_type == "INT_CONST" and token_type == "INT_CONST") or \
             (expect_type == "STRING_CONST" and token_type == "STRING_CONST") or\
             (expect_type == "IDENTIFIER" and token_type == "IDENTIFIER") :
            ret = True
        # else:
            # token = self.tokenizer.cur_token
            # if not __debug__:
            #     print("Error: token[", token, "]/type[", token_type, "] doesn't match term[", expect_term, "]/type[", expect_type, "]")
            
        return ret
            
    def getTerminalMarkup(self, term_type):
        markup = ""
        tag    = self.tag_terminal.get(term_type, "")
        
        if term_type == "KEYWORD":
            keyWord = self.tokenizer.keyWord()
            markup = "<" + tag + "> " + keyWord.lower() + " </" + tag + ">"   # change lower case letters
        elif term_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            # <, >, & convert for XML Markup
            if symbol == "<":
                symbol = "&lt;"
            elif symbol == ">":
                symbol = "&gt;"
            elif symbol == "&":
                symbol = "&amp;"
            markup = "<" + tag + "> " + symbol + " </" + tag + ">" 
        elif term_type == "INT_CONST":
            int_const = self.tokenizer.intVal()
            markup = "<" + tag + "> " + str(int_const) + " </" + tag + ">"             
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
        self.writeTerminal("SYMBOL", "\(")        
        self.compileParameterList()
        self.writeTerminal("SYMBOL", "\)")
        self.compileSubroutineBody() 
        self.writeNonTerminalTagEnd("subroutineDec")        
        return 

    def compileParameterList(self):
        '''  
        ((type varName) (',' type varName)*)?  
        '''        
        self.writeNonTerminalTagStart("parameterList")

        if self.isTerminal("KEYWORD", "int|char|boolean") or self.isTerminal("IDENTIFIER"): # isType
            self.compileType()
            self.writeTerminal("IDENTIFIER") # varName
            # (',' type varName)*
            while self.isTerminal("SYMBOL", ",") == True:
                self.writeTerminal("SYMBOL", ",")
                self.compileType()
                self.writeTerminal("IDENTIFIER") # varName
                
        self.writeNonTerminalTagEnd("parameterList")        
        return 

    def compileSubroutineBody(self):
        '''  '{' varDec* statements '}'  '''        
        self.writeNonTerminalTagStart("subroutineBody")
        self.writeTerminal("SYMBOL", "{")
        # varDec*        
        while self.isTerminal("KEYWORD", "var") == True:
            self.compileVarDec()
        self.compileStatements()
        self.writeTerminal("SYMBOL", "}")        
        self.writeNonTerminalTagEnd("subroutineBody")        
        return 
    
    def compileVarDec(self):
        '''  
        'var' type varName (',' varName)* ';'  
        '''        
        self.writeNonTerminalTagStart("varDec")
        self.writeTerminal("KEYWORD", "var")
        self.compileType()
        self.writeTerminal("IDENTIFIER") # varName
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ",") == True:
            self.writeTerminal("SYMBOL", ",")
            self.writeTerminal("IDENTIFIER") # varName
        self.writeTerminal("SYMBOL", ";")
        self.writeNonTerminalTagEnd("varDec")               
        return 

    def compileStatements(self):
        '''  statement*  '''        
        self.writeNonTerminalTagStart("statements")
        while self.isTerminal("KEYWORD", "let|if|while|do|return") == True:
            self.compileStatement()
        self.writeNonTerminalTagEnd("statements")         
        return 

    def compileStatement(self):
        '''  
        letStatement | ifStatement | whileStatement | doStatement | returnStatement  
        '''
        if self.isTerminal("KEYWORD", "let") == True:
            self.compileLet()
        elif self.isTerminal("KEYWORD", "if") == True:
            self.compileIf()
        elif self.isTerminal("KEYWORD", "while") == True:
            self.compileWhile()
        elif self.isTerminal("KEYWORD", "do") == True:
            self.compileDo()
        elif self.isTerminal("KEYWORD", "return") == True:
            self.compileReturn()
            
        return
    
    def compileDo(self):
        '''  
        'do' subroutineCall ';'  
        '''        
        self.writeNonTerminalTagStart("doStatement")
        self.writeTerminal("KEYWORD", "do")
        self.compileSubroutineCall();
        self.writeTerminal("SYMBOL", ";")
        self.writeNonTerminalTagEnd("doStatement")        
        return 

    def compileLet(self):
        '''  
        'let' varName ('[' expression ']')? '=' expression ';'  
        '''        
        self.writeNonTerminalTagStart("letStatement")
        self.writeTerminal("KEYWORD", "let")
        self.writeTerminal("IDENTIFIER") # varName

        if self.isTerminal("SYMBOL", "\[") == True:
            self.writeTerminal("SYMBOL", "\[")
            self.compileExpression()
            self.writeTerminal("SYMBOL", "\]")

        self.writeTerminal("SYMBOL", "\=")
        self.compileExpression()            
        self.writeTerminal("SYMBOL", ";")
        
        self.writeNonTerminalTagEnd("letStatement")  
        return 

    def compileWhile(self):
        '''  
        'while' '(' expression ')' '{' statements '}'
        '''        
        self.writeNonTerminalTagStart("whileStatement")
        self.writeTerminal("KEYWORD", "while")
        self.writeTerminal("SYMBOL", "\(")
        self.compileExpression()
        self.writeTerminal("SYMBOL", "\)")        
        self.writeTerminal("SYMBOL", "{")
        self.compileStatements()
        self.writeTerminal("SYMBOL", "}")
        self.writeNonTerminalTagEnd("whileStatement")                
        return 

    def compileReturn(self):
        '''
        'return' expression? ';'
        '''        
        self.writeNonTerminalTagStart("returnStatement")
        self.writeTerminal("KEYWORD", "return")

        # TODO : isExpression() => isTerm()
        if self.isTerm() == True:
            self.compileExpression()
        self.writeTerminal("SYMBOL", ";")        

        self.writeNonTerminalTagEnd("returnStatement")      
        return 

    def compileIf(self):
        '''
        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        '''        
        self.writeNonTerminalTagStart("ifStatement")

        self.writeTerminal("KEYWORD", "if")
        self.writeTerminal("SYMBOL", "\(")
        self.compileExpression()
        self.writeTerminal("SYMBOL", "\)")

        self.writeTerminal("SYMBOL", "{")
        self.compileStatements()
        self.writeTerminal("SYMBOL", "}")          

        # ('else' '{' statements '}')?
        if self.isTerminal("KEYWORD", "else") == True:
            self.writeTerminal("KEYWORD", "else")  
            self.writeTerminal("SYMBOL", "{")
            self.compileStatements()
            self.writeTerminal("SYMBOL", "}")          

        self.writeNonTerminalTagEnd("ifStatement")         
        return 

    def compileExpression(self):
        '''
        term (op term)*  
        '''
        # symbol_regexp = re.escape('+|-|*|/|&|\||<|>|=')
        op = "\+|\-|\*|\/|\&|\||\<|\>|\="
        self.writeNonTerminalTagStart("expression")
        self.compileTerm()
        while self.isTerminal("SYMBOL", op) == True:
            self.writeTerminal("SYMBOL", op)
            self.compileTerm()
        self.writeNonTerminalTagEnd("expression")   

        return 
    
    def compileTerm(self):
        '''
        integerConstant | stringConstant | keywordConstant | varName | 
        varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        '''        
        self.writeNonTerminalTagStart("term")

        if self.isTerminal("INT_CONST") == True:
            self.writeTerminal("INT_CONST")
        elif self.isTerminal("STRING_CONST") == True:
            self.writeTerminal("STRING_CONST")
        elif self.isTerminal("KEYWORD", "true|false|null|this") == True:            
            self.writeTerminal("KEYWORD", "true|false|null|this")
        elif self.isTerminal("SYMBOL", "\(") == True:
            self.writeTerminal("SYMBOL", "\(")
            self.compileExpression()
            self.writeTerminal("SYMBOL", "\)")
        elif self.isTerminal("SYMBOL", "\-|\~") == True:
            # unaryOp term
            self.writeTerminal("SYMBOL", "\-|\~")
            self.compileTerm()
        elif self.isTerminal("IDENTIFIER") == True:
            # varName | varName '[' expression ']' | subroutineCall
            
            self.writeTerminal("IDENTIFIER") # varName | subroutineName
            if self.isTerminal("SYMBOL", "\[") == True:
                # '[' expression ']'                
                self.writeTerminal("SYMBOL", "\[")
                self.compileExpression()
                self.writeTerminal("SYMBOL", "\]")
            elif self.isTerminal("SYMBOL", "\(") == True:
                # subroutineCall =>  subroutineName '(' expressionList ')'
                self.writeTerminal("SYMBOL", "\(")
                self.compileExpressionList()
                self.writeTerminal("SYMBOL", "\)")
            elif self.isTerminal("SYMBOL", "\.") == True:
                # subroutineCall =>  (className | varName) '.' subroutineName '(' expressionList ')' 
                self.writeTerminal("SYMBOL", "\.")
                self.writeTerminal("IDENTIFIER") # subroutineName
                self.writeTerminal("SYMBOL", "\(")
                self.compileExpressionList()
                self.writeTerminal("SYMBOL", "\)")
        else:
            print("Invalid Term = [", self.tokenizer.cur_token, "]!")
                
        self.writeNonTerminalTagEnd("term")                
        return 

    def isTerm(self):
        '''
        integerConstant | stringConstant | keywordConstant | 
        varName | varName '[' expression ']' | subroutineCall | 
        '(' expression ')' | 
        unaryOp term
        '''
        ret = False
        if self.isTerminal("INT_CONST") == True or\
           self.isTerminal("STRING_CONST") == True or\
           self.isTerminal("KEYWORD", "true|false|null|this") == True or\
           self.isTerminal("IDENTIFIER") == True or\
           self.isTerminal("SYMBOL", "\(") == True or\
           self.isTerminal("SYMBOL", "\-|\~") == True:
            ret = True

        return ret
    
    def compileSubroutineCall(self):
        '''
        subroutineName '(' expressionList ')' | 
        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        self.writeTerminal("IDENTIFIER") # subroutineName | className | varName
        if self.isTerminal("SYMBOL", "\(") == True:
            # subroutineName '(' expressionList ')'
            self.writeTerminal("SYMBOL", "\(")
            self.compileExpressionList()
            self.writeTerminal("SYMBOL", "\)")
        elif self.isTerminal("SYMBOL", "\.") == True:
            # (className | varName) '.' subroutineName '(' expressionList ')' 
            self.writeTerminal("SYMBOL", "\.")
            self.writeTerminal("IDENTIFIER") # subroutineName
            self.writeTerminal("SYMBOL", "\(")
            self.compileExpressionList()
            self.writeTerminal("SYMBOL", "\)")
            
        return
    
    def compileExpressionList(self):
        '''
        (expression (',' expression)* )?
        '''        
        self.writeNonTerminalTagStart("expressionList")

        # TODO : isTerm()
        if self.isTerm() == True:
            self.compileExpression()
            
            while self.isTerminal("SYMBOL", ",") == True:
                self.writeTerminal("SYMBOL", ",")
                self.compileExpression()
        
        self.writeNonTerminalTagEnd("expressionList")        
        return 
    
