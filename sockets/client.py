

from backend.utils import *
import socket
import pickle
import pyaudio
import numpy as np
from time import sleep
from scipy.io.wavfile import write
import soundfile as sf


HOST = "127.0.0.1"  # The server'socket hostname or IP address
PORT = 65432  # The port used by the server


stego_audio = []
receive = 0




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
            embedding_key = message[1]

            if len(message) == 3:
                break
           


if mode and embedding_key:
    # chunk mode
    if mode == 1:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
            socket.connect((HOST, PORT))
            packet = None
            audio = []
            stego_text = ""
            p = pyaudio.PyAudio()
            # Setting audio streamer
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            output=True)
            done = 0
            while 1:

                data = socket.recv(3000)  # Receiving 3kb from server

                if not data:    #If no data client quits
                    break

                
                stream.write(data)  # Playing sound
                data = np.frombuffer(data, dtype=np.int16)
                
                if done == 0:

                    recovered_bits = recovering_info(data,embedding_key)  # groups bits in group of 8

                    for group in recovered_bits:
                        # transforming bytes to char
                    
                    
                        if sum(group) == 8:  # message has ended
                            print("Transmission ended, the message is: "+ stego_text)
                            
                            done = 1
                        else:
                        
                            stego_text += bits2string(group)
                audio.extend(data)
            
            print("saving copy")
            sf.write("stego.wav",np.array(audio) , 44100)



    # real time text sending

    if mode == 2:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
            socket.connect((HOST, PORT))
            packet = []
            transmited = 0
            prints = 0
            receive = 0
            process = 0
            while 1:

                data = socket.recv(500)
                if not data:
                    break
                message = pickle.loads(data)
            
                if len(message) == 1:
                    process = 1
                    print("start processings")

                receive += 1
                stego_audio.append(message)

                if transmited == 0 and process == 1 and len(message) == 3:
                    result = reconstruct_partial(message, embedding_key)
                    if result > -1:

                        packet.append(result)

                    if len(packet) == 8:

                        if sum(packet) == 8:
                            prints = 0
                            process = 0
                            print("end transmission")

                        if bits2string(packet) == chr(0x02):
                            prints = 1

                        if prints:
                            print(bits2string(packet))
                        packet = []


    
    # channel_1_splited = split_channel(audio,3)
    # result = reconstruct(channel_1_splited,embedding_key)

    # result = slice_chunks(result,8)
    # for group in result:
    #     print(bits2string(group), end="")
    #     if sum(group) == 8:

    #         break

       # stego_audio = pickle.loads(packet)

        # stego_audio.append(frame)
