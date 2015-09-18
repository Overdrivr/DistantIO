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
import timeit

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

        self.start_time = timeit.default_timer()

        self.refresh_last_time = timeit.default_timer()
        self.refresh_rate = 0.1 # Redraw every hundred millisecond

    def on_value_received(self,var_id,var_type,var_value,**kwargs):
        if not self.plotted_varid == var_id:
            return

        t = timeit.default_timer()

        #self.x.appendleft(var_values)
        self.y.append(var_value)
        self.x.append(t - self.start_time)

        if t - self.refresh_last_time > self.refresh_rate:
            self.refresh_last_time = t

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
