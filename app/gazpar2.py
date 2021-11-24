#!/usr/bin/env python3

import sys
import logging
import argparse
import pygazpar

parser = argparse.ArgumentParser()
parser.add_argument("--pygazpar-login", dest="PYGAZPAR_LOGIN", help="pygazpar login")
parser.add_argument("--pygazpar-password", dest="PYGAZPAR_PASSWORD", help="pygazpar password")

client = pygazpar.Client(args.PYGAZPAR_LOGIN,
                         args.PYGAZPAR_PASSWORD,
                         'geckodriver',
                         30,
                         '/tmp')

log.debug('Starting to update pygazpar data')
client.update()
log.debug('End update pygazpar data')

data = client.data()

for measure in data:
    print(measure['volume_m3'])
