# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import matplotlib, sys
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as Tk
import tkinter.ttk as ttk
import numpy as np
from collections import deque
import time as time

"""
2D Plot GUI Frame
"""
class Plot2D_Frame(Tk.Frame):
    def __init__(self,parent,var_id,**kwargs):
        Tk.Frame.__init__(self,parent,**kwargs)
        self.plotmode = 'scalar'
        self.plotted_varid = var_id

        self.ymin = None
        self.ymax = None
        self.xmin = None
        self.xmax = None

        self.x = deque(maxlen=128)
        self.y = deque(maxlen=128)

        # Widgets
        #self.grid(row=0,column=0,sticky="WENS")

        #
        #self.bouton_add_var = Tk.Button(self, text="PLOT SELECTION", command = self.add_var_to_plot)
        #self.bouton_add_var.grid(column=0,row=2,rowspan=2,pady=3,padx=3,sticky='NSEW')

        #
        #self.bouton_switch_mode = Tk.Button(self, text="REMOVE VAR", command = self.remove_var_from_plot)
        #self.bouton_switch_mode.grid(column=2,row=3,pady=3,padx=3)

        #
        #self.bouton_Clear = Tk.Button(self, text="Clear", command = self.clear_plot)
        #self.bouton_Clear.grid(column=3,row=3,pady=3,padx=3)

        #
        self.f = Figure(figsize=(5,4), dpi=100)
        self.a = self.f.add_subplot(111)
        self.a.set_xlim([0, 127])
        self.a.set_ylim([-255, 255])
        self.line1, = self.a.plot([],[])
        self.a.set_autoscale_on(True)
        #
        self.plotFrame = Tk.Frame(self)
        self.dataPlot = FigureCanvasTkAgg(self.f, master=self)
        self.dataPlot.show()
        self.dataPlot.get_tk_widget().grid(column=0,row=0,sticky='WENS',columnspan=5)


        self.toolbar = NavigationToolbar2TkAgg(self.dataPlot, self.plotFrame)
        self.plotFrame.grid(row=1,column=0,columnspan=5,sticky="WENS")

        self.start_time = time.time()

        #
        """
        self.selected_var_name = Tk.StringVar()
        self.selected_var_name.set("No variable")
        self.selected_var = Tk.Label(self,textvariable=self.selected_var_name,bd=2,relief=Tk.GROOVE)
        self.selected_var.grid(column=2,row=2,sticky='EW',pady=3,padx=3)
        #
        self.selected_value = Tk.DoubleVar()
        self.selected_value.set(0.0)
        self.selected_var_val = Tk.Label(self,textvariable=self.selected_value,bd=2,relief=Tk.GROOVE)
        self.selected_var_val.grid(column=3,row=2,sticky='EW',pady=3,padx=3)
        """


    def on_value_received(self,var_id,var_type,var_value,**kwargs):
        if not self.plotted_varid == var_id:
            return


        #self.x.appendleft(var_values)
        self.y.append(var_value)
        self.x.append(time.time()-self.start_time)

        self.a.set_xlim([self.x[0],self.x[-1]])
        self.line1.set_data(self.x,self.y)
        self.a.relim()
        self.a.autoscale_view(False,False,True)
        self.dataPlot.draw()

if __name__=="__main__":
    root = Tk.Tk()
    Plot_frm = Plot2D_Frame(root,None, root)
    root.minsize(width=300, height=200)
    root.mainloop()
