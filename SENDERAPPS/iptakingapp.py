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
import socket
import os
import zipfile
import pandas as pd

node_port = 12345
# Default list of receiver IPs
default_ip_list = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]


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

        # Use Default IP List Checkbox
        self.default_checkbox = QCheckBox("Use Default IP List", self)
        layout.addWidget(self.default_checkbox)

        # Manual IP Entry
        self.manual_ip_label = QLabel(
            "Enter IP addresses manually (comma-separated):", self
        )
        layout.addWidget(self.manual_ip_label)
        self.manual_ip_list_entry = QLineEdit(self)
        layout.addWidget(self.manual_ip_list_entry)

        # Excel Upload Button
        self.excel_upload_button = QPushButton("Upload Excel IP List", self)
        self.excel_upload_button.clicked.connect(self.select_ip_list_file)
        layout.addWidget(self.excel_upload_button)

        # IP List Entry
        self.ip_list_label = QLabel(
            "Or select an Excel file containing IP addresses:", self
        )
        layout.addWidget(self.ip_list_label)
        self.ip_list_entry = QLineEdit(self)
        layout.addWidget(self.ip_list_entry)

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

    def select_ip_list_file(self):
        ip_list_file, _ = QFileDialog.getOpenFileName(
            self, "Upload Excel IP List", "", "Excel Files (*.xlsx)"
        )
        self.ip_list_entry.setText(ip_list_file)

    def send_folder_to_receivers(self):
        folder_path = self.folder_path_entry.text()
        use_default = self.default_checkbox.isChecked()

        if use_default:
            node_ips = default_ip_list
        else:
            ip_list_file = self.ip_list_entry.text()
            if ip_list_file:
                try:
                    df = pd.read_excel(ip_list_file)
                    node_ips = df["IP"].tolist()
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error reading IP list from Excel file: {str(e)}",
                    )
                    return
            else:
                node_ips = self.manual_ip_list_entry.text().split(",")

        zip_filename = "my_folder.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=arcname)

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


def main():
    app = QApplication(sys.argv)
    ex = FolderSenderApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
