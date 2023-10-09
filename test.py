import socket
import os
import zipfile
from scapy.all import ARP, Ether, srp
import nmap
node_mac_addresses = ['8C:EC:4B:B8:BF:1C']
nm = nmap.PortScanner()
def get_mac_from_ip(ip_address):
    
    nm.scan(hosts=ip_address, arguments='-sn')  # Perform an ARP scan for the given IP

    if ip_address in nm.all_hosts() and 'mac' in nm[ip_address]['addresses']:
        return nm[ip_address]['addresses']['mac'].upper()
    else:
        return None

def find_ip():
    
    nm.scan(hosts='10.7.3.0/24', arguments='-sn')  # Replace with your network range

    node_ips = []
    print(nm.all_hosts())
    for ip in nm.all_hosts():
        mymac=get_mac_from_ip(ip)
        print(mymac)
        if mymac in node_mac_addresses:
            node_ips.append(ip)

    return node_ips

node_ips = find_ip()
print(node_ips)
# List of IP addresses of the target node PCs
node_port=12345
# Define the path to the folder you want to send
folder_path = './tp'  # Replace with the path to your folder

# Create a ZIP archive of the folder
zip_filename = 'my_folder.zip'
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_path)
            zipf.write(file_path, arcname=arcname)

# Iterate through the list of target node IPs and send the ZIP archive
for node_ip in node_ips:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((node_ip, node_port))

        # Send the ZIP archive
        with open(zip_filename, 'rb') as zip_file:
            zip_data = zip_file.read()
            s.send(zip_data)

    print(f"ZIP archive sent to the node PC at IP {node_ip}.")

# Clean up: Remove the ZIP archive after sending to all target PCs
os.remove(zip_filename)
