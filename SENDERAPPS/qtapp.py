import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtGui import QIcon
import os
import zipfile
import pandas as pd
import socket
import nmap

node_port = 12345
default_mac_list = ['DC:21:48:F7:36:95']  # Default list of MAC addresses

class FolderSenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CaTsLeaf Tool")
        self.setGeometry(200, 200, 800, 500)
        self.setWindowIcon(QIcon("logo.png"))

        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Use Default MAC List Checkbox
        self.default_checkbox = QCheckBox("Use Default MAC List", self)
        layout.addWidget(self.default_checkbox)

        # Manual MAC Entry
        self.manual_mac_label = QLabel(
            "Enter MAC addresses manually (comma-separated):", self
        )
        layout.addWidget(self.manual_mac_label)
        self.manual_mac_list_entry = QLineEdit(self)
        layout.addWidget(self.manual_mac_list_entry)

        # Excel Upload Button
        self.excel_upload_button = QPushButton("Upload Excel MAC List", self)
        self.excel_upload_button.clicked.connect(self.select_mac_list_file)
        layout.addWidget(self.excel_upload_button)

        # MAC List Entry
        self.mac_list_label = QLabel(
            "Or select an Excel file containing MAC addresses:", self
        )
        layout.addWidget(self.mac_list_label)
        self.mac_list_entry = QLineEdit(self)
        layout.addWidget(self.mac_list_entry)

        # Subnet Entry
        self.subnet_label = QLabel("Enter Subnet (e.g., 192.168.1.0/24):", self)
        layout.addWidget(self.subnet_label)
        self.subnet_entry = QLineEdit(self)
        layout.addWidget(self.subnet_entry)

        # Folder Selection
        self.folder_label = QLabel("Select a folder to send:", self)
        layout.addWidget(self.folder_label)
        self.folder_path_entry = QLineEdit(self)
        layout.addWidget(self.folder_path_entry)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.select_folder)
        layout.addWidget(self.browse_button)

        # Send Button
        self.send_button = QPushButton("Send Folder", self)
        self.send_button.clicked.connect(self.send_folder_to_receivers)
        layout.addWidget(self.send_button)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a folder to send")
        self.folder_path_entry.setText(folder_path)

    def select_mac_list_file(self):
        mac_list_file, _ = QFileDialog.getOpenFileName(
            self, "Upload Excel MAC List", "", "Excel Files (*.xlsx)"
        )
        self.mac_list_entry.setText(mac_list_file)

    def send_folder_to_receivers(self):
        folder_path = self.folder_path_entry.text()
        use_default = self.default_checkbox.isChecked()

        if use_default:
            mac_addresses = default_mac_list
        else:
            mac_list_file = self.mac_list_entry.text()
            if mac_list_file:
                try:
                    df = pd.read_excel(mac_list_file)
                    mac_addresses = df["MAC"].tolist()
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error reading MAC list from Excel file: {str(e)}",
                    )
                    return
            else:
                mac_addresses = self.manual_mac_list_entry.text().split(",")

        subnet = self.subnet_entry.text().strip()
        if not subnet:
            QMessageBox.critical(
                self,
                "Error",
                "Please enter a subnet (e.g., 192.168.1.0/24).",
            )
            return

        zip_filename = "my_folder.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=arcname)

        node_ips = find_ip(mac_addresses, subnet)

        for node_ip in node_ips:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((node_ip.strip(), node_port))

                    with open(zip_filename, "rb") as zip_file:
                        zip_data = zip_file.read()
                        s.send(zip_data)

                QMessageBox.information(
                    self,
                    "Success",
                    f"ZIP archive sent to the node PC at IP {node_ip.strip()}.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to send to {node_ip.strip()}. Error: {str(e)}",
                )

        os.remove(zip_filename)


def find_ip(mac_addresses, subnet):
    node_ips = []

    nm = nmap.PortScanner()
    
    nm.scan(hosts=subnet, arguments='-sn')
    
    for ip in nm.all_hosts():
        my_mac = get_mac_from_ip(ip)
        if my_mac and my_mac in mac_addresses:
            node_ips.append(ip)
    
    return node_ips

def get_mac_from_ip(ip_address):
    nm = nmap.PortScanner()
    
    nm.scan(hosts=ip_address, arguments='-sn')  # Perform an ARP scan for the given IP

    if ip_address in nm.all_hosts() and 'mac' in nm[ip_address]['addresses']:
        return nm[ip_address]['addresses']['mac'].upper()
    else:
        return None

def main():
    app = QApplication(sys.argv)
    ex = FolderSenderApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
