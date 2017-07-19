from Tkinter import*
from tkFileDialog import*
from simulate import*
import tkMessageBox
import os

class SPICE(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        #self.master.geometry('220x120')
        self.msg = '>>Running status:'
        self.master.title('My spice')
        self.grid()
        self.createWidgets()
        self.mainloop()

    def createWidgets(self):
        self.lable = Label(self, text = 'Welcome to my simple spice!')
        self.lable.grid(row=0, columnspan=5)
        self.openButton = Button(self, text = 'Open', width=10, command=self.open)
        self.openButton.grid(row=1, column=0)
        self.editButton = Button(self, text= 'EditNL', width=10, state=DISABLED, command=self.editnl)
        self.editButton.grid(row=1, column=1)
        self.simButton = Button(self, text='Simulate', width=10, state=DISABLED, command=self.simulate)
        self.simButton.grid(row=1, column=2)
        self.waveButton = Button(self, text='Avanwave', width=10, state=DISABLED, command=self.avanwave)
        self.waveButton.grid(row=1, column=3)
        self.quitButton = Button(self, text='Quit', width=10, command=self.quit)
        self.quitButton.grid(row=1, column=4)


    
    def avanwave(self):
        self.sim.print_result()

    def simulate(self):
        self.sim = Simulate(self.filename)
        self.waveButton['state'] = ACTIVE
        var = StringVar()
        self.text = Message(self, textvariable=var, width=400)
        self.text.grid(row=2, columnspan=55, sticky=W)
        self.msg += self.sim.message
        var.set(self.msg)
    def open(self):
        self.filename = askopenfilename(filetypes=[('sp','.sp')])
        if self.filename:
            self.simButton['state'] = ACTIVE
            self.editButton['state'] = ACTIVE
            self.lable['text'] = 'Design:  '+self.filename
    def editnl(self):
        os.startfile(self.filename)

SPICE()
