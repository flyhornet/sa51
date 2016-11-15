import phash
import string
import sys
import io
import re

generate_hash = phash.generate_hash
get_hash_options = phash.get_hash_options
read_template = phash.read_template
cStringIO = io
verbose = 1


def keyDict(keys_hashes):
    """
    Checks a list with (key, hashvalue) tupels and returns dictionary.
    >>> d = keyDict([(1, 2), (3, 4), (5, 6)])
    >>> d[3]
    4
    """
    k = len(keys_hashes)  # number of keys
    if verbose >= 2:
        sys.stderr.write('K = %i\n' % k)

    key_dic = dict(keys_hashes)
    if len(key_dic) < k:
        sys.stderr.write('Warning: Input contains duplicate keys\n')

    if len(set(key_dic.values())) < k:
        sys.stderr.write('Warning: Input contains duplicate hash values\n')

    return key_dic


class Format:
    """
    >>> class o:
    ...     pass
    >>> o.delimiter = ': '
    >>> o.width = 75
    >>> o.indent = 4
    >>> x = Format( o )
    >>> x( range(10) )
    '0: 1: 2: 3: 4: 5: 6: 7: 8: 9'
    >>> o.delimiter = '; '
    >>> x = Format( o )
    >>> x( range(5) )
    '0; 1; 2; 3; 4'
    >>> o.delimiter = ' '
    >>> x = Format( o )
    >>> x( range(5), quote = True )
    '"0" "1" "2" "3" "4"'
    >>> x(42)
    '42'
    >>> x('Hello')
    'Hello'
    """

    def __init__(self, options):
        names = ['width', 'indent', 'delimiter']

        for name in names:
            setattr(self, name, getattr(options, name))

        if verbose >= 2:
            sys.stderr.write("Format options:\n")
            for name in names:
                sys.stderr.write('  %s: %r\n' % (name, getattr(self, name)))

    def __call__(self, data, quote=False):
        if type(data) != type([]):
            return str(data)

        lendel = len(self.delimiter)
        aux = cStringIO.StringIO()
        pos = 20
        for i, elt in enumerate(data):
            last = bool(i == len(data) - 1)

            s = ('"%s"' if quote else '%s') % elt
            if pos + len(s) + lendel > self.width:
                aux.write('\n' + (self.indent * ' '))
                pos = self.indent

            aux.write(s)
            pos += len(s)
            if not last:
                aux.write(self.delimiter)
                pos += lendel

        return aux.getvalue()


class Code(object):
    """docstring for Code Generator"""

    def __init__(self):
        self.hash = None
        self.options = None
        self.f1 = None
        self.f2 = None
        self.G = None
        self.keys = None
        self.key_hash = None
        self.out_name = None
        self.temp_file = None

    def __call__(self, keys, temp_file, outname='std'):
        self.keys = keys
        self.out_name = outname
        self.temp_file = temp_file

    def write_code(self, code):
        if self.out_name == 'std':
            sys.stdout.write(code)
        else:
            try:
                out_stream = open(self.out_name, 'w')
                out_stream.write(code)
                out_stream.close()
            except IOError:
                exit("Error: Could not open `%s' for writing." % self.out_name)

    ########################DIRECTIVE############################
    def format_c_directiv(self):
        # ---------------- prepare hash and options
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        # ---------------- generated code
        self.key_hash = keyDict(self.keys)
        f1, f2, g = generate_hash(self.key_hash, hashes)
        assert f1.N == f2.N == len(g)
        assert len(f1.salt) == len(f2.salt)

        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            NS=len(f1.salt),
            S1=fmt(f1.salt),
            S2=fmt(f2.salt),
            NG=len(g),
            G=fmt(g),
            NK=len(self.keys),
            K=fmt([key[0] for key in self.keys], quote=True)))

    def format_h_directiv(self):
        fmt = Format(self.options)
        temp_content = read_template(self.temp_file)
        temp_list = ["D_" + key[0].upper() for key in self.keys]
        temp_list.append("D_UNKNOWN")
        temp_list.append("D_NONE")
        self.write_code(string.Template(temp_content).substitute(
            V=fmt(temp_list),
            NV=len(self.keys)))

    ########################INSTRUCTION############################
    def format_c_instruct(self):
        hashes, self.options = get_hash_options()
        self.options.delimiter = ""
        fmt = Format(self.options)
        inst_list_info = ""
        inst_list = []
        inst_detail_set = "static const struct itemplate {name}[] = {{\n{info}\tITEMPLATE_END\n}};"
        inst_list_set = "{insnlist}\n"
        para_info = "{{{opcode},{length},{operands},{{{opList}}},{{{relList}}},{{{codeList}}},{chip}}},"
        for (k, ls) in self.keys.instSet:
            name = ''
            info = ''
            for v in ls:
                if not v.ignore:
                    item = para_info.format(opcode=v.opcode, length=v.length, operands=v.operands,
                                            opList=v.opStr, relList=v.relStr, codeList=v.codeStr, chip=v.chip)
                    item = item.replace('[', '').replace(']', '').replace("'", '')
                    info = info + '\t' + item + '\n'
                    name = "instrux" + v.opcode[1:]
                else:
                    name = "instrux" + v.opcode[1:]
                    info = ""
            inst_list.append(inst_detail_set.format(name=name, info=info))
            inst_list_info = inst_list_info + '\t' + name + ",\n"

        enum_list = inst_list_set.format(insnlist=inst_list_info)
        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            INSN=fmt(inst_list),
            LIST=enum_list))

    def format_h_instruct(self):
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        rex_ext = []
        rel_set = ["REL_NONE = 0", "REL_DWORD0"]
        ins_set = ["I_NONE = -1"]
        rel_byte = ["BYTE0", "BYTE1", "BYTE2", "BYTE3", "WORD0", "WORD2"]

        max_inst_len = 0
        for (k, v) in self.keys.instSet:
            ins_set.append(k)
            cur_len = len(k) - len("I_")
            max_inst_len = cur_len if cur_len > max_inst_len else max_inst_len

        for k in rel_byte:
            rel_set.append("REL_"+k)

        for (k, v) in self.keys.relSet:
            if k != 'REL_NONE':
                rel_set.append(k)
                if re.search('IMM', k):
                    for it in rel_byte:
                        rex_ext.append(k.replace("REL", "REL_EX_" + it))

        for k in rex_ext:
            rel_set.append(k)

        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            OP=fmt(ins_set),
            RC=fmt(rel_set),
            MI=max_inst_len))

    ##########################REGISTER############################
    def format_c_register(self):
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        reg_name_set = ""
        reg_name_list = []
        reg_flag_list = [0]
        max_leaf_len = 0
        for (k, v) in self.keys:
            leaf_len = len(v.leaf)
            max_leaf_len = leaf_len if leaf_len > max_leaf_len else max_leaf_len
            reg_name_set = reg_name_set + '\t' + k + ",\n"
            reg_name_list.append(k)
            reg_flag_list.append(v.leaf)

        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            RN=fmt(reg_name_list, True),
            RF=fmt(reg_flag_list)))

    def format_h_register(self):
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        reg_name_set = "\n\tR_ZERO = 0,\n\tR_NONE = -1,\n"
        reg_name_list = ["R_ZERO = 0", "R_NONE = -1"]
        start = False
        for (k, v) in self.keys:
            if not start:
                k += " = EXPR_REG_START"
                start = True

            if re.search('@', k):
                k = k.replace('@', "AT_R_")
            elif k == "C":
                k = "B_" + k
            else:
                k = "R_" + k
            reg_name_set = reg_name_set + '\t' + k + ",\n"
            reg_name_list.append(k)

        reg_name_list.append('REG_ENUM_LIMIT')
        reg_count = len(self.keys)
        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            R=fmt(reg_name_list),
            NR=reg_count))

    #############################TOKENS############################
    def format_c_tokens(self):
        # ---------------- prepare hash and options
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        # ---------------- generated code
        tok_hash = []
        for k in self.keys.tok_list:
            tok_hash.append((k.name, k.hash_val))

        self.key_hash = keyDict(tok_hash)
        f1, f2, g = generate_hash(self.key_hash, hashes)
        assert f1.N == f2.N == len(g)
        assert len(f1.salt) == len(f2.salt)

        tok_arr = []
        tok_tmpl = '\t{{ "{name}", {type}, {aux}, {flag}, {num} }}'
        for val in self.keys.tok_list:
            line = tok_tmpl.format(name=val.name, type=val.type, aux=val.aux, flag=val.flag, num=val.num)
            tok_arr.append(line)

        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            NS=len(f1.salt),
            S1=fmt(f1.salt),
            S2=fmt(f2.salt),
            NG=len(g),
            G=fmt(g),
            NK=len(self.keys.tok_list),
            K=fmt([key for key in tok_arr])))

    def format_h_tokens(self):
        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            NW=self.keys.max_tok_len))

    #############################IFLAG############################
    def format_c_iflag(self):
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        flag_val = {}
        for (k, v) in self.keys:
            index = v / 32
            val = 1 << (v % 32)
            try:
                flag_val[index]
            except:
                flag_val[index] = val
            else:
                flag_val[index] |= val

        flag_val = sorted(flag_val.items(), key=lambda d: d[0])
        res_list = []
        for (k, v) in flag_val:
            res_list.append("\t/* %4d */ {{ UINT32_C(0x%08x) }}\n" % (k, v))

        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            NF=len(flag_val),
            F=fmt(res_list)))

    def format_h_iflag(self):
        hashes, self.options = get_hash_options()
        fmt = Format(self.options)
        max_index = 0
        chip = []
        for (k, v) in self.keys:
            chip.append(k.name)
            max_index = v if v > max_index else max_index
        words = ((max_index / 32) + 1)
        temp_content = read_template(self.temp_file)
        self.write_code(string.Template(temp_content).substitute(
            CI=fmt(chip),
            FC=int(words)))
