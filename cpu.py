"""CPU functionality."""

import sys

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0b01010000: self.CALL,
            0b10100111: self.CMP,
            0b01010110: self.JNE,
            0b01010101: self.JEQ,
            0b01010100: self.JMP

        }
        self.operand_a = None
        self.operand_b = None
        self.FL = 0b00000000
        

    def ram_read(self, mar):
        # mar is the address being read
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        # mdr is the data being written
        self.ram[mar] = mdr

    def push_value(self, value):
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[SP])

    def pop_value(self):
        value = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return value      

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        with open(filename) as f:
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        sys.exit()

    def LDI(self):
        self.reg[self.operand_a] = self.operand_b
        self.pc += 3

    def PRN(self):
        print(self.reg[self.operand_a])
        self.pc += 2

    def ADD(self):
        self.reg[self.operand_a] += self.reg[self.operand_b]
        self.pc += 3

    def MUL(self):
        self.reg[self.operand_a] *= self.reg[self.operand_b]
        self.pc += 3

    def PUSH(self):
        self.push_value(self.reg[self.operand_a])     
        self.pc += 2

    def POP(self):
        self.reg[self.operand_a] = self.pop_value()                                       
        self.pc +=2     
    
    def CALL(self):
        self.push_value(self.pc + 2)
        self.pc = self.reg[self.operand_a]

    def RET(self):
        self.pc = self.pop_value()
        
    
    def JMP(self):
        """Jump to the address stored in the given register."""
        address = self.reg[self.operand_a]
        
        self.pc = address
        
    def JEQ(self):
        """
        If the equal flag is set to (true), go to the address that's stored in the 
        given register
        """
        address = self.reg[self.operand_a]
        
        if self.FL == 1:
            self.pc = address
        else:
            self.pc += 2
            
    def JNE(self):
        """
        if 'E' flag is clear(false, 0), go to the address stored in the given register
        """
        address = self.reg[self.operand_a]
        
        if self.FL == 0:
            self.pc = address
        else:
            self.pc += 2

    def CMP(self):
        valueA = self.reg[self.operand_a]
        valueB = self.reg[self.operand_b]
        
        if valueA == valueB: #Flag -> 0000LGE
            self.FL = 0b0000100
        
        if valueA < valueB:
            self.FL = 0b00000100
        
        if valueA > valueB:
            self.FL = 0b00000010
        print(self.FL)
        
        self.pc += 3





    def run(self):
        """Run the CPU."""

        while True:
            # ir == Instruction Register
            ir = self.ram_read(self.pc)
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            if ir in self.branch_table:
                self.branch_table[ir]()
            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit()