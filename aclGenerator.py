#!/usr/bin/env python

aclTotal = 2
aceCount = 250
count = 0
aclNum = 200
action = "permit"
prot = "tcp"
src = "any"
dstHost = "10.100.200.44"
portNum = 2024

while count <= aclTotal:
    print "ip access-list %d" % (aclNum + count)
    for ace in range(aceCount):
        print "  %s %s %s host %s eq %d" % (
            action, prot, src, dstHost, portNum)
        portNum = portNum + 1
    count = count + 1
