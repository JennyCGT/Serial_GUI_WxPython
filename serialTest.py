import serial
import sys
import time
import struct
analog =0
dato1=0
SOH = b'H'
STX = b'T'
ETX = b'E'
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
flag_soh=False
flag_stx=False

while True:
    # bytesToRead = ser.inWaiting()
    # c= ser.read()
    # for c in ser.read():
    # print(c)
    # if (c != b''):
    #     print(c)
    tipo=''
    data='/b'''
    aux=0;
    c=['','','',''] 
    if ser.inWaiting() > 0:    
        # a=ser.read_until(ETX,8)
        a = ser.readline(1)
        # tipo= struct.unpack('<s',a.read(2))
        # print(a)
        if a==SOH:
            b = ser.readline(5)
            c= struct.unpack('sshs',b)
        # if c=ser.readline(1)== STX:
            # c = ser.readline(1)
        # print(b.e)
        print(c)

        # if int.from_bytes(a,sys.byteorder) == 66:
        #     tipo='B'            
        # if int.from_bytes(a,sys.byteorder) == 65:
        #     tipo='A'
        # if a == STX:
        #     b=ser.read(4)
            # print(b)


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
            
        # if ser.read(1)== ETX :
        #     # flag_soh=False
        #     # flag_stx=False
        #     print('end')
        #     # if(tipo !=b''):
        #     #     analog= int.from_bytes(tipo, sys.byteorder)
        #     # if(data !=b''):
        #     #     dato1= int.from_bytes(data, sys.byteorder)
        #     # print('tipo  : ' + str(analog)+'  datos : ' + str(dato1))
        #     # print('datos : ' + str(dato1))
    # time.sleep(0.05)
 
ser.close()
