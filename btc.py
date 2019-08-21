
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import os

class DaemonBTC:

    def __init__(self, url):
        self.rpc = AuthServiceProxy(url)

        self.height = self.rpc.getblockcount()


    def get_block(self, i):
        block = self.rpc.getblockhash(i)
        block_data = self.rpc.getblock(block)
        block_data['transactions'] = len(block_data['tx'])
        block_data['difficulty'] = int(block_data['difficulty'])
        del(block_data['tx'])

        return block_data

    def get_transaction(self, tx):
        rtx = self.rpc.getrawtransaction(tx)
        dtx = self.rpc.decoderawtransaction(rtx)

        return dtx

    def get_transactions(self, txs):
        rtx = self.rpc.batch_([["getrawtransaction", t] for t in txs])
        dtx = self.rpc.batch_([["decoderawtransaction", t] for t in rtx])

        return dtx

    def get_block_transactions(self, block):

        # The genesis block is special
        if block == 0:
            return []

        blockhash = self.rpc.getblockhash(block)
        block_data = self.rpc.getblock(blockhash)

        transactions = []

        rtx = self.rpc.batch_([["getrawtransaction", t] for t in block_data['tx']])
        dtx = self.rpc.batch_([["decoderawtransaction", t] for t in rtx])

        for tx in dtx:
            tx['height'] = block_data['height']
            tx['block'] = block_data['hash']
            tx['time'] = block_data['time']
            print (tx['txid'])
            for i in tx['vin']:
                if 'scriptSig' in i:
                    del(i['scriptSig'])
            for i in tx['vout']:
                if 'hex' in i['scriptPubKey']:
                    del(i['scriptPubKey']['hex'])
                if 'asm' in i['scriptPubKey']:
                    del(i['scriptPubKey']['asm'])
            print (i['value'])
            transactions.append(tx)

        return transactions

    def get_block_transactions_bulk(self, block):
        "Return an iterable object for bulk transactions"

        transactions = self.get_block_transactions(block)
        tx = Transactions()
        for i in transactions:
            tx.add_transaction(i)

        return tx

    def get_blocks_bulk(self, blocks):

        rbh = self.rpc.batch_([["getblockhash", t] for t in blocks])

        dbh = self.rpc.batch_([["get_block", t] for t in rbh])

        output = []
        for block_data in dbh:
            block_data['transactions'] = len(block_data['tx'])
            block_data['chainwork_int'] = int(block_data['chainwork'], 16)
            del(block_data['tx'])
            output.append(block_data)

        return output

    def get_max_block(self):
        return self.rpc.getblockcount()

class Transactions:

    def __init__(self):
        self.transactions = []
        self.current = -1

    def add_transaction(self, tx):
        temp = {    '_type': 'doc',
                    '_op_type': 'update',
                    '_index': "btc-transactions-%d" % (tx['height'] / 100000),
                    '_id': tx['hash'],
                    'doc_as_upsert': True,
                    'doc': tx
                }

        self.transactions.append(temp)


    def __next__(self):
        "handle a call to next()"

        self.current = self.current + 1
        if self.current >= len(self.transactions):
            raise StopIteration

        return self.transactions[self.current]

    def __iter__(self):
        "Just return ourself"
        return self

    def __len__(self):
        return len(self.transactions)

