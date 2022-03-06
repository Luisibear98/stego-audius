
from  scipy.io import wavfile

import numpy as np
from decimal import *
from utils import plot_wav, split_channel, process_channel, embed_info, insert_on_channel_2, reconstruct


_, data =  wavfile.read("test.wav")

data = np.transpose(data)

# data[0] = np.array(data[0],dtype=np.float32)
# data[1] = np.array(data[1],dtype=np.float32)


# data = np.transpose(data)
# #plot_wav(length,data)
# data = np.transpose(data)

channel_1 = data[0]
# channel_2 = data[1] 
splitedSize = 3
channel_1_splited = split_channel(channel_1,splitedSize)
#channel_2_splited = split_channel(channel_2,splitedSize)
embding_key = 50 #This is crucial for invisibility (need to study)
insert = [1,1,1,0,0,0,1,0,1,1,1]
print("inserting")
print(insert)
insert_on_channel_1 = insert_on_channel_2(insert,channel_1_splited,embding_key)
reconstruct(insert_on_channel_1,embding_key)

