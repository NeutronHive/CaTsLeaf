import socket
import os
import zipfile
import subprocess

# IP and port for the node PC to listen on
listen_ip = '0.0.0.0'  # Listen on all available network interfaces
listen_port = 12345

while True:
    try:
        # Create a socket to listen for incoming connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((listen_ip, listen_port))
            s.listen()

            print(f"Listening for connections on {listen_ip}:{listen_port}")

            # Accept a connection from the admin PC
            conn, addr = s.accept()
            print(f"Connection from {addr[0]}:{addr[1]}")

            # Receive the ZIP archive
            with open('received_folder.zip', 'wb') as zip_file:
                zip_data = conn.recv(1024)
                while zip_data:
                    zip_file.write(zip_data)
                    zip_data = conn.recv(1024)

        print("ZIP archive received on the node PC.")

        # Extract the received ZIP archive
        with zipfile.ZipFile('received_folder.zip', 'r') as zip_ref:
            zip_ref.extractall('extracted_folder')

        # Execute the batch file from the extracted folder
        batch_file_path = os.path.join('extracted_folder', 'run_program.bat')
        print(batch_file_path)
        try:
            subprocess.run([batch_file_path], shell=True, check=True)
            print("Batch file executed successfully.")
        except subprocess.CalledProcessError:
            print("Batch file execution failed.")
        # Delete the extracted folder and ZIP file
        os.remove('received_folder.zip')
        os.rmdir('extracted_folder')

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Add a delay before listening for the next connection
    # Adjust the duration of the delay as needed
    import time
    time.sleep(5)  # Wait for 5 seconds before checking for the next connection
