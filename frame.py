from Tkinter import *
from tkinter.ttk import *
import serial
import serial.tools.list_ports
from tkinter import scrolledtext
import threading
      


class thread_with_trace(threading.Thread): 
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
  
def fill_ports():
    for p in list(serial.tools.list_ports.comports()):
        cb_ports['values'] += str(p).split(" ")[0]
    
def open_port():
    if not t.is_alive():
        t.start()


def close_port():
    t.kill()

def read_port():
     with serial.Serial(cb_ports.get(), int(cb_baud_rate.get()),timeout=1) as ser:      
            while 1:
                txt_output.insert(INSERT,ser.readline())
                topframe.update()

root = Tk()

footframe = Frame(root)
footframe.pack(anchor = NW, side = BOTTOM)

bottomframe = Frame(root)
bottomframe.pack(anchor = NW, side = BOTTOM )

centerframe = Frame(root)
centerframe.pack(anchor = NW, side = BOTTOM )

topframe = Frame(root)
topframe.pack(anchor = NW, side = BOTTOM)

cb_ports = Combobox(topframe, width=10)

killed = False

t = thread_with_trace(target=read_port)

lbl_port = Label(topframe, text="Select serial port:")
lbl_port.pack(side = LEFT)

cb_ports = Combobox(topframe, width=10)
cb_ports.pack(side = LEFT)

fill_ports()

lbl_baud = Label(topframe, text="Baudrate:")
lbl_baud.pack(side = LEFT)

cb_baud_rate = Combobox(topframe, values = ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
cb_baud_rate.pack(side = LEFT)

cb_baud_rate.current(6)

btn_open = Button(footframe, text="Open port", command=open_port)
btn_open.pack(side = LEFT)

btn_close = Button(footframe, text="Close port", command=close_port)
btn_close.pack(side = LEFT)


lbl_parity = Label(centerframe, text="Parity:")
lbl_parity.pack(side = LEFT)

cb_parity = Combobox(centerframe, values = ["PARITY_NONE", "PARITY_EVEN", "PARITY_ODD", "PARITY_MARK", "PARITY_SPACE"])
cb_parity.pack(side = LEFT)

cb_parity.current(0)

lbl_bytesize = Label(centerframe, text="Bytesyze:")
lbl_bytesize.pack(side = LEFT)

cb_bytesize = Combobox(centerframe, values = ["FIVEBITS", "SIXBITS", "SEVENBITS", "EIGHTBITS"])
cb_bytesize.pack(side = LEFT)

cb_bytesize.current(3)

lbl_stopbits = Label(centerframe, text="Stopbits:")
lbl_stopbits.pack(side = LEFT)

cb_stopbit = Combobox(centerframe, values = ["STOPBITS_ONE", "STOPBITS_ONE_POINT_FIVE", "STOPBITS_TWO"])
cb_stopbit.pack(side = LEFT)

cb_stopbit.current(0)

txt_output = scrolledtext.ScrolledText(bottomframe, width=80,height=20)
txt_output.pack(side = LEFT)

root.mainloop()