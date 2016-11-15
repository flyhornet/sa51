import format
import config
import re
import xml.etree.cElementTree as ET

code = format.Code
gRegList = []
gMaxOperand = 5
gCurChip = config.gCurChip

gRegisterXml = config.gRegisterXml
gInstructXml = config.gInstructXml
gInsnsaTemplC = config.gInsnsaTemplC
gInsnsaTemplH = config.gInsnsaTemplH
gOutputNameC = config.gInsnsOutputNameC
gOutputNameH = config.gInsnsOutputNameH


class InstMgr(object):
    """class for managing instruction"""

    def __init__(self):
        self.instSet = {}
        self.relSet = {}

    def add(self, inst):
        try:
            for x in inst.relList:
                if x != "0":
                     self.relSet[x] = x
            self.instSet[inst.opcode]
        except:            
            self.instSet[inst.opcode] = [inst]            
        else:
            self.instSet[inst.opcode].append(inst)

    def show(self):
        keys = self.instSet.keys()
        for k in keys:        
            instList = self.instSet[k]
            for inst in instList:
                print ('\n'.join(['%s:%s' % item for item in inst.__dict__.items()]))

    def sort(self):
        self.instSet = sorted(self.instSet.items(), key=lambda d: d[0])
        self.relSet = sorted(self.relSet.items(), key=lambda d: d[0])


class Inst(object):
    """class for instruction information"""

    def __init__(self):
        self.relList = []
        self.relStr = ""
        self.opStr = ""
        self.codeStr = ""
        self.chip = ""
        self.opcode = ""
        self.syntax = ""
        self.length = 0
        self.operands = 0
        self.type = "TOKEN_INSN"
        self.ignore = False

    def parseOp(self, opInfo):
        if opInfo != "ignore":
            self.syntax = opInfo
            self.operands = int(opInfo.count(",")) + 1
            opList =[]
            try:
                opList = opInfo.split(" ")[1].split(",")
            except Exception:
                self.operands = 0
            else:
                pass
            
            resList = []
            for op in opList:
                if "C" == op:
                    op = "BIT_C"
                elif op[0] == '/':
                    op = "BIT_REV_8"
                elif op == "RAMADDR":
                    op = "MEMORY"
                elif op == "ROMADDR":
                    op = "MEMORY"
                elif op == "BIT8":
                    op = "MEMORY|BIT_8"
                elif op == "OFFSET":
                    op = "MEMORY|OFFSET"
                elif re.search("addr", op):
                    op = "MEMORY"
                elif op == "void":
                    op = "0"
                elif re.search("@", op):
                    op = op.replace("@", "AT_REG_")
                    if re.search("\+", op):
                        op = op.replace("+", "_")
                else:
                    for reg in gRegList:
                        if op == reg:
                            op = "REG_" + op;

                resList.append(op)
            if len(resList) == 0:
                self.opStr = "0"
            else:
                self.opStr = str(resList)
        else:
            self.ignore = True

    def parseCode(self, code):
        resList = []
        if code != 'ignore':
            self.length = int(code.count(" ")) + 1
            codeList = code.split(" ")
            for x in codeList:
                resList.append("0X%s" % x)
            self.codeStr = str(resList)

    def parseRel(self, rel):
        nLen = 0
        if rel != "ignore":
            self.relList = rel.split(",")
            self.relStr = str(self.relList)

    def parseName(self, name):
        self.opcode = "I_" + name


gInstMgr = InstMgr()


def load_xml():
    """function for load directive basic information"""
    root = ET.parse(gRegisterXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                gRegList.append(item.get("name"))

    root = ET.parse(gInstructXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                inst = Inst()
                inst.chip = gCurChip
                inst.parseRel(item.get("rel"))
                inst.parseOp(item.get("syntax"))
                inst.parseName(item.get("name"))
                inst.parseCode(item.get("opcode"))
                gInstMgr.add(inst)
    gInstMgr.sort()


def gen_instruct():
    """function for generate codes for directive"""
    load_xml()
    c = code()
    c(gInstMgr, gInsnsaTemplC, gOutputNameC)
    c.format_c_instruct()
    c(gInstMgr, gInsnsaTemplH, gOutputNameH)
    c.format_h_instruct()
    print("**** success to generate instructions ****")
