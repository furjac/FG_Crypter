import os
import stat
import platform
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from colorama import Fore, Style


def generate_random_key(key_size):
    return os.urandom(key_size)


def encrypt_file(input_file, output_file):
    key = generate_random_key(32)  # Generate a random 256-bit key
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        while True:
            chunk = f_in.read(16)
            if not chunk:
                break
            padded_chunk = pad(chunk, 16)
            encrypted_chunk = cipher.encrypt(padded_chunk)
            f_out.write(encrypted_chunk)

    print(Fore.GREEN + "Encryption completed successfully.")
    print("Encryption Key: " + key.hex() + Style.RESET_ALL)


def decrypt_file(input_file, output_file):
    key = input("Enter the encryption key: ")
    key = bytes.fromhex(key)
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        while True:
            encrypted_chunk = f_in.read(32)
            if not encrypted_chunk:
                break
            decrypted_chunk = unpad(cipher.decrypt(encrypted_chunk), 32)
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
    print("1. Encrypt a file")
    print("2. Decrypt a file")
    print("3. Quit" + Style.RESET_ALL)


# Example usage
while True:
    display_menu()
    choice = input("Enter your choice: ")

    if choice == "1":
        input_file = input("Enter the path of the input file: ")
        output_file = input("Enter the path of the output file: ")
        encrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
    elif choice == "2":
        input_file = input("Enter the path of the input file: ")
        output_file = input("Enter the path of the output file: ")
        decrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
    elif choice == "3":
        print(Fore.RED + "Cleaning up FG_Crypter" + Style.RESET_ALL)
        break
    else:
        print(Fore.YELLOW + "Invalid choice. Please try again." + Style.RESET_ALL)
