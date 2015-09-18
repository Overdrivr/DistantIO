import tkinter as Tk
import tkinter.ttk as ttk

class SerialHealth_Frame(ttk.LabelFrame):
    def __init__(self,parent,model,root,**kwargs):
        ttk.LabelFrame.__init__(self,parent,text="RX Processing queues",**kwargs)
        self.parent = parent
        self.model = model
        self.root = root

        #Widgets
        self.txt_queue1 = ttk.Label(self,text="Raw serial queue size :",style="BW.TLabel")
        self.txt_queue1.grid(column=0,row=0,sticky='EW',pady=3,padx=3)

        self.queue1_size = Tk.StringVar()
        self.queue1_size.set(0)

        self.txt_size_queue1 = ttk.Label(self,textvariable=self.queue1_size)
        self.txt_size_queue1.grid(column=1,row=0,sticky='EW',pady=3,padx=3)

        self.txt_queue2 = ttk.Label(self,text="Delimited frame queue size :",style="BW.TLabel")
        self.txt_queue2.grid(column=0,row=1,sticky='EW',pady=3,padx=3)

        self.queue2_size = Tk.StringVar()
        self.queue2_size.set(0)

        self.txt_size_queue2 = ttk.Label(self,textvariable=self.queue2_size)
        self.txt_size_queue2.grid(column=1,row=1,sticky='EW',pady=3,padx=3)

        self.txt_queue3 = ttk.Label(self,text="Instruction deque queue size :",style="BW.TLabel")
        self.txt_queue3.grid(column=0,row=2,sticky='EW',pady=3,padx=3)

        self.queue3_size = Tk.StringVar()
        self.queue3_size.set(0)

        self.txt_size_queue3 = ttk.Label(self,textvariable=self.queue3_size)
        self.txt_size_queue3.grid(column=1,row=2,sticky='EW',pady=3,padx=3)

        self.root.after(300,self.refresh)

    def refresh(self):
        self.queue1_size.set(self.model.input_queue.qsize())
        self.queue2_size.set(self.model.output_queue.qsize())
        self.queue3_size.set(len(self.model.instructions))
        self.root.after(300,self.refresh)
