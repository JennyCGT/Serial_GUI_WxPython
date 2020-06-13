from threading import Thread, Lock, Event
import time
import serial
import sys
import wx
import sys
import glob
import os
import struct   
from csv import writer
import numpy as np
from collections import deque 
import serial.tools.list_ports
import numpy as np
import matplotlib as mtp
mtp.use('WxAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
import matplotlib.animation as manim
from datetime import datetime

look= Lock()
# Global Parametes

stop_threads = False
stop_threads_1 = False
flag_data=False
flag_save= False
analog =0
dato1=0
event = Event()

# ser = serial.Serial()

data_serial = [b'', b'', b'',b'']

# Class for serial Comunication 
class Serial_com:
    def __init__(self, port, baud):
        self.running = 1
        self.analog =0
        self.dato1=0
        self.ser= serial.Serial(port,baud,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=(0.5))
        self.SOH = b'H'
        self.STX = b'T'
        self.ETX = b'E'
        self.flag_data= False
        # Thread for reading serial Port
        self.t1 = Thread(target = self.loop)
        self.t1.start()
        self.t2 = Thread(target = self.update)
        self.t2.start()


    def loop (self):
        c=['','','','']
        global data_serial
        while True:
            global stop_threads, data_serial, flag_data, event
            if stop_threads: 
                break
                # stop_threads_1= True
            
            # Waiting for serial buffer
            if self.ser.inWaiting() > 0:    
                # a=ser.read_until(ETX,8)
                a = self.ser.readline(1)
                # Define the start of protocol
                if a == self.SOH:
                    # Read the rest of the protocol
                    b = self.ser.readline(5)
                    # if its correct the number of bytes separate data received
                    if len(b) ==5:
                        c= struct.unpack('sshs',b)

                # use look for blocking changes from other threads
                look.acquire()
                data_serial =c
                if(data_serial[0]==b'R'):
                    data.save(data_serial[2],0)
                    # data.axis_data1 = data_serial[2]
                    # print (data.axis_data1)
                if(data_serial[0]==b'B'):
                    data.save(data_serial[2],1)                
                look.release()
                # flag_data = True
                # event.set()
        self.ser.close()    
    
    def update (self):
        i = 0
        while True:
            global flag_data, event
            if stop_threads:
                break
            if event.is_set():
                # print(data.tim)
                # print("%d   %d",data.axis_data1[-1], data.axis_data2[-1])
                frame.value_data1.SetLabel(str(data.axis_data1[-1]))
                frame.value_data2.SetLabel(str(data.axis_data2[-1]))
                # frame.Refresh()
                global flag_save
                if(flag_save):
                    # print('guardar')
                    data_save=[data.tim ,str(frame.baud_selec),str(data.axis_data1[-1]),str(data.axis_data2[-1])]
                    print(data_save)
                    # frame.text_msg.SetLabel('Data 1:    '+str(data1) +'      Data2:     '+str(data2))
                    append_list_as_row(frame.path_dir,frame.data_rec, data_save)

                event.clear()
                # look.release()
                # flag_data= False

# Lists serial port names
# A list of the serial ports available on the system

def serial_ports():
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


# Function for save data in CSV file
def append_list_as_row(path,file_name, list_of_elem):
    # Open file in append mode
    f='csv/'+"\\"+file_name+'.csv'
    with open(f, 'a', newline='') as write_obj:    
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)



# Class of GUI
class Screen(wx.Frame):
    def __init__(self, parent, title):
        super(Screen, self).__init__(parent, title=title)
        # wx.Frame.__init__(self, None, -1, name='Name')
        # self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.port_selec=''
        self.baud_selec='115200'
        self.choices=[]
        self.y_max = 100
        self.y_min = 0
        self.path_dir = 'C:'
        self.data_rec=''
        # panel = self
        panel = wx.Panel(self, size=(1000,600))
        # panel.SetBackgroundColour('#364958')
        # panel.SetBackgroundColour('#5B5F97')
        panel.SetBackgroundColour('#C0C0C0')
        sizer = wx.GridBagSizer(5, 10)
# --------------------------------BOX SERIAL SETTINGS-----------------------------------------------------------
        b1 = wx.StaticBox(panel, label="Serial Settings")
        b1.SetBackgroundColour('#F1F7EE')
        box_serial = wx.StaticBoxSizer(b1, wx.HORIZONTAL)
        
        # BOX TEXT AND PORT OPTIONS
        text_port=wx.StaticText(panel, label="Port")
        text_port.SetBackgroundColour('#F1F7EE')

        box_serial.Add(text_port, flag=wx.LEFT|wx.TOP, border=15)
        self.port = wx.ComboBox(panel,value='Choose a port',choices=self.choices)
        self.port.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.List_port)
        self.port.Bind(wx.EVT_TEXT, self.write_port)
        self.port.Bind(wx.EVT_COMBOBOX, self.selec_port)
        box_serial.Add(self.port,flag=wx.LEFT|wx.TOP, border=15)

        # BOX TEXT AND BAUDRATE OPTIONS
        text_baud=wx.StaticText(panel, label="Baudrate")
        text_baud.SetBackgroundColour('#F1F7EE')
        
        box_serial.Add(text_baud,flag=wx.LEFT|wx.TOP, border=15)
        self.baud =wx.ComboBox(panel,value='115200',choices=['2400','4800','9600','19200','38400','57600','74880'
        ,'115200','230400', '460800'])
        self.baud.Bind(wx.EVT_COMBOBOX, self.selec_baud)
        box_serial.Add(self.baud,flag=wx.LEFT|wx.TOP, border=15)
        self.connect_button = wx.Button(panel, label='Connect')
        self.connect_button.Bind(wx.EVT_BUTTON, self.onConnect)
        
        box_serial.Add(self.connect_button,flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(box_serial, pos=(0, 0), span=(1, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
# --------------------------------------------------------------------------------------------
        b3 = wx.StaticBox(panel, label="Real Time Graph")
        b3.SetBackgroundColour('#87BBA2')

        self.box_plot = wx.StaticBoxSizer(b3, wx.VERTICAL)
        self.fig = Figure(figsize=([5.3,4]),tight_layout = {'pad': 2})
        self.a = self.fig.add_subplot(111)
        # self.lineplot, = self.a.plot([],'ro-', label="Data1",markersize=1, linewidth=1)

        # self.lineplot, = self.a.plot([],[],"bo-",label="Data1",markersize=0.5)
        # self.lineplot1, = self.a.plot([],[],"ro-",label="Data1",markersize=0.5)

        # self.a.legend(loc=1) 
        # self.a.minorticks_on()
        # self.a.grid(which='major', linestyle='-', linewidth='0.5', color='black') 
        # self.a.grid(which='minor', linestyle=':', linewidth='0.5', color='black') 


        # Function for realtime plot
        self.canvas = FigureCanvasWxAgg(panel, wx.ID_ANY, self.fig)
        # self.data_plot = RealtimePlot(axes,self.canvas,fig) 

        self.box_plot.Add(self.canvas, flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=5)
        # sizer.Add(self.canvas,pos=(1, 1), span=(10, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        sizer.Add(self.box_plot, pos=(1, 0), span=(3, 5),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        self._plot = RealtimePlot(self.a, self.canvas, self.fig)
# ----------------------BOX RECORD SETTINGS---------------------------------------------------
        b2 = wx.StaticBox(panel, label="Record / Export")
        b2.SetBackgroundColour('#F1F7EE')
        self.box_rec = wx.StaticBoxSizer(b2, wx.HORIZONTAL)
        
        # BUTTON BROWSER

        self.text_port=wx.StaticText(panel, label="Path")
        self.text_port.SetBackgroundColour('#F1F7EE')
        self.box_rec.Add(self.text_port, flag=wx.LEFT|wx.TOP, border=15)

        # self.path = wx.TextCtrl(panel,value=os.path.abspath(os.getcwd())+'\csv',size=wx.Size(200,15))
        # self.box_rec.Add(self.path, flag=wx.LEFT|wx.TOP|wx.EXPAND,border=15)

        # self.browser_button= wx.Button(panel,label="Browser")
        # self.browser_button.Bind(wx.EVT_BUTTON, self.onDir)
        # self.box_rec.Add(self.browser_button, flag=wx.LEFT|wx.TOP, border=15)
        # BUTTON  REC
        self.rec_button= wx.Button(panel,label="REC",)
        self.rec_button.Bind(wx.EVT_BUTTON, self.onRec)
        self.box_rec.Add(self.rec_button, flag=wx.LEFT|wx.TOP, border=15)
        sizer.Add(self.box_rec, pos=(0, 4), span=(1, 4),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        line = wx.StaticLine(panel)


# -------------------- CURRENT SETTINGS -----------------------------------------------------

        b4 = wx.StaticBox(panel,label="Current Value")
        b4.SetBackgroundColour('#87BBA2')
        # b4.SetBackgroundColour('#143642')
        self.box_data = wx.StaticBoxSizer(b4, wx.VERTICAL)
        
        text_data1=wx.StaticText(panel, label="Analogue Data 1")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        self.value_data1=wx.StaticText(panel, label="00")
        self.value_data1.SetBackgroundColour('#F1F7EE')
        self.value_data1.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(self.value_data1, flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER , border=15)

        text_data1=wx.StaticText(panel, label="Analogue Data 2")
        text_data1.SetBackgroundColour('#364958')
        text_data1.SetForegroundColour('#F1F7EE')
        text_data1.SetFont(wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_data.Add(text_data1, flag=wx.LEFT|wx.TOP, border=15)

        self.value_data2=wx.StaticText(panel, label="00")
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
        self.Limit_max = wx.SpinCtrl(panel, value="100" , min=0, max=100, initial=100)        
        # self.Limit_max = wx.TextCtrl(panel,value='100', size=wx.Size(40,20))
        # self.Limit_max.Bind(wx.EVT_TEXT, self.Set_Limit)
        
        text_min=wx.StaticText(panel, label="Y-Limit Max")
        text_min.SetBackgroundColour('#F1F7EE')
        text_min.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.Limit_min = wx.SpinCtrl(panel, value="0" , min=0, max=100, initial=0)        
        # self.Limit_min = wx.TextCtrl(panel,value='0', size=wx.Size(40,20))
        # self.Limit_min.Bind(wx.EVT_TEXT,self.Set_Limit)

        self.box_princ= wx.StaticBoxSizer(b5,wx.VERTICAL)
        self.box_param = wx.BoxSizer(wx.HORIZONTAL)        
        self.box_min = wx.BoxSizer( wx.HORIZONTAL)

        self.box_param.Add(text_max,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.box_param.Add(self.Limit_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.box_min.Add(text_min,  0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.box_min.Add(self.Limit_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.box_princ.Add(self.box_param,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=5)
        self.box_princ.Add(self.box_min,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=5)
        self.set_button= wx.Button(panel,label="SET")
        self.set_button.Bind(wx.EVT_BUTTON, self.Set_Limit)
        self.box_princ.Add(self.set_button,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=5)

        sizer.Add(self.box_princ, pos=(3,5), span=(1, 3),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM , border=10)

# -------------------- MESSAGE SETTINGS -----------------------------------------------------
        b6 = wx.StaticBox(panel,label="Messages")
        b6.SetBackgroundColour('#F1F7EE')
        self.box_msg = wx.StaticBoxSizer(b6, wx.HORIZONTAL)

        text_1 = wx.StaticText(panel, label="Serial Comunication: ")
        text_1.SetBackgroundColour('#F1F7EE')
        text_1.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_msg.Add(text_1,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)


        self.ser_msg=wx.StaticText(panel, label="Close", size=wx.Size(150,18))
        self.ser_msg.SetBackgroundColour('#F1F7EE')
        self.ser_msg.SetForegroundColour('#364958')
        self.ser_msg.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_msg.Add(self.ser_msg,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)
        
        text_2 = wx.StaticText(panel, label="Recording Data: ")
        text_2.SetBackgroundColour('#F1F7EE')
        text_2.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_msg.Add(text_2,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)


        self.text_msg=wx.StaticText(panel, label=" Stop", size=wx.Size(150,18))
        self.text_msg.SetBackgroundColour('#F1F7EE')
        self.text_msg.SetForegroundColour('#3B6064')
        self.text_msg.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.box_msg.Add(self.text_msg,flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER, border=1)
        

        sizer.Add(self.box_msg, pos=(4,0), span=(1, 8),flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM , border=10)


        sizer.AddGrowableCol(2)

        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()
        self.Show(True)    
#------------------------------------------------------------------------------------------------
    
    def onRec(self,event):
        # ------------ Function for export data
        # print('rec')
        # print(self.rec_button.Label)
        if self.rec_button.Label=='REC':
            print('rec')
            # self.path_dir= os.path.abspath(os.getc wd())
            self.data_rec = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            self.text_msg.SetLabel('Exporting file ...'+ self.data_rec+'.csv')
            # f=self.path_dir+"\\"+self.data_rec+'.csv'
            f='csv/'+self.data_rec+'.csv'
            print(self.path_dir)

            # Create CSV file
            with open(f, 'w') as write_obj:
            # Create a writer object from csv module
                csv_writer = writer(write_obj)
            # Add header to the csv file
                csv_writer.writerow(['Date Time','Baudrate','Data analog1','Data analog2'])
            global flag_save
            flag_save = True
            self.rec_button.SetLabel('STOP')
        else:
            self.text_msg.SetLabel('Stop')
            self.rec_button.SetLabel('REC')        
            flag_save = False

    # List COM availables 
    def List_port(self,event):
        # print(serial_ports)
        ports = list(serial.tools.list_ports.comports())
        lst = []
        for p in ports:
            print (type(p.device))
            lst.append(p.device)
        self.choices=lst
        self.port.SetItems(self.choices)
        print(ports)
    
    # Get de Baudrate selected
    def selec_baud(self,event):
        self.baud_selec=self.baud.GetStringSelection()
        print(self.baud_selec)

    # Get Port Selected or writer
    def selec_port(self,event):
        self.port_selec =self.port.GetStringSelection()
        print(self.port.GetStringSelection())

    def write_port(self,event):
        self.port_selec = self.port.GetValue()

    # Open System Directory to choose a folder
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
    
    # Start thread of Serial Communication
    def onConnect(self, event):
        global stop_threads
        global stop_threads_1 
        # global ser
        print('port: '+ self.port_selec +'Baud: '+self.baud_selec)
        if self.connect_button.Label=='Connect':
            if(self.port_selec == '' or self.port_selec == 'Choose a port'):
                wx.MessageBox(message=" Choose a Port", caption= "Warning")
            else:
                self.connect_button.SetLabel('Disconnect')
                stop_threads = False
                stop_threads_1 = False
                print('Start')
                self.Serial=Serial_com(self.port_selec,self.baud_selec)
                # wx.MessageBox(message=" Connection Started", caption= "Connect")
                self.ser_msg.SetLabel("Open")
                self.port.Disable()
                self.baud.Disable()
        else:
            self.connect_button.SetLabel('Connect')
            stop_threads = True
            # stop_threads_1 = True
            # wx.MessageBox(message=" Connection Ended", caption= "Disconnect")
            self.ser_msg.SetLabel("Close")            
            # self.Serial.endApplication()
            self.port.Enable()
            self.baud.Enable()
    
    # Reset Plot Limits  
    def Set_Limit(self,event):
        self.y_max= int(self.Limit_max.GetValue())
        self.y_min= int(self.Limit_min.GetValue())
        self._plot.y_max = self.y_max
        self._plot.y_min = self.y_min
        # print(self.y_max)
        # print(self.y_min)

    # Stop all threads 
    def OnClose(self, event):
        self.Serial.t1._stop()
        self.Serial.t2._stop()
        self._plot.t3._stop()
        global stop_threads, stop_threads_1
        # self.animator.event_source.stop()
        stop_threads =True
        stop_threads_1 = True
        self.Destroy() 


            
# Class for save data received and create arrays for plotting
class DataPlot:
    def __init__(self, max_entries = 60):
        self.axis_t = deque([0],maxlen=max_entries)
        self.axis_data1 = deque([0],maxlen=max_entries)
        self.axis_data2 = deque([0],maxlen=max_entries)
        self.tim = 0
        self.data = [0, 0]
        self.data_save=[]
        self.max_entries = max_entries
        self.count=0

    # function for save data for plotting, save data in CSV  and update current value
    def save_all(self,data1,data2):
        self.tim=datetime.now().strftime('%Y %m %d %H:%M:%S')
        ######## DATA1 ##########################
        self.axis_t.append(datetime.now().strftime('%H:%M:%S'))
        # print(self.axis_t)
        self.axis_data1.append(data1)
        # print(self.axis_data1)
        ######## DATA2 ##############
        self.axis_data2.append(data2)
        # print(self.axis_data2)
        # frame.plot_data(data.axis_data1,data.axis_t)
         
    # Wait for get two data form serial before save
    def save (self,a,i):
        self.count=self.count+1
        self.data[i]=a        
        if(self.count==2):
            # print(self.data)
            self.save_all(self.data[0],self.data[1])
            self.count=0
            global event
            event.set()

class RealtimePlot:
    def __init__(self, a,canvas, fig):
        self.y_min = 0
        self.y_max = 100
# -------------------- PLOT SETTINGS -----------------------------------------------------
        self.a = a
        self.canvas = canvas
        self.fig = fig
        self.lineplot, = self.a.plot([],[],'ro-', label="Data1",markersize=1, linewidth=1)
        self.lineplot1, = self.a.plot( [],[],'bo-', label="Data2",markersize=1,linewidth=1)
        self.a.legend(loc=1) 
        self.a.minorticks_on()
        self.a.grid(which='major', linestyle='-', linewidth='0.5', color='black') 
        self.a.grid(which='minor', linestyle=':', linewidth='0.5', color='black') 
        self.fig.canvas.draw()

        self.t3= Thread(target = self.loop)
        self.t3.start()    
    # Plotting Real timeF
    def loop (self):
        while True:
            global stop_threads_1, event
            if stop_threads_1:
                break
            # print(data.axis_data1)
            # print(data.axis_data2)
            self.anim()
            time.sleep(0.5)
    
    def anim (self):
        self.a.clear()
        self.a.set_xticklabels(data.axis_t, fontsize=8)
        self.a.set_ylim([self.y_min , self.y_max ])
        # print(self.y_min,self.y_max)
        y=np.arange(self.y_min, self.y_max+5,10)
        self.a.set_yticks(y) 
        # self.a.set_yticklabels(y, fontsize=8)
        self.a.autoscale_view(True)
        self.a.relim()
        self.a.plot(list(range(len(data.axis_data1))),data.axis_data1,'ro-', label="Data1",markersize=1, linewidth=1)
        self.a.plot(list(range(len(data.axis_data2))),data.axis_data2,'bo-', label="Data2",markersize=1,linewidth=1)            # self.a.plot(list(range(len(data.axis_data1))),data.axis_data1,'ro-', label="Data1",markersize=1, linewidth=1)
        # self.lineplot.set_data(np.arange(0,len(data.axis_data1),1),np.array(data.axis_data1))
        # self.lineplot1.set_data(np.arange(0,len(data.axis_data2),1),np.array(data.axis_data2))

        self.a.legend(loc=1) 
        self.a.minorticks_on()
        self.a.grid(which='major', linestyle='-', linewidth='0.5', color='black') 
        self.a.grid(which='minor', linestyle=':', linewidth='0.5', color='black') 
        self.fig.canvas.draw()
        # self.fig.canvas.draw_idle()



 
if __name__ == '__main__':
    # object for save data
    data = DataPlot()
    # GUI panel
    app = wx.App(False)
    frame = Screen(None, 'Datalogger')
    # Main loop for GUI
    app.MainLoop()

    


