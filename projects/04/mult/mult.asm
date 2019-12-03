// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

(INIT)    
    @R2     // store the result of R0*R1
    M=0     // R2=0	
    @i
    M=0     // i=0	
	
(LOOP)
    @R1     // RAM[1]
    D=M
    @i
    D=D-M
    @END
    D;JEQ   // if R1-i == 0, Goto END

    @R0     // RAM[0]
    D=M
    @R2
    M=D+M   // R2 += R0
	
    @i
    M=M+1   // i++	
    @LOOP  
    0;JMP   // go to LOOP
	
(END)
    @END
    0;JMP
	
