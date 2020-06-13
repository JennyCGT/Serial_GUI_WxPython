import serial
import sys
import time
import struct
from datetime import datetime
from csv import writer

analog =0
dato1=0
count = 0
i = 0
data = [0,0]

SOH = b'H'
STX = b'T'
ETX = b'E'

data_rec = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
f='csv/'+ data_rec +'.csv'
    # print(self.path_dir)
with open(f, 'w') as write_obj:
# Create a writer object from csv module
    csv_writer = writer(write_obj)
# Add header to the csv file
    csv_writer.writerow(['Date Time','Baudrate','Data analog1','Data analog2'])
        
ser = serial.Serial(
    port='COM9',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=(0.5)
    )

print("connected to: " + ser.portstr)
#this will store the line
line = []

def append_list_as_row(path,file_name, list_of_elem):
    # Open file in append mode
    f='csv/'+"\\"+file_name+'.csv'
    with open(f, 'a', newline='') as write_obj:    
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def save (num, data1):
    global count, data
    count = count+1
    # print(num, type( num))
    # print(data[num])
    data[int(num)] = data1
    if(count == 2):
        # print(self.data)
        line= (datetime.now().strftime('%Y %m %d %H:%M:%S'), 115200,data[0],data[1])
        append_list_as_row('csv',data_rec,line)
        print (line)
        count=0

while True:
    # tipo=''
    # data='/b'''
    aux=0
    c=['','','',''] 
    if ser.inWaiting() > 0:    
        # a=ser.read_until(ETX,8)
        a = ser.readline(1)
        if a==SOH:
            b = ser.readline(5)
            c= struct.unpack('sshs',b)
        # print(b.e)
        # print(c)

        if c[0] == b'R':
            a= c[2]
            save(0,a)
            # print(type(c[0])) 
            # line[0] = c[2]            
        if c[0] == b'B':
            a= c[2]
            save(1,c[2])
            # line[1] = c[2]            


        #     # tipo = ser.read(1)
        #     # tipo = ser.read_until(STX.encode('utf-8'))
        #     # flag_soh=True
        #     # print('tipo')
        #     if a.read(2) == STX:
        #         # data = ser.read(4)
        #         # flag_stx= True
        #         # data= ser.read_until(b'E')
        #         # data= ser.read_until(b'\x00E')
        #         print(len(data))
        #         # data1=data.decode('utf-8')
        #         # print(int.from_bytes(data,sys.byteorder))
        #         # print('dato')
            


ser.close()
