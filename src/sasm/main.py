import tokens
import insnsa
import directiv
import regs
import iflag


def generate():
    print("**** BEG ****")
    regs.gen_register()
    insnsa.gen_instruct()
    directiv.gen_directive()
    tokens.gen_token()
    iflag.gen_flag()
    print("**** END ****")


if __name__ == '__main__':
    generate()
