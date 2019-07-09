from Tkinter import *
from tkinter.ttk import *
import serial
import serial.tools.list_ports
from tkinter import scrolledtext

import threading


window = Tk() 
window.geometry('640x480')
window.title("tkcom")
cb_ports = Combobox(window, width=10)

def fill_ports():
    for p in list(serial.tools.list_ports.comports()):
        cb_ports['values'] += str(p).split(" ")[0]
    cb_ports.grid(column=0, row=0)

def btn_ports_clicked():
    t = threading.Thread(target=read_port)
    t.start()

         
def read_port():
     with serial.Serial(cb_ports.get(), 9600, timeout=1) as ser:      
            while 1:
                #x = ser.read()          # read one byte
                #s = ser.read(10)        # read up to ten bytes (timeout)
                line = ser.readline()   # read a '\n' terminated line
                print(line)
                txt.insert(INSERT,line)
                window.update()   

btn = Button(window, text="Click Me", command=btn_ports_clicked)
btn.grid(column=0, row=20)
txt = scrolledtext.ScrolledText(window,width=40,height=10)
txt.grid(column=0,row=2)
fill_ports()
window.mainloop()   
