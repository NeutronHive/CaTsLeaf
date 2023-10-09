import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import socket
import os
import zipfile
import pandas as pd
node_port=12345
# Default list of receiver IPs
default_ip_list = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]

# Function to send the folder to receiver PCs
def send_folder_to_receivers():
    folder_path = folder_path_entry.get()
    use_default = default_checkbox_var.get()
    
    if use_default:
        node_ips = default_ip_list
    else:
        # Check if the admin provided an IP list file
        ip_list_file = ip_list_entry.get()
        if ip_list_file:
            # Read IP addresses from the Excel file
            try:
                df = pd.read_excel(ip_list_file)
                node_ips = df['IP'].tolist()
            except Exception as e:
                messagebox.showerror("Error", f"Error reading IP list from Excel file: {str(e)}")
                return
        else:
            # Read IP addresses from manual input
            node_ips = manual_ip_list_entry.get().split(',')

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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node_ip.strip(), node_port))

                # Send the ZIP archive
                with open(zip_filename, 'rb') as zip_file:
                    zip_data = zip_file.read()
                    s.send(zip_data)

            messagebox.showinfo("Success", f"ZIP archive sent to the node PC at IP {node_ip.strip()}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send to {node_ip.strip()}. Error: {str(e)}")

    # Clean up: Remove the ZIP archive after sending to all target PCs
    os.remove(zip_filename)

# Function to browse and select a folder
def select_folder():
    folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)

# Function to browse and select an Excel file containing IP addresses
def select_ip_list_file():
    ip_list_file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    ip_list_entry.delete(0, tk.END)
    ip_list_entry.insert(0, ip_list_file)

# Create the main GUI window
root = tk.Tk()
root.title("Folder Sender App")

# Set window dimensions
root.geometry("400x400")

# Create a frame for IP options
ip_frame = tk.Frame(root)
ip_frame.pack(pady=10)

# Default IP List Checkbox
default_checkbox_var = tk.BooleanVar()
default_checkbox = tk.Checkbutton(ip_frame, text="Use Default IP List", variable=default_checkbox_var)
default_checkbox.grid(row=0, column=0, padx=10)

# Manual IP Entry
manual_ip_label = tk.Label(ip_frame, text="Enter IP addresses manually (comma-separated):")
manual_ip_label.grid(row=1, column=0, padx=10, pady=5)
manual_ip_list_entry = tk.Entry(ip_frame)
manual_ip_list_entry.grid(row=2, column=0, padx=10, pady=5)

# Excel Upload Button
excel_upload_button = tk.Button(ip_frame, text="Upload Excel IP List", command=select_ip_list_file)
excel_upload_button.grid(row=3, column=0, padx=10, pady=5)

# IP List Entry
ip_list_label = tk.Label(ip_frame, text="Or select an Excel file containing IP addresses:")
ip_list_label.grid(row=4, column=0, padx=10, pady=5)
ip_list_entry = tk.Entry(ip_frame)
ip_list_entry.grid(row=5, column=0, padx=10, pady=5)

# Create a frame for folder selection
folder_frame = tk.Frame(root)
folder_frame.pack(pady=10)

# Folder Selection
folder_label = tk.Label(folder_frame, text="Select a folder to send:")
folder_label.grid(row=0, column=0, padx=10)
folder_path_entry = tk.Entry(folder_frame)
folder_path_entry.grid(row=1, column=0, padx=10)
browse_button = tk.Button(folder_frame, text="Browse", command=select_folder)
browse_button.grid(row=1, column=1, padx=10)

# Send Button
send_button = tk.Button(root, text="Send Folder", command=send_folder_to_receivers)
send_button.pack(pady=10)

# Start the GUI application
root.mainloop()
