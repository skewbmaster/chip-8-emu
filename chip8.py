from random import randint

class CPU:
    chip8_fontset = (
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        )

    def __init__(self):
        # Current opcode running
        self.opcode = 0

        # Index register and program counter ( 0x000 -> 0xFFF )
        self.I = 0
        self.pc = 0x200

        # Current Memory and Registers ( V0 -> VE/VF )
        self.memory = bytearray(4096)
        self.V = bytearray(16)


        # 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
        # 0x200-0xFFF - Program ROM and rest for RAM


        # Graphics ( 2048 pixel, 64x32, Monochrome )
        self.gfx = bytearray(64 * 32)
        self.drawFlag = False

        # Timer Registers
        self.delay_timer = 0
        self.sound_timer = 0

        # Stack levels and pointers
        self.stack = [i for i in range(16)]
        self.sp = 0

        # Current inputs
        self.key = bytearray(16)

        for i in range(80):
            self.memory[i] = self.chip8_fontset[i]


    def reInit(self):
        self.opcode = 0
        self.I = 0
        self.pc = 0x200
        self.memory = bytearray(4096)
        self.V = bytearray(16)
        self.gfx = bytearray(64 * 32)
        self.drawFlag = False
        self.stack = [i for i in range(16)]
        self.sp = 0
        self.key = bytearray(16)
        self.delay_timer = 0
        self.sound_timer = 0
        for i in range(80):
            self.memory[i] = self.chip8_fontset[i]


    def loadGame(self, fp):
        with open(fp, 'rb') as romread:
            data = romread.read()

            for i in range(len(data)):
                self.memory[0x200 + i] = data[i]


    def emulationCycle(self):
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.decodeExecOpcode(self.opcode)

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP")
            self.sound_timer -= 1



    def decodeExecOpcode(self, opcode):
        op1 = opcode & 0xF000 # First to last byte separated by AND
        op2 = opcode & 0x0F00
        op3 = opcode & 0x00F0
        op4 = opcode & 0x000F

        if op1 == 0x0000:
            if op4 == 0x0000: # Clear the screen ( 0x00E0 )
                self.gfx = bytearray(64 * 32)
                self.drawFlag = True

            elif op4 == 0x000E: # Return from subroutine ( 0x00EE )
                self.sp -= 1
                self.pc = self.stack[self.sp]
                self.stack[self.sp] = 0x0

            self.pc += 2


        elif op1 == 0x1000: # Jump to address NNN
            self.pc = opcode & 0x0FFF


        elif op1 == 0x2000: # Call a function at NNN
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = opcode & 0x0FFF


        elif op1 == 0x3000: # Skip the next instruction if VX == NN
            if self.V[op2 >> 8] == opcode & 0x00FF:
                self.pc += 4
            else:
                self.pc += 2

        elif op1 == 0x4000: # Skip the next instruction if VX != NN
            if self.V[op2 >> 8] != opcode & 0x00FF:
                self.pc += 4
            else:
                self.pc += 2

        elif op1 == 0x5000: # Skip the next instruction if VX == VY
            if self.V[op2 >> 8] == self.V[op3 >> 4]:
                self.pc += 4
            else:
                self.pc += 2


        elif op1 == 0x6000: # Sets VX to NN
            self.V[op2 >> 8] = opcode & 0x00FF
            self.pc += 2


        elif op1 == 0x7000: # Adds NN to VX
            self.V[op2 >> 8] = (self.V[op2 >> 8] + (opcode & 0x00FF)) & 0xFF

            self.pc += 2


        elif op1 == 0x8000:
            X = op2 >> 8 # Second byte
            Y = op3 >> 4 # Third byte

            if op4 == 0x0000:
                self.V[X] = self.V[Y] # Set VX to VY

            elif op4 == 0x0001:
                self.V[X] |= self.V[Y] # Set VX to VX OR VY

            elif op4 == 0x0002:
                self.V[X] &= self.V[Y] # Set VX to VX AND VY

            elif op4 == 0x0003:
                self.V[X] ^= self.V[Y] # Set VX to VX XOR VY


            elif op4 == 0x0004: # Add VY to VX and set VF to 1 if carry
                if self.V[Y] > (0xFF - self.V[X]):
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0

                self.V[X] = (self.V[X] + self.V[Y]) & 0xFF

            elif op4 == 0x0005: # Subtract VY from VX and set VF to 1 if no borrow and vice versa
                if self.V[X] > self.V[Y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                    
                self.V[X] = (self.V[X] - self.V[Y]) & 0xFF


            elif op4 == 0x0006: # Stores the least significant bit of VX in VF and then shifts VX to the right by 1
                self.V[0xF] = self.V[X] & 0x1
                self.V[X] >>= 1

            elif op4 == 0x0007:
                if self.V[Y] > self.V[X]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                    
                self.V[X] = (self.V[Y] - self.V[X]) & 0xFF

            elif op4 == 0x000E: # Stores the most significant bit of VX in VF and then shifts VX to the left by 1
                self.V[0xF] = self.V[X] >> 7
                self.V[X] = (self.V[X] << 1) & 0xFF # If the bit shift overflows the byte

            self.pc += 2


        elif op1 == 0x9000: # Skip the next instruction if VX != VY
            if self.V[op2 >> 8] != self.V[op3 >> 4]:
                self.pc += 4
            else:
                self.pc += 2


        elif op1 == 0xA000: # Set I to address NNN
            self.I = opcode & 0x0FFF
            self.pc += 2

        elif op1 == 0xB000: # Jumps to the address NNN plus V0.
            self.pc = self.V[0] + (opcode & 0x0FFF)

        elif op1 == 0xC000: # Sets VX to rand(0,255) AND NN
            self.V[op2 >> 8] = randint(0,255) & (opcode & 0x00FF)
            self.pc += 2



        elif op1 == 0xD000: # Drawing to the screen
            X = self.V[op2 >> 8]
            Y = self.V[op3 >> 4]

            height = op4

            self.V[0xF] = 0

            for yline in range(height):
                pixel = self.memory[self.I + yline]

                for xline in range(8):
                    if pixel & (0x80 >> xline) != 0:
                        if self.gfx[(X + xline + ((Y + yline) * 64)) % (64*32)] == 1:
                            self.V[0xF] = 1

                        self.gfx[(X + xline + ((Y + yline) * 64)) % (64*32)] ^= 1
            
            self.drawFlag = True
            self.pc += 2

        
        elif op1 == 0xE000:
            if op4 == 0x000E:
                if self.key[self.V[op2 >> 8]] != 0:
                    self.pc += 4
                else:
                    self.pc += 2
                
            elif op4 == 0x0001:
                if self.key[self.V[op2 >> 8]] == 0:
                    self.pc += 4
                else:
                    self.pc += 2


        elif op1 == 0xF000:
            subcode = opcode & 0x00FF
            X = op2 >> 8

            if subcode == 0x0007: # Set VX to the delay timer
                self.V[X] = self.delay_timer

            elif subcode == 0x000A: # Block PC increments until any keypress, which will be stored in VX
                keypress = False

                for i in range(16):
                    if self.key[i] != 0:
                        self.V[X] = i
                        keypress = True

                if not keypress:
                    return
                

            elif subcode == 0x0015: # Sets delay timer to VX
                self.delay_timer = self.V[X]
            
            elif subcode == 0x0018: # Sets sound timer to VX
                self.sound_timer = self.V[X]

            elif subcode == 0x001E: # Add VX to I; VF affected if overflows ram
                #if self.I + self.V[X] > 0xFFF:
                    #self.V[0xF] = 1
                #else:
                    #self.V[0XF] = 0

                self.I += self.V[X]

            elif subcode == 0x0029: # Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
                self.I = self.V[X] * 0x5 

            elif subcode == 0x0033:                              # Stores the binary-coded decimal representation of VX,
                self.memory[self.I]   = self.V[X] // 100         # with the most significant of three digits at the address in I,
                self.memory[self.I+1] = (self.V[X] // 10) % 10   # the middle digit at I plus 1, and the least significant digit at I plus 2.
                self.memory[self.I+2] = self.V[X] % 10

            elif subcode == 0x0055: # Stores V0 to VX values into memory[from I to I+X]
                for i in range(X+1):
                    self.memory[self.I + i] = self.V[i]

                #self.I += X + 1

            elif subcode == 0x0065: # Stores memory[from I to I+X] into V0 to VX
                for i in range(X+1):
                    self.V[i] = self.memory[self.I + i]

                #self.I += X + 1


            self.pc += 2

        else:
            print("Unkown opcode:", hex(opcode))

