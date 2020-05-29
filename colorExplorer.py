# -*- coding: utf-8 -*-
"""
Created on Wed May  6 09:25:55 2020
"""

"""
TODO (anyone):
    
- fix error message in console (can't invoke "destroy")
- protect against problematic functions (div by 0, ...)
- fix flickering
- make it so the default function (i.e. the one returned in func(...)) is shown in the entry when starting
- save/open that stores functions and parameters
- improve looks (if possible without using ttk)
- remove the 3 global functions (sliderUpdate, ...) and replace them in the main class
- put the sliders/buttons in a loop to make the code more readable

TODO (Corentin):
- make image independant of sizex sizey
- add submenus for color modes
    - HSV: modify S/V, scale
    - RGB: scale
    - BW: threshold
- write "help & tips"
- do something more clever from hole1 and hole2
- normalization option

"""

# list of available functions:
# https://numpy.org/doc/stable/reference/ufuncs.html#available-ufuncs
# sin cos exp fabs bitwise_or/and/xor rint

from tkinter import *
from PIL import  Image, ImageTk
import numpy as np
from random import randrange,random
from scipy.ndimage.filters import gaussian_filter
import tkinter as tk
import colorsys
import matplotlib
from time import sleep

hole1 = (0.5,0.5)
hole2 = (-0.1,-0.2)


def func(xx,yy, p1, p2, offx, offy, f=""):
    scale = 256*256*256/1000
    
    
    i = xx-offx
    j = yy-offy
    
    dh1 = i-hole1[0]
    dh1b = j-hole1[1]
    dh2 = i-hole2[0]
    dh2b = j-hole2[1]
    
    n,m = xx.shape
    nb,mb = yy.shape   
    
    
    if f != "":
        return eval(f)

    return 255*np.sin((i+j)*p1/20+np.cos((i-j)*p2/20)*5) #wavies
    #return scale*np.sin(dh1*dh1b)**2
    return 255*255*np.deg2rad(i*j**2)
    return np.power(((dh1+dh1b)**2*10*p1).astype(int),((dh1-dh1b)**2*10*p2).astype(int))
    return np.bitwise_xor(((dh1+dh1b)**2*10*p1).astype(int),((dh1-dh1b)**2*10*p2).astype(int)) #kilts
    return np.bitwise_or(((dh1+dh1b)**2*10*p1).astype(int),((dh1-dh1b)**2*10*p2).astype(int)) #cardigan
    
    return np.bitwise_and((i*j*10*p1).astype(int),((dh1*dh1b)*10*p2).astype(int))
    
    return ( 255*np.sin(i*j*100/p1)*np.sin((i**3-j**2)*100/p2))
    
    return scale*( (1-np.exp(-(dh1**2+dh1b**2)/p1)) ) #other sparkling sun
    return 255*np.sin((i+j*1.8)**2*p1/50+np.cos((i-j*1.8)**2*p2/100)*5)
    return np.bitwise_and(((dh1+dh1b)**2*10*p1).astype(int),((dh1-dh1b)**2*10*p2).astype(int)) #red minecraft
    return 10000*np.cos( ((i+j)**2)*100/p1 )*np.sin(((i-j)**2)*100/p1) #quadrillage
    return p1*np.cos(np.sin(i*10/p2))+p1*np.cos(np.sin(j*10/p2)) #grandma's wallpaper
    return (i-j*p2/50)*(i+j*p2/50)*i*(j*p2/50)*np.exp(p1/100)/10 #starry star
    
    return (scale*np.sin( (i*22+np.cos(j*4)*5)/10)*(scale*np.sin( (i*22+np.cos(j*4)*5)/10) > 0)   *np.exp((-(((i+45/100)*3)**10))/1000)*np.exp((-(((j-23/100)*4)**10))/1000)  + scale*np.sin( ((-i+p1/100)*22+np.cos(j*4)*5)/10)*(scale*np.sin( ((-i+p1/100)*22+np.cos(j*4)*5)/10) > 0)*np.exp((-((((-i+p1/100)+45/100)*3)**10))/1000)*np.exp((-(((j-23/100)*4)**10))/1000))/(p2/1) 
    # above: heart
    return scale*np.sin(xx*10+np.cos(yy*10)*5) #waves
    return scale*(np.exp(-(i**2)*p1) + np.exp(-((i-1)**2)*p1) + np.exp(-(j**2)*p1) + np.exp(-((j-1)**2)*p1)) #squares
    return scale*np.log( p1*i**2 + p1*j**2 +1+p2 ) #dongdong's log
    return scale*(np.sin(dh1)+np.cos(dh1b)*p2)**p1 #surf, high beta
    return scale*np.exp(-p1*xx/(0.1+np.cos(yy*p2))) #fangs
    return scale*np.cos(p1*xx)*np.exp(np.sin(p2*xx*yy)) #lines with dots
    return (dh1*100*p1)**2 + (dh1b *100*p2)**2 #blobs
    return scale*np.exp(-dh1*dh1b*p1-dh1*dh1*p2) #cross
    return scale*(np.sin(dh1)+np.cos(dh1b)*p2)**p1 #eye?
    return (i**2 + j**2)*1000 #sparkling sun
    return ((np.sin((dh1+dh1b)**2*p1)*200+np.cos(dh1b*p2)*200)) #boutons disco
    return scale*i*p1/1000+p2*scale*np.cos(j) #wavy
    return scale*np.sin(p1*i**2 + j**2)*np.cos(p2*i*j) #damier
    return 1 #pear of illusions (see image)

def sliderUpdate(n):
    global app
    app.genImg()

def changeModulation():
    global app
    #app.randomModulation = not(app.randomModulation)
    app.genImg()
    
def updateImg():
    global app
    app.genImg()

class GUI(Frame):    
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        w,h = 750, 750
        fixedSize = False
        if fixedSize:
            master.minsize(width=w, height=h)
            master.maxsize(width=w, height=h)
        self.grid()
        self.sizex = 640 #Size of image on tk window
        self.sizey = 360 
        
        
        ## -- SLIDERFRAME -- ##
        
        self.sliderFrame = tk.Frame(self, bg="#efefef")
        
        self.sl1 = Scale(self.sliderFrame,from_=0, to=200, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl1.set(100)
        self.sl1.grid(row=1,column=0)
        Label(self.sliderFrame, text="α").grid(row=2,column=0, pady=10)
        
        self.sl2 = Scale(self.sliderFrame,from_=0, to=200, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl2.set(100)
        self.sl2.grid(row=1,column=1)
        Label(self.sliderFrame, text="β").grid(row=2,column=1)
        
        self.sl3 = Scale(self.sliderFrame,from_=100, to=-100, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl3.set(0)
        self.sl3.grid(row=1,column=2)
        Label(self.sliderFrame, text="off_x").grid(row=2,column=2)
        
        self.sl4 = Scale(self.sliderFrame,from_=100, to=-100, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl4.set(0)
        self.sl4.grid(row=1,column=3)
        Label(self.sliderFrame, text="off_y").grid(row=2,column=3)
        

        self.sl5 = Scale(self.sliderFrame,from_=500, to=0, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl5.set(0)
        self.sl5.grid(row=1,column=4)
        Label(self.sliderFrame, text="σ").grid(row=2,column=4)
        
        self.sl6 = Scale(self.sliderFrame,from_=100, to=1, orient=VERTICAL, command=sliderUpdate, length=200)
        self.sl6.set(30)
        self.sl6.grid(row=1,column=5)
        Label(self.sliderFrame, text="res").grid(row=2,column=5)
        
        self.sliderFrame.grid(row=1,column=1,padx=20,pady=20)
        
        
        ## -- CHECKFRAME -- ##
        
        self.checkFrame = tk.Frame(self, bg="#efefef")
                                   
        self.randomModulation = IntVar(value=0)
        self.check1 = Checkbutton(self.checkFrame, text="Random Modulation",var=self.randomModulation, command=changeModulation)
        self.check1.grid(row=0,column=1,columnspan=3)
        
        self.colorMode = StringVar(value="RGB")
        self.rad1 = Radiobutton(self.checkFrame, variable=self.colorMode, text="RGB", value="RGB", command=updateImg)
        self.rad1.grid(row=1,column=1,sticky="W")
        
        self.rad2 = Radiobutton(self.checkFrame, variable=self.colorMode, text="BW", value="BW", command=updateImg)
        self.rad2.grid(row=1,column=2,sticky="W")
        
        self.rad3 = Radiobutton(self.checkFrame, variable=self.colorMode, text="HSV", value="HSV", command=updateImg)
        self.rad3.grid(row=1,column=3,sticky="W")
        
        
        
        
        self.subMenu = tk.Frame(self.checkFrame, bg="#efefef")
        self.subMenuTitle = Label(self.subMenu,text="color menu here") #TODO: delete this
        self.subMenuTitle.grid(row=1,column=1)
        self.subMenu.grid(row=3,column=1,padx=20,pady=20, columnspan=3)               
        
        self.play = Button(self, text='Play', command=self.play)
        self.play.grid(row=5,column=1)
        
        self.checkFrame.grid(row=2,column=1,padx=20,pady=20)
        
        ## -- FORMULAFRAME -- ##
        
        self.formulaFrame = tk.Frame(self, bg="#efefef")
        self.formula = StringVar(value = "")
        self.activeFunction = ""
        
        self.bfi = Button(self.formulaFrame, text='i', command= lambda: self.addFormula("i"))
        self.bfi.grid(row=1, column = 1)
        
        self.bfj = Button(self.formulaFrame, text='j', command= lambda: self.addFormula("j"))
        self.bfj.grid(row=1, column = 2)
        
        self.bf1 = Button(self.formulaFrame, text='exp', command= lambda: self.addFormula("exp"))
        self.bf1.grid(row=1, column = 4)
        
        self.bf2 = Button(self.formulaFrame, text='cos', command= lambda: self.addFormula("cos"))
        self.bf2.grid(row=1, column = 5)
        
        self.bf3 = Button(self.formulaFrame, text='sin', command= lambda: self.addFormula("sin"))
        self.bf3.grid(row=1, column = 6)
        
        self.formulaEntry = Entry(self.formulaFrame, textvariable=self.formula, width=60)
        self.formulaEntry.grid(row=2, column = 1,columnspan=5)
        
        self.bApply = Button(self.formulaFrame, text='Apply', command=self.applyFunction)
        self.bApply.grid(row=2, column = 6)
        
        self.bClear = Button(self.formulaFrame, text='Clear', command=self.clearFunction)
        self.bClear.grid(row=2, column = 7)
        self.bSave = Button(self.formulaFrame, text='Save', command=self.saveImg)
        self.bSave.grid(row=3, column = 1)
        
        self.formulaFrame.grid(row=2,column=2)
        
        
        ## -- PRESETFRAME -- ##
        
        self.presetFrame = tk.Frame(self, bg="#efefef")
        self.bPreset1 = Button(self.presetFrame, text='Preset 1', command= lambda: self.preset(0))
        self.bPreset1.grid(row=1, column = 1, pady=15)
        self.bPreset2 = Button(self.presetFrame, text='Preset 2', command= lambda: self.preset(1))
        self.bPreset2.grid(row=2, column = 1, pady=15)
        self.bPreset3 = Button(self.presetFrame, text='Preset 3', command= lambda: self.preset(2))
        self.bPreset3.grid(row=3, column = 1, pady=15)
        
        self.presetFrame.grid(row=1,column=3)
        
        self.presetFrame = tk.Frame(self, bg="#efefef")
        
        self.genImg()
        
        
    def genImg(self):

        fact1 = self.sl1.get()
        fact2 = self.sl2.get()
        
        resx = self.sl6.get()*1600//100
        resy = self.sl6.get()*900//100
        offx = 640*(self.sl3.get())/10000 
        offy = 360*(self.sl4.get())/10000
        
        minx = (-640/2)/100
        maxx = (+640/2)/100
        miny = (-360/2)/100
        maxy = (+360/2)/100
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
            
            scale = 256*256*256
            
            type0 = "uint8"
            array = np.zeros((3,resx,resy),type0)
            array[0,:,:] = res % scale
            array[1,:,:] = np.full((res.shape[0],res.shape[1]), 102, type0)
            array[2,:,:] = np.full((res.shape[0],res.shape[1]), 230, type0)
        
        elif self.colorMode.get()=="RGB":
            array = np.zeros((3,resx,resy),'uint8')
            array[0,:,:] = res %256
            array[1,:,:] = (res/256) %256
            array[2,:,:] = (res/(256*256)) %256
            
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
            img0 = Image.fromarray(array, 'HSV')
            
        elif self.colorMode.get()=="RGB":
            array = np.ascontiguousarray(array.transpose(2,1,0))
            img0 = Image.fromarray(array, 'RGB')
        else:
            img0 = Image.fromarray(array.transpose())
        #img0 = Image.fromarray(array)
        self.fullImage = img0 #saving full res picture to output it
        
        ANTIALIAS = False
        if ANTIALIAS:
            img0 = img0.resize((self.sizex, self.sizey), Image.ANTIALIAS)
        else:
            img0 = img0.resize((self.sizex, self.sizey))
        
        img = ImageTk.PhotoImage(img0)
        self.image = img
        self.label = Label(self,image=self.image)
        self.label.grid(row=1,column=2,pady=10,padx=10)
        

    def play(self):
        if self.sl5.get() > 0:
            print("Sigma not zero, cannot play in reasonable time")
            return
        for i in range(25):
            self.after(150*i, self.genImg)
        
    def addFormula(self, string):
        txt = self.formula.get()
        pos = self.formulaEntry.index(INSERT)
        if string in ["exp","cos","sin"]:
            txt = txt[:pos] + "np."+string+"()" + txt[pos:]
        if string in ["i","j"]:
            txt += string
        self.formula.set( txt )
        print(self.formula.get())
        
    def applyFunction(self):
        self.activeFunction = self.formula.get()
        self.genImg()

    def clearFunction(self):
        self.formula.set("")
        self.activeFunction = ""
        self.genImg()
        
    def saveImg(self):
        img = ImageTk.PhotoImage(self.fullImage)
        img._PhotoImage__photo.write("Images/out.png")
    
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
  

root = Tk()
app = GUI(master=root)
#s = Style() #style with ttk
#s.theme_use('default')
# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
app.mainloop()

root.destroy()