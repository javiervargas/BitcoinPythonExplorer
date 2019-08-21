#!/usr/bin/env python

import sys
import getopt
import time

from btc import DaemonBTC
import logging

btcdaemon = DaemonBTC("http://user:password@127.0.0.1:8332")

height = btcdaemon.get_max_block()

size = 0
transactions = True

try:
    opts, args = getopt.getopt(sys.argv[1:],"b1",["blocksonly"])
except getopt.GetoptError:
    print("Usage: ")
    print(' %s [--blocksonly,-b] [min] [max]' % sys.argv[0])
    sys.exit(2)

#if (('-1', '') in opts):
#    size = es.get_max_block() + 1

if len(args) > 0:
    size = int(args[0])

if len(args) > 1:
    height = int(args[1])

if len(args) > 2:
    size = int(args[0])
    height = int(args[1])

for i in range(size, height + 1):
        block = btcdaemon.get_block(i)
        print("block %d/%d"%(block['height'], height))

        if transactions is True:
            txs = btcdaemon.get_block_transactions_bulk(i)
            print("  Transactions: %i" % len(txs))
