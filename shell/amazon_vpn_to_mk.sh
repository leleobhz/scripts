#!/bin/bash

TXTF=$1
IFACE="bridge1"

KEY1=$(awk -vx=0 '/- Pre-Shared Key/ && m++==x {print $5}' $TXTF)
KEY2=$(awk -vx=1 '/- Pre-Shared Key/ && m++==x {print $5}' $TXTF)

OutIP_CG=$(awk -vx=0 '/- Customer Gateway/ && m++==x {print $5}' $TXTF)

IntIP1_CG=$(awk -vx=1 '/- Customer Gateway/ && m++==x {print $5}' $TXTF)

OutIP1_VPG=$(awk -vx=0 '/- Virtual Private Gateway/ && m++==x {print $6}' $TXTF)
IntIP1_VPG=$(awk -vx=1 '/- Virtual Private Gateway/ && m++==x {print $6}' $TXTF)

# BUG: BGP and AWK issues
OutIP2_CG=$(awk -vx=3 '/- Customer Gateway/ && m++==x {print $5}' $TXTF)
IntIP2_CG=$(awk -vx=4 '/- Customer Gateway/ && m++==x {print $5}' $TXTF)
OutIP2_VPG=$(awk -vx=2 '/- Virtual Private Gateway/ && m++==x {print $6}' $TXTF)
IntIP2_VPG=$(awk -vx=3 '/- Virtual Private Gateway/ && m++==x {print $6}' $TXTF)


BGP_ASN=$(awk -vx=0 '/- Customer Gateway ASN/ && m++==x {print $6}' $TXTF)
AMAZON_ASN=$(awk -vx=1 '/Gateway ASN/ && m++==x {print $7}' $TXTF)
NEIGH_IP=$(awk -vx=0 '/Neighbor IP Address/ && m++==x {print $6}' $TXTF)

IntIP1_VPG_NETWORK=$(ipcalc $IntIP1_VPG | grep Network | cut -d\  -f4 | cut -d\/ -f1)
IntIP2_VPG_NETWORK=$(ipcalc $IntIP2_VPG | grep Network | cut -d\  -f4 | cut -d\/ -f1)

echo -e "#Start of MK Config\n#Created by file $1\n#\n#Parameters:\n#\tCustomer Gateway: $OutIP_CG\n#\n#\t#1 Outside VPN Gateway: $OutIP1_VPG\n#\t#1 Inside Customer Gateway: $IntIP1_CG\n#\t#1 Inside VPN Gateway: $IntIP1_VPG\n#\t#1 Key: $KEY1\n#\n#\t#2 Outside VPN Gateway: $OutIP2_VPG\n#\t#2 Inside Customer Gateway: $IntIP2_CG\n#\t#2 Inside VPN Gateway: $IntIP2_VPG\n#\t#2 Key: $KEY2\n#"

echo -e "/ip ipsec proposal add auth-algorithms=sha1 comment=\"Amazon Pharase 1 Parameters\" enc-algorithms=aes-128 lifetime=1h name=aws pfs-group=modp1024\n#"

echo "/ip ipsec peer add address=$OutIP1_VPG/32 auth-method=pre-shared-key dh-group=modp1024 dpd-interval=10s dpd-maximum-failures=3 enc-algorithm=aes-128 exchange-mode=main hash-algorithm=sha1 lifetime=8h proposal-check=obey secret=$KEY1 send-initial-contact=yes"
echo -e "/ip ipsec peer add address=$OutIP2_VPG/32 auth-method=pre-shared-key dh-group=modp1024 dpd-interval=10s dpd-maximum-failures=3 enc-algorithm=aes-128 exchange-mode=main hash-algorithm=sha1 lifetime=8h proposal-check=obey secret=$KEY2 send-initial-contact=yes\n#"

echo "/ip ipsec policy add action=encrypt dst-address=10.0.0.0/16 dst-port=any ipsec-protocols=esp level=unique proposal=aws protocol=all sa-dst-address=$OutIP1_VPG sa-src-address=$OutIP_CG src-address=0.0.0.0/0 src-port=any tunnel=yes"
echo "/ip ipsec policy add action=encrypt dst-address=10.0.0.0/16 dst-port=any ipsec-protocols=esp level=unique proposal=aws protocol=all sa-dst-address=$OutIP2_VPG sa-src-address=$OutIP_CG src-address=0.0.0.0/0 src-port=any tunnel=yes"

echo "/ip ipsec policy add action=encrypt dst-address=$IntIP1_VPG dst-port=any ipsec-protocols=esp level=unique proposal=aws protocol=all sa-dst-address=$OutIP1_VPG sa-src-address=$OutIP_CG src-address=0.0.0.0/0 src-port=any tunnel=yes"
echo -e "/ip ipsec policy add action=encrypt dst-address=$IntIP2_VPG dst-port=any ipsec-protocols=esp level=unique proposal=aws protocol=all sa-dst-address=$OutIP2_VPG sa-src-address=$OutIP_CG src-address=0.0.0.0/0 src-port=any tunnel=yes\n#"

echo "ip address add address=$IntIP1_CG disabled=no interface=$IFACE network=$IntIP1_VPG_NETWORK"
echo "ip address add address=$IntIP2_CG disabled=no interface=$IFACE network=$IntIP2_VPG_NETWORK"
