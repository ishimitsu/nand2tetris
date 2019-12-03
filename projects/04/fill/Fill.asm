// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
	
	// column * line = 512 * 256 pixel
	// [line=r, column=c pixel] = RAM[16384 + r*32 + c/16]

(TOP)
	@SCREEN	    // RAM[16384], written data will be outputed to screen
	D=A
	@pixeladdr 	// refer pixel address, initialize addr=SCREEN=16384
	M=D
	@KBD        // RAM[24576], inputed data from keyboard will be stored 
	D=M

	@BLACK      // If KBD > 0, Color=Black
	D;JGT

	@WHITE      // If KBD = 0, Color=White
	0;JMP

(BLACK)
	@color      // variable for storing color param, at RAM[16]
	M=-1
	@DRAW
	0;JMP
	
(WHITE)	
	@color
	M=0
	@DRAW
	0;JMP
	
(DRAW)
	@color
	D=M
	@pixeladdr
	A=M
	M=D 	// *pixeladdr =color

	@pixeladdr
	M=M+1

	@8192 	// 512 * 256/16
	D=A
	@SCREEN
	D=D+A
	@pixeladdr
	D=D-M  // D = 8192 + SCREEN - addr
	// Loop While pixeladdr != SCREEN+8192, all pixels are written.
	@DRAW
	D;JGT
	
	@TOP
	0;JMP
