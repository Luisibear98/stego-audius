from __future__ import print_function, unicode_literals
from PyInquirer import prompt
import socket
import pickle
from backend.utils import *
import numpy as np
import threading
from tqdm import tqdm
from examples import custom_style_2


modeSelector = {
    'type': 'list',
    'name': 'modes',
    'message': 'Select a mode',
    'choices': [
        'Fix text',
        'Transfer',
        'Help (?)',
    ],
}


textInput = {
    'type': 'input',
    'name': 'text',
    'message': 'Type the texto to send',
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

mode = prompt(modeSelector, style=custom_style_2)["modes"]

if mode != "Help (?)":

    embding_key = int(input("insert embedding key the higher the noiser: "))


    communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);


    communication_socket.connect((HOST, PORT+1))
    metadata = []
    if mode == "Fix text":
        metadata.append(1)
    elif mode == "Transfer":
        metadata.append(2)

    if metadata:
        metadata.append(embding_key)
        
    send_package = pickle.dumps(metadata)
    communication_socket.sendall(send_package)
    communication_socket.close()




# Inserts text in audio and sends it in stream to he client
if mode == "Fix text":
    str = input("Introduce the text to send: ")
    str = normalize(str)
    insert_on_channel_1 = process_audio(str, embding_key)
    print("Audio processed ...")
    to_send = serialize_channel(insert_on_channel_1)  # Serializing data
    # Transforming information to bytes
    bytes = np.array(to_send, np.int16).tobytes()
    to_send = list(slice_chunks(bytes, 3000))  # Splitting in chunks of 12 kb

    # Opening socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))  # Binding socket
        s.listen()
        print("Waiting for a connection ...")
        metadata.append(1)
        
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


# Procesamiento en tiempo real
elif mode == "Transfer":
   #real time text sending
    audio = read_wav()
    channel_1 = audio[0]    
    insert = []
   
    channel_1_splited = split_channel(channel_1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        send_info = chr(0x02)

        s.bind((HOST, PORT))
        s.listen()
        print("listening")
        position = 0
        sent = 0
        processing = 0
        print("sending flag")
        metadata.append(1)
        communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        communication_socket.connect((HOST, PORT+1))
        communication_socket.sendall(pickle.dumps(metadata))
        communication_socket.close()
        print("Now you can insert data on the fly")
        while 1:
            conn, addr = s.accept()
            with conn:
                
                #envío del audio con texto
                kthread = KeyboardThread(my_callback)
                for position in range(len(channel_1_splited)):
                 
                    multiple = sent % 8
                    if flag and multiple == 0 :
                        if not processing:
                            start = [1]
                            send_package = pickle.dumps(start)
                            conn.sendall(send_package)
                            processing = 1
            
                        bina = binarize(send_info)
                        insert =[]
                        bit_sent = 0
  
                        for bit in bina:
                            insert.append(int(bit))
                        
                        for i in range(8):
                            insert.append(1)
                       
                        while bit_sent < len(insert):
                          
                            package,inserted= insert_on_real_time(insert[bit_sent],channel_1_splited[position],key=50)
                            if inserted:
                                bit_sent += 1
                            send_package = pickle.dumps(package)
                           
                            conn.sendall(send_package)
                            position += 1
                        flag = 0
                        send_info = chr(0x02)
                        processing = 0
                      
                    else:
                      
                        package = channel_1_splited[position]
                        send_package = pickle.dumps(package)
                        conn.sendall(send_package)
                        sent += 1
                        
                      
                  

elif mode == "Help (?)":
    print("\
        This tool lets you send hidden and encrypted messages via network sockets\
        inside any song, the available options are:\n\
        'Fix text: Ask you for a text and inserts it into the song, the client plays the music in streaming',\
        'Transfer: You can transfer a song to the client and insert any song during the process'\
    ")
    #Add Y/n
    #os.execl(sys.executable, sys.executable, *sys.argv)


