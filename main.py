from Tkinter import *
from tkinter.ttk import *
import Tkinter, Tkconstants, tkFileDialog
import serial
import serial.tools.list_ports
from tkinter import scrolledtext
import threading
import time
import sys
import datetime
import os

baud_values = ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]

parity_values = { "NONE": serial.PARITY_NONE , 
                  "EVEN": serial.PARITY_EVEN, 
                  "ODD": serial.PARITY_ODD, 
                  "MARK": serial.PARITY_MARK, 
                  "SPACE": serial.PARITY_SPACE }

bytesize_values = { "5": serial.FIVEBITS, 
                    "6": serial.SIXBITS, 
                    "7": serial.SEVENBITS,  
                    "8": serial.EIGHTBITS }

stopbits_values = { "1": serial.STOPBITS_ONE,
                   "1.5": serial.STOPBITS_ONE_POINT_FIVE,
                   "2": serial.STOPBITS_TWO }

FILE_NAME_FMT = "serial_log_%Y%m%d-%H%M%S.log"

log_dir = "/tmp"

log_filename = datetime.datetime.today().strftime(FILE_NAME_FMT)

def fmt_line(line):
    pre = datetime.datetime.today().strftime("%a, %d %b %Y %H:%M:%S")
    line = "%s;%s\n" % (pre, line)
    print(line)
    return line

def temp_getter(compl_line):
    temp = compl_line.split(";")[0]
    temp = temp.split(":")[1]
    temp = temp[:-1]
    phase = compl_line.split("/")[1]+"/"+compl_line.split("/")[2]
    return temp,phase

class Writethread(threading.Thread): 
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 

    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 

    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None

    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line': 
                raise SystemExit() 
            return self.localtrace 

    def kill(self): 
        self.killed = True
        
class Fieldmaneger():
    def __init__(self,gui,serialport):
        self.serialport = serialport
        self.text_field = gui.txt_output
        self.log_file = os.path.join(log_dir, log_filename)
        self.f = open(self.log_file, "w+")
        gui.lbl_log.config(text = "Log file: %s" % self.log_file)
        self.compl_line = ""
        self.temp = ""
        self.phase = ""
        
    def readtotext(self):
        self.line = self.serialport.read_from_port()
        self.text_field.insert(INSERT,self.line)
        if self.line:
            self.compl_line = self.compl_line + self.line   
            if "\r\n" == self.compl_line[-2:]:
                if "TEMP" == self.compl_line[:4]:
                    self.temp,self.phase = temp_getter(self.compl_line)
                else:
                    self.f.write(fmt_line(self.compl_line[:-2] + self.temp + ";" + self.phase))
                    self.f.flush()
                self.compl_line = ""
        #self.f.write(fmt_line(self.compl_line))
        #self.f.flush()
        
class Serialmanager():
    def __init__(self,port, baudrate, bytesize, parity, stopbits):
        self.serialport = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout=None)
    
    def read_from_port(self):
        return self.serialport.readline()

    def write_to_port(self,msg):          
        self.serialport.write(msg)     

class Gui:
    def __init__(self):       
        self.write_thread = Writethread(target=self.read)
        self.root = Tk()

        self.logsection = Frame(self.root)
        self.logsection.pack(anchor = NW, side = BOTTOM)
        
        self.footframe = Frame(self.root)
        self.footframe.pack(anchor = NW, side = BOTTOM)
        
        self.bottomframe = Frame(self.root)
        self.bottomframe.pack(anchor = NW, side = BOTTOM )
        
        self.centerframe = Frame(self.root)
        self.centerframe.pack(anchor = NW, side = BOTTOM )
        
        self.topframe = Frame(self.root)
        self.topframe.pack(anchor = NW, side = BOTTOM)

        self.lbl_port = Label(self.topframe, text="Select serial port:")
        self.lbl_port.pack(side = LEFT)

        self.cb_ports = Combobox(self.topframe, width=11)
        self.cb_ports.pack(side = LEFT)

        self.lbl_baud = Label(self.topframe, text="Baudrate:")
        self.lbl_baud.pack(side = LEFT)

        self.cb_baud_rate = Combobox(self.topframe, values = baud_values)
        self.cb_baud_rate.pack(side = LEFT)

        self.cb_baud_rate.current(6)

        self.btn_open = Button(self.footframe, text="Open port", command=self.open_port)
        self.btn_open.pack(side = LEFT)

        self.btn_close = Button(self.footframe, text="Close port", command=self.close_port)
        self.btn_close.pack(side = LEFT)

        self.btn_clear = Button(self.footframe, text="Clear output", command=self.clear)
        self.btn_clear.pack(side = LEFT)

        self.btn_send = Button(self.footframe, text="Send", command=self.send)
        self.btn_send.pack(side = RIGHT)

        self.txt_to_send = Text(self.footframe, width=50, height=1)
        self.txt_to_send.pack(side = RIGHT)

        self.lbl_log = Label(self.logsection, text="")
        self.lbl_log.pack(side = LEFT)
        
        self.lbl_parity = Label(self.centerframe, text="Parity:")
        self.lbl_parity.pack(side = LEFT)

        self.cb_parity = Combobox(self.centerframe, values = parity_values.keys())
        self.cb_parity.pack(side = LEFT)

        self.cb_parity.current(1)

        self.lbl_bytesize = Label(self.centerframe, text="Bytesyze:")
        self.lbl_bytesize.pack(side = LEFT)

        self.cb_bytesize = Combobox(self.centerframe, values = bytesize_values.keys() )
        self.cb_bytesize.pack(side = LEFT)

        self.cb_bytesize.current(0)

        self.lbl_stopbits = Label(self.centerframe, text="Stopbits:")
        self.lbl_stopbits.pack(side = LEFT)

        self.cb_stopbit = Combobox(self.centerframe, values = stopbits_values.keys())
        self.cb_stopbit.pack(side = LEFT)

        self.cb_stopbit.current(0)

        self.txt_output = scrolledtext.ScrolledText(self.bottomframe, width=90,height=20)
        self.txt_output.pack(side = LEFT)

        self.fill_ports()

        self.serial = None
    
    def start_gui(self):
        self.root.mainloop()
        
    def fill_ports(self):
        for p in list(serial.tools.list_ports.comports()):
            self.cb_ports['values'] += str(p).split(" ")[0]

    def open_port(self):
        self.write_thread = Writethread(target=self.read)
        print("Starting reading thread")
        self.write_thread.start()
          
    def close_port(self):
        print("Stopping reading thread")
        self.write_thread.kill()

    def read(self):
        self.serial = Serialmanager(port = self.cb_ports.get(), baudrate = int(self.cb_baud_rate.get()), bytesize = bytesize_values.get(self.cb_bytesize.get()), parity = parity_values.get(self.cb_parity.get()), stopbits = stopbits_values.get(self.cb_stopbit.get()))   
        self.fm = Fieldmaneger(self,self.serial)
        while True:
                self.fm.readtotext()
                #self.txt_output.insert(INSERT,self.serial.read_from_port())

    def send(self):
        text = self.txt_to_send.get("1.0",END)
        print("Invio su seriale.." + text)
        self.serial.write_to_port(text.encode())
    
    def clear(self):
        self.txt_output.delete('1.0', END)

    


def main():
    print("Starting main...")
    main_gui = Gui()
    print("Starting GUI...")
    main_gui.start_gui()
    
if __name__ == "__main__":

    main()
