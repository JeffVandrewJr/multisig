import bitcointx
from bitcointx.core import COutPoint, CMutableTxIn, CMutableTxOut, \
        CMutableTransaction, CTxInWitness, lx, COIN
from bitcointx.core.script import CScript, CScriptOp, CScriptWitness, \
        OP_0, OP_CHECKMULTISIG
from bitcointx.wallet import P2WSHBitcoinAddress, CBitcoinSecret
from hashlib import sha256
import os
from stat import S_IREAD, S_IRGRP, S_IROTH
import subprocess


def generate_multisig_redeem_script(pubkeys, m):
    '''
    creates m of n multisig redeem script
    pubkeys is a list of pubkeys
    m is the number of signatures required to redeem
    '''
    op_m = CScriptOp.encode_op_n(m)
    op_n = CScriptOp.encode_op_n(len(pubkeys))
    redeem_list = pubkeys
    redeem_list.insert(0, op_m)
    redeem_list.append(op_n)
    redeem_list.append(OP_CHECKMULTISIG)
    redeem_tuple = tuple(redeem_list)
    redeem_script = CScriptWitness(redeem_tuple)
    return redeem_script


def generate_transaction(amount, txin_txid, txin_vout, txout_addr):
    txin = CMutableTxIn(COutPoint(txin_txid, txin_vout))
    txout = CMutableTxOut(amount*COIN, txout_addr.addr.to_scriptPubKey())
    witness_script = CScriptWitness(redeem_script)
    witness = CTxInWitness(witness_script)
    tx = CMutableTransaction(
            vin=[txin], vout=[txout], witness=witness)


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
    script_pub_key = CScript(
            [OP_0, sha256(CScript(redeem_script.stack)).digest()])
    address = P2WSHBitcoinAddress.from_scriptPubKey(script_pub_key)
    counter = 1
    while counter <= len(privkeys):
        if counter == 1:
            input('Insert a USB Drive. Press any key when complete.')
        else:
            input('Insert another USB Drive. Press any key when complete or \
                    press CTL+C to cancel.')
        subprocess.run(['df', '-h'])
        path = input(
                'Enter the drive path (ex: /run/media/root/sample): '
                )
        try:
            if not path:
                raise ValueError('Bad Path.')
            keypath = os.path.join(path, f'key{counter}')
            addresspath = os.path.join(path, 'address')
            scriptpath = os.path.join(path, 'script')
            with open(keypath, 'w') as key_file:
                key_file.write(str(privkeys[(counter - 1)]))
            with open(addresspath, 'w') as address_file:
                address_file.write(str(address))
            with open(scriptpath, 'w') as script_file:
                script_file.write(str(redeem_script))
            for file in [keypath, addresspath, scriptpath]:
                os.chmod(file, S_IREAD | S_IRGRP | S_IROTH)
        except Exception as e:
            print(e)
            print('Bad path given. Try again.')
            continue
        subprocess.run(['umount', path])
        counter = counter + 1
    print('Process complete.')


if __name__ == '__main__':
    main()
