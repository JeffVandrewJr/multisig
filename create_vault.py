import bitcointx
from bitcointx.core.script import CScript, CScriptOp, OP_0, OP_CHECKMULTISIG
from bitcointx.wallet import P2WSHBitcoinAddress, CBitcoinSecret
from hashlib import sha256
import os
import subprocess


def generate_multisig_redeem_script(pubkeys, m):
    '''
    creates hex-encoded m of n multisig redeem script
    pubkeys is a list of pubkeys
    m is the number of signatures required to redeem
    '''
    op_m = CScriptOp.encode_op_n(m)
    op_n = CScriptOp.encode_op_n(len(pubkeys))
    redeem_list = pubkeys
    redeem_list.insert(0, op_m)
    redeem_list.append(op_n)
    redeem_list.append(OP_CHECKMULTISIG)
    redeem_script = CScript(redeem_list)
    return redeem_script


def main():
    bitcointx.SelectParams('mainnet')
    m = int(input('How many total signatures will be required (aka "m"): '))
    n = int(input('How many total keys do you want to generate (aka "n"): '))
    counter = 0
    privkeys = []
    pubkeys = []
    while counter < n:
        privkey = CBitcoinSecret.from_secret_bytes(os.urandom(32))
        pubkey = privkey.pub
        privkeys.append(privkey)
        pubkeys.append(pubkey)
        counter = counter + 1
    redeem_script = generate_multisig_redeem_script(pubkeys, m)
    script_pub_key = CScript([OP_0, sha256(redeem_script).digest()])
    address = P2WSHBitcoinAddress.from_scriptPubKey(script_pub_key)
    counter = 1
    while counter <= len(privkeys):
        if counter == 1:
            input('Insert a USB Drive. Press any key when complete.')
        else:
            input('Insert a new USB Drive. Press any key when complete.')
        subprocess.run(['df', '-h'])
        path = input(
                'Enter the drive path (ex: /run/media/root/sample): '
                )
        try:
            if not path:
                raise ValueError('Bad Path.')
            with open((os.path.join(path, f'key{counter}')), 'w') as key_file:
                key_file.write(str(privkeys[(counter - 1)]))
            with open((os.path.join(path, 'address')), 'w') as address_file:
                address_file.write(str(address))
        except Exception as e:
            print(e)
            print('Bad path given. Try again.')
            continue
        counter = counter + 1
    print('Process complete.')


if __name__ == '__main__':
    main()
