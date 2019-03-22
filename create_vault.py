import bitcoin
from bitcoin.core import script, x
from bitcoin.core.key import CECKey
from bitcoin.wallet import P2SHBitcoinAddress
import os
import subprocess


def generate_multisig_redeem_script(keypairs, m):
    '''
    creates m of n multisig redeem script
    keypairs is a list of dictionaries
    each dictionary is a keypair with indices 'pubkey' & 'privkey'
    m is the number of signatures required to redeem
    '''
    pubkeys = []
    for keypair in keypairs:
        pubkeys.append(keypair['pubkey'])
    op_m = script.CScriptOp.encode_op_n(m)
    op_n = script.CScriptOp.encode_op_n(len(pubkeys))
    redeem_list = [x(pubkey) for pubkey in pubkeys]
    redeem_list.insert(0, op_m)
    redeem_list.append(op_n)
    redeem_list.append(script.OP_CHECKMULTISIG)
    redeem_script = script.CScript(redeem_list).hex()
    return redeem_script


if __name__ == '__main__':
    bitcoin.SelectParams('mainnet')
    m = int(input('How many total signatures will be required (aka "m"): '))
    n = int(input('How many total keys do you want to generate (aka "n"): '))
    counter = 0
    keypairs = []
    while counter <= n:
        key = CECKey()
        keypairs.append(
                {'privkey': key.get_privkey(), 'pubkey': key.get_pubkey()})
        counter = counter + 1
    redeem_script = generate_multisig_redeem_script(keypairs, m)
    address = P2SHBitcoinAddress.from_redeemScript(
            script.CScript(x(redeem_script))
        )
    counter = 1
    while counter <= len(keypairs):
        if counter == 1:
            input('Insert a USB Drive. Press any key when complete.')
        else:
            input('Insert a new USB Drive. Press any key when complete.')
        subprocess.run(['df', '-h'])
        path = input(
                'Enter the drive path (ex: /run/media/root/sample): '
                )
        try:
            with open(os.path.join(path, f'key{counter}', 'w')) as key_file:
                key_file.write(keypairs[(counter - 1)])
            with open(os.path.join(path, 'address', 'w')) as address_file:
                address_file.write(address)
        except Exception:
            print('Bad path given. Try again.')
            continue
        counter = counter + 1
    print('Process complete/')
