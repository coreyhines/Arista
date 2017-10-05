#!/bin/sh

find /sys/class/net/ -maxdepth 1 -name 'en*' |
    while read device; do
        basename "$device"
    done |
    while read interface; do
        {
            lldptool set-lldp -i "$interface" adminStatus=rxtx
            for item in sysName portDesc sysDesc sysCap mngAddr; do
                lldptool set-tlv -i "$interface" -V "$item" enableTx=yes |
                    sed -e "s/^/$item /"
            done
        } |
            sed -e "s/^/$interface /"
    done
