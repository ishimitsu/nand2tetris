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
	@SCREEN	
	D=A
	@pixeladdr 	// refer pixel address, init value=16384
	M=D
	
	@KBD // Check RAM[24576], Input from keyboard
	D=M

	@BLACK // If RAM[24576] > 0, Color =  Black
	D;JGT

	@WHITE // If RAM[24576] = 0, Color = White
	0;JMP

(BLACK)
	@color
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
	M=D 	// *addr =color

	@pixeladdr
	M=M+1

	@8192 	// 512 * 256/16
	D=A
	@SCREEN
	D=D+A
	@pixeladdr
	D=D-M  // D = 8192 + SCREEN - addr
	// Loop While Drawing Finish	
	@DRAW
	D;JGT
	
	@TOP
	0;JMP
