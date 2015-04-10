from array import array
from random import randint

class CPU:
    fonts = ([0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
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
          ])

    leading_bit_instruction_set = {0x0 : self.zero_subcase,
                                   0x1 : self.jump,
                                   0x2 : self.call,
                                   0x3 : self.skip_if_eq,
                                   0x4 : self.skip_if_neq,
                                   0x5 : self.skip_if_reg_eq,
                                   0x6 : self.load_byte,
                                   0x7 : self.add_byte,
                                   0x8 : self.eight_subcase,
                                   0x9 : self.skip_if_reg_neq,
                                   0xA : self.set_index,
                                   0xB : self.jump_plus_V0,
                                   0xC : self.rand_AND,
                                   0xD : self.draw_sprite,
                                   0xE : self.e_subcase,
                                   0xF : self.f_subcase}

    zero_instruction_set = {0xE0 : self.clear_display,
                            0xEE : self.sub_return}

    eight_instruction_set = {0x0 : self.load_reg,
                             0x1 : self.OR,
                             0x2 : self.AND,
                             0x3 : self.XOR,
                             0x4 : self.ADD,
                             0x5 : self.SUB,
                             0x6 : self.SHR,
                             0x7 : self.SUBN,
                             0xE : self. SHL}

    e_instruction_set = {0x9E : self.skip_if_keypressed,
                         0xA1 : self.skip_if_not_keypressed}

    f_instruction_set = {0x07 : self.load_delay_timer,
                         0x0A : self.load_keypress,
                         0x15 : self.set_delay_timer,
                         0x18 : self.set_sound_timer}
    
    def __init__(self):
        self.current_opcode = [None]
        self.memory = [None for i in range(4096)]
        self.V = [None for i in range(16)]
        self.index = 0x000
        self.pc = 0x200
        self.stack = [None for i in range(16)]
        self.sp = 0
        self.keypad = [None for i in range(16)]
        self.delay_timer = 0
        self.sound_timer = 0   

        for i in range(80):
            self.memory[i] = self.fonts[i]

    def emulate_cycle(self):
        pc = self.pc
        self.current_opcode = (self.memory[pc] << 8) | self.memory[pc + 1]
        self.pc += 2

        leading_nibble = (current_opcode & 0xF000) >> 12
        self.VX = self.current_opcode & 0x0F00
        self.VY = self.current_opcode & 0x00F0

        try:
            instruction_set[leading_nibble]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")
            pass

    def zero_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            zero_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")
            pass

    def eight_subcase(self):
        latter_nibble = self.current_opcode & 0x000F

        try:
            eight_instruction_set[latter_nibble]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")
            pass

    def e_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            e_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")
            pass

    def f_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            f_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")
            pass

    # def clear_display(self):

    def sub_return(self):
        self.pc = self.stack.pop()

    def jump(self):
        address = self.current_opcode & 0x0FFF
        self.pc = address

    def call(self):
        address = self.current_opcode & 0x0FFF
        self.sp += 1
        self.stack.append(self.pc)
        self.pc = address

    def skip_if_eq(self):
        if self.V[self.VX] == (self.current_opcode & 0x00FF):
            self.pc += 2

    def skip_if_neq(self):
        if self.V[self.VX] != (self.current_opcode & 0x00FF):
            self.pc += 2

    def skip_if_reg_eq(self):
        if self.V[self.VX] == self.V[self.VY]:
            self.pc += 2

    def load_byte(self):
        self.V[self.VX] = (self.current_opcode & 0x00FF)

    def add_byte(self):
        self.V[self.VX] += (self.current_opcode & 0x00FF)

    def load_reg(self):
        self.V[self.VX] = self.V[self.VY]

    def OR(self):
        self.V[self.VX] = (self.V[self.VX] | self.V[self.VY])

    def AND(self):
        self.V[self.VX] = (self.V[self.VX] & self.V[self.VY])

    def XOR(self):
        self.V[self.VX] = (self.V[self.VX] ^ self.V[self.VY])

    def ADD(self):
        result = self.V[self.VX] + self.V[self.VY]
        if result > 255:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0
        self.V[self.VX] = (result & 0xFF)

    def SUB(self):
        if self.V[self.VX] > self.V[self.VY]:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0
        self.V[self.VX] -= self.V[self.VY]
        self.V[self.VX] &= 0xFF

    def SHR(self):
        if (self.V[self.VX] & 0x01) == 1:
            self.V[0xF] == 1
        else:
            self.V[0xF] == 0
        self.V[self.VX] >> 1

    def SUBN(self):
        if self.V[self.VY] > self.V[self.VY]:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0
        self.V[self.VX] -= self.V[self.VY]

    def SHL(self):
        if (self.V[self.VX] & 0xF0) == 1:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0
        self.V[self.VX] << 1

    def skip_if_reg_neq(self):
        if self.V[self.VX] != self.V[self.VY]:
            self.pc += 2

    def set_index(self):
        self.index = (self.current_opcode & 0x0FFF)

    def jump_plus_V0(self):
        self.pc = (self.current_opcode & 0x0FFF) + self.V[0x00]

    def rand_AND(self):
        self.V[self.VX] = randint(0, 255) & (self.current_opcode & 0x00FF)

    
    
    
        

        
    
        
       
