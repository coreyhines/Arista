#!/usr/bin/env python

'''

This script relies on a few things
1. you cave a .eapi.conf file in your ~/

    ** example .eapi.conf
    [connection:tg254]
    host: 172.28.129.56
    username: admin
    #password: (this test env did not need a password)
    transport: https

2. You have enabled eapi on your switch: conf; management api https commands; no shut
3. You have enabled vlan counters on the 7280R

    tg254.08:41:49(config)#hardware counter feature vlan in
    tg254.08:47:33(config)#hardware counter feature vlan out

4. you have installed pyeapi 'pip install pyeapi'

There is a lot of formatting and likely stripping away some of the output for your needs. Let me know if you need help with that.

EXAMPLE OUTPUT:
chines@mbp-arista-13122[~]$ ./getVlanCounters.py
[{'command': 'show vlan counters',
  'encoding': 'json',
  'result': {u'vlanCountersInfo': {u'1': {u'inBcastPkts': 0,
                                          u'inMcastPkts': 0,
                                          u'inOctets': 858146,
                                          u'inUcastPkts': 5306,
                                          u'outBcastPkts': 0,
                                          u'outMcastPkts': 0,
                                          u'outOctets': 232100,
                                          u'outUcastPkts': 2398},
                                   u'125': {u'inBcastPkts': 0,
                                            u'inMcastPkts': 0,
                                            u'inOctets': 0,
                                            u'inUcastPkts': 0,
                                            u'outBcastPkts': 0,
                                            u'outMcastPkts': 0,
                                            u'outOctets': 0,
                                            u'outUcastPkts': 0},
                                   u'25': {u'inBcastPkts': 0,
                                           u'inMcastPkts': 0,
                                           u'inOctets': 22374,
                                           u'inUcastPkts': 198,
                                           u'outBcastPkts': 0,
                                           u'outMcastPkts': 0,
                                           u'outOctets': 0,
                                           u'outUcastPkts': 0},
                                   u'89': {u'inBcastPkts': 0,
                                           u'inMcastPkts': 0,
                                           u'inOctets': 0,
                                           u'inUcastPkts': 0,
                                           u'outBcastPkts': 0,
                                           u'outMcastPkts': 0,
                                           u'outOctets': 0,
                                           u'outUcastPkts': 0}}}}]



'''


import pyeapi
from pprint import pprint as pp

node = pyeapi.connect_to('tg254')
pp(node.enable('show vlan counters'))
