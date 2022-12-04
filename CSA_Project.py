import os
import argparse
#from __future__ import print_function
MemSize = 1000 # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.

class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        with open(ioDir + "\\imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        instruction_bin = self.IMem[ReadAddress]+self.IMem[ReadAddress+1]+self.IMem[ReadAddress+2]+self.IMem[ReadAddress+3]
        instruction=hex(int(instruction_bin, 2))[2:]
        return instruction_bin
        #read instruction memory
        #return 32 bit hex val
        pass
          
class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "\\dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def readInstr(self, ReadAddress):
        print(ReadAddress)
        print(self.DMem)
        data_bin = self.DMem[ReadAddress] + self.DMem[ReadAddress + 1] + self.DMem[ReadAddress + 2] + self.DMem[ReadAddress + 3]
        data = hex(int(data_bin, 2))[2:]
        return data_bin
        #read data memory
        #return 32 bit hex val
        pass
        
    def writeDataMem(self, Address, WriteData):

        #append Dmem list to address+3 length
        Dmem_length= len(self.DMem)
        if Dmem_length < Address + 3:
            i = Address + 3 - Dmem_length+1
            while(i>0):
                self.DMem.append("00000000")
                i=i-1

        self.DMem[Address] = WriteData[:8]
        self.DMem[Address + 1] = WriteData[8:16]
        self.DMem[Address + 2] = WriteData[16:24]
        self.DMem[Address + 3] = WriteData[24:32]
        # write data into byte addressable memory
        pass
                     
    def outputDataMem(self):
        resPath = self.ioDir + "\\" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]
    
    def readRF(self, Reg_addr):
        # Fill in
        return self.Registers[int(Reg_addr,2)]
        pass
    
    def writeRF(self, Reg_addr, Wrt_reg_data):
        #Reg_addr should be a binary string of length 5
        #Wrt_reg_data should be binary string of length 32
        #we cannot write into register x0
        if int(Reg_addr,2)>0:
            self.Registers[int(Reg_addr,2)] = Wrt_reg_data
        pass
         
    def outputRF(self, cycle):
        op = ["-"*70+"\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val)+"\n" for val in self.Registers])
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": False, "Instr": 0}
        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False, "rd_mem": 0, 
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0, 
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem

    def seperate_bits(self, cur_b):
        #IF Steps
        #get 32 bits instructions
        print(cur_b)

        rs1=""
        rs2=""
        rd=""
        imm=""
        INS=""
        ALU=0

        #ID Steps
        #R
        if(cur_b[(31-6):(32-0)] == "0110011"):
            print("r", end="")
            if(cur_b[(31-14):(32-12)] == "000" and cur_b[(31-31):(32-25)] == "0000000"):
                print("-ADD")
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="ADD"

            elif(cur_b[(31-14):(32-12)] == "000" and cur_b[(31-31):(32-25)] == "0100000"):
                print("_SUB")
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="SUB"

            elif(cur_b[(31-14):(32-12)] == "100" and cur_b[(31-31):(32-25)] == "0000000"):
                print("_XOR")
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="XOR"

            elif(cur_b[(31-14):(32-12)] == "110" and cur_b[(31-31):(32-25)] == "0000000"):
                print("_OR")
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="OR"

            elif(cur_b[(31-14):(32-12)] == "111" and cur_b[(31-31):(32-25)] == "0000000"):
                print("_AND")
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="AND"

            else:
                print("ERROR: No matching R type command")
        #I
        elif(cur_b[25:32] == "0010011"):
            print("i", end="")
            if(cur_b[(31-14):(32-12)] == "000"):
                print("-ADDI")
                imm=cur_b[(31-31):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="ADDI"

            elif(cur_b[(31-14):(32-12)] == "100"):
                print("-XORI")
                imm=cur_b[(31-31):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="XORI"

            elif(cur_b[(31-14):(32-12)] == "110"):
                print("-ORI")
                imm=cur_b[(31-31):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="ORI"

            elif(cur_b[(31-14):(32-12)] == "111"):
                print("-ANDI")
                imm=cur_b[(31-31):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="ANDI"

            else:
                print("ERROR: No matching I type command")

        elif(cur_b[25:32] == "0000011"):
            print("i", end="")
            if(cur_b[(31-14):(32-12)] == "000"):
                print("-LW")
                imm=cur_b[(31-31):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                rd=cur_b[(31-11):(32-7)]
                INS="LW"

            else:
                print("ERROR: No matching I type command")
        #J
        elif(cur_b[25:32] == "1101111"):
            print("j-JAL")
            imm=cur_b[(31-31):(32-12)]
            rd=cur_b[(31-11):(32-7)]
            INS="JAL"
        #B
        elif(cur_b[25:32] == "1100011"):
            print("b", end="")
            if(cur_b[(31-14):(32-12)] == "000"):
                imm=cur_b[(31-31):(32-25)]+cur_b[(31-11):(32-7)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                print("-BEQ")
                INS="BEQ"

            elif(cur_b[(31-14):(32-12)] == "001"):
                print("-BNE")
                imm=cur_b[(31-31):(32-25)]+cur_b[(31-11):(32-7)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                INS="BNE"

            else:
                print("ERROR: No matching B type command")
        #S
        elif(cur_b[25:32] == "0100011"):
            print("s", end="")
            if(cur_b[(31-14):(32-12)] == "010"):
                print("-SW")
                imm=cur_b[(31-31):(32-25)]+cur_b[(31-11):(32-7)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                INS="SW"

            else:
                print("ERROR: No matching S type command")
        #HALT
        elif(cur_b[25:32] == "1111111"):
            print("h-HALT")
            INS="HALT"
            self.state.IF["nop"] = True
        else:
            print("ERROR: No matching type")
            INS="HALT"


        value=""
        #EX Steps
        #Calculate the instruction
        if INS == "ADD":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2)+int(operand2,2))
            value = value[2:]
            print(value)
        elif INS == "LW":
            ALU = int(rs1, 2) + int(imm, 2)
        elif INS == "SW":
            ALU = int(rs1, 2) + int(imm, 2)
        elif INS == "HALT":
                print("HALT")

        #MEM Steps
        if INS == "ADD":
            print("NOP")
        elif INS == "LW":
            #get value from the address of ALU
            value = DataMem.readInstr(self.ext_dmem, ALU)
        elif INS == "SW":
            value = RegisterFile.readRF(self.myRF, rs2)
            DataMem.writeDataMem(self.ext_dmem,ALU,value)
        elif INS == "HALT":
            print("HALT")

        #WB Steps
        if INS == "ADD":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "LW":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "SW":
            print("NOP")
        elif INS == "HALT":
            print("HALT")

class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "\\SS_", imem, dmem)
        self.opFilePath = ioDir + "\\StateResult_SS.txt"

    def step(self):
        if self.state.IF["nop"]:
            self.halted = True
        
        if not self.halted:
            Current_bits = InsMem.readInstr(self.ext_imem,self.state.IF["PC"])
            self.seperate_bits(Current_bits)
            if not self.state.IF["nop"]:
                self.nextState.IF["PC"]+=4
        

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1



    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")
        
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "\\FS_", imem, dmem)
        self.opFilePath = ioDir + "\\StateResult_FS.txt"

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------
        
        
        
        # --------------------- MEM stage --------------------
        
        
        # --------------------- EX stage ---------------------
        
        
        # --------------------- ID stage ---------------------
        
        
        # --------------------- IF stage ---------------------
        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True
        
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

if __name__ == "__main__":
     
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)


    #remove this test line --sp6966
    ioDir = ioDir+"\\Test"



    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)
    
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while(True):
        if not ssCore.halted:
            ssCore.step()
        
        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break
    
    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()