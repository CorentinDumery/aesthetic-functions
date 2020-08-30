# -*- coding: utf-8 -*-
"""
Created on Wed May  6 09:25:55 2020
"""

"""
TODO (anyone):
- replace Entry with Text, and check compatibility with load/save
- prevent formulas with potentially harmful commands ("exec", "import", ...)
- add parameter t, and option to record video with t going from 0 to 100
- automatically replace ** with pow during evaluation
- add rotation slider that replaces i with t*i+(1-t)*j, etc
- protect against problematic functions (div by 0, ...)
- improve formula buttons, make the writing "|" change with button call
- improve saving window
    * check file name doesn't already exist before saving (image / parameters)
- improve looks (if possible without using ttk)
- put the sliders/buttons in a loop to make the code more readable
- add label that shows maximum/minimum reached by current formula on frame
- if the input function is constant, it should still be shown
- make color mode menus of a fixed size (so that the window doesn't change size)
- replace alpha and beta with p1 and p2 upon saving parameters
- add "open & multiply" button to easily combine formulas
TODO (Corentin):
- make image independant of sizex sizey
- do something clever from hole1 and hole2
- normalization option
"""

# list of available functions:
# https://numpy.org/doc/stable/reference/ufuncs.html#available-ufuncs
# sin cos exp fabs bitwise_or/and/xor rint

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, END
from PIL import Image, ImageTk
import numpy as np #needed for compatibility with formulas with np.
from numpy import * #needed for simple formula interpretation
from random import randrange,random
from scipy.ndimage.filters import gaussian_filter
import colorsys
import matplotlib
from time import sleep


mainColor = "#ccebe4"
secondaryColor = "#daede9"
hole1 = (0.5,0.5)
hole2 = (-0.1,-0.2)


def func(xx,yy, p1, p2, offx, offy, f=""):
    i = xx-offx
    j = yy-offy

    #some constants, needed for compatibility with old formulas:
    scale = 256*256*256/1000
    dh1 = i-hole1[0]
    dh1b = j-hole1[1]
    dh2 = i-hole2[0]
    dh2b = j-hole2[1]

    n,m = xx.shape
    nb,mb = yy.shape

    f = f.replace("α",str(p1))
    f = f.replace("β",str(p2))
    f = f.replace("alpha",str(p1))
    f = f.replace("beta",str(p2))
    return eval(f)

class GUI():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('ColorExplorer')
        self.root.grid()
        self.root.configure(background=mainColor)
        self.root.sizex = 960  #Size of image on tk window
        self.root.sizey = 540

        ## -- SLIDERFRAME -- ##

        self.sliderFrame = tk.Frame(self.root, bg= secondaryColor, pady=10)

        self.sl1 = tk.Scale(self.sliderFrame,from_=0, to=200, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl1.set(100)
        self.sl1.grid(row=1,column=0)
        tk.Label(self.sliderFrame, text="α",padx=5, pady=5, bg= secondaryColor).grid(row=0,column=0,sticky="E")

        self.sl2 = tk.Scale(self.sliderFrame,from_=0, to=200, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl2.set(100)
        self.sl2.grid(row=1,column=1)
        tk.Label(self.sliderFrame, text="β",padx=5, bg= secondaryColor).grid(row=0,column=1,sticky="E")

        self.sl3 = tk.Scale(self.sliderFrame,from_=100, to=-100, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl3.set(0)
        self.sl3.grid(row=1,column=2)
        tk.Label(self.sliderFrame, text="off_x", bg= secondaryColor).grid(row=0,column=2,sticky="E")

        self.sl4 = tk.Scale(self.sliderFrame,from_=100, to=-100, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl4.set(0)
        self.sl4.grid(row=1,column=3)
        tk.Label(self.sliderFrame, text="off_y", bg= secondaryColor).grid(row=0,column=3,sticky="E")


        self.sl5 = tk.Scale(self.sliderFrame,from_=500, to=0, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl5.set(0)
        self.sl5.grid(row=1,column=4)
        tk.Label(self.sliderFrame, text="σ",padx=5, bg= secondaryColor).grid(row=0,column=4,sticky="E")

        self.sl6 = tk.Scale(self.sliderFrame,from_=100, to=1, orient=tk.VERTICAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl6.set(30)
        self.sl6.grid(row=1,column=5)
        tk.Label(self.sliderFrame, text="res", bg= secondaryColor).grid(row=0,column=5,sticky="E")

        self.sliderFrame.grid(row=1,column=1)


        ## -- CHECKFRAME -- ##

        self.checkFrame = tk.Frame(self.root, bg=secondaryColor)

        self.randomModulation = tk.IntVar(value=0)
        self.check1 = tk.Checkbutton(self.checkFrame, text="Random Modulation",var=self.randomModulation, bg=secondaryColor, command=self.genImg)
        self.check1.grid(row=0,column=1,columnspan=3)

        self.colorMode = tk.StringVar(value="RGB")
        self.rad1 = tk.Radiobutton(self.checkFrame, variable=self.colorMode, text="RGB", value="RGB", bg=secondaryColor, command=self.changeColorMode)
        self.rad1.grid(row=1,column=1,sticky="W")

        self.rad2 = tk.Radiobutton(self.checkFrame, variable=self.colorMode, text="BW", value="BW", bg=secondaryColor, command=self.changeColorMode)
        self.rad2.grid(row=1,column=2,sticky="W")

        self.rad3 = tk.Radiobutton(self.checkFrame, variable=self.colorMode, text="HSV", value="HSV", bg=secondaryColor, command=self.changeColorMode)
        self.rad3.grid(row=1,column=3,sticky="W")

        self.RGBModeMenu = tk.Frame(self.checkFrame, bg=secondaryColor)
        self.RGBModeMenu.grid_columnconfigure(0, weight=1, uniform="RGB_uniform")
        self.RGBModeMenu.grid_columnconfigure(1, weight=1, uniform="RGB_uniform")
        self.sl_rgb_scale = tk.Scale(self.RGBModeMenu, from_=0, to=256, orient=tk.HORIZONTAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl_rgb_scale.set(256)
        self.sl_rgb_scale.grid(row=1, column=0, columnspan=2)
        self.RGBModeMenu.grid(row=2, column=1, columnspan=3) #RGB menu used as default

        self.HSVModeMenu = tk.Frame(self.checkFrame, bg=secondaryColor)
        self.HSVModeMenu.grid_columnconfigure(0, weight=1, uniform="HSV_uniform")
        self.HSVModeMenu.grid_columnconfigure(1, weight=1, uniform="HSV_uniform")
        self.sl_s_value = tk.Scale(self.HSVModeMenu, from_=0, to=255, orient=tk.HORIZONTAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl_s_value.set(102)
        self.sl_s_value.grid(row=1, column=0, columnspan=2)
        self.sl_v_value = tk.Scale(self.HSVModeMenu, from_=0, to=255, orient=tk.HORIZONTAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl_v_value.set(230)
        self.sl_v_value.grid(row=2, column=0, columnspan=2)

        self.BWModeMenu = tk.Frame(self.checkFrame, bg=secondaryColor)
        self.BWModeMenu.grid_columnconfigure(0, weight=1, uniform="BW_uniform")
        self.BWModeMenu.grid_columnconfigure(1, weight=1, uniform="BW_uniform")
        self.sl_bw_scale = tk.Scale(self.BWModeMenu, from_=0, to=200, orient=tk.HORIZONTAL, command=self.genImg, length=200, bg= secondaryColor)
        self.sl_bw_scale.set(100)
        self.sl_bw_scale.grid(row=1, column=0, columnspan=2)

        #testLabel = tk.Label(HSVModeMenu, text="Test", bg=secondaryColor)
        #testLabel.grid(row=0, column=0)
        #testEntry = tk.Entry(HSVModeMenu) #, textvariable=self.formula, width=10);
        #testEntry.grid(row=0, column=1)

        self.checkFrame.grid(row=2, column=1, padx=20, pady=20)

        self.play = tk.Button(self.root, text='Play', bg=secondaryColor, command=self.play)
        self.play.grid(row=3,column=1)


        ## -- FORMULAFRAME -- ##

        self.formulaFrame = tk.Frame(self.root, bg=mainColor)
        self.activeFunction = f"alpha*(i**2+j**2)" #default formula here
        self.formula = tk.StringVar(value=self.activeFunction)

        display_help_buttons = False
        if display_help_buttons:
            self.bfi = tk.Button(self.formulaFrame, text='i', bg=secondaryColor, command= lambda: self.addFormula("i"), padx=5)
            self.bfi.grid(row=1, column=1)

            self.bfj = tk.Button(self.formulaFrame, text='j', bg=secondaryColor, command= lambda: self.addFormula("j"), padx=5)
            self.bfj.grid(row=1, column=2)

            self.bfalpha = tk.Button(self.formulaFrame, text='α', bg=secondaryColor, command= lambda: self.addFormula("alpha"))
            self.bfalpha.grid(row=1, column = 3)

            self.bfbeta = tk.Button(self.formulaFrame, text='β', bg=secondaryColor, command= lambda: self.addFormula("beta"))
            self.bfbeta.grid(row=1, column = 4)

            self.bf1 = tk.Button(self.formulaFrame, text='exp', bg=secondaryColor, command= lambda: self.addFormula("exp"))
            self.bf1.grid(row=1, column = 5)

            self.bf2 = tk.Button(self.formulaFrame, text='cos', bg=secondaryColor, command= lambda: self.addFormula("cos"))
            self.bf2.grid(row=1, column = 6)

            self.bf3 = tk.Button(self.formulaFrame, text='sin', bg=secondaryColor, command= lambda: self.addFormula("sin"))
            self.bf3.grid(row=1, column = 7)

        self.formulaEntry = tk.Entry(self.formulaFrame, textvariable=self.formula, width=60)
        self.formulaEntry.grid(row=2, column=1, columnspan=5, pady =20)

        self.bApply = tk.Button(self.formulaFrame, text='Apply', bg=secondaryColor, command=self.applyFunction)
        self.bApply.grid(row=2, column=6)

        self.bClear = tk.Button(self.formulaFrame, text='Clear', bg=secondaryColor, command=self.clearFunction)
        self.bClear.grid(row=2, column=7)

        self.bSaveIm = tk.Button(self.formulaFrame, text='Save Image', bg=secondaryColor, command=self.saveImg)
        self.bSaveIm.grid(row=3, column=1)

        self.bSaveParams = tk.Button(self.formulaFrame, text='Save Parameters', bg=secondaryColor, command=self.saveParams)
        self.bSaveParams.grid(row=3, column=2)

        self.bLoadParams = tk.Button(self.formulaFrame, text='Load Parameters', bg=secondaryColor, command=self.loadParams)
        self.bLoadParams.grid(row=3, column=3)

        self.formulaFrame.grid(row=2,column=2)


        ## -- PRESETFRAME -- ##

        self.presetFrame = tk.Frame(self.root, bg=mainColor)
        self.bPreset1 = tk.Button(self.presetFrame, text='Preset 1', bg=secondaryColor, command= lambda: self.preset(0))
        self.bPreset1.grid(row=1, column = 1, padx=10, pady=15)
        self.bPreset2 = tk.Button(self.presetFrame, text='Preset 2', bg=secondaryColor, command= lambda: self.preset(1))
        self.bPreset2.grid(row=1, column = 2, padx=10, pady=15)
        self.bPreset3 = tk.Button(self.presetFrame, text='Preset 3', bg=secondaryColor, command= lambda: self.preset(2))
        self.bPreset3.grid(row=1, column = 3, padx=10, pady=15)

        self.presetFrame.grid(row=3,column=2)

        self.label = tk.Label(self.root)

        self.genImg()

        self.root.mainloop()

    def genImg(self, event = None):

        fact1 = self.sl1.get()
        fact2 = self.sl2.get()

        resx = self.sl6.get()*1600//100
        resy = self.sl6.get()*900//100
        offx = 640*2*(self.sl3.get())/10000
        offy = 360*2*(self.sl4.get())/10000

        minx = (-640*2/2)/100
        maxx = (+640*2/2)/100
        miny = (-360*2/2)/100
        maxy = (+360*2/2)/100
        stepx = (maxx-minx)/resx
        stepy = (maxy-miny)/resy

        printInterval = False
        if printInterval:
            print("Interval x:",minx,maxx)
            print("Interval y:",miny,maxy)

        x = np.arange(minx, maxx, stepx)
        y = np.arange(miny, maxy, stepy)
        xx, yy = np.meshgrid(x, y, sparse=True)

        res = func(xx,yy,fact1,fact2,offx,offy,self.activeFunction)
        res = res.transpose()

        if res.shape[1] > resy: #fix potential floating error imprecision
            res = res[:,:-1]

        normalized = False
        if normalized:
            res = 256*res/np.max(res)

        if self.randomModulation.get():
            randMat = np.random.rand(res.shape[0],res.shape[1])
            res = res*randMat

        if self.colorMode.get()=="HSV":

            type0 = "uint8"
            array = np.zeros((3,resx,resy),type0)
            array[0,:,:] = res % (256*256*256)
            array[1,:,:] = np.full((res.shape[0],res.shape[1]), self.sl_s_value.get(), type0)
            array[2,:,:] = np.full((res.shape[0],res.shape[1]), self.sl_v_value.get(), type0)

        elif self.colorMode.get()=="RGB":
            scale = self.sl_rgb_scale.get()
            max_value = min(scale, 256)

            array = np.zeros((3,resx,resy),'uint8')
            array[0,:,:] = res % max_value
            array[1,:,:] = (res/max_value) %max_value
            array[2,:,:] = (res/(max_value*max_value)) %max_value

        else:
            array = res

        sigma = self.sl5.get()/100
        if sigma > 0:
            if array.ndim == 3:
                array[0,:,:] = gaussian_filter(array[0,:,:], sigma=sigma)
                array[1,:,:] = gaussian_filter(array[1,:,:], sigma=sigma)
                array[2,:,:] = gaussian_filter(array[2,:,:], sigma=sigma)
            else:
                array[:,:] = gaussian_filter(array[:,:], sigma=sigma)

        if self.colorMode.get()== "HSV":
            array = np.ascontiguousarray(array.transpose(2,1,0))
            if (array.shape[0]<self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array, 'HSV')

        elif self.colorMode.get()=="RGB":
            array = np.ascontiguousarray(array.transpose(2,1,0))

            if (array.shape[0]<self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)

            img0 = Image.fromarray(array, 'RGB')
        else: #mode == "BW"
            array *= float(self.sl_bw_scale.get()/100)
            if (array.shape[0]<self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array.transpose())
        #img0 = Image.fromarray(array)

        self.fullImage = img0 #saving full res picture to output it

        ANTIALIAS = False
        if ANTIALIAS:
            img0 = img0.resize((self.root.sizex, self.root.sizey), Image.ANTIALIAS)
        else:
            img0 = img0.resize((self.root.sizex, self.root.sizey))

        img = ImageTk.PhotoImage(img0)
        self.image = img
       # self.label = tk.Label(self.root,image=self.image)
        self.label.configure(image = self.image)
        self.label.grid(row=1,column=2,pady=10,padx=10)


    def changeColorMode(self):
        self.RGBModeMenu.grid_forget()
        self.HSVModeMenu.grid_forget()
        self.BWModeMenu.grid_forget()
        if self.colorMode.get()=="HSV":
            self.HSVModeMenu.grid(row=2, column=1, columnspan=3)
        if self.colorMode.get()=="RGB":
            self.RGBModeMenu.grid(row=2, column=1, columnspan=3)
        if self.colorMode.get()=="BW":
            self.BWModeMenu.grid(row=2, column=1, columnspan=3)
        self.genImg()

    def play(self): #TODO
        if self.sl5.get() > 0:
            print("Sigma not zero, cannot play in reasonable time")
            return
        self.root.after(100, self.genImg())

    def addFormula(self, string):
        txt = self.formula.get()
        pos = self.formulaEntry.index(tk.INSERT)
        if string in ["exp","cos","sin"]:
            txt = txt[:pos] + "np."+string+"()" + txt[pos:]
        if string in ["i","j","α","β"]:
            txt = txt[:pos]+ string + txt[pos:]
        self.formula.set( txt )
        print(self.formula.get())

    def applyFunction(self):
        self.activeFunction = self.formula.get()
        self.genImg()

    def clearFunction(self):
        self.activeFunction = ""
        self.formula.set(self.activeFunction)

    def saveImg(self):
        name = simpledialog.askstring("", "Name of this image?")
        if name: # not None
            self.fullImage.convert('RGB').save("Images/{}.png".format(name))
            messagebox.showinfo("", "{}.png saved!".format(name))
            self.saveParams(name)
        else:
            messagebox.showinfo("", "Saving cancelled!")

    def saveParams(self, name=""):
        if name == "":
            name = simpledialog.askstring("", "Name of this set of parameters?")
        file = open("Parameters/"+name+".txt","a")
        params = "formula "+ self.activeFunction + "\n"
        params += "alpha "+ str(self.sl1.get())+"\n"
        params += "beta "+ str(self.sl2.get())+"\n"
        params += "offx "+ str(self.sl3.get())+"\n"
        params += "offy "+ str(self.sl4.get())+"\n"
        params += "sigma "+ str(self.sl5.get())+"\n"
        params += "resolution "+ str(self.sl6.get())+"\n"
        params += "colorMode "+ self.colorMode.get() +"\n"
        params += "randomModulation "+ str(self.randomModulation.get())+"\n"
        params += "sValue "+ str(self.sl_s_value.get()) + "\n"
        params += "vValue "+ str(self.sl_v_value.get()) + "\n"
        params += "bwScale "+ str(self.sl_bw_scale.get()) + "\n"
        params += "rgbScale "+ str(self.sl_rgb_scale.get()) + "\n"
        file.write(params)
        file.close()
       # self.genImg()

    def loadParams(self):

        filepath = filedialog.askopenfilename(initialdir = "../colorExplorer/Parameters/",
                                 title = "Select parameters file",
                                 filetypes = (("txt files","*.txt"),("all files","*.*")))
        if filepath == ():
            return
        file = open(filepath,"r")
        line = "example"
        while (line != ""):
            line = file.readline()
            words = line.split()
            if len(words) <1:
                continue
            if words[0] =="formula":
                self.activeFunction = line[8:-1]
                self.formula.set(line[8:-1])
                self.formulaEntry.delete(0,END)
                self.formulaEntry.insert(0,line[8:-1])
            else :
                if len(words) != 2:
                    print("Warning : file misread, wrong number of values per line")

                tags = ["alpha", "beta", "offx", "offy", "sigma",
                        "resolution", "colorMode", "randomModulation", "sValue", "vValue",
                        "bwScale", "rgbScale"]
                widgets = [self.sl1, self.sl2, self.sl3, self.sl4, self.sl5,
                           self.sl6, self.colorMode, self.randomModulation, self.sl_s_value, self.sl_v_value,
                           self.sl_bw_scale, self.sl_rgb_scale]
                for i in range(len(tags)):
                    if words[0] == tags[i]:
                        widgets[i].set(words[1])
        file.close()
        self.changeColorMode()

    def preset(self, n):
        functions = []
        functions.append("p1*np.cos(np.sin(i*10/p2))+p1*np.cos(np.sin(j*10/p2))")
        functions.append("10000*np.cos( ((i+j)**2)*100/p1 )*np.sin(((i-j)**2)*100/p1)")
        functions.append("255*np.sin((i+j*1.8)**2*p1/50+np.cos((i-j*1.8)**2*p2/100)*5)")
        alpha = [110, 93, 19]
        beta = [5, 151, 8]
        offx = [0, 0, 0]
        offy = [0, 0, 0]
        sigma = [0, 0, 500]
        colorMode = ["HSV","BW","HSV"]
        randomMod = [False, False, False]

        self.formula.set( functions[n] )
        self.sl1.set(alpha[n])
        self.sl2.set(beta[n])
        self.sl3.set(offx[n])
        self.sl4.set(offy[n])
        self.sl5.set(sigma[n])
        self.colorMode.set(colorMode[n])
        self.randomModulation.set(randomMod[n])

        self.applyFunction()

app = GUI()
