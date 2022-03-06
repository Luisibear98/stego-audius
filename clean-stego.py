
# from  scipy.io import wavfile

# import numpy as np
# import random
# import math

# from utils import plot_wav, split_channel, process_channel, embed_info, insert_on_channel, reconstruct


# samplerate, data = wavfile.read("test1.wav")
# print("Sample rate is: " + str(samplerate))

# length = data.shape[0] / samplerate
# print("plotting sound")




# data = np.transpose(data)

# data[0] = np.array(data[0],dtype=np.float32)
# data[1] = np.array(data[1],dtype=np.float32)


# data = np.transpose(data)
# plot_wav(length,data)
# data = np.transpose(data)

# channel_1 = data[0]
# channel_2 = data[1] 




# splitedSize = 3
# channel_1_splited = split_channel(channel_1,splitedSize)
# channel_2_splited = split_channel(channel_2,splitedSize)
# print(channel_1_splited)
# channel_1_values = process_channel(channel_1_splited)
# channel_2_values = process_channel(channel_2_splited)



# embding_key = 5 #This is crucial for invisibility (need to study)


# channel_1_good = embed_info(channel_1_values,embding_key)
# channel_2_good = embed_info(channel_2_values,embding_key)

# insert = [0,1,1]

# insert_on_channel_1 = insert_on_channel(insert,channel_1_good,channel_1_splited,channel_1_values)
# insert_on_channel_2 = insert_on_channel(insert,channel_2_good,channel_2_splited,channel_2_values)


# reconstruct_channel_1 = reconstruct(insert_on_channel_1)
# reconstruct_channel_2 = reconstruct(insert_on_channel_2)

# print("original data:")

# data[0] = reconstruct_channel_1
# data[1] = reconstruct_channel_2

# print("modified data:")


# print("EXTRACTION")


# channel_1_extract = data[0]
# channel_2_extract = data[1]


# channel_1_extract_splited = split_channel(channel_1_extract,splitedSize)
# channel_2_extract_splited = split_channel(channel_2_extract,splitedSize)


# channel_1_extract_values = process_channel(channel_1_extract_splited)
# channel_2_extract_values = process_channel(channel_2_extract_splited)



# channel_1_good = embed_info(channel_1_extract_values,embding_key)
# channel_2_good = embed_info(channel_2_extract_values,embding_key)

# def extract_from_channel(channel_1_good,channel_1_extract_values):

#     pointer = 0
#     extract = []
    
#     while pointer < len(channel_1_good):

#         if channel_1_good[pointer] == 1:
            
#             if channel_1_extract_values[pointer] > 0:
               
#                 extract.append(1)
#             else:
#                 extract.append(0)
#         pointer += 1

#     return extract
            
# print(channel_1_values[0:10])
# print(channel_1_extract_values[0:10])

# extracted = extract_from_channel(channel_1_good,channel_1_extract_values)
# total = len(insert)
# good = 0
# for i in range(0,len(insert)):
    
#     if extracted[i] == insert[i]:
#         good += 1

# print("percentaje good: "+ str(good/total)+"%")