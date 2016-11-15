import format
import config
import xml.etree.cElementTree as ET

code = format.Code
gCurChip = config.gCurChip
gDirectXml = config.gDirectXml
gDirectTemplC = config.gDirectTemplC
gDirectTemplH = config.gDirectTemplH
gOutputNameC = config.gDirectOutputNameC
gOutputNameH = config.gDirectOutputNameH


class DircMgr(object):
    """class for managing directive"""

    def __init__(self):
        """directive must be not duplicate"""
        self.dircList = []

    def add(self, elem):
        self.dircList.append(elem)


gDirectMgr = DircMgr()


def load_xml():
    """function for load directive basic information"""
    root = ET.parse(gDirectXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            hash_val = 0
            for item in chip:
                try:
                    skip = item.get("skip")
                except:
                    pass
                else:
                    if skip == "1":
                        continue
                name = item.get("name")
                gDirectMgr.add((name, hash_val))
                hash_val += 1


def gen_directive():
    """function for generate codes for directive"""
    load_xml()
    c = code()
    c(gDirectMgr.dircList, gDirectTemplC, gOutputNameC);
    c.format_c_directiv()
    c(gDirectMgr.dircList, gDirectTemplH, gOutputNameH);
    c.format_h_directiv()
    print("**** success to generate direcitve ****")
