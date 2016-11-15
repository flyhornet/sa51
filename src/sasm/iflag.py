import format
import config
import xml.etree.cElementTree as ET

code = format.Code
gCurChip = config.gCurChip

gFlagXml = config.gInstructXml
gFlagTemplC = config.gFlagTemplC
gFlagTemplH = config.gFlagTemplH
gOutputNameC = config.gFlagOutputNameC
gOutputNameH = config.gFlagOutputNameH


class IflagMgr(object):
    """docstring for IflagMgr"""

    def __init__(self):
        self.flagSet = {}

    def add(self, chipid, index):
        self.flagSet[chipid] = index

    def sort(self):
        self.flagSet = sorted(self.flagSet.items(), key=lambda d: d[1])


class Iflag(object):
    """docstring for Iflag"""

    def __init__(self, name):
        self.name = name


gIflagMgr = IflagMgr()


def load_xml():
    root = ET.parse(gFlagXml).getroot()
    index = 0
    for chip in root:
        chip = Iflag(chip.get("chip"))
        gIflagMgr.add(chip, index)
        index += 1
    gIflagMgr.sort()


def gen_flag():
    load_xml()
    c = code()
    c(gIflagMgr.flagSet, gFlagTemplC, gOutputNameC)
    c.format_c_iflag()
    c(gIflagMgr.flagSet, gFlagTemplH, gOutputNameH)
    c.format_h_iflag()
    print("**** success to generate flag information ****")
