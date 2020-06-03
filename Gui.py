from threading import Thread
import time
import serial
import sys
import wx

    

analog =0
dato1=0
SOH = b'H'
STX = b'T'
ETX = b'E'

def _serial(ser):
    analog =0
    dato1=0
    SOH = b'H'
    STX = b'T'
    ETX = b'E'

    while True:
        bytesToRead = ser.inWaiting()
        c= ser.read()
        if c == SOH:
            tipo = ser.read(1)
        if c == STX:
            data = ser.read(4)
        if c== ETX:
            print('end')
            if(tipo !=b''):
                analog= int.from_bytes(tipo,sys.byteorder)
            if(data !=b''):
                dato1= int.from_bytes(data,sys.byteorder)
            print('tipo  : ' + str(analog))
            print('datos : ' + str(dato1))

class Serial_com:
    def __init__(self, ser):
        self.SOH = b'H'
        self.STX = b'T'
        self.ETX = b'E'
        self.analog =0
        self.dato1=0
        self.ser= ser
        t1 = Thread(target = self.loop)
        t1.start()
    def loop (self):
        while True:
            bytesToRead = self.ser.inWaiting()
            c= self.ser.read()
            if c == self.SOH:
                tipo = self.ser.read(1)
            if c ==  self.STX:
                data = ser.read(4)
            if c== self.ETX:
                print('end')
                if(self.tipo !=b''):
                    self.analog= int.from_bytes(tipo,sys.byteorder)
                if(self.data !=b''):
                    self.dato1= int.from_bytes(data,sys.byteorder)
                print('tipo  : ' + str(self.analog))
                print('datos : ' + str(self.dato1))
                break 
    # def start(self):
    #     t1 = Thread(target = self.loop)
    #     t1.start()
    def close(self):
        self.ser.close()
    
class Screen(wx.Frame):
    def __init__(self, parent, title):
        super(Screen, self).__init__(parent, title=title)
        self.InitUI()        
        self.Center()
        self.Show(True)    
    def InitUI(self):

        panel = wx.Panel(self, size=(1000,600))
        panel.SetBackgroundColour('#B0BEA9')
        sizer = wx.GridBagSizer(5, 10)
        # --------------------------------BOX SERIAL SETTINGS-----------------------------------------------------------
        b1 = wx.StaticBox(panel, label="Serial Settings")
        b1.SetBackgroundColour('#F1F7EE')
        box_serial = wx.StaticBoxSizer(b1, wx.HORIZONTAL)
        # BOX TEXT AND PORT
        text_port=wx.StaticText(panel, label="Port")
        text_port.SetBackgroundColour('#F1F7EE')
        box_serial.Add(text_port, flag=wx.LEFT|wx.TOP, border=15)
        box_serial.Add( wx.ComboBox(panel,choices=['COM1','COM2','COM4','COM5']),flag=wx.LEFT|wx.TOP, border=15)
        # BOX TEXT AND BAUDRATE
        text_baud=wx.StaticText(panel, label="Baudrate")
        text_baud.SetBackgroundColour('#F1F7EE')
        box_serial.Add(text_baud,flag=wx.LEFT|wx.TOP, border=15)
        box_serial.Add( wx.ComboBox(panel,value='9600',choices=['2400','4800','9600','19200','38400','57600','74880'
        ,'115200','230400']),flag=wx.LEFT|wx.TOP, border=15)
        connect_button = wx.Button(panel, label='Connect')
        box_serial.Add(connect_button,flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(box_serial, pos=(0, 0), span=(1, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # ----------------------BOX RECORD SETTINGS---------------------------------------------------
        b2 = wx.StaticBox(panel, label="Record / Export")
        b2.SetBackgroundColour('#F1F7EE')
        box_rec = wx.StaticBoxSizer(b2, wx.HORIZONTAL)
        # BUTTON BROWSER
        text_port=wx.StaticText(panel, label="Path")
        text_port.SetBackgroundColour('#F1F7EE')
        box_rec.Add(text_port, flag=wx.LEFT|wx.TOP, border=15)
        folder= wx.Button(panel,label="Browser")
        folder.Bind(wx.EVT_BUTTON, self.onDir)
        box_rec.Add(folder, flag=wx.LEFT|wx.TOP, border=15)
        # BOX TEXT AND BAUDRATE
        text_baud=wx.StaticText(panel, label="Baudrate")
        text_baud.SetBackgroundColour('#F1F7EE')
        box_rec.Add(text_baud,flag=wx.LEFT|wx.TOP, border=15)
        box_rec.Add( wx.ComboBox(panel,value='9600',choices=['2400','4800','9600','19200','38400','57600','74880'
        ,'115200','230400']),flag=wx.LEFT|wx.TOP, border=15)
        connect_button = wx.Button(panel, label='Connect')
        box_rec.Add(connect_button,flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(box_rec, pos=(0, 5), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 9),
            flag=wx.EXPAND|wx.BOTTOM, border=10)

        text2 = wx.StaticText(panel, label="Name")
        sizer.Add(text2, pos=(2, 0), flag=wx.LEFT, border=10)

        tc1 = wx.TextCtrl(panel)
        sizer.Add(tc1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND)

        text3 = wx.StaticText(panel, label="Package")
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        tc2 = wx.TextCtrl(panel)
        sizer.Add(tc2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND,
            border=5)

        button1 = wx.Button(panel, label="Browse...")
        sizer.Add(button1, pos=(3, 4), flag=wx.TOP|wx.RIGHT, border=5)

        text4 = wx.StaticText(panel, label="Extends")
        sizer.Add(text4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)

        combo = wx.ComboBox(panel)
        sizer.Add(combo, pos=(4, 1), span=(1, 3),
            flag=wx.TOP|wx.EXPAND, border=5)

        button2 = wx.Button(panel, label="Browse...")
        sizer.Add(button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)

        sb = wx.StaticBox(panel, label="Optional Attributes")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(wx.CheckBox(panel, label="Public"),
            flag=wx.LEFT|wx.TOP, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Generate Default Constructor"),
            flag=wx.LEFT, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Generate Main Method"),
            flag=wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(boxsizer, pos=(5, 0), span=(1, 5),
            flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        button3 = wx.Button(panel, label='Help')
        sizer.Add(button3, pos=(7, 0), flag=wx.LEFT, border=10)

        button4 = wx.Button(panel, label="Ok")
        sizer.Add(button4, pos=(7, 3))

        button5 = wx.Button(panel, label="Cancel")
        sizer.Add(button5, pos=(7, 4), span=(1, 1),
            flag=wx.BOTTOM|wx.RIGHT, border=10)

        sizer.AddGrowableCol(2)

        panel.SetSizer(sizer)
        sizer.Fit(self)
    
    def onDir(self, event):
        """
        Show the DirDialog and print the user's choice to stdout
        """
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            print ("You chose %s" % dlg.GetPath())
        dlg.Destroy()


def Main():
    ser = serial.Serial(
    port='COM9',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

    # Serial=Serial_com(ser)
    Serial =_serial(ser)
    print ("Starting Thread 1")
    # t1 = Thread(target = _serial(ser))
    # t1.start()

    # Serial.start()
    print ("=== exiting ===")
    # Serial.close()
    ser.close()

#  app = wx.App(False)
#  frame = Screen(None, 'Small editor')
#  app.MainLoop()

if __name__ == '__main__':
 app = wx.App(False)
 frame = Screen(None, 'Datalogger')
 app.MainLoop()

    


