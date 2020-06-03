import serial
import sys
analog =0
dato1=0
SOH = b'H'
STX = b'T'
ETX = b'E'
ser = serial.Serial(
    port='COM9',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

print("connected to: " + ser.portstr)
#this will store the line
line = []

while True:
    bytesToRead = ser.inWaiting()
    c= ser.read()
    # for c in ser.read():
    # print(c)
    # if (c != b''):
        # print(c)
    if c == SOH:
        tipo = ser.read(1)
        # tipo = ser.read_until(STX.encode('utf-8'))
        # print(tipo)
        # print('tipo')
    if c == STX:
        data = ser.read(4)
        # data= ser.read_until(b'E')
        # data= ser.read_until(b'\x00E')
        # print(data)
        # data1=data.decode('utf-8')
        # print(int.from_bytes(data,sys.byteorder))
        # print('dato')
    if c== ETX:
        print('end')
        if(tipo !=b''):
            analog= int.from_bytes(tipo,sys.byteorder)
        if(data !=b''):
            dato1= int.from_bytes(data,sys.byteorder)
        print('tipo  : ' + str(analog))
        print('datos : ' + str(dato1))

 
ser.close()
