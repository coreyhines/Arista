#!/usr/bin/env python

from jsonrpclib import Server
import json
import ssl
import argparse
import string
import random

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
     "-s", "--session", type=str, default="",
     help="specify config session name", required=True)
  parser.add_argument(
      "-f", "--file", type=str, default="",
      help="specify a file with static MACs to apply", required=True)
  parser.add_argument(
      "-d", "--device", type=str, default="",
      help="specify an EOS device which static MACs are to applied", required=True)
  parser.add_argument(
      "-u", "--undo", action='store_true',
      help="specify --undo, to remove applied static mac addresses", required=False)
  args = parser.parse_args()
  n = 4 
  rand = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = n))
  session = args.session + "-" + rand
  file = args.file
  hostname = args.device
  undo = args.undo

  _create_unverified_https_context = ssl._create_unverified_context
  ssl._create_default_https_context = _create_unverified_https_context

  user = 'admin'
  passwd = '***REMOVED***'

  current_file = open(file, "r")
  macaddresses = current_file.readlines()

  device = Server('https://{}:{}@{}/command-api'.format(user, passwd, hostname))

  for mac in macaddresses:
    #mac addresses in file should have format aa:aa:aa:aa:aa:aa.vlan#.interface#
    bits = mac.split(".")
    macaddr = bits[0]
    vlan = bits[1]
    intf = bits[2]
    
    if undo == True:
      result = device.runCmds(1, ['enable', 'configure session {0}'.format(session), 'no mac address-table static {0}'.format(macaddr) + ' vlan {0}'.format(vlan) + ' interface {0}'.format(intf)])
    else:
      result = device.runCmds(1, ['enable', 'configure session {0}'.format(session), 'mac address-table static {0}'.format(macaddr) + ' vlan {0}'.format(vlan) + ' interface {0}'.format(intf)])

  
  result2 = device.runCmds(1, ['enable', 'configure session {0}'.format(session) + ' commit'])


if __name__ == '__main__':
    main()
