

from turtle import bye
from backend.utils import *
import socket
import pickle
import pyaudio
import numpy as np
from time import sleep
from scipy.io.wavfile import write
import soundfile as sf
import threading
import asyncio
import gc
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

HOST = "127.0.0.1"  # The server'socket hostname or IP address
PORT = 65432  # The port used by the server

stream = None
stego_audio = []
receive = 0

salt = None



async def play(data):
    global stream
    stream.write(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as meta:

    meta.bind((HOST, PORT+1))  # Binding socket
    meta.listen()
    print("Waiting for metada synchronization ...")

    while 1:
        conn, addr = meta.accept()
        with conn:
            data = conn.recv(100)
            message = pickle.loads(data)
           
            mode = message[0]
            embedding_key = int(message[1])
            print("received information")
            if len(message) >= 3:
                if len(message) == 4:
                    salt = message[3]
                break
           

print("Synchronized")
if mode and embedding_key:
    # chunk mode
    if mode == 1 and salt:
        try:
            password = bytes(getpass.getpass(prompt="Enter password: "), "utf-8")
            if salt == None:
                print("No salt, could not decrypt message.")
                exit()
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256, length=32, salt=salt, iterations=390000)
            key = base64.urlsafe_b64encode(kdf.derive(password))
            print(key)
            fernet = Fernet(key)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
                socket.connect((HOST, PORT))
                packet = None
                audio = []
                stego_text = ""
                
                done = 0

                while 1:
                    data = socket.recv(6000)  # Receiving 3kb from server
                    
                    if not data:    #If no data client quits
                        break
                    
                    stream.write(data)  # Playing sound
                    data = np.frombuffer(data, dtype=np.int16)
                    
                    if done == 0:
                        recovered_bits = recovering_info(data,embedding_key)  # groups bits in group of 8
                    
                        for group in recovered_bits:
                            # transforming bytes to char
                        
                            if sum(group) == 8:  # message has ended decrypted_message
                                print(type(stego_text))
                                lol = bytes(stego_text.replace("b'",'').replace("'",''), "utf-8")
                                print(lol)
                                print(type(lol))
                                

                                decrypted_message = fernet.decrypt(lol)
                                print(decrypted_message)
                        
                                print("Transmission ended, the message is: " + decrypted_message.decode("utf-8"))
                                
                                done = 1
                            else:
                            
                                stego_text+= bits2string(group)
                            
                    audio.extend(data)

                print("Saving copy")
                sf.write("stego.wav",np.array(audio) , 44100)
        except:
            print("Error. Could not decrypt message.")
            exit(0)



    # real time text sending
    if mode == 2:
        
        
        buffer_audio = []

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            packet = []
            transmited = 0
            prints = 0
            process = 0
            bytes = b''
            p = pyaudio.PyAudio()
            # # Setting audio streamer
        
            stream = p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=44100,
                             output=True)
            #kthread = audioThread()
                            
                            
           
           
            while 1:
                data = None
               
                data = s.recv(153)
                
               
                if not data:
                    break
               
                # Recieve bytes and process them
                message = pickle.loads(data)
              
                if len(message) == 1:
                    process = 1
                    
                    

                   
                more_info = np.array(message, np.int16).tobytes()
                
                if len(buffer_audio) == 0 or len(buffer_audio[-1]) >= 3000:
                    buffer_audio.append(more_info)
                else:
                    buffer_audio[-1] += more_info
                
                
                # Wait until buffer is long enough
                if len(buffer_audio) > 5:
                    byte_sound = buffer_audio.pop(0)
                    #task = asyncio.create_task(play(byte_sound))
                    asyncio.run(play(byte_sound))
                    #stream.write(byte_sound)
                    
                    
                               
                #stego_audio.append(message)
               
                if transmited == 0  and len(message) == 3 and process == 1:
                   
                    result = reconstruct_partial(message, embedding_key)
                    if result > -1:
                        packet.append(result)
                    
                    if len(packet) == 8:
                       
                        if sum(packet) == 8:
                            prints = 0
                            process = 0
                            print("End transmission")
                       
       
                        if bits2string(packet) == chr(0x02):
                            print("start")
                            prints = 1

                        if prints:
                            print(bits2string(packet))
                        packet = []
