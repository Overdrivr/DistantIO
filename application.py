# coding=utf-8
# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk
import logging
import distantio
from distantio.TimingUtils import timeit
from UI.COM_Frame import COM_Frame
from UI.VariableTable_Frame import VariableTable_Frame
from UI.SerialHealth_Frame import SerialHealth_Frame

class Application(ttk.Frame):
    def __init__(self,parent,**kwargs):
        # Init
        self.root = parent
        ttk.Frame.__init__(self,parent,**kwargs)

        # Init configuration
        ttk.Style().configure("BW.TLabel")
        ttk.Style().configure("BW.TButton")

        self.grid(row=0,column=0,sticky="WENS")

        # DistantIO api
        self.model = distantio.DistantIO()
        # Serial port will be our IO in this application
        self.serial = distantio.SerialPort(self.model.decode_rx_data)

        # Init COM port frame
        self.com_ports = COM_Frame(self,self.model,relief=Tk.GROOVE)
        self.com_ports.grid(column=0,row=0,sticky='NSEW',pady=2,padx=5)


        # Init table frame
        self.var_table = VariableTable_Frame(self,self.model,relief=Tk.GROOVE)
        self.var_table.grid(column=0,row=1,sticky='NSEW',pady=2,padx=5)

        # Init serial health Frame
        self.health_frame = SerialHealth_Frame(self,self.model,self.root,relief=Tk.GROOVE)
        self.health_frame.grid(column=0,row=2,sticky='NSEW',pady=2,padx=5)

        self.com_ports.refresh_COM_ports()
        self.update()

    def disconnect(self):
        self.serial.close()
        self.model.export_data()

    def connect(self,port,baudrate):
        self.serial.connect(port,baudrate)

    def stop(self):
        self.serial.close()
        logging.info('SerialPort stopped.')
        self.model.terminate()
        logging.info('Model terminated.')

    def update(self):
        # Decode 100 instructions max
        self.model.update(10)
        self.root.after(10,self.update)

    def available_ports(self):
        return self.serial.get_ports()

    def request_write(self,variable_id,data):
        frame = self.model.request_write(variable_id, data)
        self.serial.write(frame)

    def request_read_all(self):
        frame_generator = self.model.request_read_all()

        for frame in frame_generator:
            self.serial.write(frame)

    def request_descriptors(self):
        frame = self.model.request_descriptors()
        self.serial.write(frame)

"""
Program startup
"""
if __name__ == '__main__':
    # Create window
    root = Tk.Tk()
    root.geometry('+0+0')

    app = Application(root,width=640, height=480)

    def onExit():
        app.stop()
        root.destroy()

    root.wm_protocol ("WM_DELETE_WINDOW", onExit)

    root.mainloop()
    print("Done.")
