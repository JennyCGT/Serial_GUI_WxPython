from threading import Thread, Lock
import time
import serial
import sys
import wx
import sys
import glob
import struct
import serial
from csv import writer
import numpy as np
import serial.tools.list_ports
import numpy as np
import matplotlib as mtp
mtp.use('WxAgg')
from collections import deque 
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
import matplotlib.animation as manim
from datetime import datetime

look= Lock()
stop_threads = False
stop_threads_1 = False
flag_data=False
flag_save= False
# wr=''
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
        timeout=0.5)

data_serial = [b'', b'', b'',b'']

class Serial_com:
    def __init__(self, ser):
        self.running = 1
        self.SOH = b'H'
        self.STX = b'T'
        self.ETX = b'E'
        self.analog =0
        self.dato1=0
        self.ser= ser
        self.flag_data= False
        self.data = [b'', b'', b'',b'']
        self.t1 = Thread(target = self.loop)
        self.t1.start()
        self.t2 = Thread(target = self.save_data_sync)
        self.t2.start()

        # self.periodicCall(  )

    def loop (self):
        c=['','','','']
        global data_serial
        while True:
            global stop_threads, data_serial,flag_data 
            if stop_threads: 
                break
                # stop_threads_1= True
            if ser.inWaiting() > 0:    
                # a=ser.read_until(ETX,8)
                a = ser.readline(1)
                # tipo= struct.unpack('<s',a.read(2))
                if a==SOH:
                    b = ser.readline(5)
                    if len(b) ==5:
                        c= struct.unpack('sshs',b)
                # if c=ser.readline(1)== STX:
                    # c = ser.readline(1)
                # print(b.e)
                # print(len(b))
                flag_data= True
                look.acquire()
                data_serial =c
                look.release()
    def endApplication(self):
        self.t1._stop()
    
    def save_data_sync(self):
        while True:
            global stop_threads_1, data_serial, flag_data
            # global data_serial, flag_data
            if stop_threads_1:
                break
            # frame.onConnect.Serial().t1.join()
            if flag_data:
                look.acquire()
                if(data_serial[0]==b'R'):
                    data.save(data_serial[2],0)
                    # data.axis_data1 = data_serial[2]
                    # print (data.axis_data1)
                if(data_serial[0]==b'B'):
                    data.save(data_serial[2],1)
                    # data.axis_data1 = data_serial[2]
                    # print (type(data.axis_data1))
                look.release()
                flag_data = False


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


def append_list_as_row(path,file_name, list_of_elem):
    # Open file in append mode
    f=path+"\\"+file_name+'.csv'
    with open(f, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

class Screen(wx.Frame):
    def __init__(self, parent, title):
        super(Screen, self).__init__(parent, title=title)
        self.port_selec=''
        self.baud_selec='9600'
        self.choices=[]
        self.y_max = 100
        self.y_min = 0
        self.path_dir = 'C:'
        self.data_rec=''
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
        self.box_rec.Add(self.rec_button, flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(self.box_rec, pos=(0, 4), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        line = wx.StaticLine(panel)

# -------------------- PLOT SETTINGS -----------------------------------------------------

        b3 = wx.StaticBox(panel, label="Real Time Graph")
        b3.SetBackgroundColour('#87BBA2')
        # sizer.Add(self.box_plot, pos=(1, 0), span=(10, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        self.box_plot = wx.StaticBoxSizer(b3, wx.VERTICAL)
        self.fig = Figure(figsize=([5.3,4]),tight_layout = {'pad': 2})
        self.a = self.fig.add_subplot(111)
        # self.a.plot([],[],"bo-",label="Data1",markersize=0.5)
        # self.a.plot([],[],"ro-",label="Data1",markersize=0.5)
        # self.a.grid()
        # self.a.legend()
        # self.a.set_ylim(0,1500)
        # self.box_plot.Add(FigureCanvasWxAgg(self,wx.ID_ANY,self.fig), flag=wx.LEFT|wx.TOP, border=15)
        self.canvas = FigureCanvasWxAgg(panel, wx.ID_ANY, self.fig)
        self.animator = manim.FuncAnimation(self.fig,self.anim, interval=500)
        # self.data_plot = RealtimePlot(axes,self.canvas,fig) 

        self.box_plot.Add(self.canvas, flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.BOTTOM, border=5)
        # sizer.Add(self.canvas,pos=(1, 1), span=(10, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        sizer.Add(self.box_plot, pos=(1, 0), span=(3, 5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

# -------------------- CURRENT SETTINGS -----------------------------------------------------

        b4 = wx.StaticBox(panel,label="Current Value")
        b4.SetBackgroundColour('#87BBA2')
        self.box_data = wx.StaticBoxSizer(b4, wx.VERTICAL)
        
        text_data1=wx.StaticText(panel, label="Analogue Data 1")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        self.value_data1=wx.StaticText(panel, label="0.00")
        self.value_data1.SetBackgroundColour('#F1F7EE')
        self.value_data1.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(self.value_data1, flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER , border=15)

        text_data1=wx.StaticText(panel, label="Analogue Data 2")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        self.value_data2=wx.StaticText(panel, label="0.00")
        self.value_data2.SetBackgroundColour('#F1F7EE')
        self.value_data2.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(self.value_data2, flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=15)
        sizer.Add(self.box_data, pos=(1,5), span=(2, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

# -------------------- GRAPH SETTINGS -----------------------------------------------------
        b5 = wx.StaticBox(panel,label="Graph Settings")
        b5.SetBackgroundColour('#F1F7EE')

        text_max=wx.StaticText(panel, label="Y-Limit Max")
        text_max.SetBackgroundColour('#F1F7EE')
        text_max.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.Limit_max = wx.TextCtrl(panel,value='100', size=wx.Size(40,20))
        # self.Limit_max.Bind(wx.EVT_TEXT, self.Set_Limit)
        
        text_min=wx.StaticText(panel, label="Y-Limit Max")
        text_min.SetBackgroundColour('#F1F7EE')
        text_min.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.Limit_min = wx.TextCtrl(panel,value='0', size=wx.Size(40,20))
        # self.Limit_min.Bind(wx.EVT_TEXT,self.Set_Limit)

        self.box_princ= wx.StaticBoxSizer(b5,wx.VERTICAL)
        bb1 = wx.StaticBox(panel)
        bb1.SetBackgroundColour('#F1F7EE')
        self.box_param = wx.StaticBoxSizer(bb1,wx.HORIZONTAL)        
        bb2 = wx.StaticBox(panel)
        bb2.SetBackgroundColour('#F1F7EE')
        self.box_min = wx.StaticBoxSizer( bb2,wx.HORIZONTAL)

        self.box_param.Add(text_max,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.box_param.Add(self.Limit_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.box_min.Add(text_min,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.box_min.Add(self.Limit_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.box_princ.Add(self.box_param,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)
        self.box_princ.Add(self.box_min,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)
        self.set_button= wx.Button(panel,label="SET")
        self.set_button.Bind(wx.EVT_BUTTON, self.Set_Limit)
        self.box_princ.Add(self.set_button,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)

        sizer.Add(self.box_princ, pos=(3,5), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM , border=10)

# -------------------- MESSAGE SETTINGS -----------------------------------------------------
        b6 = wx.StaticBox(panel,label="Graph Settings")
        b6.SetBackgroundColour('#F1F7EE')

        text_max=wx.StaticText(panel, label="Y-Limit Max")
        text_max.SetBackgroundColour('#F1F7EE')
        text_max.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.Limit_max = wx.TextCtrl(panel,value='100', size=wx.Size(40,20))


        sizer.AddGrowableCol(2)

        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()
        self.Show(True)    
#------------------------------------------------------------------------------------------------
    def onRec(self,event):
        # print('rec')
        # print(self.rec_button.Label)
        if self.rec_button.Label=='REC':
            print('rec')
            self.path_dir= str(self.path.GetValue())
            print(self.path_dir)
            self.data_rec = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            f=self.path_dir+"\\"+self.data_rec+'.csv'
            with open(f, 'w') as write_obj:
            # Create a writer object from csv module
                csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
                csv_writer.writerow(['Date Time','Baudrate','Data analog1','Data analog2'])
            global flag_save
            flag_save = True
            self.rec_button.SetLabel('STOP')
        else:
            self.rec_button.SetLabel('REC')        
            flag_save = False

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
        Show the DirDialog and print the user's choice 
        """
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            print ("You chose %s" % dlg.GetPath())
            self.path.SetValue(dlg.GetPath())
            self.path_dir = dlg.GetPath()
        dlg.Destroy()
    
    def onConnect(self, event):
        global stop_threads
        global stop_threads_1 
        global ser
        print('port: '+ self.port_selec +'Baud: '+self.baud_selec)
        if self.connect_button.Label=='Connect':
            if(self.port_selec == '' or self.port_selec=='Choose a port'):
                wx.MessageBox(message=" Choose a Port", caption= "Warning")
            else:
                self.connect_button.SetLabel('Disconnect')
                stop_threads = False
                stop_threads_1 = False
                print('Start')
                ser.port=self.port_selec
                ser.baudrate = int(self.baud_selec)
                self.Serial=Serial_com(ser)
                wx.MessageBox(message=" Connection Started", caption= "Connect")
                
        else:
            self.connect_button.SetLabel('Connect')
            stop_threads = True
            stop_threads_1 = True
            wx.MessageBox(message=" Connection Ended", caption= "Disconnect")
            
            # self.Serial.endApplication()
    
    def Set_Limit(self,event):
        self.y_max= int(self.Limit_max.GetValue())
        self.y_min= int(self.Limit_min.GetValue())
        print(self.y_max)
        print(self.y_min)

    def anim(self,i):
            if i%10 == 0:
                self.values = []
            else:
                self.values = data.axis_data1
            self.a.clear()
            self.a.set_xticklabels(data.axis_t, fontsize=8)
            self.a.set_ylim([self.y_min, self.y_max])
            # print(np.arange(self.y_min,self.y_max+5,5))
            y=np.arange(self.y_min,self.y_max+5,10)
            self.a.set_yticks(y) 
            # self.a.set_yticklabels(y, fontsize=8)
            # self.a.relim()
            self.a.plot(list(range(len(data.axis_data1))),data.axis_data1,'ro-', label="Data1",markersize=1, linewidth=1)
            self.a.plot(list(range(len(data.axis_data2))),data.axis_data2,'bo-', label="Data2",markersize=1,linewidth=1)
            self.a.legend(loc=1) 
            self.a.minorticks_on()
            self.a.grid(which='major', linestyle='-', linewidth='0.5', color='black') 
            self.a.grid(which='minor', linestyle=':', linewidth='0.5', color='black') 
            
class DataPlot:
    def __init__(self, max_entries = 120):
        self.axis_t = deque([0],maxlen=max_entries)
        self.axis_data1 = deque([0],maxlen=max_entries)
        self.axis_data2 = deque([0],maxlen=max_entries)
        # self.data_mqtt=[0]
        self.data = [0, 0]
        self.data_save=[]
        self.max_entries = max_entries
        self.count=0
    def save_all(self,data1,data2):
        tim=datetime.now().strftime('%Y %m %d %H:%M:%S')
        ######## DATA1 ##########################
        self.axis_t.append(datetime.now().strftime('%H:%M:%S'))
        # print(self.axis_t)
        self.axis_data1.append(data1)
        # print(self.axis_data1)
        ######## DATA2 ##############
        self.axis_data2.append(data2)
        # print(self.axis_data2)
        frame.value_data1.SetLabel(str(data1))
        frame.value_data2.SetLabel(str(data2))
        global flag_save
        if(flag_save):
            # print('guardar')
            self.data_save=[tim ,str(frame.baud_selec),str(data1),str(data2)]
            # append_list_as_row(frame.path_dir,frame.data_rec, data.data_save)
       
        # frame.plot_data(data.axis_data1,data.axis_t)
         
    def save (self,a,i):
        self.count=self.count+1
        self.data[i]=a        
        if(self.count==2):
            # print(self.data)
            self.save_all(self.data[0],self.data[1])
            self.count=0



 
if __name__ == '__main__':
    data = DataPlot()
    app = wx.App(False)
    frame = Screen(None, 'Datalogger')
    app.MainLoop()

    


