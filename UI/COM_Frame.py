# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk
import numpy as np
from collections import deque

"""
COM GUI Frame
"""

class COM_Frame(ttk.LabelFrame):
    def __init__(self,parent,model,**kwargs):
        ttk.LabelFrame.__init__(self,parent,text="COM Ports",**kwargs)
        self.parent = parent
        self.model = model

        self.grid(row=0,column=0,sticky="WENS")

        #Widgets
        self.txt_ports = ttk.Label(self,text="STATUS :",style="BW.TLabel")
        self.txt_ports.grid(column=0,row=0,sticky='EW',pady=3,padx=3)

        #
        self.listbox_frame = ttk.Frame(self)
        self.listbox_frame.grid(column=0,row=1,sticky='NSEW',pady=3,padx=3,columnspan=3)

        self.liste = Tk.Listbox(self.listbox_frame,height=6,width=40)
        self.liste.grid(column=0,row=0,sticky="WENS")

        self.scrollbar_liste = ttk.Scrollbar(self.listbox_frame)
        self.scrollbar_liste.config(command = self.liste.yview)
        self.liste.config(yscrollcommand = self.scrollbar_liste.set)
        self.scrollbar_liste.grid(column=1,row=0,sticky="WNS")

        #
        self.bouton_refresh_ports = ttk.Button(self, text="REFRESH", command = self.refresh_COM_ports)
        self.bouton_refresh_ports.grid(column=0,row=2,sticky='EW',pady=3,padx=3)

        self.bouton_connect = ttk.Button(self, text="CONNECT", command = self.start_com)
        self.bouton_connect.grid(column=1,row=2,sticky='EW',pady=3,padx=3)

        self.bouton_disconnect = ttk.Button(self, text="DISCONNECT", command = self.stop_com)
        self.bouton_disconnect.grid(column=2,row=2,sticky='EW',pady=3,padx=3)

        self.txt_connected = Tk.Label(self,text="NOT CONNECTED",fg='red')
        self.txt_connected.grid(column=2,row=0,sticky='E')

        #redimensionnement:
        self.parent.grid_columnconfigure(0,weight=1)
        self.parent.grid_rowconfigure(0,weight=1)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1, minsize=40)

        self.listbox_frame.grid_columnconfigure(0,weight=1)
        self.listbox_frame.grid_rowconfigure(0,weight=1)

        # Connect Signals from model to callbacks
        self.model.signal_connected.connect(self.com_connected)
        self.model.signal_disconnected.connect(self.com_disconnected)
        self.model.signal_connecting.connect(self.com_connecting)

    def refresh_COM_ports(self):
        ports_list = self.model.get_ports()
        self.liste.delete(0,Tk.END)

        print('COM ports list :')
        for p, desc, hwid in sorted(ports_list):
            print('--- %s %s\n' % (p, desc))
            self.liste.insert(Tk.END,p)

    def start_com(self):
        if not self.liste.curselection():
            print("No port selected, aborting.")
            return

        chosen_port = self.liste.get(Tk.ACTIVE)
        self.model.connect(chosen_port)

    def stop_com(self):
        self.model.disconnect()

    def com_connected(self,port,**kwargs):
        self.txt_connected.config(text="CONNECTED",fg='green')
        self.parent.update_idletasks()

    def com_disconnected(self,**kwargs):
        self.txt_connected.config(text="DISCONNECTED",fg='red')
        self.parent.update_idletasks()
        self.connected = False

    def com_connecting(self,**kwargs):
        self.txt_connected.config(text="CONNECTING",fg="orange")
        self.parent.update_idletasks()


if __name__=="__main__":
    root = Tk.Tk()
    COM_frm = COM_Frame(root,None)
    root.minsize(width=300, height=120)
    root.mainloop()
