
import matplotlib.pyplot as plt
import math
from scipy.io import wavfile
import numpy as np


def slice_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def plot_wav(lenght, data):

    time = np.linspace(0., lenght, data.shape[0])

    plt.plot(time, data[:, 0], label="Left channel")
    plt.plot(time, data[:, 1], label="Right channel")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()


def read_wav():

    sp, data = wavfile.read("./backend/totoro.wav")

    data = np.transpose(data)
    return data


def reconstruct_partial(package, key):

    if len(package) == 3:
        delta_value = package[1] + ((package[0]+package[2])/2)*-1

        if abs(delta_value) > 0 and abs(delta_value) <= key:

            if delta_value > 0:
                return 1
            else:
                return 0

    return -1


def reconstruct(channel, key):

    position = 0
    extracted = 0
    result = []
    while position < len(channel):
        group = channel[position]
        delta_value = group[1] + ((group[0]+group[2])/2)*-1

        if abs(delta_value) > 0 and abs(delta_value) <= key:

            if delta_value > 0:
                result.append(1)
            else:
                result.append(0)
        position += 1

    return result


def insert_on_channel(to_insert, channel_splitted, key):

    position = 0
    inserted = 0

    for bit in to_insert:
       
        inserted = 0

        while inserted == 0:
            group = channel_splitted[position]
            delta_value = group[1] + ((group[0]+group[2])/2)*-1

            if abs(delta_value) > 0 and abs(delta_value) <= key:
                inserted = 1

                if bit == 1:

                    if delta_value < 0:

                        group[1] = math.ceil((group[0]+group[2])/2) + 1

                else:
                    if delta_value > 0:

                        group[1] = math.floor((group[0]+group[2])/2) - 1

                channel_splitted[position] = group

            position += 1
    return channel_splitted


'''
Sampling points are grouped by every three successive ones and the amplitude values f1, f2, f3 are calculated.
input: [f1,f2,f3,f4,f5,f6,f7,f8,f9, ... ] (channel amplitudes values)
output:
[
    [f1,f2,f3]
    [f4,f5,f6]
    [f1,f2,f9]
       ...
]

'''


def split_channel(channel):
    channel_splited = [channel[x:x+3] for x in range(0, len(channel), 3)]
    #channel_splited = np.array(channel_splited, dtype=np.float32)

    return channel_splited


def serialize_channel(data):

    audio = []

    for i in range(len(data)):
        if len(data[i]) == 3:
            for j in range(3):
                audio.append(data[i][j])
    return audio


def bits2string(b=None):

    return "".join(chr(int("".join(map(str, b[i:i+8])), 2)) for i in range(0, len(b), 8))



# Eliminar tildes


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def binarize(str):

    return ("".join(f"{ord(i):08b}" for i in str))


def insert_on_real_time(bit, group, key):

    if len(group) == 3:
        delta_value = group[1] + ((group[0]+group[2])/2)*-1
        inserted = 0
        if abs(delta_value) > 0 and abs(delta_value) <= key:

            inserted = 1
            if bit == 1:

                if delta_value < 0:

                    group[1] = math.ceil((group[0]+group[2])/2) + 1

            else:
                if delta_value > 0:

                    group[1] = math.floor((group[0]+group[2])/2) - 1

    else:
        inserted = 0

    return group, inserted


def process_text(text):

    text = normalize(text)
    text_in_bits = binarize(text)

    return text_in_bits


def process_audio(str, embding_key):
    information = process_text(str)
    audio = read_wav()
    print("read")
    insert = []
    # conversion del texto a bits
    for bit in information:
        insert.append(int(bit))
    ending = [1, 1, 1, 1, 1, 1, 1, 1]
    insert.extend(ending)
   
    channel_1 = audio[0]
    channel_1_splited = split_channel(channel_1)
   
    return insert_on_channel(insert, channel_1_splited, embding_key)


def recovering_info(data,embedding_key):
    
    data2 = split_channel(data) 
    result = reconstruct(data2, embedding_key)

    return slice_chunks(result, 8)