import format
import config
import xml.etree.cElementTree as ET

code = format.Code

gCurChip = config.gCurChip

gRegisterXml = config.gRegisterXml
gRegisterTemplC = config.gRegisterTemplC
gRegisterTemplH = config.gRegisterTemplH
gOutputNameC = config.gRegisterOutputNameC
gOutputNameH = config.gRegisterOutputNameH


class RegsMgr(object):
    """docstring for RegMgr	"""

    def __init__(self):
        self.regSet = {}

    def add(self, reg):
        self.regSet[reg.name] = reg

    def sort(self):
        self.regSet= sorted(self.regSet.items(), key=lambda d:d[0])

class Register(object):
    """docstring for RegInfo"""

    def __init__(self, item):
        self.name = item.get("name")
        self.leaf = item.get("leaf")
        self.root = item.get("root")
        self.chip = gCurChip


gRegsMgr = RegsMgr()


def load_xml():
    """function for load register basic information"""
    root = ET.parse(gRegisterXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                reg = Register(item)
                gRegsMgr.add(reg)
    gRegsMgr.sort()


def gen_register():
    """function for generate codes for register"""
    load_xml()
    c = code()
    c(gRegsMgr.regSet, gRegisterTemplC, gOutputNameC)
    c.format_c_register()
    c(gRegsMgr.regSet, gRegisterTemplH, gOutputNameH)
    c.format_h_register()
    print("**** success to generate registers ****")



