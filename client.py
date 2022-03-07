

from re import I
from turtle import bye
from backend.utils import *
import socket
import pickle
import pyaudio
import numpy as np
from time import sleep
from scipy.io.wavfile import write
import asyncio

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import wave
HOST = "127.0.0.1"  # The server'socket hostname or IP address
PORT = 65432  # The port used by the server

stream = None
stego_audio = []
receive = 0

salt = None
expected_size = 0
sound = None


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
            password = bytes(getpass.getpass(
                prompt="Enter password: "), "utf-8")
            if salt == None:
                print("No salt, could not decrypt message.")
                exit()
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256, length=32,
                             salt=salt, iterations=390000)
            key = base64.urlsafe_b64encode(kdf.derive(password))
          
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            output=True)
            fernet = Fernet(key)
            printed = 0
            done = 0

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
                socket.connect((HOST, PORT))
                packet = None
                audio = []
                stego_text = ""
                total_data = np.array([])
                while 1:
                    data = socket.recv(800000000)  # Receiving 3kb from server

                    if not data:  # If no data client quits
                        break

                    stream.write(data)  # Playing sound
                    if total_data.size == 0:
                        total_data = np.frombuffer(data, dtype=np.int16)
                    else:
                       
                        total_data = np.concatenate((total_data, np.frombuffer(data, dtype=np.int16)), axis=None)
                        
                    #print(len(total_data))
             
                recovered_bits = recovering_info(
                        total_data, embedding_key)  # groups bits in group of 8
              
                for group in recovered_bits:
                        # transforming bytes to char
                     
                    if sum(group) == 8 and done == 0:  # message has ended decrypted_message
                            #print(stego_text)
                        lol = bytes(stego_text.replace(
                                "b'", '').replace("'", ''), "utf-8")

                        decrypted_message = fernet.decrypt(lol)
                        print("Transmission ended, the message is: " +
                                    decrypted_message.decode("utf-8"))
                            #print("Done: " + str(done))

                        done = 1
                    else:
                        stego_text += bits2string(group)

        except:
            #print(traceback.print_exc())
            print("Error. Could not decrypt message.")
            exit()

    if mode == 2:

        buffer_audio = []

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # Control flags
            packet = []
            transmited = 0
            prints = 0
            process = 0
            bytes = b''
            last_message = ""
            p = pyaudio.PyAudio()
            # # Setting audio streamer
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            output=True)

            while 1:

                data = None
                data = s.recv(153)  # Receivinf data

                if not data:
                    break

                # Recieve bytes and process them
                message = pickle.loads(data)

                if len(message) == 1:
                    process = 1

                more_info = np.array(message, np.int16).tobytes()


                # Inserting in buffer
                if len(buffer_audio) == 0 or len(buffer_audio[-1]) >= 3000:
                    buffer_audio.append(more_info)
                else:
                    buffer_audio[-1] += more_info

                # Wait until buffer is long enough
                if len(buffer_audio) > 5:
                    byte_sound = buffer_audio.pop(0)

                    asyncio.run(play(byte_sound))

                # Reconstruct data
                if transmited == 0 and len(message) == 3 and process == 1:
                    result = reconstruct_partial(message, embedding_key)
                    if result > -1:
                        packet.append(result)
                    if len(packet) == 8:

                        if sum(packet) == 8:
                            prints = 0
                            process = 0
                            print("Message transmission: " + last_message)
                            last_message = ""

                        if bits2string(packet) == chr(0x02):
                            prints = 1
                        if prints:
                            last_message += bits2string(packet)
                        packet = []
