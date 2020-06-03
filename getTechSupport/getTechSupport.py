#!/usr/bin/env python

import requests, json, pyeapi
from jsonrpclib import Server
#import xmlrpc
from rcvpapi.rcvpapi import *

cvp_ip = "10.0.5.107"
cvp_user = "cvpadmin"
cvp_user_pwd = '!ndenter=munkeyme|'
switches = []
showtech = {}

# Create connection to CloudVision
cvp_cnt = CVPCON(cvp_ip,cvp_user,cvp_user_pwd)

# Check current CloudVision sessionId/Cookie
#cvp_cnt.SID

# Get the current CVP Version
#cvpversion = cvp_cnt.version
#print (cvpversion)

inventory = cvp_cnt.inventory
for element in inventory:
    dut = element.split(".", 1)
    dut = dut[0]
    switches.append(dut)

#print(switches)

# """ for switch in switches:
#     switch = switch.lower()
#     print(switch)
#     node = pyeapi.connect_to(switch)
#     showtech = node.enable('show tech-support')
#     filename = "/tmp/" + switch
#     print(filename)
#     with open(filename, "w") as fh:
#         for line in showtech:
#             fh.writelines(line)
#     fh.close() """

for switch in switches:
    switch = switch.lower()
    node = Server('https://{0}:{1}@{2}/command-api'.format(cvp_user, cvp_user_pwd, switch))
    showtech = node.runCmds(version = 1, cmds = ['show tech-support'], format = 'text')[0]['output'].split('\n')
    filename = "/tmp/{0}".format(switch)
    with open(filename, "w") as fh:
        for line in showtech:
            fh.write("{0}\n".format(line))

# Logout/End session
#cvp_cnt.execLogout()