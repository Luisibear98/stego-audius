import imp
from this import d
from unittest import result
import matplotlib.pyplot as plt
import math
import random
import numpy as np

def plot_wav(lenght,data):

    time = np.linspace(0., lenght, data.shape[0])

    plt.plot(time, data[:, 0], label="Left channel")
    plt.plot(time, data[:, 1], label="Right channel")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

def generate_key(number):
    return random.seed(number)


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
def split_channel(channel,splittedSize):
    channel_splited = [channel[x:x+splittedSize] for x in range(0, len(channel), splittedSize)]
    channel_splited = np.array(channel_splited, dtype=np.float32)
    return channel_splited


""" 
Get the delta values of each data chunk formula (1) of the paper
"""
def process_channel(channel):

    delta_values = []

    for group in channel:
        value = group[1] - ((group[0] + group[2])/2)
        
        delta_values.append(value)

    return delta_values



""" 
Get the delta values of each data chunk formula (1) of the paper
"""
def embed_info(delta_values,embeding_key):
    
    #esto se puede hacer con lambda
    get_or_not = []
    for value in delta_values:
        value = abs(value)
        if value > 0.01 and value <= embeding_key:
            get_or_not.append(1)
        else:
            get_or_not.append(0)

    return get_or_not





def insert_on_channel(to_insert,channel_good,channel_splitted,channel_values):
   
    pointer = 0
   
    for bit in to_insert:
        
        found = 0
        print("inserting "+ str(bit))
        if bit == 1: #just to clarify
            while found == 0:
                if channel_good[pointer] == 1:
                    found = 1
                   
                else:
                    pointer += 1



            value_lambda = channel_values[pointer]
            print("value lamda: "+ str(value_lambda))
            print("at pos: "+ str(pointer))
            if value_lambda < 0:
                modify = channel_splitted[pointer]
                print(modify)
                modify[1] = math.ceil((modify[0]+modify[2])/ 2) - 1
                
                channel_splitted[pointer] = modify
            print(channel_splitted[pointer])
        

        elif bit == 0:
            
            while found == 0:
                if channel_good[pointer] == 1:
                    found = 1
                else:
                    pointer += 1
                         
            value_lambda = channel_values[pointer]
            print("value lamda: "+ str(value_lambda))
            print("at pos: "+ str(pointer))
            if value_lambda > 0:
                modify = channel_splitted[pointer]
                print(modify)
                modify[1] = math.floor((modify[0]+modify[2])/ 2) + 1
                
                channel_splitted[pointer] = modify
                print(channel_splitted[pointer])
        pointer += 1
   
    return channel_splitted


def reconstruct(channel,key):
    print("reconstruct")
   
    position = 0
    extracted = 0
    result = []
    while position < 10000: 
        group = channel[position]
        delta_value = group[1] + ((group[0]+group[2])/2)*-1

        
        if abs(delta_value) > 0 and abs(delta_value) <= key:
           
            if delta_value > 0:
                result.append(1)
            else:
                result.append(0)
        position += 1
    print(result[0:11])
    return result

           

def insert_on_channel_2(to_insert,channel_splitted,key):
    
    position = 0
    inserted = 0
  
    for bit in to_insert:
      
        inserted = 0
        print("e")
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
    



# def insert_on_channel_2(to_insert,channel_splitted,key):
   
#     position = 0
#     inserted = 0
#     print(channel_splitted[0:5])
#     for bit in to_insert:
#         print(bit)
#         inserted = 0
#         while not inserted:
#             group = channel_splitted[position]
#             delta_value = group[1] - ((group[0]+group[2])/2)
#             print(delta_value)
#             if abs(delta_value) > 0 and abs(delta_value) <= key:
#                 if bit == 1:

#                     if delta_value < 0.01:
#                         group[1] = math.ceil((group[0]+group[2])/2) - 1
#                         print("mod")
#                 else:
#                     if delta_value > 0.01:
#                         group[1] = math.floor((group[0]+group[2])/2) + 1
#                         print("modefied")

#                 channel_splitted[position] = group

#                 inserted = 1

#             else:
#                 position += 1
    
#     print(channel_splitted[0:5])

    # for bit in to_insert:
        
    #     found = 0
    #     print("inserting "+ str(bit))
    #     if bit == 1: #just to clarify
    #         while found == 0:
    #             if channel_good[pointer] == 1:
    #                 found = 1
                   
    #             else:
    #                 pointer += 1



    #         value_lambda = channel_values[pointer]
    #         print("value lamda: "+ str(value_lambda))
    #         print("at pos: "+ str(pointer))
    #         if value_lambda < 0:
    #             modify = channel_splitted[pointer]
    #             print(modify)
    #             modify[1] = math.ceil((modify[0]+modify[2])/ 2) - 1
                
    #             channel_splitted[pointer] = modify
    #         print(channel_splitted[pointer])
        

    #     elif bit == 0:
            
    #         while found == 0:
    #             if channel_good[pointer] == 1:
    #                 found = 1
    #             else:
    #                 pointer += 1
                         
    #         value_lambda = channel_values[pointer]
    #         print("value lamda: "+ str(value_lambda))
    #         print("at pos: "+ str(pointer))
    #         if value_lambda > 0:
    #             modify = channel_splitted[pointer]
    #             print(modify)
    #             modify[1] = math.floor((modify[0]+modify[2])/ 2) + 1
                
    #             channel_splitted[pointer] = modify
    #             print(channel_splitted[pointer])
    #     pointer += 1
   
    return channel_splitted

