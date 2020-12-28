import os
import json
import sys
from time import time
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext, END
import random
import importlib
from src.image_canvas import Canvas
from src.style import frame_style, title_style, scale_style, base_style, text_style, widget_style
from src.style import main_color, frame_grid, button_grid


class Interface():

    def __init__(self, size):
        self.root = tk.Tk()
        self.root.title('ColorExplorer')
        self.root.grid()
        self.root.configure(background=main_color)

        self.init_user_module()
        self.canvas = Canvas(size[0], size[1])

        self.computation_time = tk.DoubleVar()
        self.fps = tk.IntVar()
        self.slider_dict = self.SliderDict()
        self.sliders = {}
        self.zoom = tk.DoubleVar(value=1)

        ## -- Frames setup -- ##

        slider_frame = tk.Frame(self.root, **frame_style)
        self.setup_slider_frame(slider_frame)

        check_frame = tk.Frame(self.root, **frame_style)
        self.setup_check_frame(check_frame)

        formula_frame = tk.Frame(self.root, **frame_style)
        self.setup_formula_frame(formula_frame)

        IO_frame = tk.Frame(self.root)
        self.setup_io_frame(IO_frame)

        info_frame = tk.Frame(self.root, **frame_style)
        self.setup_info_frame(info_frame)

        self.canvas_label = tk.Label(self.root)

        ## -- Frames layout -- ##

        slider_frame.grid(row=1, rowspan=2, column=1, **frame_grid)
        check_frame.grid(row=3, column=1, **frame_grid)
        info_frame.grid(row=4, column=1, **frame_grid)

        self.canvas_label.grid(row=1, column=2, pady=10, padx=10)
        formula_frame.grid(row=3, column=2, rowspan=2, **frame_grid)
        IO_frame.grid(row=2, column=2, sticky=tk.S+tk.W+tk.E)

    def launch(self):
        self.MouseMover(self, self.canvas_label)
        self.compute_minmax()
        self.change_color_mode()
        self.root.mainloop()

    def init_user_module(self):
        if not(os.path.exists("src/userdef.py")):
            libfile = open("src/userdef.py", "w")
            libfile.write("")
        import src.userdef as user
        global user

    def update_canvas(self, event=None):
        try:
            # will be replaced if no error found
            self.error_message.set("Formula: Error, see console")
            time_beginning = time()

            # TODO bind canvas attributes to interface widgets
            # and remove this part
            self.canvas.resolution = self.sl_res.get()
            self.canvas.set_function(self.formula.get())
            self.canvas.set_function_R(self.formula_R.get())
            self.canvas.set_function_G(self.formula_G.get())
            self.canvas.set_function_B(self.formula_B.get())
            self.canvas.random_modulation = self.random_modulation.get()
            self.canvas.s_value = self.sl_s_value.get()
            self.canvas.v_value = self.sl_v_value.get()
            self.canvas.rgb_scale = self.sl_rgb_scale.get()
            self.canvas.bw_scale = self.sl_bw_scale.get()
            self.canvas.sigma = self.sl_sigma.get()

            self.update_slider_parameters()
            self.canvas.set_slider_dict(self.slider_dict)

            img = self.canvas.generate_image()
            self.image = img
            self.canvas_label.configure(image=self.image)
            self.canvas_label.grid(row=1, column=2, pady=10, padx=10)
            self.computation_time.set(round(time() - time_beginning, 5))
            self.fps.set(int(1/(time() - time_beginning + 0.00001)))
            self.max_label_text.set(
                "Max value: "+f"{self.canvas.get_max():.2f}")
            self.error_message.set("Formula: No Error")

        except:
            e = sys.exc_info()[0].__name__
            message = sys.exc_info()[1]
            print("Error caught:")
            print(message)
            self.error_message.set("Formula: "+e)

    def setup_slider_frame(self, frame):
        title_slider = tk.Label(frame, text="SLIDERS", **title_style)
        title_slider.grid(row=0, column=0, columnspan=4)

        self.sl_sigma = tk.Scale(frame, orient=tk.VERTICAL,
                                 command=self.update_canvas, **scale_style)
        self.sl_sigma.set(0)
        self.sl_sigma.grid(row=2, column=2)
        sigma_label = tk.Label(frame, text="σ", padx=5, **text_style)
        sigma_label.grid(row=1, column=2, sticky="E")

        self.sl_res = tk.Scale(frame, **scale_style,  orient=tk.VERTICAL,
                               command=self.update_canvas)
        self.sl_res.config(from_=100, to_=1)
        self.sl_res.set(30)
        self.sl_res.grid(row=2, column=3)
        tk.Label(frame, text="res", **text_style).grid(
            row=1, column=3, sticky="E")

        self.save_with_max_resolution = tk.BooleanVar(value=True)
        check_max_resolution = tk.Checkbutton(frame, text="Save with max resolution",
                                              var=self.save_with_max_resolution, **widget_style)
        check_max_resolution.grid(row=3, column=1, columnspan=3)

        add_slider_frame = tk.Frame(frame, **base_style)
        self.new_slider_name = tk.StringVar(value="my_param")
        new_slider_entry = tk.Entry(
            add_slider_frame, textvariable=self.new_slider_name)
        new_slider_entry.pack(side=tk.LEFT)

        new_slider_button = tk.Button(
            add_slider_frame, text="+", command=self.new_slider, **widget_style)
        new_slider_button.pack(side=tk.RIGHT)

        add_slider_frame.grid(row=4, column=0, columnspan=4)

        # Empty frame for now, but user can add sliders here
        self.user_slider_frame = tk.Frame(frame, **base_style)
        self.user_slider_frame.grid(row=6, column=0, columnspan=4)

        delete_slider_button = tk.Button(
            frame, text="Delete sliders", command=self.delete_sliders, **widget_style)
        delete_slider_button.grid(row=5, column=1, columnspan=5)

    def setup_check_frame(self, frame):
        title_check = tk.Label(
            frame, text="COLOR MODEL", **title_style)
        title_check.grid(row=0, column=0, columnspan=8)

        self.color_mode = tk.StringVar(value="RGB")
        rad_rgb = tk.Radiobutton(frame, variable=self.color_mode,
                                 text="RGB", value="RGB", **widget_style, command=self.change_color_mode)
        rad_rgb.grid(row=2, column=1, sticky="W")

        rad_bw = tk.Radiobutton(frame, variable=self.color_mode,
                                text="BW", value="BW", **widget_style, command=self.change_color_mode)
        rad_bw.grid(row=2, column=2, sticky="W")

        rad_hsv = tk.Radiobutton(frame, variable=self.color_mode,
                                 text="HSV", value="HSV", **widget_style, command=self.change_color_mode)
        rad_hsv.grid(row=2, column=3, sticky="W")

        rad_r_g_b = tk.Radiobutton(frame, variable=self.color_mode,
                                   text="R/G/B", value="R/G/B", **widget_style, command=self.change_color_mode)
        rad_r_g_b.grid(row=2, column=4, sticky="W")

        # Display different menus for different color models
        self.RGB_mode_menu = tk.Frame(frame, **base_style)
        self.RGB_mode_menu.grid_columnconfigure(
            0, weight=1, uniform="RGB_uniform")
        self.RGB_mode_menu.grid_columnconfigure(
            1, weight=1, uniform="RGB_uniform")
        self.sl_rgb_scale = tk.Scale(self.RGB_mode_menu,
                                     orient=tk.HORIZONTAL, command=self.update_canvas, **scale_style)
        self.sl_rgb_scale.set(255)
        self.sl_rgb_scale.grid(row=1, column=0, columnspan=2)

        self.HSV_mode_menu = tk.Frame(frame, **base_style)
        self.HSV_mode_menu.grid_columnconfigure(
            0, weight=1, uniform="HSV_uniform")
        self.HSV_mode_menu.grid_columnconfigure(
            1, weight=1, uniform="HSV_uniform")
        self.sl_s_value = tk.Scale(self.HSV_mode_menu,
                                   orient=tk.HORIZONTAL, command=self.update_canvas, **scale_style)
        self.sl_s_value.set(102)
        self.sl_s_value.grid(row=1, column=0, columnspan=2)

        self.sl_v_value = tk.Scale(self.HSV_mode_menu,
                                   orient=tk.HORIZONTAL, command=self.update_canvas, **scale_style)
        self.sl_v_value.set(230)
        self.sl_v_value.grid(row=2, column=0, columnspan=2)

        self.BW_mode_menu = tk.Frame(frame, **base_style)
        self.BW_mode_menu.grid_columnconfigure(
            0, weight=1, uniform="BW_uniform")
        self.BW_mode_menu.grid_columnconfigure(
            1, weight=1, uniform="BW_uniform")
        self.sl_bw_scale = tk.Scale(self.BW_mode_menu,
                                    orient=tk.HORIZONTAL, command=self.update_canvas, **scale_style)
        self.sl_bw_scale.set(100)
        self.sl_bw_scale.grid(row=1, column=0, columnspan=2)

        self.random_modulation = tk.IntVar(value=0)
        check1 = tk.Checkbutton(frame, text="Random Modulation",
                                var=self.random_modulation, **widget_style, command=self.update_canvas)
        check1.grid(row=4, column=1, columnspan=3)

        new_random_button = tk.Button(frame, text="New Random Seed",
                                      **widget_style, command=self.new_random)
        new_random_button.grid(row=5, column=1, columnspan=5, **button_grid)

    def setup_formula_frame(self, frame):
        title_formula = tk.Label(
            frame, text="FORMULAS", **title_style)
        title_formula.grid(row=0, column=0, columnspan=10)

        self.active_function = f"255*(i**2+j**2)"  # default formula here
        self.formula = tk.StringVar(value=self.active_function)

        # Formulas for R/G/B color mode
        self.formula_R = tk.StringVar(value=f"255*(i**2+j**2)")
        self.formula_G = tk.StringVar(value=f"200*(i**2+j**2)")
        self.formula_B = tk.StringVar(value=f"150*(i**2+j**2)")

        self.userdef_entry = scrolledtext.ScrolledText(
            frame, width=100, height=12)
        self.userdef_entry.insert(
            END, "# Your definitions here.\n# They will be imported in the module 'user'.")
        self.userdef_entry.grid(
            row=1, column=1, rowspan=2, columnspan=5, pady=5)

        # Formula frame will be different based on color model, so we grid
        # some of these only later in change_color_mode()
        self.formula_entry = tk.Entry(
            frame, textvariable=self.formula, width=100)

        self.three_formula_frame = tk.Frame(frame, **base_style)

        formula_red_entry = tk.Entry(
            self.three_formula_frame, textvariable=self.formula_R, width=100)
        formula_red_entry.grid(row=1, column=1, columnspan=5, pady=0)

        formula_green_entry = tk.Entry(
            self.three_formula_frame, textvariable=self.formula_G, width=100)
        formula_green_entry.grid(row=2, column=1, columnspan=5, pady=0)

        formula_blue_entry = tk.Entry(
            self.three_formula_frame, textvariable=self.formula_B, width=100)
        formula_blue_entry.grid(row=3, column=1, columnspan=5, pady=0)

        bApply = tk.Button(
            frame, text='Apply', **widget_style, command=self.apply_function)
        bApply.grid(row=3, column=6, **button_grid)

        self.error_userdef = tk.StringVar()
        self.error_userdef.set("Userdef: no error.")
        error_label_user = tk.Label(
            frame, textvariable=self.error_userdef, **text_style)
        error_label_user.grid(row=1, column=6)

        self.error_message = tk.StringVar()
        self.error_message.set("Formula: no error.")
        error_label_formula = tk.Label(
            frame, textvariable=self.error_message, **text_style)
        error_label_formula.grid(row=2, column=6)

    def setup_io_frame(self, frame):
        for i in range(1, 6):
            frame.grid_columnconfigure(
                i, weight=1, uniform="IOFrameUniform")

        b_save_im = tk.Button(
            frame, text='Save Image', **widget_style, command=self.save_image)
        b_save_im.grid(row=7, column=1, **button_grid)

        b_save_params = tk.Button(
            frame, text='Save Parameters', **widget_style, command=self.save_params)
        b_save_params.grid(row=7, column=2, **button_grid)

        b_load_params = tk.Button(
            frame, text='Load Parameters', **widget_style, command=self.load_params)
        b_load_params.grid(row=7, column=3, **button_grid)

        b_append_params = tk.Button(
            frame, text='Append Parameters', **widget_style, command=self.append_params)
        b_append_params.grid(row=7, column=4, **button_grid)

        b_open_random = tk.Button(
            frame, text='Open Random', **widget_style, command=self.open_random)
        b_open_random.grid(row=7, column=5, **button_grid)

    def setup_info_frame(self, frame):
        title_info = tk.Label(frame, text="STATS", **title_style)
        title_info.grid(row=1, column=0, columnspan=2)

        self.max_label_text = tk.StringVar(value="Max value: X")
        max_label = tk.Label(
            frame, textvariable=self.max_label_text, **text_style)
        max_label.grid(row=2, column=0, sticky="E")

        zoom_label_text = tk.StringVar(value="Zoom value:")
        zoom_label = tk.Label(
            frame, textvariable=zoom_label_text, **text_style)
        zoom_label.grid(row=3, column=0, sticky="W")
        zoom_label_value = tk.Label(
            frame, textvariable=self.zoom, anchor=tk.W, **text_style)
        zoom_label_value.grid(row=3, column=1, sticky="W")

        time_label_text = tk.StringVar(value="Computation time:")
        time_label = tk.Label(
            frame, textvariable=time_label_text, **text_style)
        time_label.grid(row=4, column=0, sticky="W")
        time_label_value = tk.Label(
            frame, textvariable=self.computation_time, anchor=tk.W, **text_style)
        time_label_value.grid(row=4, column=1, sticky="W")

        fps_label_text = tk.StringVar(value="FPS:")
        fps_label = tk.Label(
            frame, textvariable=fps_label_text, **text_style)
        fps_label.grid(row=5, column=0, sticky="W")
        fps_label_value = tk.Label(
            frame, textvariable=self.fps, anchor=tk.W, **text_style)
        fps_label_value.grid(row=5, column=1, sticky="W")

    def new_random(self):
        self.canvas.new_random_seed()
        self.update_canvas()

    def change_color_mode(self):
        ''' Forget previous layout and apply new one '''
        self.RGB_mode_menu.grid_forget()
        self.HSV_mode_menu.grid_forget()
        self.BW_mode_menu.grid_forget()
        self.formula_entry.grid_forget()
        self.three_formula_frame.grid_forget()
        if self.color_mode.get() == "HSV":
            self.HSV_mode_menu.grid(row=3, column=1, columnspan=3)
        if self.color_mode.get() == "RGB":
            self.RGB_mode_menu.grid(row=3, column=1, columnspan=3)
        if self.color_mode.get() == "BW":
            self.BW_mode_menu.grid(row=3, column=1, columnspan=3)
        if self.color_mode.get() in ["HSV", "RGB", "BW"]:
            self.formula_entry.grid(row=3, column=1, columnspan=5, pady=5)
        if self.color_mode.get() == "R/G/B":
            self.RGB_mode_menu.grid(row=3, column=1, columnspan=3)
            self.three_formula_frame.grid(row=3, column=1, columnspan=5)
        self.canvas.set_color_mode(self.color_mode.get())
        self.update_canvas()

    def apply_function(self):
        self.active_function = self.formula.get()

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
            self.userdef_entry.get("1.0", END), self.sliders)
        self.error_userdef.set(error_str)
        self.update_canvas()

    def compute_minmax(self):
        self.canvas.minx = self.zoom.get()*(-640)/100
        self.canvas.maxx = self.zoom.get()*(+640)/100
        self.canvas.miny = self.zoom.get()*(-360)/100
        self.canvas.maxy = self.zoom.get()*(+360)/100

    class MouseMover():

        def __init__(self, window, label):
            self.last_x = 0
            self.last_y = 0
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
            self.last_x = event.x
            self.last_y = event.y

        def drag_b1(self, event):
            sx = self.window.canvas.sizex
            sy = self.window.canvas.sizey
            dx = self.window.canvas.maxx-self.window.canvas.minx
            dy = self.window.canvas.maxy-self.window.canvas.miny

            self.window.canvas.offx += (event.x - self.last_x) * dx/sx
            self.window.canvas.offy += (event.y - self.last_y) * dy/sy
            self.last_x = event.x
            self.last_y = event.y
            self.window.update_canvas()

    ### --- I/O parameters and images --- ###

    def save_image(self):
        name = simpledialog.askstring("", "Name of this image?")
        if name:
            if self.save_with_max_resolution.get():
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

        while os.path.exists("parameters/"+name+".json"):
            name = simpledialog.askstring(
                "", "Name already exists, please pick another one")

        json_data = {}
        json_data['formula'] = self.formula.get()
        json_data['formulaRed'] = self.formula_R.get()
        json_data['formulaGreen'] = self.formula_G.get()
        json_data['formulaBlue'] = self.formula_B.get()
        json_data['menu_parameters'] = {
            'offx': self.canvas.offx,
            'offy': self.canvas.offy,
            'zoom': self.zoom.get(),
            'sigma': self.sl_sigma.get(),
            'resolution': self.sl_res.get(),
            'colorMode': self.color_mode.get(),
            'randomModulation': self.random_modulation.get(),
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

        json_data['userdef_entry'] = self.userdef_entry.get("1.0", END)

        with open("parameters/"+name+".json", 'a') as outfile:
            json.dump(json_data, outfile, sort_keys=True, indent=4)

    def open_random(self):
        dir = "./parameters"
        random.seed()
        file = random.choice([dir + "/" + x for x in os.listdir(
            dir) if os.path.isfile(os.path.join(dir, x))])
        print("Opening "+file)
        self.load_params(filepath=file)

    def load_params(self, append=False, filepath=""):

        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir="./parameters/",
                                                  title="Select parameters file",
                                                  filetypes=(("json files", "*.json"), ("all files", "*.*")))

        if filepath == ():
            return

        if not(append):
            self.delete_sliders()

        with open(filepath) as json_file:
            json_data = json.load(json_file)
            if not(append):
                self.active_function = json_data['formula']
            else:
                self.active_function += " + "+json_data['formula']
            self.formula.set(self.active_function)
            self.formula_entry.delete(0, END)
            self.formula_entry.insert(0, self.active_function)

            menu_params = json_data['menu_parameters']
            self.canvas.offx = menu_params['offx']
            self.canvas.offy = menu_params['offy']
            self.sl_sigma.set(menu_params['sigma'])
            self.sl_res.set(menu_params['resolution'])
            self.color_mode.set(menu_params['colorMode'])
            self.random_modulation.set(menu_params['randomModulation'])
            self.sl_s_value.set(menu_params['sValue'])
            self.sl_v_value.set(menu_params['vValue'])
            self.sl_bw_scale.set(menu_params['bwScale'])
            self.sl_rgb_scale.set(menu_params['rgbScale'])

            if 'zoom' in menu_params.keys():
                self.zoom.set(round(menu_params['zoom'], 5))

            attributes = [('formulaRed', self.formula_R), ('formulaGreen',
                                                           self.formula_G), ('formulaBlue', self.formula_B)]

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
                self.userdef_entry.delete('1.0', END)
            self.userdef_entry.insert(END, json_data['userdef_entry'])

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
        for param_name in self.sliders:
            sl = self.sliders[param_name]
            self.slider_dict[param_name] = sl.get()

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
        new_sl = tk.Scale(self.user_slider_frame,
                          orient=tk.VERTICAL, command=self.update_canvas, **scale_style)
        new_sl.set(value)
        new_sl.grid(row=4, column=len(self.sliders))
        tk.Label(self.user_slider_frame, text="slider." + name, padx=5, pady=5,
                 **text_style).grid(row=3, column=len(self.sliders), sticky="E")
        self.sliders[name] = new_sl

    def delete_sliders(self):
        self.sliders = {}
        for widget in self.user_slider_frame.winfo_children():
            widget.destroy()
        self.slider_dict = self.SliderDict()
