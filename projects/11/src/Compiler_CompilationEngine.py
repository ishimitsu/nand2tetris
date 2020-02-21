import os
import sys
import glob
import pprint
import re

from Compiler_SymbolTable     import SymbolTable

class CompilationEngine:

    def __init__(self, tokenizer, vmwriter):
        self.vmwriter       = vmwriter
        self.tokenizer      = tokenizer
        self.className = self.cur_subroutineName = self.cur_subroutineType = None
        self.label_idx_while = self.label_idx_if = 0

        self.nextToken() # get first token
        return

    def close(self):
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

    def getVMLabelWhile(self):
        label_idx  = str(self.label_idx_while)
        label_loop = self.className + "." + self.cur_subroutineName + ".WHILE_LOOP_" + label_idx
        label_end  = self.className + "." + self.cur_subroutineName + ".WHILE_END_"  + label_idx
        self.label_idx_while += 1
        return label_loop, label_end
    
    def getVMLabelIf(self):
        label_idx  = str(self.label_idx_if)        
        label_else = self.className + "." + self.cur_subroutineName + ".IF_ELSE_" + label_idx
        label_end  = self.className + "." + self.cur_subroutineName + ".IF_END_"  + label_idx
        self.label_idx_if += 1
        return label_else, label_end

    def append2SymbolTable(self, identifier, keyWord, dataType=None, kind="none"):
        if kind in ["var", "argument", "static", "field"]:
            self.symboltable.define(identifier, dataType, kind)
        else:
            print(identifier, "has Invalid kind", kind, ", so ignored.")
            return

        return
    
    def getSegment(self, varName):
        kind     = self.symboltable.kindOf(varName)
        index    = self.symboltable.indexOf(varName)
        dataType = self.symboltable.typeOf(varName)        
        segment  = None
        if kind == "argument":
            segment = "argument"
        elif kind == "var":
            segment = "local"
        elif kind == "static":
            segment = "static"
        elif kind == "field":
            segment = "this"
            
        return segment, index
    
    def pushIdentifier(self, varName):
        segment, index = self.getSegment(varName)
        self.vmwriter.writePush(segment, index)
        return

    def popIdentifier(self, varName):
        segment, index = self.getSegment(varName)
        self.vmwriter.writePop(segment, index)
        return
    
    def compileClass(self):
        '''  
        'class' className '{' classVarDec* subroutineDec* '}'  
        '''
        self.symboltable = SymbolTable()
        
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
        self.append2SymbolTable(varName, keyWord, dataType, kind)  # varName
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ","):
            self.analysisTerminal("SYMBOL", ",")
            varName = self.analysisTerminal("IDENTIFIER")
            self.append2SymbolTable(varName, keyWord, dataType, kind)
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
        
        self.cur_subroutineType = self.analysisTerminal("KEYWORD", "constructor|function|method")
        DataType = None
        # ('void' | type)
        if self.isTerminal("KEYWORD", "void"):
            Datatype = self.analysisTerminal("KEYWORD", "void")
        else:
            Datatype = self.compileType()
        self.cur_subroutineName = self.analysisTerminal("IDENTIFIER")
        
        self.analysisTerminal("SYMBOL", "\(")
        self.compileParameterList()
        self.analysisTerminal("SYMBOL", "\)")        

        self.compileSubroutineBody()
        
        return 

    def compileParameterList(self):
        '''  
        ((type varName) (',' type varName)*)?  
        '''
        if self.cur_subroutineType == "method":
            # method => VM function has numArgs+1, arg0=this refers "this" segment base addr(like self of python).
            self.append2SymbolTable("this", "argument", self.className, "argument")
            
        if self.isTerminal("KEYWORD", "int|char|boolean") or self.isTerminal("IDENTIFIER"):
            keyWord = kind = "argument"
            
            dataType = self.compileType()            
            varName = self.analysisTerminal("IDENTIFIER")            
            self.append2SymbolTable(varName, keyWord, dataType, kind)
            # (',' type varName)*
            while self.isTerminal("SYMBOL", ","):
                self.analysisTerminal("SYMBOL", ",")
                dataType = self.compileType()
                varName = self.analysisTerminal("IDENTIFIER")            
                self.append2SymbolTable(varName, keyWord, dataType, kind)

        return

    def compileSubroutineBody(self):
        '''  '{' varDec* statements '}'  '''
        numLocals = 0 
        self.analysisTerminal("SYMBOL", "{")
        # varDec*
        while self.isTerminal("KEYWORD", "var"):
            self.compileVarDec()
            numLocals += 1

        # "xxx()" subroutine of "Yyy" class => VM functionName is "Yyy.xxx"
        VMfunctionName = self.className + "." + self.cur_subroutineName
        numLocals      = self.symboltable.varCount("var")
        self.vmwriter.writeFunction(VMfunctionName, numLocals)

        if self.cur_subroutineType == "constructor":
            # if VMfunc is constructor, "this"=Memory.alloc(size of field) and return this.            
            numfield = self.symboltable.varCount("field")
            self.vmwriter.writePush("constant", numfield)
            self.vmwriter.writeCall("Memory.alloc", 1)
            self.vmwriter.writePop("pointer", 0)
            
        numArgs = self.symboltable.varCount("argument")                
        for args in range(numArgs):
            # push all argument from segment to stack
            self.vmwriter.writePush("argument", args)
            if self.cur_subroutineType == "method" and args == 0:
                # if VMfunc is "method", need to push arg0="this" to set it as "this" segment base.
                self.vmwriter.writePop("pointer", 0)

        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")
        return 

    def compileVarDec(self):
        '''  
        'var' type varName (',' varName)* ';'  
        varName of "var" is in "local" segment.
        compileVarDec() entry them to SymbolTable.
        '''
        keyWord = kind = "var"
        self.analysisTerminal("KEYWORD", keyWord)
        dataType = self.compileType()
        varName  = self.analysisTerminal("IDENTIFIER")
        self.append2SymbolTable(varName, keyWord, dataType, kind)
        # (',' varName)* ;
        while self.isTerminal("SYMBOL", ","):
            self.analysisTerminal("SYMBOL", ",")
            varName = self.analysisTerminal("IDENTIFIER")
            self.append2SymbolTable(varName, keyWord, dataType, kind)
            
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
        "do" ignore ret-val
        '''        
        self.analysisTerminal("KEYWORD", "do")
        self.compileSubroutineCall("do");
        self.analysisTerminal("SYMBOL", ";")

        self.vmwriter.writePop("temp", 0) # pop compieExpression() val from stack
        return 

    def compileLet(self):
        '''  
        'let' varName ('[' expression ']')? '=' expression ';'  
        '''
        isArrayAccess = False
        self.analysisTerminal("KEYWORD", "let")
        varName = self.analysisTerminal("IDENTIFIER")
        if self.isTerminal("SYMBOL", "\["):
            isArrayAccess = True
            self.analysisTerminal("SYMBOL", "\[")
            self.compileExpression()
            self.analysisTerminal("SYMBOL", "\]")
            
            self.pushIdentifier(varName)
            self.vmwriter.writeArithmetic("add") # pop address of *(varName + expression) to stack

        self.analysisTerminal("SYMBOL", "\=")
        self.compileExpression()
        self.analysisTerminal("SYMBOL", ";")

        if isArrayAccess:
            self.vmwriter.writePop("temp", 0)    # Once store result of " = expression;"
            self.vmwriter.writePop("pointer", 1) # get address of *(varName + expression) from stack
            self.vmwriter.writePush("temp", 0)   # push result of " = expression;" to stack
            
            self.vmwriter.writePop("that", 0)    # pop result result of " = expression;" to *(varName + expression)
        else:
            self.popIdentifier(varName) # pop result to segment of varName
        
        return 

    def compileWhile(self):
        '''  
        'while' '(' expression ')' '{' statements '}'
        Notice: if-goto in while should refers result of ~(conditional), please check P260
        '''
        label_loop, label_end = self.getVMLabelWhile()
        conditional = True
        self.vmwriter.writeLabel(label_loop)        
        self.analysisTerminal("KEYWORD", "while")
        self.analysisTerminal("SYMBOL", "\(")
        self.compileExpression(conditional)
        self.analysisTerminal("SYMBOL", "\)")
        self.vmwriter.writeArithmetic("not") # if-goto refers result of ~(conditional)        
        self.vmwriter.writeIf(label_end)
        
        self.analysisTerminal("SYMBOL", "{")
        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")
        self.vmwriter.writeGoto(label_loop)
        self.vmwriter.writeLabel(label_end)         
        
        return 

    def compileIf(self):
        '''
        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        Notice: if-goto in if should refers result of ~(conditional), please check P260
        '''
        label_else, label_end = self.getVMLabelIf()
        conditional = True
        self.analysisTerminal("KEYWORD", "if")
        self.analysisTerminal("SYMBOL", "\(")
        self.compileExpression(conditional)                
        self.analysisTerminal("SYMBOL", "\)")

        self.vmwriter.writeArithmetic("not") # if-goto refers result of ~(conditional)        
        self.vmwriter.writeIf(label_else)          
        self.analysisTerminal("SYMBOL", "{")
        self.compileStatements()
        self.analysisTerminal("SYMBOL", "}")
        self.vmwriter.writeGoto(label_end)        

        self.vmwriter.writeLabel(label_else)
        # ('else' '{' statements '}')?
        if self.isTerminal("KEYWORD", "else"):
            self.analysisTerminal("KEYWORD", "else")
            self.analysisTerminal("SYMBOL", "{")
            self.compileStatements()
            self.analysisTerminal("SYMBOL", "}")
            
        self.vmwriter.writeLabel(label_end)
            
        return 

    def compileReturn(self):
        '''
        'return' expression? ';'
        '''        
        self.analysisTerminal("KEYWORD", "return")
        if self.isExpression():
            self.compileExpression()
        else:
            # void-func should return 0. And the code call void-func, should pop return-val=0
            self.vmwriter.writePush("constant", 0)
            
        self.vmwriter.writeReturn()
        self.analysisTerminal("SYMBOL", ";")

        return 
    
    def compileExpression(self, conditional=False):
        '''
        term (op term)*  
        '''
        oplist = "\+|\-|\*|\/|\&|\||\<|\>|\="
        op     = None
        self.compileTerm()
        while self.isTerminal("SYMBOL", oplist):
            op = self.analysisTerminal("SYMBOL", oplist)
            self.compileTerm()

            if op == "+":
                self.vmwriter.writeArithmetic("add")
            elif op == "-":
                self.vmwriter.writeArithmetic("sub")
            elif op == "*":
                self.vmwriter.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vmwriter.writeCall("Math.divide", 2)
            elif op == "&":
                self.vmwriter.writeArithmetic("and")
            elif op == "|":
                self.vmwriter.writeArithmetic("or")                
            elif op == "<":
                self.vmwriter.writeArithmetic("lt")                 
            elif op == ">":
                self.vmwriter.writeArithmetic("gt")                
            elif op == "=":
                self.vmwriter.writeArithmetic("eq")                  

        if conditional:
            # This expression is conditional
            if op == None:
                # if there is no lt/gt/eq, it means "= True" omitted.
                self.vmwriter.writePush("constant", 1)
                self.vmwriter.writeArithmetic("neg")
                self.vmwriter.writeArithmetic("eq")                              
                
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
            strLen = len(strVal)
            self.vmwriter.writePush("constant", strLen)
            self.vmwriter.writeCall("String.new", 1)
            for i in range(strLen):
                c = ord(strVal[i])
                self.vmwriter.writePush("constant", c)
                self.vmwriter.writeCall("String.appendChar", 2)
            
        elif self.isTerminal("KEYWORD", "true|false|null|this"):            
            fixVal = self.analysisTerminal("KEYWORD", "true|false|null|this")
            if fixVal == "true":
                # true=-1
                self.vmwriter.writePush("constant", 1)
                self.vmwriter.writeArithmetic("neg")                
            elif fixVal == "false" or fixVal == "null":
                # false = null = 0
                self.vmwriter.writePush("constant", 0)
            elif fixVal == "this":
                self.vmwriter.writePush("pointer", 0) # return "this" segment base addr
                
        elif self.isTerminal("SYMBOL", "\("):
            self.analysisTerminal("SYMBOL", "\(")
            self.compileExpression()
            self.analysisTerminal("SYMBOL", "\)")
            
        elif self.isTerminal("SYMBOL", "\-|\~"):
            # unaryOp(-|~) term
            unaryOp = self.analysisTerminal("SYMBOL", "\-|\~")
            self.compileTerm()
            if unaryOp == "-":
                self.vmwriter.writeArithmetic("neg")
            elif unaryOp == "~":
                self.vmwriter.writeArithmetic("not")
                
        elif self.isTerminal("IDENTIFIER"):
            # varName | varName '[' expression ']' | subroutineCall
            tmpName = self.analysisTerminal("IDENTIFIER") # varName | subroutineName
            if self.isTerminal("SYMBOL", "\["):
                # varName '[' expression ']' => Array Access
                varName = tmpName
                self.analysisTerminal("SYMBOL", "\[")
                self.compileExpression()
                self.analysisTerminal("SYMBOL", "\]")

                self.pushIdentifier(varName)
                self.vmwriter.writeArithmetic("add")
                self.vmwriter.writePop("pointer", 1) # set pointer to *(varName + expression)
                self.vmwriter.writePush("that", 0)   # push the value of *(varName + expression)
                
            elif self.isTerminal("SYMBOL", "\(") or self.isTerminal("SYMBOL", "\."):
                # subroutineCall
                self.compileSubroutineCall("let", tmpName)
            else:
                # varName
                self.pushIdentifier(tmpName)  
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
    
    def compileSubroutineCall(self, flag, already_read_head=None):
        '''
        subroutineName '(' expressionList ')' | 
        (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        numArgs = 0
        head    = already_read_head
        subroutineType = None
        varName = None
        if head == None:
            head = self.analysisTerminal("IDENTIFIER") # subroutineName | className | varName
        if self.isTerminal("SYMBOL", "\("):
            # subroutineName '(' expressionList ')' => "this.subroutineName" method
            subroutineName = self.className + "." + head
            subroutineType = "method"
        elif self.isTerminal("SYMBOL", "\."):
            # (className | varName) '.' subroutineName '(' expressionList ')'
            className = ""
            dataType = self.symboltable.typeOf(head)
            if len(dataType) > 0 and not dataType in ["int", "char", "boolean"]:
                # varName(in SymbolTable).subroutineName => method
                # varName = "this" segment base addr
                className = dataType
                varName   = head
                subroutineType = "method"
            else:
                # className.subroutineName => constructor or method
                # let varName = className.subroutine => constructor
                # do  className.subroutine           => function
                className = head                  
                if flag == "let":
                    subroutineType = "constructor"
                elif flag == "do":
                    subroutineType = "function"                     

            self.analysisTerminal("SYMBOL", "\.")
            subroutineName = self.analysisTerminal("IDENTIFIER")
            subroutineName = className + "." + subroutineName # like className.subroutineName                

        if subroutineType == "method":
            # if VMfunc is "method", need to push obj-addr as Arg0
            numArgs += 1
            if not varName == None:
                self.pushIdentifier(varName)
            else:
                # if varName(objct Name)=None, caller already has "this" as Arg0, and push it to "pointer".
                self.vmwriter.writePush("pointer", 0) 
            
        self.analysisTerminal("SYMBOL", "\(")
        numArgs += self.compileExpressionList()
        self.analysisTerminal("SYMBOL", "\)")

        self.vmwriter.writeCall(subroutineName, numArgs)
        
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

        return ExpressionCnt
    
