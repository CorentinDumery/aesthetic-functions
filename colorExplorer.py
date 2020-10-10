# -*- coding: utf-8 -*-
"""
Created on Wed May 6 09:25:55 2020
"""

"""
TODO:
- make .json from the old .txt files
- expand frames to fit
- reset button
- Use global style variables (in progress)
- catch errors and show warning sign on interface
    - show them with https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/
- Add radial coordinates option
- Add BGR/RGB/GBR/... instead of RGB
- Add 4th color mode with different formulas for R G and B
- add option to keep/discard previous stuff upon loading parameters
- remove useless sliders and make sure loading still works
    - if there's an "alpha/beta" in a txt, it should create such sliders
- make ImageHolder class with everything related to the canvas (also, use actual Canvas ?)
- Change MouseMover to get x/y in picture coordinates, and show label with value under mouse
- prevent formulas with potentially harmful commands ("exec", "import", ...)
- add parameter t, and option to record video with t going from 0 to 100
- automatically replace ** with pow during evaluation
- add rotation slider that replaces i with t*i+(1-t)*j, etc
- protect against problematic functions (div by 0, ...)
- improve formula buttons, make the writing "|" change with button call
- improve looks (if possible without using ttk)
- put the sliders/buttons in a loop to make the code more readable
- add label that shows maximum/minimum reached by current formula on frame
- if the input function is constant, it should still be shown
- make color mode menus of a fixed size (so that the window doesn't change size)
- make image independant of sizex sizey
"""

# list of available functions:
# https://numpy.org/doc/stable/reference/ufuncs.html#available-ufuncs
# sin cos exp fabs bitwise_or/and/xor rint


from importlib import reload
from os import path
import json
import math
from time import sleep
import matplotlib
import colorsys
from scipy.ndimage.filters import gaussian_filter
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext, END
from PIL import Image, ImageTk
import numpy as np  # needed for compatibility with formulas with np.
from random import randrange, random
import userdef as user # user is the module used to load user definition
from time import time
mainColor = "#ccebe4"
secondaryColor = "#daede9"
mainColor = "#f1faee"
secondaryColor = "#e1eade"
thick_val = 0

frameStyle = {
    'bg': secondaryColor,
    'highlightthickness': thick_val,
    'padx': 5,
    'pady': 5,
    'bd': 10,
    'relief': tk.RIDGE
}

scaleStyle = {
    'bg': secondaryColor,
    'highlightthickness': thick_val
}


def setStyle(obj, bg="#000000", highlightthickness=0, padx=0, pady=0, bd=0, relief=tk.RIDGE):
    obj.configure(bg=bg)
    obj.configure(highlightthickness=highlightthickness)
    if obj.winfo_class() == 'Frame':
        obj.configure(padx=padx)
        obj.configure(pady=pady)
        obj.configure(bd=bd)
        obj.configure(relief=relief)
    if obj.winfo_class() == 'Scale':
        pass  # obj.configure(eee = "55")


class Slider(dict):
    '''Stores slider parameters'''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value


slider = Slider()


def func(xx, yy, offx, offy, f=""):
    '''Generic function that computes pixel values for canvas'''
    i = xx-offx
    j = yy-offy

    # some constants, needed for compatibility with old formulas:
    scale = 256*256*256/1000
    hole1 = (0.5, 0.5)
    hole2 = (-0.1, -0.2)
    dh1 = i-hole1[0]
    dh1b = j-hole1[1]
    dh2 = i-hole2[0]
    dh2b = j-hole2[1]

    n, m = xx.shape
    nb, mb = yy.shape

    return eval(f)


def updateUserDefLib(text, sliders):
    '''Writes text in userdef.py and reloads the module'''
    libfile = open("userdef.py", "w")
    libfile.write(text)
    libfile.close()
    reload(user)


class GUI():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('ColorExplorer')
        self.root.grid()
        self.root.configure(background=mainColor)
        self.root.sizex = 960  # Size of image on tk window
        self.root.sizey = 540

        self.offx = 0  # TODO: put these in some ImageHolder class
        self.offy = 0
        self.zoom = tk.DoubleVar()
        self.zoom.set(1)
        self.minx = self.zoom.get()*(-640)/100
        self.maxx = self.zoom.get()*(+640)/100
        self.miny = self.zoom.get()*(-360)/100
        self.maxy = self.zoom.get()*(+360)/100
        self.computationTime = tk.DoubleVar()
        self.fps = tk.IntVar()

        ## -- SLIDERFRAME -- ##

        self.sliderFrame = tk.Frame(self.root)
        # use dictionaries as keyword arguments
        setStyle(self.sliderFrame, **frameStyle)

        self.sliders = {}  # self defined sliders TODO rename ?

        self.sl_sigma = tk.Scale(self.sliderFrame, from_=500, to=0, orient=tk.VERTICAL,
                                 command=self.genImg, length=200, bg=secondaryColor, highlightthickness=thick_val)
        self.sl_sigma.set(0)
        self.sl_sigma.grid(row=1, column=2)
        tk.Label(self.sliderFrame, text="σ", padx=5,
                 bg=secondaryColor).grid(row=0, column=2, sticky="E")

        self.sl_res = tk.Scale(self.sliderFrame, from_=100, to=1, orient=tk.VERTICAL, command=self.genImg,
                               length=200)
        setStyle(self.sl_res, **scaleStyle)
        self.sl_res.set(30)
        self.sl_res.grid(row=1, column=3)
        tk.Label(self.sliderFrame, text="res", bg=secondaryColor, highlightthickness=thick_val).grid(
            row=0, column=3, sticky="E")

        self.saveWithMaxResolution = tk.BooleanVar()
        self.saveWithMaxResolution.set(True)
        self.checkMaxResolution = tk.Checkbutton(self.sliderFrame, text="Save with max resolution",
                                     var=self.saveWithMaxResolution, bg=secondaryColor, highlightthickness=thick_val)
        self.checkMaxResolution.grid(row=2, column=1, columnspan=3)

        self.addSliderFrame = tk.Frame(
            self.sliderFrame, bg=secondaryColor, highlightthickness=thick_val)
        self.newSliderName = tk.StringVar(value="my_param")
        self.newSliderEntry = tk.Entry(
            self.addSliderFrame, textvariable=self.newSliderName)
        self.newSliderEntry.pack(side=tk.LEFT)
        self.newSliderButton = tk.Button(
            self.addSliderFrame, text="+", command=self.newSlider)
        self.newSliderButton.pack(side=tk.RIGHT)
        self.addSliderFrame.grid(row=3, column=0, columnspan=4)

        self.userSliderFrame = tk.Frame(
            self.sliderFrame, bg=secondaryColor, highlightthickness=thick_val)
        self.userSliderFrame.grid(row=4, column=0, columnspan=4)

        self.sliderFrame.grid(row=1, column=1)

        ## -- CHECKFRAME -- ##
        self.checkFrame = tk.Frame(self.root)
        setStyle(self.checkFrame, **frameStyle)

        self.randomModulation = tk.IntVar(value=0)
        self.check1 = tk.Checkbutton(self.checkFrame, text="Random Modulation",
                                     var=self.randomModulation, bg=secondaryColor, highlightthickness=thick_val, command=self.genImg)
        self.check1.grid(row=0, column=1, columnspan=3)

        self.colorMode = tk.StringVar(value="RGB")
        self.rad1 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="RGB", value="RGB", bg=secondaryColor, highlightthickness=thick_val, command=self.changeColorMode)
        self.rad1.grid(row=1, column=1, sticky="W")

        self.rad2 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="BW", value="BW", bg=secondaryColor, highlightthickness=thick_val, command=self.changeColorMode)
        self.rad2.grid(row=1, column=2, sticky="W")

        self.rad3 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="HSV", value="HSV", bg=secondaryColor, highlightthickness=thick_val, command=self.changeColorMode)
        self.rad3.grid(row=1, column=3, sticky="W")

        self.RGBModeMenu = tk.Frame(
            self.checkFrame, bg=secondaryColor, highlightthickness=thick_val)
        self.RGBModeMenu.grid_columnconfigure(
            0, weight=1, uniform="RGB_uniform")
        self.RGBModeMenu.grid_columnconfigure(
            1, weight=1, uniform="RGB_uniform")
        self.sl_rgb_scale = tk.Scale(self.RGBModeMenu, from_=0, to=256,
                                     orient=tk.HORIZONTAL, command=self.genImg, length=200)
        setStyle(self.sl_rgb_scale, **scaleStyle)
        self.sl_rgb_scale.set(256)
        self.sl_rgb_scale.grid(row=1, column=0, columnspan=2)
        # RGB menu used as default
        self.RGBModeMenu.grid(row=2, column=1, columnspan=3)

        self.HSVModeMenu = tk.Frame(
            self.checkFrame, bg=secondaryColor, highlightthickness=thick_val)
        self.HSVModeMenu.grid_columnconfigure(
            0, weight=1, uniform="HSV_uniform")
        self.HSVModeMenu.grid_columnconfigure(
            1, weight=1, uniform="HSV_uniform")
        self.sl_s_value = tk.Scale(self.HSVModeMenu, from_=0, to=255,
                                   orient=tk.HORIZONTAL, command=self.genImg, length=200)
        setStyle(self.sl_s_value, **scaleStyle)
        self.sl_s_value.set(102)
        self.sl_s_value.grid(row=1, column=0, columnspan=2)

        self.sl_v_value = tk.Scale(self.HSVModeMenu, from_=0, to=255,
                                   orient=tk.HORIZONTAL, command=self.genImg, length=200)
        setStyle(self.sl_v_value, **scaleStyle)
        self.sl_v_value.set(230)
        self.sl_v_value.grid(row=2, column=0, columnspan=2)

        self.BWModeMenu = tk.Frame(
            self.checkFrame, bg=secondaryColor, highlightthickness=thick_val)
        self.BWModeMenu.grid_columnconfigure(0, weight=1, uniform="BW_uniform")
        self.BWModeMenu.grid_columnconfigure(1, weight=1, uniform="BW_uniform")
        self.sl_bw_scale = tk.Scale(self.BWModeMenu, from_=0, to=200,
                                    orient=tk.HORIZONTAL, command=self.genImg, length=200)
        setStyle(self.sl_bw_scale, **scaleStyle)
        self.sl_bw_scale.set(100)
        self.sl_bw_scale.grid(row=1, column=0, columnspan=2)

        self.checkFrame.grid(row=2, column=1, padx=20, pady=20)

        # TODO : Add button that records video using variable "Time"
        #self.playButton = tk.Button(self.root, text='Play',
        #                            bg=secondaryColor, highlightthickness=thick_val, command=self.playAnimation)
        #self.playButton.grid(row=3, column=1)

        ## -- FORMULAFRAME -- ##

        self.formulaFrame = tk.Frame(self.root)
        setStyle(self.formulaFrame, **frameStyle)

        self.activeFunction = f"255*(i**2+j**2)"  # default formula here
        self.formula = tk.StringVar(value=self.activeFunction)

        display_help_buttons = False  # TODO replace with something more appropriate
        if display_help_buttons:
            self.bfi = tk.Button(self.formulaFrame, text='i', bg=secondaryColor, highlightthickness=thick_val,
                                 command=lambda: self.addFormula("i"), padx=5)
            self.bfi.grid(row=1, column=1)

            self.bfj = tk.Button(self.formulaFrame, text='j', bg=secondaryColor, highlightthickness=thick_val,
                                 command=lambda: self.addFormula("j"), padx=5)
            self.bfj.grid(row=1, column=2)

            self.bfalpha = tk.Button(
                self.formulaFrame, text='α', bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.addFormula("alpha"))
            self.bfalpha.grid(row=1, column=3)

            self.bfbeta = tk.Button(
                self.formulaFrame, text='β', bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.addFormula("beta"))
            self.bfbeta.grid(row=1, column=4)

            self.bf1 = tk.Button(self.formulaFrame, text='exp',
                                 bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.addFormula("exp"))
            self.bf1.grid(row=1, column=5)

            self.bf2 = tk.Button(self.formulaFrame, text='cos',
                                 bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.addFormula("cos"))
            self.bf2.grid(row=1, column=6)

            self.bf3 = tk.Button(self.formulaFrame, text='sin',
                                 bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.addFormula("sin"))
            self.bf3.grid(row=1, column=7)

        self.userDefEntry = scrolledtext.ScrolledText(
            self.formulaFrame, width=100, height=10)
        self.userDefEntry.insert(
            END, "# Your definitions here.\n# They will be imported in the module 'user'.")
        self.userDefEntry.grid(row=1, column=1, columnspan=5, pady=20)

        self.formulaEntry = tk.Entry(
            self.formulaFrame, textvariable=self.formula, width=100)
        self.formulaEntry.grid(row=2, column=1, columnspan=5, pady=20)

        self.bApply = tk.Button(
            self.formulaFrame, text='Apply', bg=secondaryColor, highlightthickness=thick_val, command=self.applyFunction)
        self.bApply.grid(row=2, column=6)

        self.bClear = tk.Button(
            self.formulaFrame, text='Clear', bg=secondaryColor, highlightthickness=thick_val, command=self.clearFunction)
        self.bClear.grid(row=2, column=7)

        self.bSaveIm = tk.Button(
            self.formulaFrame, text='Save Image', bg=secondaryColor, highlightthickness=thick_val, command=self.saveImg)
        self.bSaveIm.grid(row=3, column=1)

        self.bSaveParams = tk.Button(
            self.formulaFrame, text='Save Parameters', bg=secondaryColor, highlightthickness=thick_val, command=self.saveParams)
        self.bSaveParams.grid(row=3, column=2)

        self.bLoadParams = tk.Button(
            self.formulaFrame, text='Load Parameters', bg=secondaryColor, highlightthickness=thick_val, command=self.loadParams)
        self.bLoadParams.grid(row=3, column=3)

        self.bAppendParams = tk.Button(
            self.formulaFrame, text='Append Parameters', bg=secondaryColor, highlightthickness=thick_val, command=self.appendParams)
        self.bAppendParams.grid(row=3, column=4)

        self.formulaFrame.grid(row=2, column=2, rowspan =2)

        ## -- PRESETFRAME -- ##

        show_preset = False  # TODO : replace with something more appropriate
        if show_preset:
            self.presetFrame = tk.Frame(
                self.root, bg=mainColor, highlightthickness=thick_val)
            self.bPreset1 = tk.Button(
                self.presetFrame, text='Preset 1', bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.preset(0))
            self.bPreset1.grid(row=1, column=1, padx=10, pady=15)
            self.bPreset2 = tk.Button(
                self.presetFrame, text='Preset 2', bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.preset(1))
            self.bPreset2.grid(row=1, column=2, padx=10, pady=15)
            self.bPreset3 = tk.Button(
                self.presetFrame, text='Preset 3', bg=secondaryColor, highlightthickness=thick_val, command=lambda: self.preset(2))
            self.bPreset3.grid(row=1, column=3, padx=10, pady=15)

            self.presetFrame.grid(row=3, column=2)

        ## -- INFOFRAME -- ##

        # TODO : add offx, offy, min value, i/j intervals, computation time

        self.infoFrame = tk.Frame(
            self.root)
        setStyle(self.infoFrame, **frameStyle)

        self.maxLabelText = tk.StringVar(value="Max value: X")
        self.maxLabel = tk.Label(
            self.infoFrame, textvariable=self.maxLabelText, bg=secondaryColor, highlightthickness=thick_val)
        self.maxLabel.grid(row=2, column=0, sticky="E")
        
        self.zoomLabelText = tk.StringVar(value="Zoom value:")
        self.zoomLabel = tk.Label(
            self.infoFrame, textvariable=self.zoomLabelText, bg=secondaryColor, highlightthickness=thick_val)
        self.zoomLabel.grid(row=3, column=0, sticky="W")
        self.zoomLabelValue = tk.Label(
            self.infoFrame, textvariable=self.zoom, width=4, anchor=tk.W, bg=secondaryColor, highlightthickness=thick_val)
        self.zoomLabelValue.grid(row=3, column=1, sticky="W")

        self.timeLabelText = tk.StringVar(value="Computation time:")
        self.timeLabel = tk.Label(
            self.infoFrame, textvariable=self.timeLabelText, bg=secondaryColor, highlightthickness=thick_val)
        self.timeLabel.grid(row=4, column=0, sticky="W")
        self.timeLabelValue = tk.Label(
            self.infoFrame, textvariable=self.computationTime, width=4, anchor=tk.W, bg=secondaryColor, highlightthickness=thick_val)
        self.timeLabelValue.grid(row=4, column=1, sticky="W")

        self.fpsLabelText = tk.StringVar(value="FPS:")
        self.fpsLabel = tk.Label(
            self.infoFrame, textvariable=self.fpsLabelText, bg=secondaryColor, highlightthickness=thick_val)
        self.fpsLabel.grid(row=5, column=0, sticky="W")
        self.fpsLabelValue = tk.Label(
            self.infoFrame, textvariable=self.fps, width=4, anchor=tk.W, bg=secondaryColor, highlightthickness=thick_val)
        self.fpsLabelValue.grid(row=5, column=1, sticky="W")

        self.infoFrame.grid(row=3, column=1)

        self.label = tk.Label(self.root)

        self.genImg()

        class MouseMover():  # https://gist.github.com/fnielsen/3810848

            def __init__(self, window):
                self.lastX = 0
                self.lastY = 0
                self.window = window

            def mouseWheel(self, event):
                self.window.zoom.set( self.window.zoom.get() * (1-event.delta/1200))
                self.window.genImg()

            def b3(self, event):
                print("b3 pressed")  # TODO: do something cool?

            def b4(self, event):  # mouse wheel up X11
                self.window.zoom.set( self.window.zoom.get() *  0.9 )
                self.window.genImg()

            def b5(self, event):  # mouse wheel down X11
                self.window.zoom.set( self.window.zoom.get() * 1.1 )
                self.window.genImg()

            def selectB1(self, event):
                self.lastX = event.x
                self.lastY = event.y

            def dragB1(self, event):

                sx = self.window.root.sizex
                sy = self.window.root.sizey

                self.window.offx += (event.x - self.lastX) * \
                    (self.window.maxx-self.window.minx)/sx
                self.window.offy += (event.y - self.lastY) * \
                    (self.window.maxy-self.window.miny)/sy
                self.lastX = event.x
                self.lastY = event.y
                self.window.genImg()

        # Get an instance of the MouseMover object
        mouse_mover = MouseMover(self)
        self.label.bind("<Button-1>", mouse_mover.selectB1)
        self.label.bind("<MouseWheel>", mouse_mover.mouseWheel)
        self.label.bind("<Button-3>", mouse_mover.b3)
        self.label.bind("<Button-4>", mouse_mover.b4)  # mouse wheel up X11
        self.label.bind("<Button-5>", mouse_mover.b5)  # mouse wheel down X11
        self.label.bind("<B1-Motion>", mouse_mover.dragB1)
        self.root.mainloop()

    def genImg(self, event=None):
        
        time_beginning = time()
        resx = self.sl_res.get()*1600//100
        resy = self.sl_res.get()*900//100

        self.minx = self.zoom.get()*(-640*2/2)/100
        self.maxx = self.zoom.get()*(+640*2/2)/100
        self.miny = self.zoom.get()*(-360*2/2)/100
        self.maxy = self.zoom.get()*(+360*2/2)/100
        stepx = (self.maxx-self.minx)/resx
        stepy = (self.maxy-self.miny)/resy

        printInterval = False
        if printInterval:
            print("Interval x:", self.minx, self.maxx)
            print("Interval y:", self.miny, self.maxy)

        x = np.arange(self.minx, self.maxx, stepx)
        y = np.arange(self.miny, self.maxy, stepy)
        xx, yy = np.meshgrid(x, y, sparse=True)

        self.updateSliderParameters()
        res = func(xx, yy, self.offx, self.offy, self.activeFunction)
        res = res.transpose()

        res = res[:resx, :resy]
        if res.shape[1] > resy:  # fix potential floating error imprecision
            res = res[:, :-1]

        normalized = False
        if normalized:
            res = 256*res/np.max(res)

        if self.randomModulation.get():
            randMat = np.random.rand(res.shape[0], res.shape[1])
            res = res*randMat

        if self.colorMode.get() == "HSV":

            type0 = "uint8"
            array = np.zeros((3, resx, resy), type0)
            array[0, :, :] = res % (256*256*256)
            array[1, :, :] = np.full(
                (res.shape[0], res.shape[1]), self.sl_s_value.get(), type0)
            array[2, :, :] = np.full(
                (res.shape[0], res.shape[1]), self.sl_v_value.get(), type0)

        elif self.colorMode.get() == "RGB":
            scale = self.sl_rgb_scale.get()
            max_value = min(scale, 256)

            array = np.zeros((3, resx, resy), 'uint8')
            array[0, :, :] = res % max_value
            array[1, :, :] = (res/max_value) % max_value
            array[2, :, :] = (res/(max_value*max_value)) % max_value

        else:
            array = res

        sigma = self.sl_sigma.get()/100
        if sigma > 0:
            if array.ndim == 3:
                array[0, :, :] = gaussian_filter(array[0, :, :], sigma=sigma)
                array[1, :, :] = gaussian_filter(array[1, :, :], sigma=sigma)
                array[2, :, :] = gaussian_filter(array[2, :, :], sigma=sigma)
            else:
                array[:, :] = gaussian_filter(array[:, :], sigma=sigma)

        if self.colorMode.get() == "HSV":
            array = np.ascontiguousarray(array.transpose(2, 1, 0))
            if (array.shape[0] < self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array, 'HSV')

        elif self.colorMode.get() == "RGB":
            array = np.ascontiguousarray(array.transpose(2, 1, 0))

            if (array.shape[0] < self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)

            img0 = Image.fromarray(array, 'RGB')
        else:  # mode == "BW"
            array *= float(self.sl_bw_scale.get()/100)
            if (array.shape[0] < self.root.sizey):
                stepx = self.root.sizex//array.shape[1]
                stepy = self.root.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array.transpose())
        #img0 = Image.fromarray(array)

        if not(math.isnan(res.max())):
            self.maxLabelText.set(
                "Max value: " + f"{res.max():.2f}"+"\nMax (hex):"+hex(int(res.max())))

        self.fullImage = img0  # saving full res picture to output it

        ANTIALIAS = False
        if ANTIALIAS:
            img0 = img0.resize(
                (self.root.sizex, self.root.sizey), Image.ANTIALIAS)
        else:
            img0 = img0.resize((self.root.sizex, self.root.sizey))

        img = ImageTk.PhotoImage(img0)
        self.image = img
       # self.label = tk.Label(self.root,image=self.image)
        self.label.configure(image=self.image)
        self.label.grid(row=1, column=2, pady=10, padx=10)
        self.computationTime.set(time() - time_beginning)
        self.fps.set(int(1/(time() - time_beginning)))

    def changeColorMode(self):
        self.RGBModeMenu.grid_forget()
        self.HSVModeMenu.grid_forget()
        self.BWModeMenu.grid_forget()
        if self.colorMode.get() == "HSV":
            self.HSVModeMenu.grid(row=2, column=1, columnspan=3)
        if self.colorMode.get() == "RGB":
            self.RGBModeMenu.grid(row=2, column=1, columnspan=3)
        if self.colorMode.get() == "BW":
            self.BWModeMenu.grid(row=2, column=1, columnspan=3)
        self.genImg()

    def playAnimation(self):  # TODO
        if self.sl_sigma.get() > 0:
            print("Sigma not zero, cannot play in reasonable time")
            return
        self.root.after(100, self.genImg())

    def addFormula(self, string):
        txt = self.formula.get()
        pos = self.formulaEntry.index(tk.INSERT)
        if string in ["exp", "cos", "sin"]:
            txt = txt[:pos] + "np."+string+"()" + txt[pos:]
        if string in ["i", "j", "α", "β"]:
            txt = txt[:pos] + string + txt[pos:]
        self.formula.set(txt)
        print(self.formula.get())

    def applyFunction(self):
        self.activeFunction = self.formula.get()
        updateUserDefLib(self.userDefEntry.get("1.0", END), self.sliders)
        self.genImg()

    def updateSliderParameters(self):
        for paramName in self.sliders:
            sl = self.sliders[paramName]
            # dynamically adjust slider attributes
            slider[paramName] = sl.get()

    def clearFunction(self):
        self.activeFunction = ""
        self.formula.set(self.activeFunction)

    def saveImg(self):
        name = simpledialog.askstring("", "Name of this image?")
        if name:  # not None
            if self.saveWithMaxResolution.get():
                old_res = self.sl_res.get()
                self.sl_res.set(100)
                self.genImg()
                self.fullImage.convert('RGB').save("Images/{}.png".format(name))
                self.sl_res.set(old_res)
                self.genImg()
            else:
                self.fullImage.convert('RGB').save("Images/{}.png".format(name))
            messagebox.showinfo("", "{}.png saved!".format(name))
            self.saveParams(name)
        else:
            messagebox.showinfo("", "Saving cancelled!")

    def saveParams(self, name=""):
        if name == "":
            name = simpledialog.askstring(
                "", "Name of this set of parameters?")

        while path.exists("Parameters/"+name+".json"):
            name = simpledialog.askstring(
                "", "Name already exists, please pick another one")

        saveToTxt = False #legacy
        if saveToTxt:
            file = open("Parameters/"+name+".txt", "a")
            params = "formula " + self.activeFunction + "\n"
            params += "alpha " + str(0)+"\n"
            params += "beta " + str(0)+"\n"
            params += "offx " + str(self.offx)+"\n"
            params += "offy " + str(self.offy)+"\n"
            params += "sigma " + str(self.sl_sigma.get())+"\n"
            params += "resolution " + str(self.sl_res.get())+"\n"
            params += "colorMode " + self.colorMode.get() + "\n"
            params += "randomModulation " + \
                str(self.randomModulation.get())+"\n"
            params += "sValue " + str(self.sl_s_value.get()) + "\n"
            params += "vValue " + str(self.sl_v_value.get()) + "\n"
            params += "bwScale " + str(self.sl_bw_scale.get()) + "\n"
            params += "rgbScale " + str(self.sl_rgb_scale.get()) + "\n"
            file.write(params)
            file.close()

        json_data = {}
        json_data['formula'] = self.formula.get()
        json_data['menu_parameters'] = {
            'offx': self.offx,
            'offy': self.offy,
            'zoom': self.zoom.get(),
            'sigma': self.sl_sigma.get(),
            'resolution': self.sl_res.get(),
            'colorMode': self.colorMode.get(),
            'randomModulation': self.randomModulation.get(),
            'sValue': self.sl_s_value.get(),
            'vValue': self.sl_v_value.get(),
            'bwScale': self.sl_bw_scale.get(),
            'rgbScale': self.sl_rgb_scale.get(),
        }

        json_data['sliders'] = []
        for slider_name in self.sliders:
            sl = self.sliders[slider_name]
            json_data['sliders'].append({
                'name': slider_name,
                'value': sl.get()
            })

        json_data['userdef_entry'] = self.userDefEntry.get("1.0", END)

        with open("Parameters/"+name+".json", 'a') as outfile:
            json.dump(json_data, outfile)

    def loadParams(self, append = False):

        filepath = filedialog.askopenfilename(initialdir="../colorExplorer/Parameters/",
                                              title="Select parameters file",
                                              filetypes=(("json files", "*.json"), ("txt files", "*.txt"), ("all files", "*.*")))
        if filepath == ():
            return

        if len(filepath) > 4 and filepath[-5:] == ".json":
            with open(filepath) as json_file:
                json_data = json.load(json_file)
                if not(append):
                    self.activeFunction = json_data['formula']
                else : 
                    self.activeFunction += " + "+json_data['formula']
                self.formula.set(self.activeFunction)
                self.formulaEntry.delete(0, END)
                self.formulaEntry.insert(0, self.activeFunction)

                menu_params = json_data['menu_parameters']
                self.offx = menu_params['offx']
                self.offy = menu_params['offy']
                self.sl_sigma.set(menu_params['sigma'])
                self.sl_res.set(menu_params['resolution'])
                self.colorMode.set(menu_params['colorMode'])
                self.randomModulation.set(menu_params['randomModulation'])
                self.sl_s_value.set(menu_params['sValue'])
                self.sl_v_value.set(menu_params['vValue'])
                self.sl_bw_scale.set(menu_params['bwScale'])
                self.sl_rgb_scale.set(menu_params['rgbScale'])

                if 'zoom' in menu_params.keys():
                    self.zoom.set(menu_params['zoom'])

                if not(append):
                    self.sliders = {} 

                # TODO use addSlider here instead
                for slider in json_data['sliders']:
                    newSliderName = slider['name']
                    newSlider = tk.Scale(self.userSliderFrame, from_=0, to=255,
                                         orient=tk.VERTICAL, command=self.genImg, length=200)
                    setStyle(newSlider, **scaleStyle)
                    newSlider.set(slider['value'])
                    newSlider.grid(row=4, column=len(self.sliders))
                    tk.Label(self.userSliderFrame, text="slider." + newSliderName, padx=5, pady=5,
                             bg=secondaryColor, highlightthickness=thick_val).grid(row=3, column=len(self.sliders), sticky="E")
                    self.sliders[newSliderName] = newSlider

                if not(append):
                    self.userDefEntry.delete('1.0', END)
                self.userDefEntry.insert(END, json_data['userdef_entry'])
                self.userDefEntry.grid(row=1, column=1, columnspan=5, pady=20)
                self.applyFunction()

        elif len(filepath) > 3 and filepath[-4:] == ".txt":

            # Legacy .txt support:
            # TODO : automatically add alpha and beta sliders & avoid naming problems

            file = open(filepath, "r")
            line = "example"

            tags = ["sigma",
                    "resolution", "colorMode", "randomModulation", "sValue", "vValue",
                    "bwScale", "rgbScale"]
            widgets = [self.sl_sigma,
                       self.sl_res, self.colorMode, self.randomModulation, self.sl_s_value, self.sl_v_value,
                       self.sl_bw_scale, self.sl_rgb_scale]

            while (line != ""):
                line = file.readline()
                words = line.split()
                if len(words) < 1:
                    continue
                if words[0] == "formula":
                    self.activeFunction = line[8:-1]
                    self.formula.set(line[8:-1])
                    self.formulaEntry.delete(0, END)
                    self.formulaEntry.insert(0, line[8:-1])
                elif words[0] == "offx":
                    self.offx = float(words[1])
                elif words[0] == "offy":
                    self.offy = float(words[1])
                elif words[0] == "alpha" or words[0] == "beta":
                    if words[1] != 0:
                        print("alpha/beta retrocompatibility not implemented:")
                        print("Please add alpha/beta sliders and adapt formula")
                        # TODO : implement this, just add sliders, add slider.* to
                        # alpha and beta in formula, and set value to words[1]
                else:
                    if len(words) != 2:
                        print(
                            "Warning : file misread, wrong number of values per line")

                    for i in range(len(tags)):
                        if words[0] == tags[i]:
                            widgets[i].set(words[1])
            file.close()

        self.changeColorMode()

    def appendParams(self):
        self.loadParams(append = True)

    def preset(self, n):
        functions = []
        functions.append(
            "p1*np.cos(np.sin(i*10/p2))+p1*np.cos(np.sin(j*10/p2))")
        functions.append(
            "10000*np.cos( ((i+j)**2)*100/p1 )*np.sin(((i-j)**2)*100/p1)")
        functions.append(
            "255*np.sin((i+j*1.8)**2*p1/50+np.cos((i-j*1.8)**2*p2/100)*5)")
        sigma = [0, 0, 500]
        colorMode = ["HSV", "BW", "HSV"]
        randomMod = [False, False, False]

        self.formula.set(functions[n])
        self.sl_sigma.set(sigma[n])
        self.colorMode.set(colorMode[n])
        self.randomModulation.set(randomMod[n])

        self.applyFunction()

    def newSlider(self):

        def checkSliderName(name):
            # reject if name already taken
            if name in self.sliders:
                return False
            # reject if name is not a variable name
            # TODO refine this
            if " " in name:
                return False
            return True

        newSliderName = self.newSliderName.get()
        if not checkSliderName(newSliderName):
            return
        newSlider = tk.Scale(self.userSliderFrame, from_=255, to=0,
                             orient=tk.VERTICAL, command=self.genImg, length=200, bg=secondaryColor, highlightthickness=thick_val)
        setStyle(newSlider, **scaleStyle)
        newSlider.set(100)
        newSlider.grid(row=4, column=len(self.sliders))
        tk.Label(self.userSliderFrame, text="slider." + newSliderName, padx=5, pady=5,
                 bg=secondaryColor, highlightthickness=thick_val).grid(row=3, column=len(self.sliders), sticky="E")
        self.sliders[newSliderName] = newSlider


app = GUI()
