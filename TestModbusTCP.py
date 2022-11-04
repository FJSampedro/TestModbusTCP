# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 03:19:30 2021

@author: WINCC
"""

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import askinteger, askfloat
from pyModbusTCP.server import ModbusServer
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import word_list_to_long, decode_ieee, long_list_to_word, encode_ieee
import time
import threading
import logging

        
class TestMODBUSTCP():
    
    """MAIN INIT APP"""
    
    def __init__(self):
        self.coils=100
        self.registers=100
        self.Floats=self.registers//2
        self.ServerConnected=False
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
        
        self.Root=Tk()
        self.Root.iconbitmap("common\g7097.ico")
        ttk.Style().theme_use('default')
        #print(ttk.Style().theme_names())
        self.Root.title("Test ModbusTCP v0.0.1")
        self.Root.resizable(False,False)
        self.ServerConfig=self.serverConfig(self.Root)

        self.updateRoot()
        self.Root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.Root.mainloop()
        
    """AUXILIARY METHODS
        -updateRoot : Updates the Root values
        -serverConfig : Manages the grid of server configuration
        -serverStart : Runs the connection with the server or build one server
        -serverStop : Closes the server connection
        -MODBUSServer : starts the server on a separate thread
        -on_closing : Manages the close window secuence"""
    
    def updateRoot(self):
        if self.ServerConnected:
            s1 = threading.Thread(target=self.readCoils,args=(self.coils,), daemon=True)
            s1.start()
            s2 = threading.Thread(target=self.readRegisters,args=(self.registers,), daemon=True)
            s2.start()
            s3 = threading.Thread(target=self.readFloats,args=(self.Floats,), daemon=True)
            s3.start()
        self.id_after=self.Root.after(500,self.updateRoot)
    
    def serverConfig(self,parentWindow, row=0):
        fr=Frame(parentWindow)
        l=Label(fr,text="Server:")
        l.grid(row=0, column=0,ipadx=1, ipady=1, sticky=NSEW)
        l=Label(fr,text="Host:")
        l.grid(row=0, column=1,ipadx=1, ipady=1, sticky=NSEW)
        l=Label(fr,text="Port:")
        l.grid(row=0, column=2,ipadx=1, ipady=1, sticky=NSEW)
        led=Label(fr,text="",bg="red")
        led.grid(row=1, column=0,ipadx=1, ipady=1, sticky=NSEW)
        Host=Entry(fr)
        Host.insert(0, "localhost")
        Host.grid(row=1, column=1,ipadx=1, ipady=1, sticky=NSEW)
        Port=Entry(fr)
        Port.insert(0, "502")
        Port.grid(row=1, column=2,ipadx=1, ipady=1, sticky=NSEW)
        Connect=Button(fr,text="Connect",command=self.serverStart,bg="Green")
        Connect.grid(row=1, column=3,ipadx=1, ipady=1, sticky=NSEW)
        fr.pack()
        return {"Led":led,"Host":Host,"Port":Port,"Button":Connect}
    
    def serverStart(self):
        LED=self.ServerConfig["Led"]
        Connect=self.ServerConfig["Button"]
        Port=self.ServerConfig["Port"]
        Host=self.ServerConfig["Host"]
        
        try:
            p=int(Port.get())
        except:
            messagebox.showwarning("Error","Numero de puerto no admitido")
        else:
            try:
                self.coilList
            except:
                self.frameReadCoils(self.Root)
            try:
                self.registerList
            except:
                self.frameReadRegisters(self.Root)
            try:
                self.FloatList
            except:
                self.frameReadFloats(self.Root)
                
            if Host.get()=="localhost":
                server = ModbusServer(port=p)

                s = threading.Thread(target=self.MODBUSServer,args=(server,), daemon=True)
                s.start()
                            
            LED["bg"]="Green"
            Connect["bg"]="red"
            Connect["command"]=self.serverStop
            Connect["text"]="Disconnect"
            if Host.get()=="localhost":
                self.ServerConfig["Server"]=server
            self.ServerConnected=True
            
        
    def serverStop(self):
        
        LED=self.ServerConfig["Led"]
        Connect=self.ServerConfig["Button"]
        Host=self.ServerConfig["Host"]
        
        if Host.get()=="localhost":
            server=self.ServerConfig["Server"]
            server.stop()
        LED["bg"]="Red"
        Connect["bg"]="Green"
        Connect["text"]="Connect"
        Connect["command"]=self.serverStart
        self.ServerConnected=False

    def MODBUSServer(self,server):
        logging.info("Server Start")
        server.start()
        logging.info("Server Stop")
    
    def on_closing(self):
        if "Server" in self.ServerConfig.keys():
            server=self.ServerConfig["Server"]
            server.stop()
        self.Root.after_cancel(self.id_after)
        self.Root.destroy()
        
    """ SINGLE COIL MANAGEMENT METHODS
        -frameReadCoils : Sets a frame with all coil values
        -readCoils : Reads the coil values
        -writeButtonHandler : handler for writing the coil value in a separate thread
        -writeCoils : writes the coil value in the server"""

    def frameReadCoils(self,parentWindow):
        fr=Frame(parentWindow)
        canvas = Canvas(fr, bg="black",bd=1)
        canvas.grid(row=0, column=0)
        
        vsbar = Scrollbar(fr, orient=VERTICAL, command=canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        canvas.configure(yscrollcommand=vsbar.set)
        
        frc=Frame(canvas, bd=2)
        
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        self.coilList=[]
        for i in range(self.coils):
            l=Label(frc,text="Coil " + str(i) + ":")
            l.grid(row=i, column=0,ipadx=1, ipady=1, sticky=NSEW)
            led=Button(frc,text="  ",command=lambda x=i:self.writeButtonHandler(x),bg="Grey")
            led.grid(row=i, column=1,ipadx=1, ipady=1, sticky=NSEW)
            self.coilList.append(led)
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        bbox = canvas.bbox(ALL)
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/2) * 2), int((h/self.coils) * 18)
        canvas.configure(scrollregion=bbox, width=dw, height=dh)
        fr.pack(fill=BOTH,side=LEFT, padx=10,pady=10)   
    
    def readCoils(self,coils):
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            bits = c.read_coils(0, coils)
            if bits:
                for i,b in enumerate(bits):
                    if b:
                        self.coilList[i]["bg"]="Green"
                    else:
                        self.coilList[i]["bg"]="Grey"
                    
                return bits
            else:
                logging.info("unable to read coils")
                return -1
    
    def writeButtonHandler(self, coilNr):
        s3 = threading.Thread(target=self.writeCoils,args=(coilNr,), daemon=True)
        s3.start()
    
    def writeCoils(self, coilNr):
        
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            if self.coilList[coilNr]["bg"]!="Green":
                is_ok = c.write_single_coil(coilNr, 1)
                logging.info(self.coilList[coilNr]["bg"] + "  :  " + str(coilNr) + " : " + "True")
            else:
                is_ok = c.write_single_coil(coilNr, 0)
                logging.info(self.coilList[coilNr]["bg"] + "  :  " + str(coilNr) + " : " + "False")
            if is_ok:
                logging.info("bit #" + str(coilNr) + ": write success" )
            else:
                logging.info("bit #" + str(coilNr) + ": unable to write " )
    
    """ BINARY REGISTERS MANAGEMENT METHODS
        -frameReadRegisters : Sets a frame with all register values
        -readRegisters : Reads the register values
        -writeRegisterHandler : handler for writing the register value in a separate thread
        -writeRegisters : writes the Register value in the server"""
                
    def frameReadRegisters(self,parentWindow):
        fr=Frame(parentWindow)
        canvas = Canvas(fr, bg="black",bd=1)
        canvas.grid(row=0, column=0)
        
        vsbar = Scrollbar(fr, orient=VERTICAL, command=canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        canvas.configure(yscrollcommand=vsbar.set)
        
        frc=Frame(canvas, bd=2)
        
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        frc.grid_columnconfigure(1, minsize=70)
        self.registerList=[]
        for i in range(self.registers):
            l=Label(frc,text="Value " + str(i) + ":")
            l.grid(row=i, column=0,ipadx=1, ipady=1, sticky=NSEW)
            register=Button(frc,text="0",bg="grey",command=lambda x=i:self.writeRegisterHandler(x))
            register.grid(row=i, column=1,ipadx=1, ipady=1, sticky=NSEW)
            self.registerList.append(register)
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        bbox = canvas.bbox(ALL)
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/2) * 2), int((h/self.registers) * 18)
        canvas.configure(scrollregion=bbox, width=dw, height=dh)
        fr.pack(fill=BOTH,side=LEFT, padx=10,pady=10)
        
    def readRegisters(self,registers):
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            regs = c.read_holding_registers(0, registers)
            if regs:
                for i,b in enumerate(regs):
                        self.registerList[i]["text"]=b
                return regs
            else:
                logging.info("unable to read registers")
                return -1
                
    def writeRegisterHandler(self,regNr):
        reg_value=askinteger("Input","Input the integer value:")
        logging.info(str(regNr) + " : " + str(reg_value))
        s4 = threading.Thread(target=self.writeRegisters,args=(regNr,reg_value,), daemon=True)
        s4.start()
                
    def writeRegisters(self, regNr, reg_value):
        
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            is_ok=c.write_single_register(regNr, reg_value)
            if is_ok:
                logging.info("register #" + str(regNr) + ": write success : " + str(reg_value))
            else:
                logging.info("register #" + str(regNr) + ": unable to write " )
        
    """ FLOAT MANAGEMENT METHODS
        -frameReadFloats : Sets a frame with all Float values
        -readFloats : Reads the float values
        -writeFloatHandler : handler for writing the float value in a separate thread
        -writeFloats : writes the float value in the server"""
    
    def frameReadFloats(self,parentWindow):
        fr=Frame(parentWindow)
        canvas = Canvas(fr, bg="black",bd=1)
        canvas.grid(row=0, column=0)
        
        vsbar = Scrollbar(fr, orient=VERTICAL, command=canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        canvas.configure(yscrollcommand=vsbar.set)
        
        frc=Frame(canvas, bd=2)
        
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        frc.grid_columnconfigure(1, minsize=150)
        self.FloatsList=[]
        for i in range(self.Floats):
            l=Label(frc,text="Float Value  " + str(i) + ":" + "Reg " + str(2*i) + " & " + str((2*i)+1))
            l.grid(row=i, column=0,ipadx=1, ipady=1, sticky=NSEW)
            register=Button(frc,text="0",bg="grey",command=lambda x=i:self.writeFloatHandler(x))
            register.grid(row=i, column=1,ipadx=1, ipady=1, sticky=NSEW)
            self.FloatsList.append(register)
        canvas.create_window((0,0), window=frc, anchor=NW)
        frc.update_idletasks()
        bbox = canvas.bbox(ALL)
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/2) * 2), int((h/self.Floats) * 18)
        canvas.configure(scrollregion=bbox, width=dw, height=dh)
        fr.pack(fill=BOTH,side=LEFT, padx=10,pady=10)
    
    def readFloats(self,Floats):
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            regs = c.read_holding_registers(0, Floats*2)
            if regs:
                regs= word_list_to_long(regs, big_endian=False)
                for i in range(Floats):
                    value= decode_ieee(regs[i])
                    self.FloatsList[i]["text"]=str(value)
                return regs
            else:
                logging.info("unable to read registers")
                return -1
            
    def writeFloatHandler(self,regNr):
        reg_value=askfloat("Input","Input the float value:")
        logging.info(str(regNr) + " : " + str(reg_value))
        s4 = threading.Thread(target=self.writeFloats,args=(regNr,reg_value,), daemon=True)
        s4.start()
                
    def writeFloats(self, regNr, reg_value):
        
        valuelist=long_list_to_word([encode_ieee(reg_value)],big_endian=False)
        SERVER_HOST = self.ServerConfig["Host"].get()
        SERVER_PORT = int(self.ServerConfig["Port"].get())
        c = ModbusClient()
        #c.debug(True)
        c.host=SERVER_HOST
        c.port=SERVER_PORT
        if not c.is_open:
            if not c.open():
                logging.info("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
        if c.is_open:
            is_ok=c.write_single_register(2*regNr, valuelist[0])
            is_ok=c.write_single_register(2*regNr+1, valuelist[1])
            if is_ok:
                logging.info("register #" + str(2*regNr) + " & " + str(2*regNr+1) + ": write success : " + str(reg_value))
            else:
                logging.info("register #" + str(2*regNr) + " & " + str(2*regNr+1) + ": unable to write " )
        

app = TestMODBUSTCP()
