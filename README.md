# Arista

bugalertUpdate.py - Script to install and update the Bug Alert Database on CVX

This script is now in limited maintenance development mode. CloudVision Portal (CVP) 2018.2.3 was released with the Compliance Dashboard feature. This feature is superior to the original bug alert service provided by th4e CVX controller. Please upgrade to CVP 2018.2.3 and enjoy bug alerts from real time telemetry and CloudVision Portal.

 This script will check to see if your CVX node has the /mnt/flash/AlertBase.json file. It will attempt to download and install it or update the database if a newer version is available.

INSTALLATION

   copy this script to /mnt/flash on the CVX EOS VM.
   change values of username and password to a valid www.arista.com account

   run the script from bash to install the alertbase database

   run the script subsequently from the EOS scheduler for periodic update checks

 To learn more about the Arista CloudVision Exchange (CVX) based Bugalert feature, see: https://eos.arista.com/eos-4-17-0f/bug-alerts/
