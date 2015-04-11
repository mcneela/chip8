from array import array
from random import randint
import pyglet

class CPU(pyglet.window.Window):
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

    KEY_MAP = {pyglet.window.key._1 : 0x1,
               pyglet.window.key._2 : 0x2,
               pyglet.window.key._3 : 0x3,
               pyglet.window.key._4 : 0xc,
               pyglet.window.key.Q : 0x4,
               pyglet.window.key.W : 0x5,
               pyglet.window.key.E : 0x6,
               pyglet.window.key.R : 0xd,
               pyglet.window.key.A : 0x7,
               pyglet.window.key.S : 0x8,
               pyglet.window.key.D : 0x9,
               pyglet.window.key.F : 0xe,
               pyglet.window.key.Z : 0xa,
               pyglet.window.key.X : 0,
               pyglet.window.key.C : 0xb,
               pyglet.window.key.V : 0xf
          }

    

    pixel = pyglet.image.load('pixel.png')
    buzzer = pyglet.resource.media('buzz.wav', streaming = False)
    
    def __init__(self, *args, **kwargs):
        super(CPU, self).__init__(*args, **kwargs)

        self.instruction_set = {0x0 : self.zero_subcase,
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

        self.zero_instruction_set = {0xE0 : self.clear_display,
                                     0xEE : self.sub_return}

        self.eight_instruction_set = {0x0 : self.load_reg,
                                      0x1 : self.OR,
                                      0x2 : self.AND,
                                      0x3 : self.XOR,
                                      0x4 : self.ADD,
                                      0x5 : self.SUB,
                                      0x6 : self.SHR,
                                      0x7 : self.SUBN,
                                      0xE : self. SHL}

        self.e_instruction_set = {0x9E : self.skip_if_keypressed,
                                  0xA1 : self.skip_if_not_keypressed}

        self.f_instruction_set = {0x07 : self.load_delay_timer,
                                  0x0A : self.load_keypress,
                                  0x15 : self.set_delay_timer,
                                  0x18 : self.set_sound_timer,
                                  0x1E : self.offset_index,
                                  0x29 : self.load_sprite_from_reg,
                                  0x33 : self.BCD,
                                  0x55 : self.store_reg_in_mem,
                                  0x65 : self.read_reg_from_meme}
    def initialize(self):
        self.current_opcode = [None]
        self.memory = [0 for i in range(4096)]
        self.V = [0 for i in range(16)]
        self.index = 0x000
        self.pc = 0x200
        self.stack = [None for i in range(16)]
        self.sp = 0
        self.keypad = [None for i in range(16)]
        self.delay_timer = 0
        self.sound_timer = 0
        self.screen_pixels = [[0 for i in range(32)] for j in range(64)]
        self.update_graphics = False
        self.key_pressed = False

        for i in range(80):
            self.memory[i] = self.fonts[i]

    def emulate_cycle(self):
        pc = self.pc
        self.current_opcode = (self.memory[pc] << 8) | self.memory[pc + 1]
        self.pc += 2
        print self.current_opcode

        leading_nibble = (self.current_opcode & 0xF000) >> 12
        self.VX = self.current_opcode & 0x0F00 >> 8
        self.VY = self.current_opcode & 0x00F0 >> 4

        try:
            self.instruction_set[leading_nibble]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")

        if self.update_graphics:
            self.draw_screen()
            
        self.countdown()

    def draw_screen(self):
        print 'here'
        if self.update_graphics:
            for i in range(64):
                for j in range(32):
                    if self.screen_pixels[i][j] == 1:
                        self.pixel.blit(i, j)
        self.update_graphics = False

    def zero_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            self.zero_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")

    def eight_subcase(self):
        latter_nibble = self.current_opcode & 0x000F

        try:
            self.eight_instruction_set[latter_nibble]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")

    def e_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            self.e_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")

    def f_subcase(self):
        latter_byte = self.current_opcode & 0x00FF

        try:
            self.f_instruction_set[latter_byte]()
        except KeyError:
            print(str(self.current_opcode) + " is not a valid OPCODE.")

    def clear_display(self):
        self.screen_pixels = [[0 for i in range(32)] for j in range(64)]

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

    def draw_sprite(self):
        num_bytes = self.current_opcode & 0x000F
        x = self.V[self.VX]
        y = self.V[self.VY]
        i = 0
        byte_list = []
        while i < num_bytes:
            byte_list.append(self.memory[self.index + i])
            i += 1
        print byte_list
        for ind, byte in enumerate(byte_list):
            j = 0
            while j < 8:
                if (byte & (0x80 >> j)) != 0:
                    if self.screen_pixels[y + ind][x + j] == 1:
                        self.V[0xF] = 1
                    self.screen_pixels[y + ind][x + j] ^= 1
                j += 1
        self.update_graphics = True
        self.pc += 2

    def record_key_pressed(self, key, mods):
        if key in KEY_MAP.keys():
            self.keypad[KEY_MAP[key]] = 1
            self.key_pressed = True

    def record_key_released(self, key, mods):
        if key in KEY_MAP.keys():
            self.keypad[KEY_MAP[key]] = 0
            self.key_pressed = False

    def skip_if_keypressed(self):
        if self.keypad[self.V[self.VX]] == 1:
            self.pc += 2

    def skip_if_not_keypressed(self):
        if self.keypad[self.V[self.VX]] != 1:
            self.pc += 2

    def load_delay_timer(self):
        self.V[self.VX] = self.delay_timer

    def load_keypress(self):
        while not self.key_pressed:
            pass
        for element in self.keypad:
            if self.keypad[element] == 1:
                self.V[self.VX] = element

    def set_delay_timer(self):
        delay_timer = self.V[self.VX]

    def set_sound_timer(self):
        sound_timer = self.V[self.VX]

    def offset_index(self):
        self.index += self.V[self.VX]

    def load_sprite_from_reg(self):
        self.index = (5 * self.V[self.VX]) & 0xFFF

    def BCD(self):
        self.memory[self.index] = self.V[self.VX] // 100
        self.memory[self.index + 1] = (self.V[self.VX] % 100) // 10
        self.memory[self.index + 2] = (self.V[self.VX]) % 10

    def store_reg_in_mem(self):
        for i in range(self.VX + 1):
            self.memory[self.index + i] = self.V[i]

    def read_reg_from_meme(self):
        for i in range(self.VX + 1):
            self.V[i] = self.memory[self.index + i]

    def load_rom(self, filepath):
        binary = open(filepath, 'rb').read()
        for i in range(len(binary)):
            self.memory[i + 0x200] = ord(binary[i])

    def countdown(self):
        if self.delay_timer != 0:
            self.delay_timer -= 1

        if self.sound_timer != 0:
            self.sound_timer -= 1
        else:
            self.buzzer.play()                         
                         


    
    

    

    
                    
            
            
    
    
    
        

        
    
        
       
