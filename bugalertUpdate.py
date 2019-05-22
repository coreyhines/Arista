#!/usr/bin/env python
#
# Copyright (c) 2017, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# bugalertUpdate.py
#
#    Written by:
#       Corey Hines, Arista Networks
#
"""
DESCRIPTION
A Python script for updating the AlertBase.json file on CVX running EOS.
Script can be run manually, or using a scheduler to automatically check www.arista.com
for database updates for the CVX Bugalerts feature.

To learn more about BugAlerts see: https://eos.arista.com/eos-4-17-0f/bug-alerts/

INSTALLATION
1. ssh to the primary CVX node in the CVX cluster
2. wget https://github.com/coreyhines/Arista/raw/master/bugalertUpdate.py
3. run the script with.. ./bugalertUpdate.py --user USERNAME --password PASSWORD
4. add --proxy and --protocol arguments if a proxy is used
"""
__author__ = 'chines'

import sys
import argparse
import cStringIO
from shutil import copyfile
import base64
import json
import warnings
import requests
import syslog
from AlertBaseImporter import AlertBaseImporter

username = 'CHANGEME'
password = 'CHANGEME'

warnings.filterwarnings("ignore")
parser = argparse.ArgumentParser()
parser.add_argument('--user', required=False,
                    default=username, help='arista.com user')
parser.add_argument('--password', required=False, default=password,
                    help='password corresponding to the username')
parser.add_argument('--proxy', default=None,
                    help='IP and port of the proxy server, e.g. 10.10.10.10:4444')
parser.add_argument('--protocol', default='https',
                    help='http or https, if not specified https is used')

args = parser.parse_args()

# Initialize the dictionary for the Proxy server and populate it with the given arguments
proxies = {}
if args.proxy:
    proxies[args.protocol] = args.proxy
print "Proxies dictionary is: ",

username = args.user
password = args.password

importdb = False

syslog.openlog("BugAlertUpdater", 0, syslog.LOG_LOCAL4)


def to_syslog(sys_title, sys_msg):
    syslog.syslog("%%BugAlert-6-LOG: %s: %s" % (sys_title, sys_msg))


# Trying to use this later to redirect output of the database import to cut the noise
stdout_ = sys.stdout
stream = cStringIO.StringIO()

string = username + ':' + password
creds = (base64.b64encode(string.encode()))

url = 'https://www.arista.com/custom_data/bug-alert/alertBaseDownloadApi.php'

warnings.filterwarnings("ignore")

jsonpost = {'user_auth': creds}

result = requests.post(url, data=json.dumps(jsonpost), proxies=proxies)
web_data = json.loads(result.text)
web_data_final = result.text

alertBaseFile = '/persist/sys/AlertBase.json'
alertBaseFileFlash = '/mnt/flash/AlertBase.json'
sysname = 'ar'

# Instantiate an object form the class AlertBaseImporter
alertBaseImporter = AlertBaseImporter(alertBaseFile, sysname)

try:
    with open(alertBaseFile) as filetest:
        # Check if the AlertBase JSON file exists
        pass
except IOError as e:
    # handle the exception (file doesn't exist) by downloading the AlertBase JSON
    print ('\n Bug Alert Database does not exist. Downloading...\n')
    alertdbfile = open(alertBaseFile, 'w')
    alertdbfile.write(web_data_final)
    alertdbfile.close()
    copyfile(alertBaseFile, alertBaseFileFlash)
    # Import the AlertBase JSON
    alertBaseImporter.loadAlertBase()
    print('\n Bug Alert Database successfully created and imported\n')
    exit(0)

# Extract the BugAlert genId and the releaseDate from local CVX SysDB
sysdb_version = alertBaseImporter.alertBaseSysdb.genId
sysdb_releaseDate = alertBaseImporter.alertBaseSysdb.releaseDate

# Extract the genId from the latest AlertBase available at arista.com
web_version = web_data['genId']

if sysdb_version != web_version:  # If the version on arista.com is newer, download and install it
    print "\n Updating BugAlert database file!\n"
    alertdbfile = open(alertBaseFile, 'w')
    alertdbfile.write(web_data_final)
    alertdbfile.close()
    importdb = True
    updatedDB = "YES"
else:
    importdb = False

if importdb:
    print('\n\n Bug Alert Database was updated, importing new entries...\n\n')
    sys.stdout = stream
    try:
        alertBaseImporter.loadAlertBase()
        sys.stdout = stdout_
        result = stream.getvalue()
        dbImported = "YES"
    except:
        sys.stdout = stdout_
        result = stream.getvalue()
        print('Bug Alert Database import failed!')
        to_syslog("BugAlert Import", "Failed")
        dbImported = "FAILED"
        exit(1)
else:
    updatedDB = "NO"
    dbImported = "NO"

# Send summary to Syslog
to_syslog("Installed Version", sysdb_version)
to_syslog("Available Version", web_version)
to_syslog("Database Updated/Imported", "%s/%s" % (updatedDB, dbImported))

# Print a summary of what occurred in a table output
print('\nSUMMARY').expandtabs(18)
print('\n' + 'alertDB' + '\t' + 'Release Date' +
      '\t' + 'Version ID').expandtabs(18)
print('----------' + '\t' + '------------' + '\t' +
      '------------------------------------').expandtabs(18)
print('installed   -->' + '\t' + sysdb_releaseDate +
      '\t' + sysdb_version).expandtabs(18)
print('available   -->' + '\t' +
      web_data['releaseDate'] + '\t' + web_version).expandtabs(18)
print('\n')
print('Database updated:' + '\t' + '\t' + updatedDB).expandtabs(18)
print('Database imported:' + '\t' + dbImported).expandtabs(18)
print('\n')

# Failsafe to make sure the AlertBase file is in Flash as well as on /persist
# This could be a case where file is deleted from /mnt/flash
try:
    with open(alertBaseFileFlash) as file:
        pass
except IOError as e:
    copyfile(alertBaseFile, alertBaseFileFlash)
exit(0)
