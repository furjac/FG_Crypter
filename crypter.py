import os
import stat
import platform
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from colorama import Fore, Style


def generate_random_key(key_size):
    return os.urandom(key_size)


def generate_random_iv():
    return os.urandom(16)  # Generate a random 128-bit IV


def encrypt_file(input_file, output_file):
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
    display_menu()
    choice = input(Fore.CYAN + "Enter your choice: " + Style.RESET_ALL)

    if choice == "1":
        input_file = input(Fore.YELLOW + "Enter the path of the input file: " + Style.RESET_ALL)
        output_file = input(Fore.YELLOW + "Enter the path of the output file: " + Style.RESET_ALL)
        encrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
    elif choice == "2":
        input_file = input(Fore.YELLOW + "Enter the path of the input file: " + Style.RESET_ALL)
        output_file = input(Fore.YELLOW + "Enter the path of the output file: " + Style.RESET_ALL)
        decrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
    elif choice == "3":
        print(Fore.RED + "Cleaning up FG_Crypter" + Style.RESET_ALL)
        break
    else:
        print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
