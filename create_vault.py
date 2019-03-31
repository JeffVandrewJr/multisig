import bitcointx
from bitcointx.core import COutPoint, CMutableTxIn, CMutableTxOut, \
        CMutableTransaction, CTxInWitness, CTxWitness, COIN
from bitcointx.core.script import CScript, CScriptOp, CScriptWitness, \
        SignatureHash, OP_0, OP_CHECKMULTISIG, SIGHASH_ALL
from bitcointx.wallet import CBitcoinSecret, P2WSHBitcoinAddress
from hashlib import sha256
import os
from stat import S_IREAD, S_IRGRP, S_IROTH
import subprocess


def generate_multisig_redeem_list(pubkeys, m):
    '''
    creates m of n multisig redeem script, encoded as a list
    pubkeys is a list of pubkeys
    m is the number of signatures required to redeem
    '''
    op_m = CScriptOp.encode_op_n(m)
    op_n = CScriptOp.encode_op_n(len(pubkeys))
    redeem_list = pubkeys
    redeem_list.insert(0, op_m)
    redeem_list.append(op_n)
    redeem_list.append(OP_CHECKMULTISIG)
    return redeem_list


def generate_transaction(
        amount, txin_txid, txin_vout, txout_addr, redeem_list):
    txin = CMutableTxIn(COutPoint(txin_txid, txin_vout))
    txout = CMutableTxOut(amount*COIN, txout_addr.addr.to_scriptPubKey())
    witness_script = CScriptWitness(tuple(redeem_list))
    witness = CTxWitness(tuple([CTxInWitness(witness_script)]))
    tx = CMutableTransaction(
            vin=[txin], vout=[txout], witness=witness)
    return tx


def sign_transaction(tx, privkeys):
    witness_list = list(tx.witness.vtxinwit[0].scriptWitness.stack)
    sighash = SignatureHash(tx.witness, tx, 0, SIGHASH_ALL)
    signatures = []
    for privkey in privkeys:
        privkey = CBitcoinSecret.from_bytes(privkey)
    for privkey in privkeys:
        signatures.append(privkey.sign(sighash) + bytes([SIGHASH_ALL]))
    counter = 0
    for signature in signatures:
        witness_list.insert(counter, signature)
        counter = counter + 1
    witness_script = CScriptWitness(tuple(witness_list))
    tx.witness = CTxWitness(tuple([CTxInWitness(witness_script)]))
    return tx.serialize()


def generate_vault():
    bitcointx.SelectParams('mainnet')
    m = int(input('How many total signatures will be required (aka "m"): '))
    n = int(input('How many total keys do you want to generate (aka "n"): '))
    privkeys = []
    pubkeys = []
    for counter in range(1, n):
        privkey = CBitcoinSecret.from_secret_bytes(os.urandom(32))
        pubkey = privkey.pub
        privkeys.append(privkey)
        pubkeys.append(pubkey)
        counter = counter + 1
    redeem_list = generate_multisig_redeem_list(pubkeys, m)
    script_pub_key = CScript(
            [OP_0, sha256(CScript(redeem_list)).digest()])
    address = P2WSHBitcoinAddress.from_scriptPubKey(script_pub_key)
    PATH = '/mnt/keys'
    if not os.path.isdir(PATH):
        subprocess.run(['mkdir', PATH])
    counter = 1
    while counter <= len(privkeys):
        if counter == 1:
            input('Insert a USB Drive. Press any key when complete.')
        else:
            input('Insert another USB Drive. Press any key when complete or \
press CTL+C to cancel.')
        subprocess.run(['lsblk'])
        dev = input(
                'Enter the device and partition of the USB drive (ex: sdb1): '
                )
        subprocess.run(
                ['umount', f'/dev/{dev}'], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        subprocess.run(['mount', f'/dev/{dev}', PATH])
        try:
            if not dev:
                raise ValueError('Bad Path.')
            keypath = os.path.join(PATH, f'key{counter}')
            addresspath = os.path.join(PATH, 'address')
            scriptpath = os.path.join(PATH, 'script')
            with open(keypath, 'w') as key_file:
                key_file.write(str(privkeys[(counter - 1)]))
            with open(addresspath, 'w') as address_file:
                address_file.write(str(address))
            with open(scriptpath, 'w') as script_file:
                script_file.write(str(redeem_list))
            for file in [keypath, addresspath, scriptpath]:
                os.chmod(file, S_IREAD | S_IRGRP | S_IROTH)
        except Exception as e:
            print(e)
            print('Bad path given. Try again.')
            continue
        subprocess.run(['umount', f'/dev/{dev}'])
        counter = counter + 1
    print('Process complete.')


if __name__ == '__main__':
    generate_vault()
