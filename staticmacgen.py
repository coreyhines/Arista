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
     "-u", "--user", type=str, default="",
     help="specify a username", required=True)
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
      "-p", "--passwd", type=str, default="",
      help="for passing password interactively", required=False)
  parser.add_argument(
      "-r", "--remove", action='store_true',
      help="to remove applied static mac addresses", required=False)
  args = parser.parse_args()
  n = 4 
  rand = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = n))
  session = args.session + "-" + rand
  file = args.file
  hostname = args.device
  remove = args.remove
  user = args.user

  if len(args.passwd) > 0:
    passwd = args.passwd
  else:
    passwd = '***REMOVED***'

  _create_unverified_https_context = ssl._create_unverified_context
  ssl._create_default_https_context = _create_unverified_https_context

  with open(file, "r") as current_file:
    macaddresses = current_file.readlines()

  device = Server('https://{}:{}@{}/command-api'.format(user, passwd, hostname))

  try:
    for mac in macaddresses:
      #mac addresses in file should have format aa:aa:aa:aa:aa:aa.vlan#.interface#
      #
      bits = mac.split(".")
      macaddr = bits[0]
      vlan = bits[1]
      intf = bits[2]
    
      if remove == True:
        result = device.runCmds(1, ['enable', 'configure session {0}'.format(session), 'no mac address-table static {0}'.format(macaddr) + ' vlan {0}'.format(vlan) + ' interface {0}'.format(intf)])
      else:
        result = device.runCmds(1, ['enable', 'configure session {0}'.format(session), 'mac address-table static {0}'.format(macaddr) + ' vlan {0}'.format(vlan) + ' interface {0}'.format(intf)])
  except: 
    print("something went wrong, check password\n\n")

  
  result2 = device.runCmds(1, ['enable', 'configure session {0}'.format(session) + ' commit'])


if __name__ == '__main__':
    main()
