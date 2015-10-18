# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import tkinter as Tk
import tkinter.ttk as ttk
from DistantIO.UI.Plot2D_Frame import Plot2D_Frame
import logging
from distantio.Utils import ValuesXY

class VariableTable_Frame(ttk.LabelFrame):
    def __init__(self,parent,model,**kwargs):
        ttk.LabelFrame.__init__(self,parent,**kwargs)
        self.parent = parent
        self.model = model
        self.selected_var_id = None
        self.define_first = False
        self.variables = dict()
        self.groups = dict()
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


        self.var_list = ttk.Treeview(self.table_frame)
        #self.var_list['show']="headings"
        self.var_list['columns']=("name","type","value")
        self.var_list['selectmode']="browse"
        self.var_list['yscrollcommand']=self.scrollbar_log.set

        self.var_list.grid(column=0,row=0,sticky='EWNS',pady=3,padx=(3,0))#columnspan=2

        self.var_list.column('#0',anchor='center',minwidth=0,width=80,stretch=Tk.NO)
        self.var_list.heading('#0', text='Group')

        self.var_list.column('name',anchor='center',minwidth=0,width=120,stretch=Tk.NO)
        self.var_list.heading('name', text='name')

        self.var_list.column('type',anchor='center',minwidth=0,width=50, stretch=Tk.NO)
        self.var_list.heading('type', text='type')

        self.var_list.column('value', anchor='center', minwidth=0, width=120, stretch=Tk.NO)
        self.var_list.heading('value', text='value')

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
        self.model.signal_received_group_descriptor.connect(self.on_group_descriptor_received)


    def request_descriptors(self):
        self.parent.request_descriptors()

    def remove_descriptors(self):
        # Empty table
        x = self.var_list.get_children()
        for item in x:
            self.var_list.delete(item)
        # Empty variable list
        self.variables = dict()
        self.groups = dict()

    def on_descriptor_received(self,var_id,var_type,var_name,var_writeable,group_id,**kwargs):
        # Check if variable is already inside ?

        if not var_id in self.variables:
            self.variables[var_id] = dict()
            self.variables[var_id]['name'] = var_name
            self.variables[var_id]['value'] = 0
            self.variables[var_id]['id'] = var_id
            self.variables[var_id]['type'] = var_type

            self.variables[var_id]['writeable'] = var_writeable
            self.variables[var_id]['group'] = group_id

            # If the group does not exists, we create it
            if not group_id in self.groups:
                # Create group
                self.groups[group_id] = dict()
                 # The root id of the group in the Treeview
                 # Child items will have to be inserted beneath it
                created_id = self.var_list.insert('','end',text="Group "+str(group_id),open=True)
                #self.var_list.set(created_id,'#0',str(group_id))
                self.groups[group_id]['index'] = created_id

            # Now insert items
            i = self.var_list.insert(self.groups[group_id]['index'],'end',text=str(var_id))
            self.variables[var_id]['index'] = i

            self.var_list.set(i,'name',var_name)
            self.var_list.set(i,'type',var_type)

    def on_group_descriptor_received(self,group_id,group_name,**kwargs):
        # If the group does not exists, we create it
        if not group_id in self.groups:
            # Create group
            self.groups[group_id] = dict()
             # The root id of the group in the Treeview
             # Child items will have to be inserted beneath it
            created_id = self.var_list.insert('','end',text=group_name,open=True)
            #self.var_list.set(created_id,'#0',str(group_id))
            self.groups[group_id]['index'] = created_id

        # Otherwise we just correct the name
        else:
            created_id = self.groups[group_id]['index']
            self.var_list.item(created_id,text=group_name)


    def on_value_received(self,var_id,**kwargs):
        if var_id in self.variables:
            i = self.variables[var_id]['index']
            self.var_list.set(i,'value',self.model.get_last_value(var_id))


    def on_checkbutton_changed(self):
        if self.checkbutton_state.get():
            self.parent.request_read_all()

    def write_value(self):
        if not self.selected_var_id in self.variables:
            logging.debug("write_value : var id "+str(self.selected_var_id)+" not found.")
            return
        # If that fails, it means the string is unvalid
        try:
            value = float(self.value.get())
        except ValueError as e:
            print(str(e))

        self.parent.request_write(self.selected_var_id,value)

    def variable_selected(self,event):
        # Get selection tree index
        it = self.var_list.selection()[0]

        # If selection is in a variable
        for key in self.variables:
            if self.variables[key]['index'] == it:
                var_id = self.variables[key]['id']
                if not var_id in self.variables:
                    return

                self.selected_var_id = var_id

                # If selected variable is writeable
                if self.variables[var_id]['writeable']:
                    self.variable.set(self.variables[var_id]['name'])
                else:
                    self.variable.set("** Variable not writeable **")
                return

        # Otherwise, if selection is a group
        for key in self.groups:
            if self.groups[key]['index'] == it:
                self.selected_var_id = None
                return

    def plot(self):
        if not self.selected_var_id in self.variables:
            return

        top = Tk.Toplevel()
        plot = Plot2D_Frame(top,self.model,self.selected_var_id)
        plot.pack()
        self.model.signal_received_value.connect(plot.on_value_received)
        self.plots.append(plot)
        top.title("Plot : "+self.variables[self.selected_var_id]['name'])
        #plot.protocol('WM_DELETE_WINDOW', self.plot_frame.stop)
        #plot.minsize(width=300, height=200)


    # Callback functions
    def on_MCU_state_changed(self,alive,**kwargs):
        if alive:
            self.txt_active.config(text="Alive",fg='green')
        else:
            self.txt_active.config(text="Disconnected",fg='blue')
        self.parent.update_idletasks()


if __name__=="__main__":
    root = Tk.Tk()
    m = None
    fr = VariableTable_Frame(root,m)
    root.minsize(width=300, height=200)
    root.mainloop()
