import re
import format
import config
import xml.etree.cElementTree as ET

code = format.Code

gCurChip = config.gCurChip

gTokensXml = config.gTokensXml
gRegisterXml = config.gRegisterXml
gInstructXml = config.gInstructXml

gTokensTemplC = config.gTokensTemplC
gTokensTemplH = config.gTokensTemplH
gOutputNameC = config.gTokensOutputNameC
gOutputNameH = config.gTokensOutputNameH


class TokensMgr(object):
    """docstring for TokensMgr"""

    def __init__(self):
        self.tok_hash = {}
        self.tok_list = []
        self.max_tok_len = 0

    def add(self, token):
        try:
            self.tok_hash[token.name]
        except:
            self.tok_hash[token.name] = token
            self.tok_list.append(token)
            max_len = len(token.name)
            self.max_tok_len = max_len if max_len > self.max_tok_len else self.max_tok_len   
            return True
        else:
            return False
 
     	

    def sort(self):
        self.tok_set = sorted(self.tok_set.items(), key=lambda d: d[1].hash_val)


class Token(object):
    """docstring for Token"""

    def __init__(self, name, types, aux, flag, prefix, hash_val):
        self.name = name
        self.type = types
        self.aux = aux
        self.flag = flag
        self.num = prefix
        self.hash_val = hash_val


gTokensMgr = TokensMgr()


def load_xml():
    """function for load tokens basic information"""
    g_hash_val = 0
    root = ET.parse(gRegisterXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                aux = "0"
                types = "TOKEN_REG"
                name = item.get("name").lower()
                if re.search('@', name):
                    flag = name.replace('@', "AT_REG_")
                    prefix = name.replace('@', "AT_R_")
                elif name == "c":
                    flag = "BIT_C"
                    prefix = "B_C"
                else:
                    flag = "REG_" + name
                    prefix = "R_" + name
                flag = flag.upper()
                prefix = prefix.upper()
                tok = Token(name, types, aux, flag, prefix, g_hash_val)
                # only one copy in list,so add if
                if gTokensMgr.add(tok):
                    g_hash_val += 1

    root = ET.parse(gInstructXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                flag = "0"
                aux = "0"
                types = "TOKEN_INSN"
                name = item.get("name").lower()
                prefix = ("I_" + name).upper()
                tok = Token(name, types, aux, flag, prefix, g_hash_val)
                # only one copy in list,so add if
                if gTokensMgr.add(tok):
                    g_hash_val += 1

    root = ET.parse(gTokensXml).getroot()
    for chip in root:
        if chip.get("chip") == gCurChip:
            for item in chip:
                aux = 0
                flag = 0
                name = item.get("name").lower()
                types = item.get("type")
                prefix = (item.get("prefix") + name).upper()
                tok = Token(name, types, aux, flag, prefix, g_hash_val)
                # only one copy in list,so add if
                if gTokensMgr.add(tok):
                    g_hash_val += 1


def gen_token():
    """function for generate codes for token"""
    load_xml()
    c = code()
    c(gTokensMgr, gTokensTemplC, gOutputNameC)
    c.format_c_tokens()
    c(gTokensMgr, gTokensTemplH, gOutputNameH)
    c.format_h_tokens()
    print("**** success to generate tokens ****")

