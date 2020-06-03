#!/usr/bin/env Python

import argparse
import wget
import sys
import re
import time
import urllib
# import urllib.request
from subprocess import Popen, call, check_output
import os
from os.path import expanduser

images = {'veos': ['vEOS-lab'],
          'ceos': ['cEOS'],
          'vmdk': ['EOS.vmdk'],
          'all': ['EOS', 'EOS-2GB', 'EOS-PDP', 'cEOS', 'vEOS-lab', 'EOS.vmdk'],
          'eos': ['EOS'],
          'eos-2gb': ['EOS-2GB'],
          'eos-pdp': ['EOS-PDP']}
outputFilename = []


def check_native_vpn():
    "Function to check if there is a native Arista VPN client"
    #native_check = check_output(["scutil", "--nc", "list"]).split('\n')
    native_check = check_output(["scutil", "--nc", "list"])
    n_check = native_check.decode("utf-8").split('\n')
    for r1 in n_check:
        if 'arista' in r1.lower():
            return(r1[r1.find('"')+1:r1.rfind('"')])
    else:
        return(False)


def get_latest_rn(r_url):
    # Function to grab the most current posted release notes and return filename
    all_release_notes = {}
    content = urllib.request.urlopen(r_url).read().split('\n')
    for r1 in content:
        if '-RN-v' in r1:
            release_file = r1[r1.find('">E')+2:r1.find('</a>')]
            ver = release_file[release_file.find(
                '-v')+2:release_file.find('.pdf')]
            all_release_notes[ver] = release_file
    latest_ver = 0.0
    for r1 in all_release_notes:
        if float(r1) > latest_ver:
            latest_ver = float(r1)
    return(all_release_notes[str(latest_ver)])


def main(args, version):
    urls = []
    rn_url = "http://dist/release/EOS-" + version + "/final/doc/"
    home = expanduser("~")
    outputDir = home + "/Downloads/EOS-" + version + "/"
    failed = False  # Default value to False
    native_vpn_disconnect = False  # Variable to determine if vpn should be disconnected
    vpn_reconnect_counter = 0  # Counter to prevent a forever loop
    vpn_max_reconnect = 2000  # Max VPN reconnect tries to prevent forever loop

    for image in images[args.package]:
        if image == "cEOS":
            ext = ".tar.xz"
        elif image == "EOS.vmdk":
            ext = ""
        else:
            ext = ".swi"
        urls.append("http://dist/release/EOS-" + version +
                    "/final/images/" + image + ext)
        if image == "EOS.vmdk":
            image = "EOS"
            ext = ".vmdk"

        outputFilename.append(outputDir + image + "-" + version + ext)

    # Check to see if native OSX vpn is configured
    vpn_name = check_native_vpn()
    if vpn_name:
        vpncheck = check_output(["scutil", "--nc", "status", vpn_name])
        vpncheckStr = vpncheck.decode("utf-8").split("\n")
        # Check to see if native vpn is connected
        if not vpncheckStr[0] == "Connected":
            print("VPN Connection is down...\n")
            print(("Attempting to connect to {0}".format(vpn_name)))
            check_output(["scutil", "--nc", "start", vpn_name])
            while True:
                vpncheck = check_output(["scutil", "--nc", "status", vpn_name])
                vpncheckStr = vpncheck.decode("utf-8").split("\n")
                vpncheckResult = vpncheckStr[0].strip()
                if vpncheckResult == "Connected":
                    if not args.stayConnected:
                        native_vpn_disconnect = True
                    break
                elif vpn_reconnect_counter >= vpn_max_reconnect:
                    failed = True
                    break
                else:
                    vpn_reconnect_counter += 1
        elif vpncheckStr[0] == "Connected":
            print("VPN Connection is up...\n")

            # Check to make sure that the VPN tunnel didn't hit reconnect max tries
            print(("FAILED is: " + str(failed)))
            if not failed:
              print(("Downloading EOS: " + version + " To: " + outputDir + "\n"))
              if not os.path.exists(outputDir):
                os.makedirs(outputDir)
                print(("Directory {0} Created".format(outputDir)))
              else:
                print(("Directory {0} already exists".format(outputDir)))
              try:
                concatDict = dict(zip(urls, outputFilename))
                for url, filename in concatDict.items():
                    # Adding in output to notify what file is currently being downloaded
                    print(("\n[Starting] Download {}".format(
                        filename.split('/')[::-1][0])))
                    try:
                        file = wget.download(url, filename)
                    except:
                        print("File Not Found Error ", sys.exc_info()[0]) 
                        try:
                            filesize = os.stat(filename)[6]
                            if filesize < 1024:
                                with open(filename) as myfile:
                                    content = myfile.read()
                                match = re.search(r'<p>(.*).</p>', content)
                                reason = match.group(1)
                                os.remove(filename)
                                print(("\n\nThere was an error downloading: " + url + "\n"))
                                print(("\t" + reason + "\n"))
                        except:
                            print(("\n[Completed] File downloaded to " + filename))
                if args.releaseNotes:
                    release_note = get_latest_rn(rn_url)
                    if release_note:
                        file = wget.download(
                            rn_url + release_note, outputDir+release_note)
                        print(("\nFile downloaded to " +
                              outputDir+release_note))
              except:
                failed = True
                file = None  # Added in so it can be used to evaluate later on
                print("Unexpected error:", sys.exc_info()[0])
        else:
            print("Unable to start VPN connection:\nEither you are not connected to the internet or you don't have the right VPN name")

    # Check to see if script opened VPN tunnel, if so disconnect from VPN
    if native_vpn_disconnect:
        print('\nDisconnecting VPN connection')
        check_output(["scutil", "--nc", "stop", vpn_name])
        print(('You have been disconnected from {0}\n'.format(vpn_name)))
    else:
        print('\nHave a great day!\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "version", type=str, help="EOS image version", default=None)

    parser.add_argument(
        "-p", "--package", type=str, default="eos", choices=["eos", "eos-2gb", "vmdk", "veos", "ceos", "pdp", "all"],
        help="specify which EOS packaging", required=False)

    # Modified to accept only the parameter
    parser.add_argument(
        "-s", "--stayConnected", action="store_true",
        help="Overrides the default behavior of disconnecting the VPN if getEOS.py made the VPN connection.", required=False)

    # Modified to accept only the parameter
    parser.add_argument(
        "-r", "--releaseNotes", action="store_true",
        help="Downloads the Current release notes for this version release.", required=False
    )

    args = parser.parse_args()
    version = args.version.upper()
    if not re.match(r"\d\.\d{1,2}\.\d{1,2}.\d{0,2}[FM]?$", version):
        parser.print_usage()
        parser.exit()
    # Adding in redundancy check in case no version supplied.
    while not version:
        version = input("Enter EOS Version: ").strip()
    main(args, version)
