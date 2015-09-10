# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk
from UI.Plot2D_Frame import Plot2D_Frame

class VariableTable_Frame(ttk.LabelFrame):
    def __init__(self,parent,model,**kwargs):
        ttk.LabelFrame.__init__(self,parent,**kwargs)
        self.parent = parent
        self.model = model
        self.selected_var_id = None
        self.define_first = False
        self.variables = dict()
        self.plots = []

        self.txt_log = Tk.Label(self,text="MCU status :")
        self.txt_log.grid(column=0,row=0,sticky='ENW',pady=3,padx=3)

        self.txt_active = Tk.Label(self,text="disconnected",fg='blue',borderwidth=2)
        self.txt_active.grid(column=1,row=0,sticky='ENW',pady=3,padx=3)

        self.txt_table = Tk.Label(self,text="Variable table :")
        self.txt_table.grid(column=0,row=1,sticky='ENW',pady=3,padx=3)

        self.bouton_activate = ttk.Button(self, text="request all", command = self.request_descriptors)
        self.bouton_activate.grid(column=1,row=1,sticky='ENW',pady=3,padx=3)

        self.bouton_clear = ttk.Button(self, text="clear", command = self.remove_descriptors)
        self.bouton_clear.grid(column=2,row=1,sticky='ENW',pady=3,padx=3)

        self.txt_read = Tk.Label(self,text="Read all variables :")
        self.txt_read.grid(column=0,row=2,sticky='ENW',pady=3,padx=3)

        self.checkbutton_state = Tk.IntVar()
        self.check_read = ttk.Checkbutton(self,command=self.on_checkbutton_changed,variable=self.checkbutton_state)
        self.check_read.grid(column=1,row=2)

        # Table + scrollbar group
        self.table_frame = ttk.Frame(self)
        self.table_frame.grid(column=0,row=3,columnspan=3, sticky="WENS")

        self.scrollbar_log = ttk.Scrollbar(self.table_frame)
        self.scrollbar_log.grid(sticky ='WNS',row=0,column=2)


        self.var_list = ttk.Treeview(self.table_frame, show="headings",columns=("name","type","value","ID"),selectmode="browse", yscrollcommand=self.scrollbar_log.set)
        self.var_list.grid(column=0,row=0,sticky='EWNS',pady=3,padx=(3,0))#columnspan=2

        self.var_list.column('name',anchor='center',minwidth=0,width=120,stretch=Tk.NO)
        self.var_list.heading('name', text='name')

        self.var_list.column('type',anchor='center',minwidth=0,width=50, stretch=Tk.NO)
        self.var_list.heading('type', text='type')

        self.var_list.column('value', anchor='center', minwidth=0, width=120, stretch=Tk.NO)
        self.var_list.heading('value', text='value')

        self.var_list.column('ID',anchor='center',minwidth=0,width=30, stretch=Tk.NO)
        self.var_list.heading('ID', text='ID')

        self.var_list.bind("<<TreeviewSelect>>", self.variable_selected)
        self.scrollbar_log.config( command=self.var_list.yview)

        # Variable name
        self.variable = Tk.StringVar()
        self.variable.set("No var")

        self.selected_var = ttk.Label(self,textvariable=self.variable)
        self.selected_var.grid(column=0,row=4,columnspan=2,sticky="NSEW",pady=3,padx=3)

        # bouton plot:
        self.bouton_plot = ttk.Button(self, text="Plot", command = self.plot)
        self.bouton_plot.grid(column=2, row=4, sticky='WENS', pady=3, padx=3)

        # fixed label
        self.label_var2 = ttk.Label(self,text="Value :")
        self.label_var2.grid(column=0,row=5, sticky="NSEW",pady=3,padx=3)

        #Variable read/write value
        self.value = Tk.DoubleVar()
        self.value.set(0.0)

        self.label_var2 = ttk.Entry(self,textvariable=self.value)
        self.label_var2.grid(column=1,row=5, sticky="NSEW",pady=3,padx=3)

        # Write button
        self.bouton_write = ttk.Button(self, text="WRITE", command = self.write_value)
        self.bouton_write.grid(column=2,row=5,sticky='WENS',pady=3,padx=3)

        # redimensionnement fenetres
        self.parent.grid_columnconfigure(0,weight=1)
        self.parent.grid_rowconfigure(0,weight=1)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.table_frame.grid_columnconfigure(0,weight=1)
        self.table_frame.grid_rowconfigure(0,weight=1)
        self.var_list.grid_columnconfigure(3, weight=1)

        # Subscriptions
        self.model.signal_MCU_state_changed.connect(self.on_MCU_state_changed)
        self.model.signal_received_value.connect(self.on_value_received)
        self.model.signal_received_descriptor.connect(self.on_descriptor_received)

    def request_descriptors(self):
        self.model.request_descriptors()

    def remove_descriptors(self):
        # Empty table
        x = self.var_list.get_children()
        for item in x:
            self.var_list.delete(item)
        # Empty variable list
        self.variables = dict()

    def on_descriptor_received(self,var_id,var_type,var_name,var_writeable,**kwargs):
        # Check if variable is already inside ?

        if not var_id in self.variables:
            i = self.var_list.insert('','end')

            self.variables[var_id] = dict()
            self.variables[var_id]['name'] = var_name
            self.variables[var_id]['value'] = 0
            self.variables[var_id]['id'] = var_id
            self.variables[var_id]['type'] = var_type
            self.variables[var_id]['index'] = i
            self.variables[var_id]['writeable'] = var_writeable

            self.var_list.set(i,'name',var_name)
            self.var_list.set(i,'type',var_type)
            self.var_list.set(i,'ID',var_id)

    def on_value_received(self,var_id,var_type,var_value,**kwargs):
        if var_id in self.variables:
            i = self.variables[var_id]['index']
            self.var_list.set(i,'value',var_value)


    def on_checkbutton_changed(self):
        if self.checkbutton_state.get():
            self.model.request_read_all()

    def write_value(self):
        # Find selected variable
        it = self.var_list.selection()
        # Get associated var_id
        var_id = self.var_list.set(it,column='ID')

        if var_id in self.variables:
            # If that fails, it means the string is unvalid
            try:
                value = self.value.get()
            except:
                return
            self.model.request_write(var_id,value)

    def variable_selected(self,event):
        # Find selected variable
        it = self.var_list.selection()

        # Get associated var_id
        var_id = self.var_list.set(it,column='ID')

        if not var_id in self.variables:
            return

        self.selected_var_id = var_id

        # If selected variable is writeable
        if self.variables[var_id]['writeable']:
            self.variable.set(self.variables[var_id]['name'])
        else:
            self.variable.set("** Variable not writeable **")

        self.defined_first = False


    def plot(self):
        # Find selected variable
        it = self.var_list.selection()

        # Get associated var_id
        var_id = self.var_list.set(it,column='ID')

        if not var_id in self.variables:
            return

        top = Tk.Toplevel()
        plot = Plot2D_Frame(top,var_id)
        plot.pack()
        self.model.signal_received_value.connect(plot.on_value_received)
        self.plots.append(plot)
        top.title("Plot : "+self.variables[var_id]['name'])
        #plot.protocol('WM_DELETE_WINDOW', self.plot_frame.stop)
        #plot.minsize(width=300, height=200)


    # Callback functions
    def on_MCU_state_changed(self,alive,**kwargs):
        if alive:
            self.txt_active.config(text="Alive",fg='green')
        else:
            self.txt_active.config(text="Disconnected",fg='blue')
        self.parent.update_idletasks()
