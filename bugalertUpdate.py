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
1. Copy the script to /mnt/flash on CVX VM
2. change values of username and password to a valid www.arista.com account
3. run the script with.. ./bugalertUpdate.py
"""
__author__ = 'chines'

import base64, json, warnings, requests
import sys
import cStringIO
from shutil import copyfile
from AlertBaseImporter import AlertBaseImporter

username = 'CHANGEME'
password = 'CHANGEME'

importdb = False

stdout_ = sys.stdout            ### Trying to use this later to redirect output of the database import to cut the noise. This isn't working yet.
stream = cStringIO.StringIO()

string = username + ':' + password
creds = (base64.b64encode(string.encode()))

url = 'https://www.arista.com/custom_data/bug-alert/alertBaseDownloadApi.php'

warnings.filterwarnings("ignore")

jsonpost = {'user_auth': creds}

result = requests.post(url, data=json.dumps(jsonpost))

web_data = json.loads(result.text)
web_data_final = result.text
alertBaseFile = '/persist/sys/AlertBase.json'
alertBaseFileFlash = '/mnt/flash/AlertBase.json'
sysname = 'ar'

alertBaseImporter = AlertBaseImporter( alertBaseFile, sysname )

try:
    with open(alertBaseFile) as file:
        pass
except IOError as e:
    print "Bug Alert Database does not exist. Downloading..."
    alertdbfile = open(alertBaseFile, 'w')
    alertdbfile.write(web_data_final)
    alertdbfile.close()
    copyfile(alertBaseFile, alertBaseFileFlash)
    alertBaseImporter.loadAlertBase()
    print('\n\n Bug Alert Database successfully created and imported\n')
    exit(0)

sysdb_version = alertBaseImporter.alertBaseSysdb.genId
sysdb_releaseDate = alertBaseImporter.alertBaseSysdb.releaseDate

web_version = web_data['genId']

if  sysdb_version != web_version:
    print "\n Updating BugAlert database file!\n"
    alertdbfile = open(alertBaseFile, 'w')
    alertdbfile.write(web_data_final)
    alertdbfile.close()
    importdb = True
    updatedDB = "YES"
else:
    importdb = False
    #print('\n\n Bug Alert Database is already up to date!\n')

if importdb == True:
    print('\n\n Bug Alert Database was updated, importing new entries...\n\n')
    sys.stdout = stream
    try:
        alertBaseImporter.loadAlertBase()
        sys.stdout = stdout_
        result = stream.getvalue()
        dbImported = "YES"
        #print('\n\n Bug Alert Database successfully imported\n')
    except:
        sys.stdout = stdout_
        result = stream.getvalue()
        print('Bug Alert Database import failed!')
        dbImported = "FAILED"
        exit (1)
else:
    updatedDB = "NO"
    dbImported = "NO"

print('\nSUMMARY').expandtabs(18)
print('\n' + 'alertDB' + '\t'+ 'Release Date' + '\t' + 'Version ID').expandtabs(18)
print('----------' + '\t' + '------------' + '\t' + '------------------------------------').expandtabs(18)
print('installed   -->' + '\t' + sysdb_releaseDate + '\t' + sysdb_version).expandtabs(18)
print('available   -->' + '\t' + web_data['releaseDate'] + '\t' + web_version).expandtabs(18)
print('\n')
print('Database updated:' + '\t' +'\t' + updatedDB).expandtabs(18)
print('Database imported:' + '\t' + dbImported).expandtabs(18)
print('\n')

try:
    with open(alertBaseFileFlash) as file:
        pass
except IOError as e:
    copyfile(alertBaseFile, alertBaseFileFlash)

exit(0)