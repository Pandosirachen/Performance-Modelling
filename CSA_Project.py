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
        print(self.DMem)
        data_bin = self.DMem[ReadAddress] + self.DMem[ReadAddress + 1] + self.DMem[ReadAddress + 2] + self.DMem[ReadAddress + 3]
        data = hex(int(data_bin, 2))[2:]
        return data_bin
        #read data memory
        #return 32 bit hex val
        pass
        
    def writeDataMem(self, Address, WriteData):
        #WriteData should be length 32, since its from register files
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
        self.Registers = ["00000000000000000000000000000000" for i in range(32)]
    
    def readRF(self, Reg_addr):
        # Fill in
        return self.Registers[int(Reg_addr,2)]
        pass
    
    def writeRF(self, Reg_addr, Wrt_reg_data:str):
        #Reg_addr should be a binary string of length 5
        #Wrt_reg_data should be binary string of length < 32
        #we cannot write into register x0
        if(len(Wrt_reg_data)<32):
            Wrt_reg_data = Wrt_reg_data.zfill(32)
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
        self.IF = {"nop": 0, "PC": 0}
        self.ID = {"nop": 1, "Instr": 0}
        self.EX = {"nop": 1, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "DestReg": 0, "is_I_type": 0, "is_B_type": 0, "is_J_type": 0,"RdDMem": 0, 
                   "WrDMem": 0, "AluOperation": 0, "WBEnable": 0}
        self.MEM = {"nop": 1, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0, 
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": 1, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

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
    
    #this function format the result to 32 bits binary
    def result_format_32(self, result:str):
        result_len = len(result)
        if result_len>32:
            result = result[result_len-32:result_len]
        elif result_len<32:
            result = result.zfill(32)
        return result

    #sign extension and 32 bits formating function
    def bin_sign_ext_32(self,op1:str):
        #op1 should be binary strings with less than 32 bits or more than 32 bits
        op1_len = len(op1)
        if op1_len<32 and op1[0:1]=="0":
            op1 = op1.zfill(32)

        elif op1_len<32 and op1[0:1]=="1":
            ones_len = 32-op1_len
            while(ones_len>0):
                op1 = "1"+op1
                ones_len=ones_len-1
        
        elif op1_len>32:
            op1 = op1[op1_len-32:op1_len]

        return op1

    #inverse bits
    def inverse_bits(slef,op1:str):
        l = len(op1)
        k=""
        for i in range(l):
            k=k+"1"
        result = bin(int(op1,2) ^ int(k,2))
        return result[2:]


    #i functions
    def func_addi(self, op1:str, op2:str):
        a = self.bin_sign_ext_32(op1)
        b = self.bin_sign_ext_32(op2)
        print(a," addi ", b )
        result = bin(int(a,2)+int(b,2))
        result = result[2:]
        result = self.result_format_32(result)
        print("addi result = "+result+" length = ",len(result))
        return result

    def func_xori(self, op1:str, op2:str):
        a = self.bin_sign_ext_32(op1)
        b = self.bin_sign_ext_32(op2)
        print(a," xori ", b )
        result = bin(int(a,2)^int(b,2))
        result = result[2:]
        result = self.result_format_32(result)
        print("xori result = "+result+" length = ",len(result))
        return result

    def func_ori(self, op1:str, op2:str):
        a = self.bin_sign_ext_32(op1)
        b = self.bin_sign_ext_32(op2)
        print(a," ori ", b )
        result = bin(int(a,2)|int(b,2))
        result = result[2:]
        result = self.result_format_32(result)
        print("ori result = "+result+" length = ",len(result))
        return result

    def func_andi(self, op1:str, op2:str):
        a = self.bin_sign_ext_32(op1)
        b = self.bin_sign_ext_32(op2)
        print(a," andi ", b )
        result = bin(int(a,2) & int(b,2))
        result = result[2:]
        result = self.result_format_32(result)
        print("andi result = "+result+" length = ",len(result))
        return result

    def func_bne(self,op1:str, op2:str):
        if len(op1)==32 and len(op2)==32:
            return int(not op1==op2)
        else:
            print("ERROR: no equal string")
            return 0

    def func_beq(self,op1:str, op2:str):
        if len(op1)==32 and len(op2)==32:
            return int(op1==op2)
        else:
            print("ERROR: no equal string")
            return 0
    
    #five_stage_IF
    def five_stage_IF(self):
        if self.state.IF["nop"] == 1:
            return
        str = InsMem.readInstr(self.ext_imem,self.state.IF["PC"])
        self.nextState.ID["Instr"] = InsMem.readInstr(self.ext_imem,self.state.IF["PC"])
        #TODO deal with HALT instruction, halt is not always the end
        if str[25:32] == "1111111":
            self.nextState.ID["nop"]=1
            self.nextState.IF["nop"]=1
        else:
            self.nextState.ID["Instr"] = str
            self.nextState.ID["nop"]=0
            self.nextState.IF["nop"]=0
        pass
    
    #five_stage_ID
    def five_stage_ID(self):
        #test case
        if self.state.ID["nop"] == 1:
            self.nextState.EX["nop"] = 1
            return
        rs1="0"
        rs2="0"
        rd="0"
        imm="0"
        INS=""
        ALU=0
        cur_b = self.state.ID["Instr"]
        print("--------->",cur_b)
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
            imm=cur_b[(31-31):(32-31)]+cur_b[(31-19):(32-12)]+cur_b[(31-20):(32-20)]+cur_b[(31-30):(32-21)]
            rd=cur_b[(31-11):(32-7)]
            INS="JAL"
        #B
        elif(cur_b[25:32] == "1100011"):
            print("b", end="")
            if(cur_b[(31-14):(32-12)] == "000"):
                imm=cur_b[(31-31):(32-31)]+cur_b[(31-7):(32-7)]+cur_b[(31-30):(32-25)]+cur_b[(31-11):(32-8)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                print("imm = ",imm,"imm.len=",len(imm))
                print("-BEQ")
                INS="BEQ"

            elif(cur_b[(31-14):(32-12)] == "001"):
                imm=cur_b[(31-31):(32-31)]+cur_b[(31-7):(32-7)]+cur_b[(31-30):(32-25)]+cur_b[(31-11):(32-8)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                print("imm = ",imm,"imm.len=",len(imm))
                print("-BNE")
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

        if INS==("ADDI" or "ANDI" or "ORI" or "XORI") :
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_I_type"] = 1
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]=0
            self.nextState.EX["WrDMem"]=0
            self.nextState.EX["WBEnable"]=1
            rs1 = RegisterFile.readRF(self.myRF, rs1)
            if INS == "ADDI":
                self.nextState.EX["AluOperation"]= "00"
            if INS == "ANDI":
                self.nextState.EX["AluOperation"]= "01"
            if INS == "ORI":
                self.nextState.EX["AluOperation"]= "10"
            if INS == "XORI":
                self.state.EX["AluOperation"]= "11"
        elif INS==("ADD" or "XOR" or "AND" or "OR" or "SUB"):
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]=0
            self.nextState.EX["WrDMem"]=0
            self.nextState.EX["WBEnable"]=1
            rs1 = RegisterFile.readRF(self.myRF, rs1)
            rs2 = RegisterFile.readRF(self.myRF, rs2)
            if INS == ("ADD" or "SUB"):
                self.nextState.EX["AluOperation"]= "00"
                if INS == "SUB":
                    self.nextState.EX["Imm"] = bin(int(self.inverse_bits(imm),2)+1)[:2]
            if INS == "AND":
                self.nextState.EX["AluOperation"]= "01"
            if INS == "OR":
                self.nextState.EX["AluOperation"]= "10"
            if INS == "XOR":
                self.nextState.EX["AluOperation"]= "11"
        elif INS==("BEQ" or "BNE"):
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_B_type"] = 1
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]=0
            self.nextState.EX["WrDMem"]=0
            self.nextState.EX["WBEnable"]=1
            rs1 = RegisterFile.readRF(self.myRF, rs1)
            rs2 = RegisterFile.readRF(self.myRF, rs2)
            if INS=="BEQ":
                self.nextState.EX["AluOperation"]= "00"
            if INS=="BNE":
                self.nextState.EX["AluOperation"]= "01"
        elif INS==("SW"):
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]=0
            self.nextState.EX["WrDMem"]=1
            self.nextState.EX["WBEnable"]=0
            rs1 = RegisterFile.readRF(self.myRF, rs1)
            rs2 = RegisterFile.readRF(self.myRF, rs2)
        elif INS==("JAL"):
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_J_type"] = 1
            self.nextState.EX["RdDMem"]=0
            self.nextState.EX["WrDMem"]=0
            self.nextState.EX["WBEnable"]=1
        elif INS==("LW"):
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]=1
            self.nextState.EX["WrDMem"]=0
            self.nextState.EX["WBEnable"]=1
        elif INS==("HALT"):
            self.nextState.EX["is_I_type"] = 0
            self.nextState.EX["is_B_type"] = 0
            self.nextState.EX["is_J_type"] = 0
            self.nextState.EX["RdDMem"]= 0
            self.nextState.EX["WrDMem"]= 0
            self.nextState.EX["WBEnable"]= 0

        self.nextState.EX["Read_data1"] = rs1
        self.nextState.EX["Read_data2"] = rs2
        self.nextState.EX["Imm"] = imm
        self.nextState.EX["DestReg"] = rd
        self.nextState.EX["nop"]=0
        if(INS == "HALT"):
            self.nextState.EX["nop"]= 1
        else:
            self.nextState.EX["nop"]= 0
    
    #five_stage_EX
    def five_stage_EX(self):

#           add 00
#           and 01
#           or  10
#           xor 11
#           bne 01
#           beq 00
        if self.state.EX["nop"] == 1:
            self.nextState.MEM["nop"] = 1
            return

        rs1 = self.state.EX["Read_data1"]
        rs2 = self.state.EX["Read_data2"]
        imm = self.state.EX["Imm"]
        rd = self.state.EX["DestReg"]

        itype = self.state.EX["is_I_type"]
        btype = self.state.EX["is_B_type"]
        jtype = self.state.EX["is_J_type"]
        alu = self.state.EX["AluOperation"]
        wbenable = self.state.EX["WBEnable"]
        rddmem = self.state.EX["RdDMem"]
        wrdmem = self.state.EX["WrDMem"]

        #ADD
        if alu == "00" and itype == 0 and btype == 0 and jtype == 0 and wbenable==1 and rddmem == 0 and wrdmem == 0:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2)+int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #XOR
        elif alu == "11" and itype == 0 and btype == 0 and jtype == 0 and wbenable==1 and rddmem == 0 and wrdmem == 0:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value=bin(int(operand1,2) ^ int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #OR
        elif alu == "10" and itype == 0 and btype == 0 and jtype == 0 and wbenable==1 and rddmem == 0 and wrdmem == 0:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2) | int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #AND
        elif alu == "01" and itype == 0 and btype == 0 and jtype == 0 and wbenable==1 and rddmem == 0 and wrdmem == 0:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2) & int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #ADDI
        elif alu == "00" and itype == 1:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_addi(operand1,imm)
        #XORI
        elif alu == "11" and itype == 1:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_xori(operand1,imm)
        #ORI
        elif alu == "10" and itype == 1:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_ori(operand1,imm)
        #ANDI
        elif alu == "01" and itype == 1:
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_andi(operand1,imm)
        #BNE
        elif alu == "01" and btype == 1 and wbenable=="1":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = self.func_bne(operand1,operand2) #value =1 true, value = 0 false
            if value:
                current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
                imm = self.bin_sign_ext_32(imm+"0")
                next_PC = int(self.func_addi(current_pc_value,imm),2)-4
                #we minus 4 here since we will add the 4 back in the step(), this could be a bad fix to make it the same as the TEST case result
                self.nextState.IF["PC"]=next_PC
        #BEQ
        elif alu == "00" and btype == 1 and wbenable=="1":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = self.func_beq(operand1,operand2) #value =1 true, value = 0 false
            if value:
                current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
                imm = self.bin_sign_ext_32(imm+"0")
                next_PC = int(self.func_addi(current_pc_value,imm),2)-4
                #we minus 4 here since we will add the 4 back in the step(), this could be a bad fix to make it the same as the TEST case result
                self.nextState.IF["PC"]=next_PC
        #JAL
        elif jtype == 1:
            #caluculate PC+4
            imm = self.bin_sign_ext_32(imm+"0")
            value = bin(self.nextState.IF["PC"]+4)[2:]
            #set next PC to imm
            value.zfill(32)
            current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
            next_PC = int(self.func_addi(current_pc_value,imm),2)-4
            self.nextState.IF["PC"]=next_PC
            pass
        #LW
        elif rddmem == 1:
            value = int(rs1, 2) + int(imm, 2)
        #SW
        elif wrdmem == 1:
            #imm is sign extension!
            #TODO!!!!!
            #TOTEST!!!!
            value = int(rs1, 2) + int(imm, 2)
            self.nextState.MEM["Store_data"] = RegisterFile.readRF(self.myRF, rs2)

        self.nextState.MEM["nop"] = 0
        self.nextState.MEM["ALUresult"] = value
        #only in sw, for sw and lw, value is ALU in single stage case
        self.nextState.MEM["Wrt_reg_addr"] = rd
        self.nextState.MEM["rd_mem"] = rddmem
        self.nextState.MEM["wrt_mem"] = wrdmem
        self.nextState.MEM["wrt_enable"] = wbenable
        pass

    def five_stage_MEM(self):
        if self.state.MEM["nop"] == 1:
            self.nextState.WB["nop"] = 1
            return
        ALU=""
        value=""
        rddmem=0
        wrdmem=0
        rs2 = self.state.MEM["Store_data"]
        ALU == self.state.MEM["ALUresult"] #this is the address
        value == self.state.MEM["Store_data"] #this only for sw
        rddmem == self.state.MEM["rd_mem"]
        wrdmem == self.state.MEM["wrt_mem"]

        #LW
        if rddmem:
            #get value from the address of ALU
            ALU = DataMem.readInstr(self.ext_dmem, ALU)
            self.nextState.WB["Wrt_data"] = result
        #SW
        elif wrdmem:
            result = RegisterFile.readRF(self.myRF, rs2)
            DataMem.writeDataMem(self.ext_dmem,value,result)
        else:
            pass


        self.nextState.WB["nop"] = 0
        self.nextState.WB["Wrt_data"] = ALU
        self.nextState.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]
        self.nextState.WB["wrt_enable"] = self.state.MEM["wrt_enable"]



    def five_stage_WB(self):
        if self.state.WB["nop"] == 1:
            return
        if self.state.MEM["nop"] == 1:
            self.nextState.WB["nop"] =1
        rd = self.state.WB["Wrt_reg_addr"]
        value = self.state.WB["Wrt_data"]
        RegisterFile.writeRF(self.myRF,rd,value)


    #single stage steps
    def seperate_bits(self, cur_b):
        #IF Steps
        #get 32 bits instructions
        print("--------->",cur_b)

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
            imm=cur_b[(31-31):(32-31)]+cur_b[(31-19):(32-12)]+cur_b[(31-20):(32-20)]+cur_b[(31-30):(32-21)]
            rd=cur_b[(31-11):(32-7)]
            INS="JAL"
        #B
        elif(cur_b[25:32] == "1100011"):
            print("b", end="")
            if(cur_b[(31-14):(32-12)] == "000"):
                imm=cur_b[(31-31):(32-31)]+cur_b[(31-7):(32-7)]+cur_b[(31-30):(32-25)]+cur_b[(31-11):(32-8)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                print("imm = ",imm,"imm.len=",len(imm))
                print("-BEQ")
                INS="BEQ"

            elif(cur_b[(31-14):(32-12)] == "001"):
                imm=cur_b[(31-31):(32-31)]+cur_b[(31-7):(32-7)]+cur_b[(31-30):(32-25)]+cur_b[(31-11):(32-8)]
                rs2=cur_b[(31-24):(32-20)]
                rs1=cur_b[(31-19):(32-15)]
                print("imm = ",imm,"imm.len=",len(imm))
                print("-BNE")
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
            value = self.result_format_32(value)
        elif INS == "SUB":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            operand2 = self.inverse_bits(operand2)
            value = bin(int(operand1,2)+int(operand2,2)+1)
            value = value[2:]
            value = self.result_format_32(value)
        #tested
        elif INS == "XOR":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value=bin(int(operand1,2) ^ int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #tested
        elif INS == "OR":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2) | int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        #tested
        elif INS == "AND":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = bin(int(operand1,2) & int(operand2,2))
            value = value[2:]
            value = self.result_format_32(value)
        elif INS == "ADDI":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_addi(operand1,imm)
        elif INS == "XORI":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_xori(operand1,imm)
        elif INS == "ORI":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_ori(operand1,imm)
        elif INS == "ANDI":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            value = self.func_andi(operand1,imm)
        elif INS == "BNE":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = self.func_bne(operand1,operand2) #value =1 true, value = 0 false
            if value:
                current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
                imm = self.bin_sign_ext_32(imm+"0")

                next_PC = int(self.func_addi(current_pc_value,imm),2)-4
                #we minus 4 here since we will add the 4 back in the step(), this could be a bad fix to make it the same as the TEST case result
                self.nextState.IF["PC"]=next_PC

        elif INS == "BEQ":
            operand1 = RegisterFile.readRF(self.myRF, rs1)
            operand2 = RegisterFile.readRF(self.myRF, rs2)
            value = self.func_beq(operand1,operand2) #value =1 true, value = 0 false
            if value:
                current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
                imm = self.bin_sign_ext_32(imm+"0")

                next_PC = int(self.func_addi(current_pc_value,imm),2)-4
                #we minus 4 here since we will add the 4 back in the step(), this could be a bad fix to make it the same as the TEST case result
                self.nextState.IF["PC"]=next_PC
        elif  INS == "JAL":
            #caluculate PC+4
            imm = self.bin_sign_ext_32(imm+"0")
            value = bin(self.nextState.IF["PC"]+4)[2:]

            #set next PC to imm
            value.zfill(32)
            current_pc_value = bin(self.nextState.IF["PC"])[2:].zfill(32)
            next_PC = int(self.func_addi(current_pc_value,imm),2)-4
            self.nextState.IF["PC"]=next_PC
            pass
        elif INS == "LW":
            ALU = int(rs1, 2) + int(imm, 2)
        elif INS == "SW":
            #imm is sign extension!
            #TODO!!!!!
            #TOTEST!!!!
            ALU = int(rs1, 2) + int(imm, 2)
        elif INS == "HALT":
            print("HALT")

        #MEM Steps
        if INS == "ADD":
            print("NOP")
        elif INS == "SUB":
            print("NOP")
        elif INS == "XOR":
            print("NOP")
        elif INS == "OR":
            print("NOP")
        elif INS == "AND":
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
        elif INS == "SUB":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "XOR":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "OR":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "AND":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "ADDI":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "XORI":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "ORI":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "ANDI":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "LW":
            RegisterFile.writeRF(self.myRF,rd,value)
        elif INS == "SW":
            print("NOP")
        elif INS == "JAL":
            RegisterFile.writeRF(self.myRF,rd,value)
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
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True
        
        if not self.halted:
            self.five_stage_WB()
            self.five_stage_MEM()
            self.five_stage_EX()
            self.five_stage_ID()
            self.five_stage_IF()

        if not (self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]):
            self.nextState.IF["PC"]+=4

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend("\n")
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend("\n")
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend("\n")
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend("\n")
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
    ioDir = ioDir+"\\Test\\TC0"



    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)
    
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)
    
    #test functions
    print("-----------------------------------------------------------------------------")

    print("-----------------------------------------------------------------------------")
    #test functions


    while(True):
        #if not ssCore.halted:
         #   ssCore.step()
        ssCore.halted = True

        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break
    
    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()