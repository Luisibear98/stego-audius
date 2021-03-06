from __future__ import print_function, unicode_literals
from time import sleep
from PyInquirer import prompt
import socket
import pickle
from backend.utils import *
import numpy as np
import threading
from tqdm import tqdm
from examples import custom_style_2
import os, sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import os.path
import math


modeSelector = {
    'type': 'list',
    'name': 'modes',
    'message': 'Select a mode',
    'choices': [
        'Fix text',
        'Streaming',
        'Quit',
    ],
}

textInput = {
    'type': 'input',
    'name': 'text',
    'message': 'Type the texto to send',
}

confirmRerun = {
    'type': 'confirm',
    'message': 'Do you want to restart the program?',
    'name': 'restart',
    'default': True,
}

confirmDetection = {
    'type': 'confirm',
    'message': 'Are you sure?',
    'name': 'detection',
    'default': False,
}

flag = 0

send_info = ""

send_buffer = []

def my_callback(inp):
    # evaluate the keyboard input
    global send_info
    global flag
    flag = 1
    send_info += inp


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())  # waits to get input + Return

  
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

print_ascii()

mode = prompt(modeSelector, style=custom_style_2)["modes"]
sure = False


if mode != "Quit":
    # Select embeding key
    embding_key = input("From 0-10 how detectable do you want the secret message to be?: ")
    try:
        embeding_key = int(embding_key) + 35    # Embeding key is between 35 and 45 according to the papers results
        if embeding_key > 45:
            print("WARNING: Parameter over 10 is not recommendable")
            sure = prompt(confirmDetection, style=custom_style_2)["detection"]

            # If user wants to select a recommended value
            while not sure:
                embding_key = input("From 0-10 how detectable do you want the secret message to be?: ")
                try:
                    embeding_key = int(embding_key) + 35
                    if embeding_key > 45:
                        print("WARNING: Parameter over 10 is not recommendable")
                        sure = prompt(confirmDetection, style=custom_style_2)["detection"]
                    elif embeding_key < 35:
                        print("ERROR: Parameter must be over 0")
                        exit(-1)
                except ValueError:
                    print("ERROR: Input must be a number")
                    exit(-1)
        elif embeding_key < 35:
            print("ERROR: Parameter must be over 0")
            exit(-1)
    except ValueError:
        print("ERROR: Input must be a number")
        exit(-1)

    have_audio = 0
    while not have_audio:
        filename = input("Please, introduce the name of the file in audio/ folder you want to strean, i.e test.wav: ")
    
        if os.path.isfile("./audio/"+filename):
            if not filename.endswith(".wav"): #Un poco chapuza y poco seguro, pero no merece la pena ir m??s all??
                print("ERROR: File provided must be a wav file")
                continue
            print("OK: File found")
            have_audio = 1
        else:
            print("ERROR: File not found")
       
    capacity =  estimate_capacity(filename,embeding_key) - 8 
    max_chars = math.floor(capacity/8)
    print("With that set up, the aproximated capacity is: " + str(capacity)+ " bits")
    print("That yields to: " + str(max_chars)+ " Characters")   
   

    communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    communication_socket.connect((HOST, PORT+1))
    metadata = []
    if mode == "Fix text":
        metadata.append(1)
    elif mode == "Streaming":
        metadata.append(2)

    if metadata:
        metadata.append(embding_key)
        
    send_package = pickle.dumps(metadata)
    communication_socket.sendall(send_package)
    communication_socket.close()




# Inserts text in audio and sends it in stream to he client
if mode == "Fix text":
    while 1:
        text_str = bytes(input("Enter the text to send: "), "utf-8")

        if len(text_str)  > max_chars:
            print("Please insert a shorter text")
        else:
            break
    
    password = bytes(getpass.getpass(prompt="Enter password to encrypt text: "), "utf-8")
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text_str)
    print(encrypted_text)
    insert_on_channel_1 = process_audio(encrypted_text, embding_key,filename)

    print("Audio processed ...")
    to_send = serialize_channel(insert_on_channel_1)  # Serializing data
    # Transforming information to bytes
    bytes = np.array(to_send, np.int16).tobytes()
    to_send = list(slice_chunks(bytes, len(bytes)))  # Splitting in chunks of 3 kb
    
    # Opening socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))  # Binding socket
        s.listen()
        print("Waiting for a connection ...")
        metadata.append(1)
        metadata.append(salt)
        
        communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        communication_socket.connect((HOST, PORT+1))
        communication_socket.sendall(pickle.dumps(metadata))
        communication_socket.close()

        while 1:
            conn, addr = s.accept()
            with conn:
                # Streaming bytes of audio with stego

                for i in tqdm(range(len(to_send))):
                    conn.sendall(to_send[i])  # Ensuring all data arrives
                print("Transminssion ended ...")
                print("Wait till song is playing :)")
                print_bye()
                exit()

# Real time processing
elif mode == "Streaming":
    #real time text sending
    audio = read_wav(filename)
    channel_1 = audio[0]    
    insert = []
    
    channel_1_splited = split_channel(channel_1,3) #Splitting audio

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        send_info = chr(0x02)
        
        s.bind((HOST, PORT))
        s.listen()
        print("Listening...")
        position = 0
        sent = 0
        processing = 0
        print("Sending flag...")    #Sending metadata to client
        metadata.append(2)
        communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        communication_socket.connect((HOST, PORT+1))
        communication_socket.sendall(pickle.dumps(metadata))
        communication_socket.close()
        flag = 0
        print("Now you can insert data on the fly")
        while 1:
            conn, addr = s.accept()
            with conn:
                
                #env??o del audio con texto
                kthread = KeyboardThread(my_callback) #Monitoring user input
                for position in range(len(channel_1_splited)):
             
                    if flag and sent % 8 == 0:          #wait until 8 bits have been sent before
                        if not processing:
                            start = [1]
                            send_package = pickle.dumps(start) #Sending synchronization flag
                            conn.sendall(send_package)
                            sleep(1)
                            processing = 1
            
                        bina = binarize(send_info)      #transforming user input to bits
                        insert =[]
                        bit_sent = 0
  
                        for bit in bina:
                            insert.append(int(bit))
                        
                        for i in range(8):
                            insert.append(1)
                       
                        while bit_sent < len(insert):
                          
                            package,inserted= insert_on_real_time(insert[bit_sent],channel_1_splited[position],embding_key) #Inserting stego

                            
                            if inserted:
                                bit_sent += 1
                            send_package = pickle.dumps(package)
                          
                          
                            conn.sendall(send_package)
                            position += 1
                        
                        flag = 0
                        send_info = chr(0x02)
                        processing = 0
                      
                    else:
                        package = channel_1_splited[position] #Normal audio stream
                        send_package = pickle.dumps(package)
                        conn.sendall(send_package)
                        sent += 1
                
                break

    print_bye()
    exit()

else:
    print_bye()
    exit()
