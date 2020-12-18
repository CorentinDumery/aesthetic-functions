import os
import json
import sys
from time import time
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext, END
import random
import src.userdef as user  # used to load user definitions
import importlib
from src.image_canvas import Canvas
from src.style import mainColor, frameStyle, titleStyle, scaleStyle, baseStyle, frameGrid, buttonGrid


class Interface():

    def __init__(self, size):
        self.root = tk.Tk()
        self.root.title('ColorExplorer')
        self.root.grid()
        self.root.configure(background=mainColor)
        self.root.sizex = size[0]  # Size of image on tk window
        self.root.sizey = size[1]

        self.canvas = Canvas(self.root.sizex, self.root.sizey)

        self.offx = 0
        self.offy = 0
        self.zoom = tk.DoubleVar()
        self.zoom.set(1)
        self.computeMinMax()
        self.computationTime = tk.DoubleVar()
        self.fps = tk.IntVar()

        self.sliderDict = self.SliderDict()
        self.sliders = {}

        ## -- SLIDERFRAME -- ##

        self.sliderFrame = tk.Frame(self.root, **frameStyle)

        title_slider = tk.Label(self.sliderFrame, text="SLIDERS", **titleStyle)
        title_slider.grid(row=0, column=0, columnspan=4)

        self.sl_sigma = tk.Scale(self.sliderFrame, from_=500, to=0, orient=tk.VERTICAL,
                                 command=self.updateCanvas, length=150, **scaleStyle)
        self.sl_sigma.set(0)
        self.sl_sigma.grid(row=2, column=2)
        tk.Label(self.sliderFrame, text="σ", padx=5,
                 **baseStyle).grid(row=1, column=2, sticky="E")

        self.sl_res = tk.Scale(self.sliderFrame, **scaleStyle, from_=100, to=1, orient=tk.VERTICAL, command=self.updateCanvas,
                               length=150)
        self.sl_res.set(30)
        self.sl_res.grid(row=2, column=3)
        tk.Label(self.sliderFrame, text="res", **baseStyle).grid(
            row=1, column=3, sticky="E")

        self.saveWithMaxResolution = tk.BooleanVar()
        self.saveWithMaxResolution.set(True)
        self.checkMaxResolution = tk.Checkbutton(self.sliderFrame, text="Save with max resolution",
                                                 var=self.saveWithMaxResolution, **baseStyle)
        self.checkMaxResolution.grid(row=3, column=1, columnspan=3)

        self.addSliderFrame = tk.Frame(self.sliderFrame, **baseStyle)
        self.newSliderName = tk.StringVar(value="my_param")
        self.newSliderEntry = tk.Entry(
            self.addSliderFrame, textvariable=self.newSliderName)
        self.newSliderEntry.pack(side=tk.LEFT)

        self.newSliderButton = tk.Button(
            self.addSliderFrame, text="+", command=self.newSlider)
        self.newSliderButton.pack(side=tk.RIGHT)

        self.addSliderFrame.grid(row=4, column=0, columnspan=4)

        self.userSliderFrame = tk.Frame(  # Empty frame for now, but user can add sliders here
            self.sliderFrame, **baseStyle)
        self.userSliderFrame.grid(row=6, column=0, columnspan=4)

        self.deleteSliderButton = tk.Button(
            self.sliderFrame, text="Delete sliders", command=self.deleteSliders)
        self.deleteSliderButton.grid(row=5, column=1, columnspan=5)

        self.sliderFrame.grid(row=1, column=1, **frameGrid)

        ## -- CHECKFRAME -- ##
        self.checkFrame = tk.Frame(self.root, **frameStyle)
        title_check = tk.Label(
            self.checkFrame, text="COLOR MODEL", **titleStyle)
        title_check.grid(row=0, column=0, columnspan=8)

        self.randomModulation = tk.IntVar(value=0)
        self.check1 = tk.Checkbutton(self.checkFrame, text="Random Modulation",
                                     var=self.randomModulation, **baseStyle, command=self.updateCanvas)
        self.check1.grid(row=1, column=1, columnspan=3)
        
        self.newRandomButton = tk.Button(self.checkFrame, text="New Random Seed", 
                                         **baseStyle, command=self.newRandom)
        self.newRandomButton.grid(row =4 , column=1, columnspan=3 )

        self.colorMode = tk.StringVar(value="RGB")
        self.rad1 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="RGB", value="RGB", **baseStyle, command=self.changeColorMode)
        self.rad1.grid(row=2, column=1, sticky="W")

        self.rad2 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="BW", value="BW", **baseStyle, command=self.changeColorMode)
        self.rad2.grid(row=2, column=2, sticky="W")

        self.rad3 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="HSV", value="HSV", **baseStyle, command=self.changeColorMode)
        self.rad3.grid(row=2, column=3, sticky="W")

        self.rad4 = tk.Radiobutton(self.checkFrame, variable=self.colorMode,
                                   text="R/G/B", value="R/G/B", **baseStyle, command=self.changeColorMode)
        self.rad4.grid(row=2, column=4, sticky="W")

        self.RGBModeMenu = tk.Frame(
            self.checkFrame, **baseStyle)
        self.RGBModeMenu.grid_columnconfigure(
            0, weight=1, uniform="RGB_uniform")
        self.RGBModeMenu.grid_columnconfigure(
            1, weight=1, uniform="RGB_uniform")
        self.sl_rgb_scale = tk.Scale(self.RGBModeMenu, from_=0, to=256,
                                     orient=tk.HORIZONTAL, command=self.updateCanvas, length=150, **scaleStyle)
        self.sl_rgb_scale.set(256)
        self.sl_rgb_scale.grid(row=1, column=0, columnspan=2)

        self.HSVModeMenu = tk.Frame(
            self.checkFrame, **baseStyle)
        self.HSVModeMenu.grid_columnconfigure(
            0, weight=1, uniform="HSV_uniform")
        self.HSVModeMenu.grid_columnconfigure(
            1, weight=1, uniform="HSV_uniform")
        self.sl_s_value = tk.Scale(self.HSVModeMenu, from_=0, to=255,
                                   orient=tk.HORIZONTAL, command=self.updateCanvas, length=150, **scaleStyle)
        self.sl_s_value.set(102)
        self.sl_s_value.grid(row=1, column=0, columnspan=2)

        self.sl_v_value = tk.Scale(self.HSVModeMenu, from_=0, to=255,
                                   orient=tk.HORIZONTAL, command=self.updateCanvas, length=150, **scaleStyle)
        self.sl_v_value.set(230)
        self.sl_v_value.grid(row=2, column=0, columnspan=2)

        self.BWModeMenu = tk.Frame(
            self.checkFrame, **baseStyle)
        self.BWModeMenu.grid_columnconfigure(0, weight=1, uniform="BW_uniform")
        self.BWModeMenu.grid_columnconfigure(1, weight=1, uniform="BW_uniform")
        self.sl_bw_scale = tk.Scale(self.BWModeMenu, from_=0, to=200,
                                    orient=tk.HORIZONTAL, command=self.updateCanvas, length=150, **scaleStyle)
        self.sl_bw_scale.set(100)
        self.sl_bw_scale.grid(row=1, column=0, columnspan=2)

        self.checkFrame.grid(row=2, column=1, **frameGrid)

        ## -- FORMULAFRAME -- ##

        self.formulaFrame = tk.Frame(self.root, **frameStyle)

        title_formula = tk.Label(
            self.formulaFrame, text="FORMULAS", **titleStyle)
        title_formula.grid(row=0, column=0, columnspan=10)

        self.activeFunction = f"255*(i**2+j**2)"  # default formula here
        self.formula = tk.StringVar(value=self.activeFunction)

        # Formulas for R/G/B color mode
        self.formulaRed = tk.StringVar(value=f"255*(i**2+j**2)")
        self.formulaGreen = tk.StringVar(value=f"200*(i**2+j**2)")
        self.formulaBlue = tk.StringVar(value=f"150*(i**2+j**2)")

        self.userDefEntry = scrolledtext.ScrolledText(
            self.formulaFrame, width=100, height=10)
        self.userDefEntry.insert(
            END, "# Your definitions here.\n# They will be imported in the module 'user'.")
        self.userDefEntry.grid(
            row=1, column=1, rowspan=2, columnspan=5, pady=5)

        self.formulaEntry = tk.Entry(
            self.formulaFrame, textvariable=self.formula, width=100)

        self.threeFormulaFrame = tk.Frame(
            self.formulaFrame, **baseStyle)

        self.formulaRedEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaRed, width=100)
        self.formulaRedEntry.grid(row=1, column=1, columnspan=5, pady=0)

        self.formulaGreenEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaGreen, width=100)
        self.formulaGreenEntry.grid(row=2, column=1, columnspan=5, pady=0)

        self.formulaBlueEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaBlue, width=100)
        self.formulaBlueEntry.grid(row=3, column=1, columnspan=5, pady=0)

        self.bApply = tk.Button(
            self.formulaFrame, text='Apply', **baseStyle, command=self.applyFunction)
        self.bApply.grid(row=3, column=6, **buttonGrid)

        self.bSaveIm = tk.Button(
            self.formulaFrame, text='Save Image', **baseStyle, command=self.saveImg)
        self.bSaveIm.grid(row=7, column=1, **buttonGrid)

        self.bSaveParams = tk.Button(
            self.formulaFrame, text='Save Parameters', **baseStyle, command=self.saveParams)
        self.bSaveParams.grid(row=7, column=2, **buttonGrid)

        self.bLoadParams = tk.Button(
            self.formulaFrame, text='Load Parameters', **baseStyle, command=self.loadParams)
        self.bLoadParams.grid(row=7, column=3, **buttonGrid)

        self.bAppendParams = tk.Button(
            self.formulaFrame, text='Append Parameters', **baseStyle, command=self.appendParams)
        self.bAppendParams.grid(row=7, column=4, **buttonGrid)

        self.openRandomButton = tk.Button(
            self.formulaFrame, text='Open Random', **baseStyle, command=self.openRandom)
        self.openRandomButton.grid(row=7, column=5, **buttonGrid)

        self.errorUserdef = tk.StringVar()
        self.errorUserdef.set("Userdef: no error.")
        self.errorLabel = tk.Label(
            self.formulaFrame, textvariable=self.errorUserdef, **baseStyle)
        self.errorLabel.grid(row=1, column=6)

        self.errorMessage = tk.StringVar()
        self.errorMessage.set("Formula: no error.")
        self.errorLabel = tk.Label(
            self.formulaFrame, textvariable=self.errorMessage, **baseStyle)
        self.errorLabel.grid(row=2, column=6)

        self.formulaFrame.grid(row=2, column=2, rowspan=2, **frameGrid)

        ## -- INFOFRAME -- ##

        self.infoFrame = tk.Frame(
            self.root, **frameStyle)

        title_info = tk.Label(self.infoFrame, text="STATS", **titleStyle)
        title_info.grid(row=1, column=0, columnspan=2)

        self.maxLabelText = tk.StringVar(value="Max value: X")
        self.maxLabel = tk.Label(
            self.infoFrame, textvariable=self.maxLabelText, **baseStyle)
        self.maxLabel.grid(row=2, column=0, sticky="E")

        self.zoomLabelText = tk.StringVar(value="Zoom value:")
        self.zoomLabel = tk.Label(
            self.infoFrame, textvariable=self.zoomLabelText, **baseStyle)
        self.zoomLabel.grid(row=3, column=0, sticky="W")
        self.zoomLabelValue = tk.Label(
            self.infoFrame, textvariable=self.zoom, anchor=tk.W, **baseStyle)
        self.zoomLabelValue.grid(row=3, column=1, sticky="W")

        self.timeLabelText = tk.StringVar(value="Computation time:")
        self.timeLabel = tk.Label(
            self.infoFrame, textvariable=self.timeLabelText, **baseStyle)
        self.timeLabel.grid(row=4, column=0, sticky="W")
        self.timeLabelValue = tk.Label(
            self.infoFrame, textvariable=self.computationTime, anchor=tk.W, **baseStyle)
        self.timeLabelValue.grid(row=4, column=1, sticky="W")

        self.fpsLabelText = tk.StringVar(value="FPS:")
        self.fpsLabel = tk.Label(
            self.infoFrame, textvariable=self.fpsLabelText, **baseStyle)
        self.fpsLabel.grid(row=5, column=0, sticky="W")
        self.fpsLabelValue = tk.Label(
            self.infoFrame, textvariable=self.fps, anchor=tk.W, **baseStyle)
        self.fpsLabelValue.grid(row=5, column=1, sticky="W")

        self.infoFrame.grid(row=3, column=1, **frameGrid)

        self.canvas_label = tk.Label(self.root)

        self.updateCanvas()

        class MouseMover():

            def __init__(self, window):
                self.lastX = 0
                self.lastY = 0
                self.window = window

            def mouseWheel(self, event):
                self.window.zoom.set(round(self.window.zoom.get()
                                           * (1-event.delta/1200), 5))
                self.window.computeMinMax()
                self.window.updateCanvas()

            def b3(self, event):  # right click
                pass

            def b4(self, event):  # mouse wheel up X11
                self.window.zoom.set(round(self.window.zoom.get() * 0.9, 5))
                self.window.computeMinMax()
                self.window.updateCanvas()

            def b5(self, event):  # mouse wheel down X11
                self.window.zoom.set(round(self.window.zoom.get() * 1.1, 5))
                self.window.computeMinMax()
                self.window.updateCanvas()

            def selectB1(self, event):
                self.lastX = event.x
                self.lastY = event.y

            def dragB1(self, event):
                sx = self.window.root.sizex
                sy = self.window.root.sizey
                self.window.computeMinMax()

                self.window.offx += (event.x - self.lastX) * \
                    (self.window.maxx-self.window.minx)/sx
                self.window.offy += (event.y - self.lastY) * \
                    (self.window.maxy-self.window.miny)/sy
                self.lastX = event.x
                self.lastY = event.y
                self.window.canvas.setOff(self.window.offx, self.window.offy)
                self.window.updateCanvas()

        mouse_mover = MouseMover(self)
        self.canvas_label.bind("<Button-1>", mouse_mover.selectB1)
        self.canvas_label.bind("<MouseWheel>", mouse_mover.mouseWheel)
        self.canvas_label.bind("<Button-3>", mouse_mover.b3)
        self.canvas_label.bind("<Button-4>", mouse_mover.b4) # mouse wheel up X11
        self.canvas_label.bind("<Button-5>", mouse_mover.b5) # mouse wheel down X11
        self.canvas_label.bind("<B1-Motion>", mouse_mover.dragB1)

        self.changeColorMode()
        self.root.mainloop()

    def updateCanvas(self, event=None):
        try:
            # will be replaced if no error found
            self.errorMessage.set("Formula: Error, see console")
            time_beginning = time()

            # We could improve perfomance by setting these
            # only when necessary, instead of every update
            self.canvas.setRes(self.sl_res.get())
            self.canvas.setFunction(self.formula.get())
            self.canvas.setFunctionRed(self.formulaRed.get())
            self.canvas.setFunctionGreen(self.formulaGreen.get())
            self.canvas.setFunctionBlue(self.formulaBlue.get())
            self.canvas.setRandomMod(self.randomModulation.get())
            self.canvas.setSValue(self.sl_s_value.get())
            self.canvas.setVValue(self.sl_v_value.get())
            self.canvas.setRGBScale(self.sl_rgb_scale.get())
            self.canvas.setBWScale(self.sl_bw_scale.get())
            self.canvas.setSigma(self.sl_sigma.get())

            self.updateSliderParameters()  # updates global dict
            self.canvas.setSliderDict(self.sliderDict)

            img = self.canvas.generateImage()
            self.image = img
            self.canvas_label.configure(image=self.image)
            self.canvas_label.grid(row=1, column=2, pady=10, padx=10)
            self.computationTime.set(round(time() - time_beginning, 5))
            self.fps.set(int(1/(time() - time_beginning + 0.00001)))
            self.maxLabelText.set("Max value: "+f"{self.canvas.getMax():.2f}")
            self.errorMessage.set("Formula: No Error")

        except:
            e = sys.exc_info()[0].__name__
            message = sys.exc_info()[1]
            print("Error caught:")
            print(message)
            self.errorMessage.set("Formula: "+e)
    
    def newRandom(self):
        self.canvas.newRandomSeed()
        self.updateCanvas()

    def changeColorMode(self):
        ''' Forget previous layout and apply new one '''
        self.RGBModeMenu.grid_forget()
        self.HSVModeMenu.grid_forget()
        self.BWModeMenu.grid_forget()
        self.formulaEntry.grid_forget()
        self.threeFormulaFrame.grid_forget()
        if self.colorMode.get() == "HSV":
            self.HSVModeMenu.grid(row=3, column=1, columnspan=3)
        if self.colorMode.get() == "RGB":
            self.RGBModeMenu.grid(row=3, column=1, columnspan=3)
        if self.colorMode.get() == "BW":
            self.BWModeMenu.grid(row=3, column=1, columnspan=3)
        if self.colorMode.get() in ["HSV", "RGB", "BW"]:
            self.formulaEntry.grid(row=3, column=1, columnspan=5, pady=5)
        if self.colorMode.get() == "R/G/B":
            self.RGBModeMenu.grid(row=3, column=1, columnspan=3)
            self.threeFormulaFrame.grid(row=3, column=1, columnspan=5)
        self.canvas.setColorMode(self.colorMode.get())
        self.updateCanvas()

    def applyFunction(self):
        self.activeFunction = self.formula.get()

        def updateUserDefLib(text, sliders):
            '''Writes text in userdef.py and reloads the module'''
            try:
                libfile = open("src/userdef.py", "w")
                libfile.write(text)
                libfile.close()            
                importlib.reload(user)
                return "Userdef: no error."
            except:
                e = sys.exc_info()[0].__name__
                message = sys.exc_info()[1]
                print("Error caught:")
                print(message)
                return "Userdef: " + e

        error_str = updateUserDefLib(
            self.userDefEntry.get("1.0", END), self.sliders)
        self.errorUserdef.set(error_str)
        self.updateCanvas()

    def computeMinMax(self):
        self.minx = self.zoom.get()*(-640)/100
        self.maxx = self.zoom.get()*(+640)/100
        self.miny = self.zoom.get()*(-360)/100
        self.maxy = self.zoom.get()*(+360)/100
        self.canvas.setMinMax((self.minx, self.maxx), (self.miny, self.maxy))

    ### --- I/O parameters and images --- ###

    def saveImg(self):
        name = simpledialog.askstring("", "Name of this image?")
        if name:
            if self.saveWithMaxResolution.get():
                old_res = self.sl_res.get()
                self.sl_res.set(100)
                self.updateCanvas()
                self.canvas.saveImage(name)
                self.sl_res.set(old_res)
                self.updateCanvas()
            else:
                self.canvas.saveImage(name)

            messagebox.showinfo("", "{}.png saved!".format(name))
            self.saveParams(name)
        else:
            messagebox.showinfo("", "Saving cancelled!")

    def saveParams(self, name=""):
        if name == "":
            name = simpledialog.askstring(
                "", "Name of this set of parameters?")

        while os.path.exists("Parameters/"+name+".json"):
            name = simpledialog.askstring(
                "", "Name already exists, please pick another one")

        json_data = {}
        json_data['formula'] = self.formula.get()
        json_data['formulaRed'] = self.formulaRed.get()
        json_data['formulaGreen'] = self.formulaGreen.get()
        json_data['formulaBlue'] = self.formulaBlue.get()
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

    def openRandom(self):
        dir = "../colorExplorer/Parameters"
        file = random.choice([dir + "/" + x for x in os.listdir(
            dir) if os.path.isfile(os.path.join(dir, x))])
        print("Opening "+file)
        self.loadParams(filepath=file)

    def loadParams(self, append=False, filepath=""):

        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir="../colorExplorer/Parameters/",
                                                  title="Select parameters file",
                                                  filetypes=(("json files", "*.json"), ("all files", "*.*")))

        if filepath == ():
            return

        if not(append):
            self.deleteSliders()

        with open(filepath) as json_file:
            json_data = json.load(json_file)
            if not(append):
                self.activeFunction = json_data['formula']
            else:
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
                self.zoom.set(round(menu_params['zoom'], 5))

            attributes = [('formulaRed', self.formulaRed), ('formulaGreen',
                                                            self.formulaGreen), ('formulaBlue', self.formulaBlue)]

            for attr in attributes:
                if attr[0] in json_data.keys():
                    if not(append):
                        attr[1].set(json_data[attr[0]])
                    else:
                        attr[1].set(attr[1].get() + " + " +
                                    json_data[attr[0]])

            if not(append):
                self.sliders = {}

            for slider in json_data['sliders']:
                self.newSlider(slider['name'], slider['value'])

            if not(append):
                self.userDefEntry.delete('1.0', END)
            self.userDefEntry.insert(END, json_data['userdef_entry'])


        self.computeMinMax()
        self.canvas.setOff(self.offx, self.offy)
        self.changeColorMode()

        self.applyFunction()

    def appendParams(self):
        self.loadParams(append=True)

    ### --- User defined sliders --- ###

    class SliderDict(dict):
        '''Convenient user sliders representation'''

        def __getattr__(self, name):
            if name in self:
                return self[name]
            else:
                raise AttributeError("No such attribute: " + name)

        def __setattr__(self, name, value):
            self[name] = value

    def updateSliderParameters(self):
        for paramName in self.sliders:
            sl = self.sliders[paramName]
            self.sliderDict[paramName] = sl.get()

    def newSlider(self, name="", value=100):

        def checkSliderName(name):
            # reject invalid names
            if name in self.sliders:
                return False
            if " " in name:
                return False
            return True

        if name == "":
            name = self.newSliderName.get()
        if not checkSliderName(name):
            return
        newSlider = tk.Scale(self.userSliderFrame, from_=255, to=0,
                             orient=tk.VERTICAL, command=self.updateCanvas, length=150, **scaleStyle)
        newSlider.set(value)
        newSlider.grid(row=4, column=len(self.sliders))
        tk.Label(self.userSliderFrame, text="slider." + name, padx=5, pady=5,
                 **baseStyle).grid(row=3, column=len(self.sliders), sticky="E")
        self.sliders[name] = newSlider

    def deleteSliders(self):
        self.sliders = {}
        for widget in self.userSliderFrame.winfo_children():
            widget.destroy()
        self.sliderDict = self.SliderDict()
