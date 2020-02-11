import os
import sys
import glob
import pprint
import re

from Compiler_SymbolTable     import SymbolTable

class CompilationEngine:

    # tag_terminal = {
    #     "KEYWORD"     : "keyword",
    #     "SYMBOL"      : "symbol",
    #     "INT_CONST"   : "integerConstant",
    #     "STRING_CONST": "stringConstant",
    #     "IDENTIFIER"  : "identifier"
    # }
    
    def __init__(self, tokenizer, vmwriter):
        # self.fp = open(file, mode='a')
        self.vmwriter       = vmwriter
        self.tokenizer      = tokenizer
        self.indent_level   = 0
        self.className = None
        
        self.nextToken() # get first token
        return

    def writeFile(self, code):
        # indent = "  " * self.indent_level        
        # self.fp.write(indent + code + '\n')
        # print(indent + code) # debug
        return
    
    def close(self):
        # self.fp.write('\n')        
        # self.fp.close()
        if self.tokenizer.hasMoreTokens():        
            print("[", self.vmwriter.fname, "] Compile failed! There are some tokens aren't compiled yet.")
            print("rest token :", self.tokenizer.cur_token)
        else:
            print("[", self.vmwriter.fname, "] All tokens Compile finished.")            
        return
    
    def nextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            return True
            
        return False
    
    def isTerminal(self, expect_type, expect_token=None):
        '''
        analysis terminal that is correct syntax or not
        '''
        token_type = self.tokenizer.tokenType()
        ret        = False
        if expect_type == "KEYWORD" and token_type == "KEYWORD":
            keyWord = self.tokenizer.keyWord()
            keyWord = keyWord.lower()    # change lower case letters
            if not re.fullmatch(expect_token, keyWord) == None:
                ret = True
        elif expect_type == "SYMBOL" and token_type == "SYMBOL":
            symbol = self.tokenizer.symbol()
            if not re.fullmatch(expect_token, symbol) == None:
                ret = True                
        elif (expect_type == "INT_CONST" and token_type == "INT_CONST") or \
             (expect_type == "STRING_CONST" and token_type == "STRING_CONST") or\
             (expect_type == "IDENTIFIER" and token_type == "IDENTIFIER") :
            ret = True                            

        return ret

    def analysisTerminal(self, expect_type, expect_token=None):
        '''
        only analysis correct syntax or not, doesn't write VMcode, and change target to next token. 
        '''
        ret = None
        if self.isTerminal(expect_type, expect_token):
            if expect_type == "KEYWORD":
                ret = self.tokenizer.keyWord().lower() # change lower case letters
            elif expect_type == "SYMBOL":
                ret = self.tokenizer.symbol()
            elif expect_type == "INT_CONST":
                ret = self.tokenizer.intVal()
            elif expect_type == "STRING_CONST":
                ret = self.tokenizer.stringVal()
            elif expect_type == "IDENTIFIER":
                ret = self.tokenizer.identifier()

            self.nextToken() # If analysis is OK, change target to next token.
        else:
            token = self.tokenizer.cur_token
            raise Exception(token, 'are NOT same as expect', expect_token, expect_type)
            
        return ret
    
    def defineVMfunctionName(self, subroutineName):
        '''
        xxx() subroutine of  Yyy class => VM functionName is "Yyy.xxx"
        '''
        return self.className + "." + subroutineName

    def regIdentifier2SymbolTable(self, identifier, keyWord, dataType=None, kind="none"):
        category = None
        if keyWord in ["var", "argument", "static", "field", "class"]:
            category = keyWord
        elif keyWord in ["constructor", "function", "method"]:
            # from compileSubroutine()
            category = "subroutine"
        else:
            print(identifier, "has Invalid keyWord", keyWord, ", so ignored.")
            return
        
        if not kind in ["var", "argument", "static", "field"]:
            print(identifier, "has Invalid kind", kind, ", so ignored.")
            return
            
        self.symboltable.define(identifier, dataType, kind)
        # DefOrUse = "defined"        
        # idx    = str(self.symboltable.indexOf(identifier))
        # symbol = " (" + category +  ", " + DefOrUse + ", " + dataType + ", " + kind + ", " + idx +  ")"
        # tag    = self.tag_terminal.get("IDENTIFIER", "")
        # markup = "<" + tag + "> " + identifier + symbol + " </" + tag + ">"
        
        return

    def compileClass(self):
        '''  
        'class' className '{' classVarDec* subroutineDec* '}'  
        '''
        self.symboltable = SymbolTable() # create SymbolTable for this class
        
        self.analysisTerminal("KEYWORD", "class")
        self.className = self.analysisTerminal("IDENTIFIER")  
        self.analysisTerminal("SYMBOL", "{")
        # classVarDec*
        while self.isTerminal("KEYWORD", "static|field"):
            self.compileClassVarDec()
        # subroutineDec*
        while self.isTerminal("KEYWORD", "constructor|function|method"):     
            self.compileSubroutine()  
        self.analysisTerminal("SYMBOL", "}")            
        
        return 
    
    def compileClassVarDec(self):
        '''  
        ('static' | 'field') type varName (',' varName)* ';'  
        '''
        keyWord  = kind = self.analysisTerminal("KEYWORD", "static|field")
        dataType = self.compileType()
        varName  = self.analysisTerminal("IDENTIFIER")        
        self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)  # varName
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ","):
            self.analysisTerminal("SYMBOL", ",")
            varName = self.analysisTerminal("IDENTIFIER")
            self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)
        self.analysisTerminal("SYMBOL", ";")

        # TODO: static values => push static segment        
        return 

    def compileType(self):
        '''  
        'int' | 'char' | 'boolean' | className  
        '''
        ret = None
        if self.isTerminal("KEYWORD", "int|char|boolean"):
            ret = self.analysisTerminal("KEYWORD", "int|char|boolean")
        elif self.isTerminal("IDENTIFIER"):
            ret = self.analysisTerminal("IDENTIFIER") # className

        return ret
        
    def compileSubroutine(self):
        '''
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName 
        '(' parameterList ')' subroutineBody
        '''
        self.symboltable.startSubroutine()        
        
        objType = self.analysisTerminal("KEYWORD", "constructor|function|method")
        # ('void' | type)
        if self.isTerminal("KEYWORD", "void"):
            # TODO: Return 0            
            self.analysisTerminal("KEYWORD", "void")
        else:
            # TODO: Return Val                        
            self.compileType()
        subroutineName = self.analysisTerminal("IDENTIFIER")
        self.analysisTerminal("SYMBOL", "\(")
        numArgs        = self.compileParameterList(objType)
        self.analysisTerminal("SYMBOL", "\)")

        # TODO:writeVMCode, pop arguments from stack                        
        '''
        if VMfunc is method, you need to add VMcode that set "this" segment base.
        if VMfunc is constructor, you need to Memory.alloc(size) for the object, 
        and set "this" segment base to the alloc-obj base.
        '''
        VMfunctionName = self.defineVMfunctionName(subroutineName)        
        self.vmwriter.writeFunction(VMfunctionName, numArgs)
        if objType == "method" and args == 0:
            # if VMfunc is "method", need to push refer-obj "this" as first-argument (like python self)
            self.vmwriter.writePush("argument", 0)
            self.vmwriter.writePop("pointer", 0)

        self.compileSubroutineBody()
        
        return 

    def compileParameterList(self, objType):
        '''  
        ((type varName) (',' type varName)*)?  
        '''
        numArgs = 0        
        if objType == "method":
            '''
            constructor|function => VM function has numArgs
            method               => VM function has numArgs+1, Arg0 refers this.
            '''
            self.regIdentifier2SymbolTable("this", "argument", self.className, kind)
            numArgs += 1
            
        if self.isTerminal("KEYWORD", "int|char|boolean") or self.isTerminal("IDENTIFIER"): # type
            keyWord = kind = "argument"
            
            dataType = self.compileType()            
            varName = self.analysisTerminal("IDENTIFIER")            
            self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)
            # (',' type varName)*
            numArgs += 1
            while self.isTerminal("SYMBOL", ","):
                self.analysisTerminal("SYMBOL", ",")
                dataType = self.compileType()
                varName = self.analysisTerminal("IDENTIFIER")            
                self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)
                numArgs += 1

        return numArgs

    def compileSubroutineBody(self):
        '''  '{' varDec* statements '}'  '''        
        self.analysisTerminal("SYMBOL", "{")
        # varDec*        
        while self.isTerminal("KEYWORD", "var"):
            self.compileVarDec()
            
        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")
        return 
    
    def compileVarDec(self):
        '''  
        'var' type varName (',' varName)* ';'  
        '''
        # TODO: writeVMcode, need local-val(in SymbolTable) to push "local" segment 
        keyWord = kind = "var"
        self.analysisTerminal("KEYWORD", keyWord)
        dataType = self.compileType()
        varName  = self.analysisTerminal("IDENTIFIER")
        self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ","):
            self.analysisTerminal("SYMBOL", ",")
            varName  = self.analysisTerminal("IDENTIFIER")
            self.regIdentifier2SymbolTable(varName, keyWord, dataType, kind)
        self.analysisTerminal("SYMBOL", ";")
        return 

    def compileStatements(self):
        '''  statement*  '''        
        while self.isTerminal("KEYWORD", "let|if|while|do|return"):
            self.compileStatement()
        return 

    def compileStatement(self):
        '''  
        letStatement | ifStatement | whileStatement | doStatement | returnStatement  
        '''
        if self.isTerminal("KEYWORD", "let"):
            self.compileLet()
        elif self.isTerminal("KEYWORD", "if"):
            self.compileIf()
        elif self.isTerminal("KEYWORD", "while"):
            self.compileWhile()
        elif self.isTerminal("KEYWORD", "do"):
            self.compileDo()
        elif self.isTerminal("KEYWORD", "return"):
            self.compileReturn()
        return
    
    def compileDo(self):
        '''  
        'do' subroutineCall ';'  
        '''        
        self.analysisTerminal("KEYWORD", "do")
        self.compileSubroutineCall();
        self.analysisTerminal("SYMBOL", ";")
        return 

    def compileLet(self):
        '''  
        'let' varName ('[' expression ']')? '=' expression ';'  
        '''        
        self.analysisTerminal("KEYWORD", "let")
        self.analysisTerminal("IDENTIFIER") # varName

        if self.isTerminal("SYMBOL", "\["):
            self.analysisTerminal("SYMBOL", "\[")
            self.compileExpression()
            self.analysisTerminal("SYMBOL", "\]")

        self.analysisTerminal("SYMBOL", "\=")
        self.compileExpression()            
        self.analysisTerminal("SYMBOL", ";")

        # TODO:writeVMcode
        return 

    def compileWhile(self):
        '''  
        'while' '(' expression ')' '{' statements '}'
        '''        
        self.analysisTerminal("KEYWORD", "while")
        self.analysisTerminal("SYMBOL", "\(")
        self.compileExpression()
        self.analysisTerminal("SYMBOL", "\)")        
        self.analysisTerminal("SYMBOL", "{")
        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")

        # TODO:writeVMcode        
        return 

    def compileReturn(self):
        '''
        'return' expression? ';'
        '''        
        self.analysisTerminal("KEYWORD", "return")
        if self.isExpression():
            self.compileExpression()
            # TODO:writeVMcode, return val
        else:
            # void-func should return 0. And the code call void-func, should pop return-val=0
            self.vmwriter.writePush("constant", 0)
            
        self.vmwriter.writeReturn()
        self.analysisTerminal("SYMBOL", ";")

        return 

    def compileIf(self):
        '''
        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        '''        
        self.analysisTerminal("KEYWORD", "if")
        self.analysisTerminal("SYMBOL", "\(")
        self.compileExpression()
        self.analysisTerminal("SYMBOL", "\)")

        self.analysisTerminal("SYMBOL", "{")
        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")          

        # ('else' '{' statements '}')?
        if self.isTerminal("KEYWORD", "else"):
            self.analysisTerminal("KEYWORD", "else")  
            self.analysisTerminal("SYMBOL", "{")
            self.compileStatements()
            self.analysisTerminal("SYMBOL", "}")

        # TODO:writeVMcode                    
        return 

    def compileExpression(self):
        '''
        term (op term)*  
        '''
        oplist = "\+|\-|\*|\/|\&|\||\<|\>|\="
        self.compileTerm()
        while self.isTerminal("SYMBOL", oplist):
            op = self.analysisTerminal("SYMBOL", oplist)
            self.compileTerm()

            if op == "+":
                self.vmwriter.writeArithmetic("add")
            elif op == "-":
                self.vmwriter.writeArithmetic("sub")
                # TODO neg case
            elif op == "*":
                # Use OS-func Math.multiply
                self.vmwriter.writeCall("Math.multiply", 2)
                
            # TODO: writeVMcode to each op                                                
            # elif op == "/":
                # Use OS-func Math.divide
            # elif op == "&":
            #     self.vmwriter.writeArithmetic("lt")                
            # elif op == "|":                
            # elif op == "<":
            #     self.vmwriter.writeArithmetic("lt")                 
            # elif op == ">":
            #     self.vmwriter.writeArithmetic("gt")                
            # elif op == "=":
            #     self.vmwriter.writeArithmetic("eq")                  

        return 
    
    def compileTerm(self):
        '''
        integerConstant | stringConstant | keywordConstant | varName | 
        varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        '''
        if self.isTerminal("INT_CONST"):
            intVal = self.analysisTerminal("INT_CONST")
            self.vmwriter.writePush("constant", intVal)
        elif self.isTerminal("STRING_CONST"):
            strVal = self.analysisTerminal("STRING_CONST")
            # TODO:writeVMcode
            # Use OS-constructor, String.new(length)
            # x="cc...c" => String.appendChar(nextChar)
        elif self.isTerminal("KEYWORD", "true|false|null|this"):            
            fixVal = self.analysisTerminal("KEYWORD", "true|false|null|this")
            # TODO:writeVMcode
            # false = null = 0, true=-1("push constant 1", and "neg")
        elif self.isTerminal("SYMBOL", "\("):
            self.analysisTerminal("SYMBOL", "\(")
            self.compileExpression()
            self.analysisTerminal("SYMBOL", "\)")
            # TODO:writeVMcode
        elif self.isTerminal("SYMBOL", "\-|\~"):
            # unaryOp term
            self.analysisTerminal("SYMBOL", "\-|\~")
            self.compileTerm()
            # TODO:writeVMcode, neg and boolean-neg
        elif self.isTerminal("IDENTIFIER"):
            # varName | varName '[' expression ']' | subroutineCall
            tmpName = self.analysisTerminal("IDENTIFIER") # varName | subroutineName
            if self.isTerminal("SYMBOL", "\["):
                # varName '[' expression ']'
                varName = tmpName
                self.analysisTerminal("SYMBOL", "\[")
                self.compileExpression()
                self.analysisTerminal("SYMBOL", "\]")
                # TODO:writeVMcode, memory-alloc can use OS-func Memory.alloc(size)
                # To access array value, "that" segment set head of array-addr,
                # and access it with "pointer 1" and "that 0"
            elif self.isTerminal("SYMBOL", "\("):
                # subroutineCall =>  subroutineName '(' expressionList ')'
                subroutineName = tmpName  
                self.analysisTerminal("SYMBOL", "\(")
                self.compileExpressionList()
                self.analysisTerminal("SYMBOL", "\)")
                # TODO:writeVMcode                
            elif self.isTerminal("SYMBOL", "\."):
                # subroutineCall =>  (className | varName) '.' subroutineName '(' expressionList ')'
                classOrvarName = tmpName                
                self.analysisTerminal("SYMBOL", "\.")
                subroutineName = self.analysisTerminal("IDENTIFIER")
                self.analysisTerminal("SYMBOL", "\(")
                self.compileExpressionList()
                self.analysisTerminal("SYMBOL", "\)")
                # TODO:writeVMcode                

        return 

    def isExpression(self):
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
           self.isTerminal("SYMBOL", "\-|\~"):
            ret = True

        return ret
    
    def compileSubroutineCall(self):
        '''
        subroutineName '(' expressionList ')' | 
        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        numArgs = 0
        head    = self.analysisTerminal("IDENTIFIER") # subroutineName | className | varName
        if self.isTerminal("SYMBOL", "\("):
            # subroutineName '(' expressionList ')'
            subroutineName = head
            self.analysisTerminal("SYMBOL", "\(")
            numArgs = self.compileExpressionList()
            self.analysisTerminal("SYMBOL", "\)")
        elif self.isTerminal("SYMBOL", "\."):
            # (className | varName) '.' subroutineName '(' expressionList ')'
            classOrvarName = head
            self.analysisTerminal("SYMBOL", "\.")
            subroutineName = self.analysisTerminal("IDENTIFIER")
            subroutineName = classOrvarName + "." + subroutineName # like className.subroutineName
            self.analysisTerminal("SYMBOL", "\(")
            numArgs = self.compileExpressionList()
            self.analysisTerminal("SYMBOL", "\)")

        # TODO:writeVMcode        
        # Before call Subroutine, you need push argument to stack.
        # argument_cnt = self.symboltable.varCount("argument")
        # for args in range(argument_cnt):
        #     self.vmwriter.writePush("argument", args)
        
        self.vmwriter.writeCall(subroutineName, numArgs)
        self.vmwriter.writePop("temp", 0) # TODO: Is it OK to pop retVal to temp segment ?
        
        return
    
    def compileExpressionList(self):
        '''
        (expression (',' expression)* )?
        '''
        ExpressionCnt = 0
        if self.isExpression():
            self.compileExpression()
            ExpressionCnt += 1
            while self.isTerminal("SYMBOL", ","):
                self.analysisTerminal("SYMBOL", ",")
                self.compileExpression()
                ExpressionCnt += 1                

        # TODO:writeVMcode                
        return ExpressionCnt
    
