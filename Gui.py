from threading import Thread
import time
import serial
import sys
import wx
import sys
import glob
import serial
import serial.tools.list_ports
import numpy as np
import matplotlib as mtp
mtp.use('WxAgg')
from collections import deque 
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
from datetime import datetime


stop_threads = False
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


class Serial_com:
    def __init__(self, ser):
        self.running = 1
        # self.gui = Screen(None, 'Dataloggger')
        self.SOH = b'H'
        self.STX = b'T'
        self.ETX = b'E'
        self.analog =0
        self.dato1=0
        self.ser= ser
        self.t1 = Thread(target = self.loop)
        self.t1.start()
        # self.periodicCall(  )

    def loop (self):
        while True:
            global stop_threads 
            if stop_threads: 
                break
            bytesToRead = self.ser.inWaiting()
            c= self.ser.read()
            if c == self.SOH:
                tipo = self.ser.read(1)
            if c ==  self.STX:
                data = ser.read(4)
            if c== self.ETX:
                print('end')
                if(tipo !=b''):
                    self.analog= int.from_bytes(tipo,sys.byteorder)
                if(data !=b''):
                    self.dato1= int.from_bytes(data,sys.byteorder)
                print('tipo  : ' + str(self.analog))
                print('datos : ' + str(self.dato1))
                # time.sleep(0.1)
    # def start(self):
    #     t1 = Thread(target = self.loop)
    #     t1.start()
    def endApplication(self):
        self.t1._stop()

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class Screen(wx.Frame):
    def __init__(self, parent, title):
        super(Screen, self).__init__(parent, title=title)
        # self.fig
        self.port_selec=''
        self.baud_selec='9600'
        self.choices=[]
        self.InitUI()        
        self.Center()
        self.Show(True)    
    def InitUI(self):

        panel = wx.Panel(self, size=(1000,600))
        panel.SetBackgroundColour('#364958')
        sizer = wx.GridBagSizer(5, 10)

        # --------------------------------BOX SERIAL SETTINGS-----------------------------------------------------------
        b1 = wx.StaticBox(panel, label="Serial Settings")
        b1.SetBackgroundColour('#F1F7EE')
        box_serial = wx.StaticBoxSizer(b1, wx.HORIZONTAL)
        
        # BOX TEXT AND PORT
        text_port=wx.StaticText(panel, label="Port")
        text_port.SetBackgroundColour('#F1F7EE')

        box_serial.Add(text_port, flag=wx.LEFT|wx.TOP, border=15)
        self.port = wx.ComboBox(panel,value='Choose a port',choices=self.choices)
        self.port.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.List_port)
        self.port.Bind(wx.EVT_COMBOBOX, self.selec_port)
        box_serial.Add(self.port,flag=wx.LEFT|wx.TOP, border=15)
        # BOX TEXT AND BAUDRATE
        text_baud=wx.StaticText(panel, label="Baudrate")
        text_baud.SetBackgroundColour('#F1F7EE')
        
        box_serial.Add(text_baud,flag=wx.LEFT|wx.TOP, border=15)
        self.baud =wx.ComboBox(panel,value='9600',choices=['2400','4800','9600','19200','38400','57600','74880'
        ,'115200','230400'])
        self.baud.Bind(wx.EVT_COMBOBOX, self.selec_baud)
        box_serial.Add(self.baud,flag=wx.LEFT|wx.TOP, border=15)
        self.connect_button = wx.Button(panel, label='Connect')
        self.connect_button.Bind(wx.EVT_BUTTON, self.onConnect)
        
        box_serial.Add(self.connect_button,flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(box_serial, pos=(0, 0), span=(1, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # ----------------------BOX RECORD SETTINGS---------------------------------------------------
        b2 = wx.StaticBox(panel, label="Record / Export")
        b2.SetBackgroundColour('#F1F7EE')
        self.box_rec = wx.StaticBoxSizer(b2, wx.HORIZONTAL)
        
        # BUTTON BROWSER
        self.path = wx.TextCtrl(panel,value='C:\\')
        self.box_rec.Add(self.path, flag=wx.TOP|wx.EXPAND,border=15)

        self.text_port=wx.StaticText(panel, label="Path")
        self.text_port.SetBackgroundColour('#F1F7EE')
        self.box_rec.Add(self.text_port, flag=wx.LEFT|wx.TOP, border=15)
        self.browser_button= wx.Button(panel,label="Browser")
        self.browser_button.Bind(wx.EVT_BUTTON, self.onDir)
        self.box_rec.Add(self.browser_button, flag=wx.LEFT|wx.TOP, border=15)
        # BUTTON  REC
        self.rec_button= wx.Button(panel,label="REC")
        self.rec_button.Bind(wx.EVT_BUTTON, self.onRec)
        self.rec_button.SetDefault()
        self.box_rec.Add(self.rec_button, flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(self.box_rec, pos=(0, 4), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        line = wx.StaticLine(panel)

        # -------------------- PLOT SETTINGS -----------------------------------------------------

        b3 = wx.StaticBox(panel, label="Real Time Graph")
        b3.SetBackgroundColour('#87BBA2')
        # sizer.Add(self.box_plot, pos=(1, 0), span=(10, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        self.box_plot = wx.StaticBoxSizer(b3, wx.VERTICAL)
        self.fig = Figure(figsize=([5.3,3.5]))
        self.a = self.fig.add_subplot(111)
        self.a.set_ylabel("°C", fontsize=8)
        self.a.plot(range(0,50),"ro-")    
        # self.a.set_title("TEMPERATURE")
        self.a.grid()
        self.a.set_ylim(0)
        # self.box_plot.Add(FigureCanvasWxAgg(self,wx.ID_ANY,self.fig), flag=wx.LEFT|wx.TOP, border=15)
        self.canvas = FigureCanvasWxAgg(panel, wx.ID_ANY, self.fig)
        self.box_plot.Add(self.canvas, flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.BOTTOM, border=5)
        # sizer.Add(self.canvas,pos=(1, 1), span=(10, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        sizer.Add(self.box_plot, pos=(1, 0), span=(2, 5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # -------------------- CURRENT SETTINGS -----------------------------------------------------

        b4 = wx.StaticBox(panel,label="Current Value")
        b4.SetBackgroundColour('#87BBA2')
        self.box_data = wx.StaticBoxSizer(b4, wx.VERTICAL)
        
        text_data1=wx.StaticText(panel, label="Analogue Data 1")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        text_data1=wx.StaticText(panel, label="0.00")
        text_data1.SetBackgroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER , border=15)

        text_data1=wx.StaticText(panel, label="Analogue Data 2")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        text_data1=wx.StaticText(panel, label="0.00")
        text_data1.SetBackgroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=15)
        sizer.Add(self.box_data, pos=(1,5), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)


        sizer.AddGrowableCol(2)

        panel.SetSizer(sizer)
        sizer.Fit(self)

    def onRec(self,event):
        # print('rec')
        # print(self.rec_button.Label)
        if self.rec_button.Label=='REC':
            print('rec')
            self.rec_button.SetLabel('STOP')
        else:
            self.rec_button.SetLabel('REC')
        

    def List_port(self,event):
        print(serial_ports)
        ports = list(serial.tools.list_ports.comports())
        lst = []
        for p in ports:
            print (type(p.device))
            lst.append(p.device)
        self.choices=lst
        self.port.SetItems(self.choices)
        print(ports)
    
    def selec_baud(self,event):
        self.baud_selec=self.baud.GetStringSelection()
        print(self.baud_selec)

    def selec_port(self,event):
        self.port_selec =self.port.GetStringSelection()
        print(self.port.GetStringSelection())

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
            self.path.SetValue(dlg.GetPath())
        dlg.Destroy()
    
    def onConnect(self, event):
        global stop_threads 
        global ser
        print('port: '+ self.port_selec +'Baud: '+self.baud_selec)
        if self.connect_button.Label=='Connect':
            if(self.port_selec == '' or self.port_selec=='Choose a port'):
                wx.MessageBox(message=" Choose a Port", caption= "Warning")
            else:
                self.connect_button.SetLabel('Disconnect')
                stop_threads = False
                print('Start')
                self.Serial=Serial_com(ser)
        else:
            self.connect_button.SetLabel('Connect')
            stop_threads = True
            # self.Serial.endApplication()

class DataPlot:
    def __init__(self, max_entries = 30):
        self.axis_t = deque([0.0],maxlen=max_entries)
        self.axis_data1 = deque([0.0],maxlen=max_entries)
        self.axis_data2 = deque([0.0],maxlen=max_entries)
        self.data_mqtt=[0.0,0.0,0.0]
        self.data = []
        self.max_entries = max_entries
        self.count=0
    def save_all(self,data1,data2):
        tim=datetime.now().strftime('%Y %m %d %H:%M:%S')
        ######## DATA1 ##########################
        self.axis_data1.append(data1)
        # self.axis_tt.append(datetime.now().strftime('%H:%M:%S'))
        # Pagina_inicio.list_t.insert("",index=0,text=tim,values=str(t))
        # Pagina_inicio.box_cur_temp.configure(text=t)
        # Pagina_inicio.box_ave_temp.configure(text=promediarLista(data.axis_t))  
        ######## DATA2 ##############
        self.axis_data2.append(data2)
        # Pagina_inicio.list_h.insert("",index=0,text=tim,values=str(h))
        # Pagina_inicio.box_cur_humd.configure(text=h)
        # Pagina_inicio.box_ave_humd.configure(text=promediarLista(data.axis_h)) 
         
    def save (self,a,i):
        self.count=self.count+1
        self.data=a
        if(self.count==2):
            print(self.data)
            self.save_all(self.data[0],self.data[1])
            self.count=0

def save_data_sync(a,tipo, data):
    if(tipo == 48):
        data.save(data,0)
    if(tipo == 49):
        data.save(data,1)

class RealtimePlot:
    def __init__(self, axes,canvas,fig):
        self.axes = axes
        self.fig = fig
        self.canvas=canvas
        self.lineplot, = axes.plot([],[], "o-")
    def plot(self, data,data1):
        self.axes.set_xticklabels(data1)
        self.axes.autoscale_view(True)
        self.axes.relim()
        self.lineplot.set_data(list(range(len(data))),data)
        self.fig.canvas.draw_idle()
        

    



def Main():
    ser = serial.Serial(
    port='COM9',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

    # Serial=Serial_com(ser)
    # Serial =_serial(ser)
    # print ("Starting Thread 1")
    # t1 = Thread(target = _serial(ser))
    # t1.start()

    # Serial.start()
    print ("=== exiting ===")
    # Serial.close()
    # ser.close()

#  app = wx.App(False)
#  frame = Screen(None, 'Small editor')
#  app.MainLoop()
 
if __name__ == '__main__':
    # ser = serial.Serial(
    # port='COM9',\
    # baudrate=9600,\
    # parity=serial.PARITY_NONE,\
    # stopbits=serial.STOPBITS_ONE,\
    # bytesize=serial.EIGHTBITS,\
    #     timeout=0)
    data = DataPlot()
    app = wx.App(False)
    frame = Screen(None, 'Datalogger')
    # Serial=Serial_com(ser)
    app.MainLoop()

    


