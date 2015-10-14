#!/bin/bash

echo "# Configuarions for Juniper JUNOS SNMPv2 MIBs download from juniper.net
#

HOST=http://www.juniper.net
ARCHIVE=juniper-mibs-14.2R4.9.zip
ARCHTYPE=zip
ARCHDIR=juniper-mibs-14.2R4.9/JuniperMibs
DIR=techpubs/software/junos/junos142
CONF=junoslist
DEST=juniper" > /etc/snmp-mibs-downloader/junos.conf

(for i in *.txt ; do echo -ne "$i\t" ; grep DEFINITION $i | head -n1 | awk '{print $1}' ; done ) > /etc/snmp-mibs-downloader/junoslist

download-mibs junos
