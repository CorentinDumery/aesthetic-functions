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
from src.style import frameStyle, titleStyle, scaleStyle, baseStyle
from src.style import mainColor, frameGrid, buttonGrid


class Interface():

    def __init__(self, size):
        self.root = tk.Tk()
        self.root.title('ColorExplorer')
        self.root.grid()
        self.root.configure(background=mainColor)
        self.canvas = Canvas(size[0], size[1])

        self.computationTime = tk.DoubleVar()
        self.fps = tk.IntVar()
        self.sliderDict = self.SliderDict()
        self.sliders = {}
        self.zoom = tk.DoubleVar()
        self.zoom.set(1)

        ## -- Frames setup -- ##

        sliderFrame = tk.Frame(self.root, **frameStyle)
        self.setup_slider_frame(sliderFrame)

        checkFrame = tk.Frame(self.root, **frameStyle)
        self.setup_check_frame(checkFrame)

        formulaFrame = tk.Frame(self.root, **frameStyle)
        self.setup_formula_frame(formulaFrame)

        IOFrame = tk.Frame(self.root)
        self.setup_io_frame(IOFrame)

        infoFrame = tk.Frame(self.root, **frameStyle)
        self.setup_info_frame(infoFrame)

        self.canvas_label = tk.Label(self.root)

        ## -- Frames layout -- ##

        sliderFrame.grid(row=1, rowspan=2, column=1, **frameGrid)
        checkFrame.grid(row=3, column=1, **frameGrid)
        infoFrame.grid(row=4, column=1, **frameGrid)

        formulaFrame.grid(row=3, column=2, rowspan=2, **frameGrid)
        IOFrame.grid(row=2, column=2, sticky=tk.S+tk.W+tk.E)

        ## -- Launch app -- ##

        self.MouseMover(self, self.canvas_label)
        self.compute_minmax()
        self.change_color_mode()
        self.root.mainloop()

    def update_canvas(self, event=None):
        try:
            # will be replaced if no error found
            self.errorMessage.set("Formula: Error, see console")
            time_beginning = time()

            # TODO bind canvas attributes to interface widgets
            # and remove this part
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

            self.update_slider_parameters()  # updates global dict
            self.canvas.setSliderDict(self.sliderDict)

            img = self.canvas.generate_image()
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

    def setup_slider_frame(self, frame):
        title_slider = tk.Label(frame, text="SLIDERS", **titleStyle)
        title_slider.grid(row=0, column=0, columnspan=4)

        self.sl_sigma = tk.Scale(frame, orient=tk.VERTICAL,
                                 command=self.update_canvas, **scaleStyle)
        self.sl_sigma.set(0)
        self.sl_sigma.grid(row=2, column=2)
        sigma_label = tk.Label(frame, text="σ", padx=5, **baseStyle)
        sigma_label.grid(row=1, column=2, sticky="E")

        self.sl_res = tk.Scale(frame, **scaleStyle,  orient=tk.VERTICAL,
                               command=self.update_canvas)
        self.sl_res.config(from_=100, to_=1)
        self.sl_res.set(30)
        self.sl_res.grid(row=2, column=3)
        tk.Label(frame, text="res", **baseStyle).grid(
            row=1, column=3, sticky="E")

        self.saveWithMaxResolution = tk.BooleanVar()
        self.saveWithMaxResolution.set(True)
        checkMaxResolution = tk.Checkbutton(frame, text="Save with max resolution",
                                            var=self.saveWithMaxResolution, **baseStyle)
        checkMaxResolution.grid(row=3, column=1, columnspan=3)

        self.addSliderFrame = tk.Frame(frame, **baseStyle)
        self.new_slider_name = tk.StringVar(value="my_param")
        self.newSliderEntry = tk.Entry(
            self.addSliderFrame, textvariable=self.new_slider_name)
        self.newSliderEntry.pack(side=tk.LEFT)

        self.newSliderButton = tk.Button(
            self.addSliderFrame, text="+", command=self.new_slider)
        self.newSliderButton.pack(side=tk.RIGHT)

        self.addSliderFrame.grid(row=4, column=0, columnspan=4)

        # Empty frame for now, but user can add sliders here
        self.userSliderFrame = tk.Frame(frame, **baseStyle)
        self.userSliderFrame.grid(row=6, column=0, columnspan=4)

        self.deleteSliderButton = tk.Button(
            frame, text="Delete sliders", command=self.delete_sliders)
        self.deleteSliderButton.grid(row=5, column=1, columnspan=5)

    def setup_check_frame(self, frame):
        title_check = tk.Label(
            frame, text="COLOR MODEL", **titleStyle)
        title_check.grid(row=0, column=0, columnspan=8)

        self.colorMode = tk.StringVar(value="RGB")
        rad1 = tk.Radiobutton(frame, variable=self.colorMode,
                              text="RGB", value="RGB", **baseStyle, command=self.change_color_mode)
        rad1.grid(row=2, column=1, sticky="W")

        rad2 = tk.Radiobutton(frame, variable=self.colorMode,
                              text="BW", value="BW", **baseStyle, command=self.change_color_mode)
        rad2.grid(row=2, column=2, sticky="W")

        rad3 = tk.Radiobutton(frame, variable=self.colorMode,
                              text="HSV", value="HSV", **baseStyle, command=self.change_color_mode)
        rad3.grid(row=2, column=3, sticky="W")

        rad4 = tk.Radiobutton(frame, variable=self.colorMode,
                              text="R/G/B", value="R/G/B", **baseStyle, command=self.change_color_mode)
        rad4.grid(row=2, column=4, sticky="W")

        self.RGBModeMenu = tk.Frame(frame, **baseStyle)
        self.RGBModeMenu.grid_columnconfigure(
            0, weight=1, uniform="RGB_uniform")
        self.RGBModeMenu.grid_columnconfigure(
            1, weight=1, uniform="RGB_uniform")
        self.sl_rgb_scale = tk.Scale(self.RGBModeMenu,
                                     orient=tk.HORIZONTAL, command=self.update_canvas, **scaleStyle)
        self.sl_rgb_scale.set(255)
        self.sl_rgb_scale.grid(row=1, column=0, columnspan=2)

        self.HSVModeMenu = tk.Frame(frame, **baseStyle)
        self.HSVModeMenu.grid_columnconfigure(
            0, weight=1, uniform="HSV_uniform")
        self.HSVModeMenu.grid_columnconfigure(
            1, weight=1, uniform="HSV_uniform")
        self.sl_s_value = tk.Scale(self.HSVModeMenu,
                                   orient=tk.HORIZONTAL, command=self.update_canvas, **scaleStyle)
        self.sl_s_value.set(102)
        self.sl_s_value.grid(row=1, column=0, columnspan=2)

        self.sl_v_value = tk.Scale(self.HSVModeMenu,
                                   orient=tk.HORIZONTAL, command=self.update_canvas, **scaleStyle)
        self.sl_v_value.set(230)
        self.sl_v_value.grid(row=2, column=0, columnspan=2)

        self.BWModeMenu = tk.Frame(frame, **baseStyle)
        self.BWModeMenu.grid_columnconfigure(0, weight=1, uniform="BW_uniform")
        self.BWModeMenu.grid_columnconfigure(1, weight=1, uniform="BW_uniform")
        self.sl_bw_scale = tk.Scale(self.BWModeMenu,
                                    orient=tk.HORIZONTAL, command=self.update_canvas, **scaleStyle)
        self.sl_bw_scale.set(100)
        self.sl_bw_scale.grid(row=1, column=0, columnspan=2)

        self.randomModulation = tk.IntVar(value=0)
        check1 = tk.Checkbutton(frame, text="Random Modulation",
                                var=self.randomModulation, **baseStyle, command=self.update_canvas)
        check1.grid(row=4, column=1, columnspan=3)

        new_random_button = tk.Button(frame, text="New Random Seed",
                                    **baseStyle, command=self.new_random)
        new_random_button.grid(row=5, column=1, columnspan=5, **buttonGrid)

    def setup_formula_frame(self, frame):
        title_formula = tk.Label(
            frame, text="FORMULAS", **titleStyle)
        title_formula.grid(row=0, column=0, columnspan=10)

        self.activeFunction = f"255*(i**2+j**2)"  # default formula here
        self.formula = tk.StringVar(value=self.activeFunction)

        # Formulas for R/G/B color mode
        self.formulaRed = tk.StringVar(value=f"255*(i**2+j**2)")
        self.formulaGreen = tk.StringVar(value=f"200*(i**2+j**2)")
        self.formulaBlue = tk.StringVar(value=f"150*(i**2+j**2)")

        self.userDefEntry = scrolledtext.ScrolledText(
            frame, width=100, height=12)
        self.userDefEntry.insert(
            END, "# Your definitions here.\n# They will be imported in the module 'user'.")
        self.userDefEntry.grid(
            row=1, column=1, rowspan=2, columnspan=5, pady=5)

        self.formulaEntry = tk.Entry(
            frame, textvariable=self.formula, width=100)

        self.threeFormulaFrame = tk.Frame(
            frame, **baseStyle)

        self.formulaRedEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaRed, width=100)
        self.formulaRedEntry.grid(row=1, column=1, columnspan=5, pady=0)

        self.formulaGreenEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaGreen, width=100)
        self.formulaGreenEntry.grid(row=2, column=1, columnspan=5, pady=0)

        self.formulaBlueEntry = tk.Entry(
            self.threeFormulaFrame, textvariable=self.formulaBlue, width=100)
        self.formulaBlueEntry.grid(row=3, column=1, columnspan=5, pady=0)

        bApply = tk.Button(
            frame, text='Apply', **baseStyle, command=self.apply_function)
        bApply.grid(row=3, column=6, **buttonGrid)

        self.errorUserdef = tk.StringVar()
        self.errorUserdef.set("Userdef: no error.")
        errorLabelUser = tk.Label(
            frame, textvariable=self.errorUserdef, **baseStyle)
        errorLabelUser.grid(row=1, column=6)

        self.errorMessage = tk.StringVar()
        self.errorMessage.set("Formula: no error.")
        errorLabelForm = tk.Label(
            frame, textvariable=self.errorMessage, **baseStyle)
        errorLabelForm.grid(row=2, column=6)

    def setup_io_frame(self, frame):
        for i in range(1, 6):
            frame.grid_columnconfigure(
                i, weight=1, uniform="IOFrameUniform")

        bSaveIm = tk.Button(
            frame, text='Save Image', **baseStyle, command=self.save_image)
        bSaveIm.grid(row=7, column=1, **buttonGrid)

        bSave_params = tk.Button(
            frame, text='Save Parameters', **baseStyle, command=self.save_params)
        bSave_params.grid(row=7, column=2, **buttonGrid)

        bLoadParams = tk.Button(
            frame, text='Load Parameters', **baseStyle, command=self.load_params)
        bLoadParams.grid(row=7, column=3, **buttonGrid)

        bAppendParams = tk.Button(
            frame, text='Append Parameters', **baseStyle, command=self.append_params)
        bAppendParams.grid(row=7, column=4, **buttonGrid)

        openRandomButton = tk.Button(
            frame, text='Open Random', **baseStyle, command=self.open_random)
        openRandomButton.grid(row=7, column=5, **buttonGrid)

    def setup_info_frame(self, frame):
        title_info = tk.Label(frame, text="STATS", **titleStyle)
        title_info.grid(row=1, column=0, columnspan=2)

        self.maxLabelText = tk.StringVar(value="Max value: X")
        maxLabel = tk.Label(
            frame, textvariable=self.maxLabelText, **baseStyle)
        maxLabel.grid(row=2, column=0, sticky="E")

        zoomLabelText = tk.StringVar(value="Zoom value:")
        zoomLabel = tk.Label(
            frame, textvariable=zoomLabelText, **baseStyle)
        zoomLabel.grid(row=3, column=0, sticky="W")
        zoomLabelValue = tk.Label(
            frame, textvariable=self.zoom, anchor=tk.W, **baseStyle)
        zoomLabelValue.grid(row=3, column=1, sticky="W")

        timeLabelText = tk.StringVar(value="Computation time:")
        timeLabel = tk.Label(
            frame, textvariable=timeLabelText, **baseStyle)
        timeLabel.grid(row=4, column=0, sticky="W")
        timeLabelValue = tk.Label(
            frame, textvariable=self.computationTime, anchor=tk.W, **baseStyle)
        timeLabelValue.grid(row=4, column=1, sticky="W")

        fpsLabelText = tk.StringVar(value="FPS:")
        fpsLabel = tk.Label(
            frame, textvariable=fpsLabelText, **baseStyle)
        fpsLabel.grid(row=5, column=0, sticky="W")
        fpsLabelValue = tk.Label(
            frame, textvariable=self.fps, anchor=tk.W, **baseStyle)
        fpsLabelValue.grid(row=5, column=1, sticky="W")

    def new_random(self):
        self.canvas.new_random_seed()
        self.update_canvas()

    def change_color_mode(self):
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
        self.update_canvas()

    def apply_function(self):
        self.activeFunction = self.formula.get()

        def update_user_def_lib(text, sliders):
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

        error_str = update_user_def_lib(
            self.userDefEntry.get("1.0", END), self.sliders)
        self.errorUserdef.set(error_str)
        self.update_canvas()

    def compute_minmax(self):
        self.minx = self.zoom.get()*(-640)/100
        self.maxx = self.zoom.get()*(+640)/100
        self.miny = self.zoom.get()*(-360)/100
        self.maxy = self.zoom.get()*(+360)/100
        self.canvas.setMinMax((self.minx, self.maxx), (self.miny, self.maxy))

    class MouseMover():

        def __init__(self, window, label):
            self.lastX = 0
            self.lastY = 0
            self.window = window
            label.bind("<Button-1>", self.select_b1)
            label.bind("<MouseWheel>", self.mouse_wheel)
            label.bind("<Button-3>", self.b3)
            # mouse wheel up/down X11:
            label.bind("<Button-4>", self.b4)
            label.bind("<Button-5>", self.b5)
            label.bind("<B1-Motion>", self.drag_b1)

        def mouse_wheel(self, event):
            self.window.zoom.set(round(self.window.zoom.get()
                                       * (1-event.delta/1200), 5))
            self.window.compute_minmax()
            self.window.update_canvas()

        def b3(self, event):  # right click
            pass

        def b4(self, event):  # mouse wheel up X11
            self.window.zoom.set(round(self.window.zoom.get() * 0.9, 5))
            self.window.compute_minmax()
            self.window.update_canvas()

        def b5(self, event):  # mouse wheel down X11
            self.window.zoom.set(round(self.window.zoom.get() * 1.1, 5))
            self.window.compute_minmax()
            self.window.update_canvas()

        def select_b1(self, event):
            self.lastX = event.x
            self.lastY = event.y

        def drag_b1(self, event):
            sx = self.window.canvas.sizex
            sy = self.window.canvas.sizey
            self.window.compute_minmax()

            self.window.canvas.offx += (event.x - self.lastX) * \
                (self.window.maxx-self.window.minx)/sx
            self.window.canvas.offy += (event.y - self.lastY) * \
                (self.window.maxy-self.window.miny)/sy
            self.lastX = event.x
            self.lastY = event.y
            self.window.update_canvas()

    ### --- I/O parameters and images --- ###

    def save_image(self):
        name = simpledialog.askstring("", "Name of this image?")
        if name:
            if self.saveWithMaxResolution.get():
                old_res = self.sl_res.get()
                self.sl_res.set(100)
                self.update_canvas()
                self.canvas.save_image(name)
                self.sl_res.set(old_res)
                self.update_canvas()
            else:
                self.canvas.save_image(name)

            messagebox.showinfo("", "{}.png saved!".format(name))
            self.save_params(name)
        else:
            messagebox.showinfo("", "Saving cancelled!")

    def save_params(self, name=""):
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
            'offx': self.canvas.offx,
            'offy': self.canvas.offy,
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

    def open_random(self):
        dir = "../colorExplorer/Parameters"
        random.seed()
        file = random.choice([dir + "/" + x for x in os.listdir(
            dir) if os.path.isfile(os.path.join(dir, x))])
        print("Opening "+file)
        self.load_params(filepath=file)

    def load_params(self, append=False, filepath=""):

        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir="../colorExplorer/Parameters/",
                                                  title="Select parameters file",
                                                  filetypes=(("json files", "*.json"), ("all files", "*.*")))

        if filepath == ():
            return

        if not(append):
            self.delete_sliders()

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
            self.canvas.offx = menu_params['offx']
            self.canvas.offy = menu_params['offy']
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
                self.new_slider(slider['name'], slider['value'])

            if not(append):
                self.userDefEntry.delete('1.0', END)
            self.userDefEntry.insert(END, json_data['userdef_entry'])

        self.compute_minmax()
        self.apply_function()
        self.change_color_mode()

    def append_params(self):
        self.load_params(append=True)

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

    def update_slider_parameters(self):
        for paramName in self.sliders:
            sl = self.sliders[paramName]
            self.sliderDict[paramName] = sl.get()

    def new_slider(self, name="", value=100):

        def check_slider_name(name):
            # reject invalid names
            if name in self.sliders:
                return False
            if " " in name:
                return False
            return True

        if name == "":
            name = self.new_slider_name.get()
        if not check_slider_name(name):
            return
        new_sl = tk.Scale(self.userSliderFrame,
                             orient=tk.VERTICAL, command=self.update_canvas, **scaleStyle)
        new_sl.set(value)
        new_sl.grid(row=4, column=len(self.sliders))
        tk.Label(self.userSliderFrame, text="slider." + name, padx=5, pady=5,
                 **baseStyle).grid(row=3, column=len(self.sliders), sticky="E")
        self.sliders[name] = new_sl

    def delete_sliders(self):
        self.sliders = {}
        for widget in self.userSliderFrame.winfo_children():
            widget.destroy()
        self.sliderDict = self.SliderDict()
