# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk

from API.Model import Model

from Frames.COM_Frame import COM_Frame
from Frames.VariableTable_Frame import VariableTable_Frame

class Application(ttk.Frame):
    def __init__(self,parent,**kwargs):
        # Init
        self.parent = parent
        ttk.Frame.__init__(self,parent,**kwargs)

        # Init configuration
        ttk.Style().configure("BW.TLabel")
        ttk.Style().configure("BW.TButton")

        self.grid(row=0,column=0,sticky="WENS")

        # Create Model
        self.model = Model()

        # Init tabs
        self.com_ports = COM_Frame(self,self.model,relief=Tk.GROOVE)
        self.com_ports.grid(column=0,row=0,sticky='NSEW',pady=2,padx=5)

        # Init tabs
        self.var_table = VariableTable_Frame(self,self.model,relief=Tk.GROOVE)
        self.var_table.grid(column=0,row=1,sticky='NSEW',pady=2,padx=5)

    def stop(self):
        self.model.finish()



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

    app.mainloop()
    print("Done.")
