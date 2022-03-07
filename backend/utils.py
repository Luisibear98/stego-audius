
import matplotlib.pyplot as plt
import math
from scipy.io import wavfile
import numpy as np


def slice_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


""" Plot the spectogram of the audio """


def plot_wav(lenght, data):
    time = np.linspace(0., lenght, data.shape[0])
    plt.plot(time, data[:, 0], label="Left channel")
    plt.plot(time, data[:, 1], label="Right channel")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()


""" Reading wav """


def read_wav(filename):

    sp, data = wavfile.read("./audio/"+filename)
    if not data.dtype == np.int16:
        print("Trying to convert the wav, is preferred to use a 16bits wav")
        data = np.int16(data/np.max(np.abs(data)) * 32767)
    data = np.transpose(data)

    return data


""" Reconstructing data on the fly """


def reconstruct_partial(package, key):
    if len(package) == 3:
        delta_value = package[1] + ((package[0]+package[2])/2)*-1

        if abs(delta_value) > 0 and abs(delta_value) <= key:

            if delta_value > 0:
                return 1
            else:
                return 0

    return -1


""" Reconstruct data  """


def reconstruct(channel, key):

    position = 0
    result = []
    while position < len(channel):
        group = channel[position]
        if len(group) == 3:
            # Checking alpha values
            delta_value = group[1] + ((group[0]+group[2])/2)*-1

            if abs(delta_value) > 0 and abs(delta_value) <= key:  # If the condition is fullfilled

                if delta_value > 0:
                    result.append(1)
                else:
                    result.append(0)
        position += 1

    return result


""" Inserting data on the channel  """


def insert_on_channel(to_insert, channel_splitted, key):

    position = 0
    inserted = 0

    for bit in to_insert:

        inserted = 0

        while inserted == 0:

            group = channel_splitted[position]
            # This conditions are explained on the report
            if len(group) == 3:
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


def split_channel(channel, size_w):
    channel_splited = [channel[x:x+size_w]
                       for x in range(0, len(channel), size_w)]

    return channel_splited


""" From list of lists to single list """


def serialize_channel(data):

    audio = []

    for i in range(len(data)):
        if len(data[i]) == 3:
            for j in range(3):
                audio.append(data[i][j])
    return audio


def bits2string(b=None):

    return "".join(chr(int("".join(map(str, b[i:i+8])), 2)) for i in range(0, len(b), 8))


def bits2bytes(bits=None):
    return create_bytearray(bits)


def create_bytearray(binary_list):
    number = 0
    for b in binary_list:
        number = (2 * number) + b
    return bytearray([number])

# delete tildes


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


def binarize(string):
    return ("".join(f"{ord(i):08b}" for i in string))


""" Inserting on real time """


def insert_on_real_time(bit, group, key):
    key = int(key)
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


""" Processing text """


def process_text(text):
    text = normalize(text)
    text_in_bits = binarize(text)
    return text_in_bits


""" Calculating total capacities of audios """


def calculate_capacity(channel, embedding_key):

    positions = 0
    for group in channel:

        if len(group) == 3:
            delta_value = group[1] + ((group[0]+group[2])/2)*-1

            if abs(delta_value) > 0 and abs(delta_value) <= embedding_key:
                positions += 1

    return positions


def estimate_capacity(filename, embedding_key):
    audio = read_wav(filename)
    channel_1 = audio[0]
    channel_1_splited = split_channel(channel_1, 3)

    return calculate_capacity(channel_1_splited, embedding_key)


def process_audio(txt_str, embeding_key, filename):
    embeding_key = int(embeding_key)

    information = process_text(str(txt_str))

    audio = read_wav(filename)

    if len(audio) == 1:
        print("Audio is mono")
        insert = []

        for bit in information:
            insert.append(int(bit))
        ending = [1, 1, 1, 1, 1, 1, 1, 1]
        insert.extend(ending)
        channel_1 = audio[0]
        channel_1_splited = split_channel(channel_1, 3)
        insert_on_channel(insert, channel_1_splited, embeding_key)

    elif len(audio) == 2:

        print("Audio is stereo")
        insert = []
        # conversion del texto a bits

        in_bytes = split_channel(information, 8)

        for bit in information:
            insert.append(int(bit))
        ending = [1, 1, 1, 1, 1, 1, 1, 1]
        insert.extend(ending)

        channel_1 = audio[0]

        print("Preparing channel 1 ... ")
        channel_1_splited = split_channel(channel_1, 3)
        print("Preparing channel 2 ... ")

    return insert_on_channel(insert, channel_1_splited, embeding_key)


def recovering_info(data, embedding_key):
    embedding_key = int(embedding_key)
    data2 = split_channel(data, 3)
    result = reconstruct(data2, embedding_key)

    return slice_chunks(result, 8)


def print_ascii():

    print("===========================================================================")
    print("\
                                .       .\n\
                            / `.   .' \\\n\
                    .---.  <    > <    >  .---.\n\
                    |    \  \ - ~ ~ - /  /    |\n\
                        ~-..-~             ~-..-~\n\
                    \~~~\.'                    `./~~~/\n\
                    \__/                        \__/\n\
                    /                  .-    .  \\\n\
            _._ _.-    .-~ ~-.       /       }   \/~~~/\n\
        _.-'q  }~     /       }     {        ;    \__/\n\
        {'__,  /      (       /      {       /      `. ,~~|  .     .\n\
        `''''='~~-.__(      /_      |      /- _      `..-'   \\\\   //\n\
                    / \   =/  ~~--~~{    ./     ~-.     `-..__\\\\_//_.-'\n\
                    {   \  +\         \  =\          ~ - . _ _ _..---~\n\
                    |  | {   }         \   \\\n\
                    '---.o___,'       .o___,'\n\
    ")
    print("                 Welcome to Stego-audius :)                         ")
    print("                   By Alex, Luis and Leo                            ")
    print("===========================================================================")
    print()
    print("\
This tool lets you send hidden and encrypted messages via network sockets inside any song you want by adding it to the execution, the available options are:\n\
Fix text: Inserts a text into the song provided, the client plays the music and extracts the message,\n\
Streaming: Stream endless audio through the socket to the clients and insert multiple messages whenever you want\n\
    ")


def print_bye():
    print("\
                                                 ░░                                      \n\
|-----------|                                ░░  ░░  ░░                                  \n\
| HAVE      |                            ░░  ░░  ░░  ░░  ░░                              \n\
| A         |                        ░░  ░░░░░░░░░░░░░░░░░░  ░░                          \n\
| GREAT     |            ░░░░░░      ░░░░░░░░░░░░░░░░░░░░░░░░        ░░  ░░  ░░          \n\
| DAY       |          ░░░░░░░░░░  ░░  ░░░░░░░░░░░░░░░░░░░░░░░░      ░░  ░░  ░░          \n\
| ありがとう|        ░░░░██░░░░░░░░  ░░░░░░░░░░░░░░░░░░░░░░░░        ░░░░░░░░░░          \n\
|-----------|        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ░░░░░░░░                \n\
    | |                ▒▒▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                 \n\
    | |                   ▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                        \n\
    | |                       ▓▓▒▒▒▒▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒░░░░                            \n\
    | |                           ░░░░  ░░░░      ░░░░  ░░░░                            \n\
    | |                           ░░░░  ░░░░      ░░░░  ░░░░                            \n\
    | |                           ░░░░  ░░░░      ░░░░  ░░░░                            \n\
    | |                           ░░░░  ░░░░      ░░░░  ░░░░                            \n\
---------------------------------------------------------------------------------------------\
    ")
