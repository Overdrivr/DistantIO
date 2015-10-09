# coding=utf-8
# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk

from API.Model import Model
from API.TimingUtils import timeit
from UI.COM_Frame import COM_Frame
from UI.VariableTable_Frame import VariableTable_Frame
from UI.SerialHealth_Frame import SerialHealth_Frame

class Application(ttk.Frame):
    @timeit
    def __init__(self,parent,**kwargs):
        # Init
        self.root = parent
        ttk.Frame.__init__(self,parent,**kwargs)

        # Init configuration
        ttk.Style().configure("BW.TLabel")
        ttk.Style().configure("BW.TButton")

        self.grid(row=0,column=0,sticky="WENS")

        # Create Model
        self.model = Model()

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

    def stop(self):
        self.model.finish()

    def update(self):
        # Decode 100 instructions max
        self.model.update(10)
        self.root.after(10,self.update)



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
