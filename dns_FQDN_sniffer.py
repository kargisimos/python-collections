#this script sniffs on all interfaces
#for DNS packets and prints the FQDNs 
#found. Saves output into dns_sniffing.log.
#Needs sudo privileges to run.

from scapy.all import sniff
from scapy.all import ARP
from scapy.all import DNSQR
from scapy.all import IPv6
from scapy.all import UDP
from scapy.all import IP
from scapy.all import DNS

from datetime import datetime

import sys

def dns_sniffer(packet):
	ip46 = IPv6 if IPv6 in packet else IP
	if packet.haslayer(DNSQR) and UDP in packet and packet[UDP].sport == 53 and ip46 in packet:	
		# packet[DNS].qd.qname == DNS name
		query = packet[DNS].qd.qname.decode("utf-8") if packet[DNS].qd != None else "?"
		print(f"{query.lower()[:-1]}\t{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}")
		with open("dns_sniffing.log",'at') as f:
			f.write(f"{query.lower()[:-1]}\t{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}\n")
		
def dns_FQDN_sniffer():
	print('[+]Sniffing on all interfaces for DNS packets...\n')
	
	try:
		sniff(filter='udp port 53', store=0, prn=dns_sniffer)
	except KeyboardInterrupt:
		print('[+]Stopping sniffing...')
		sys.exit(1)

dns_FQDN_sniffer()
