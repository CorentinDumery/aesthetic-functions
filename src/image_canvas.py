import numpy as np
from PIL import Image, ImageTk
from scipy.ndimage.filters import gaussian_filter
import math
import random

use_global_image = False
# functionality works, but still needs refinement
# just set to True to test it
if use_global_image:
    img_star = Image.open("starrynight.jpg")


class Canvas:
    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey

        # Default values
        self.resolution = 30
        self.offx = 0
        self.offy = 0
        self.random_seed = 0
        self.color_mode = "HSV"
        self.active_function = "i**2 + j**2"
        self.function_R = "i**2 + j**2"
        self.function_G = "i**2 + j**2"
        self.function_B = "i**2 + j**2"
        self.slider_dict = {}
        self.random_modulation = False
        self.s_value = 200
        self.v_value = 200
        self.rgb_scale = 255
        self.bw_scale = 100
        self.sigma = 0

    def generate_array(self, x_values, y_values, slider={}, f=""):
        """Generic function that computes pixel values for canvas"""
        i = x_values - self.offx
        j = y_values - self.offy
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

        import src.userdef as user

        image = eval(f)
        if type(image).__module__ != "numpy":
            print("Warning: your formula leads to invalid arrays.")
            if isinstance(image, int) or isinstance(image, float):
                print("Interpreting formula as a constant.")
                image = np.full((y_values.shape[0], x_values.shape[1]), image)
        return image

    def generate_image(self):
        resx = self.resolution * 1600 // 100
        resy = self.resolution * 900 // 100
        stepx = (self.maxx - self.minx) / resx
        stepy = (self.maxy - self.miny) / resy

        x = np.arange(self.minx, self.maxx, stepx)
        y = np.arange(self.miny, self.maxy, stepy)
        xx, yy = np.meshgrid(x, y, sparse=True)

        if self.color_mode != "R/G/B":
            res = self.generate_array(xx, yy, self.slider_dict, self.active_function)
            res = res.transpose()

            res = res[:resx, :resy]
            if res.shape[1] > resy:  # fix potential floating error imprecision
                res = res[:, :-1]

            normalized = False  # Could be worth adding this to interface
            if normalized:
                res = 256 * res / np.max(res)

            if self.random_modulation:
                np.random.seed(self.random_seed)
                res = res * np.random.rand(res.shape[0], res.shape[1])

            if self.color_mode == "HSV":
                type0 = "uint8"
                array = np.zeros((3, resx, resy), type0)
                array[0, :, :] = res % (256 * 256 * 256)
                array[1, :, :] = np.full(
                    (res.shape[0], res.shape[1]), self.s_value, type0
                )
                array[2, :, :] = np.full(
                    (res.shape[0], res.shape[1]), self.v_value, type0
                )

                if use_global_image:  # WIP
                    global img_star
                    img_resized = img_star.resize((resx, resy))
                    img_np = np.asarray(img_resized, dtype="uint8")
                    np.add(
                        array[0, :, :],
                        img_np[:, :, 0].transpose(),
                        out=array[0, :, :],
                        casting="unsafe",
                    )
                    np.add(
                        array[1, :, :],
                        img_np[:, :, 1].transpose(),
                        out=array[1, :, :],
                        casting="unsafe",
                    )
                    np.add(
                        array[2, :, :],
                        img_np[:, :, 2].transpose(),
                        out=array[2, :, :],
                        casting="unsafe",
                    )

            elif self.color_mode == "RGB":
                scale = self.rgb_scale
                max_value = min(scale + 1, 256)

                array = np.zeros((3, resx, resy), "uint8")
                array[0, :, :] = res % max_value
                array[1, :, :] = (res / max_value) % max_value
                array[2, :, :] = (res / (max_value * max_value)) % max_value

                if use_global_image:  # WIP
                    img_resized = img_star.resize((resx, resy))
                    img_np = np.asarray(img_resized, dtype="uint8")
                    np.add(
                        array[0, :, :],
                        img_np[:, :, 0].transpose(),
                        out=array[0, :, :],
                        casting="unsafe",
                    )
                    np.add(
                        array[1, :, :],
                        img_np[:, :, 1].transpose(),
                        out=array[1, :, :],
                        casting="unsafe",
                    )
                    np.add(
                        array[2, :, :],
                        img_np[:, :, 2].transpose(),
                        out=array[2, :, :],
                        casting="unsafe",
                    )

            else:  # BW
                array = res

        else:  # R/G/B
            scale = self.rgb_scale
            max_value = min(scale + 1, 256)
            array = np.zeros((3, resx, resy), "uint8")
            functions = [self.function_R, self.function_G, self.function_B]
            for channel in range(3):
                res = self.generate_array(xx, yy, self.slider_dict, functions[channel])
                res = res.transpose()

                res = res[:resx, :resy]
                if res.shape[1] > resy:  # fix potential floating error imprecision
                    res = res[:, :-1]

                if self.random_modulation:
                    np.random.seed(self.random_seed)
                    res = res * np.random.rand(res.shape[0], res.shape[1])

                array[channel, :, :] = res % max_value

        sigma = self.sigma / 100
        if sigma > 0:
            if array.ndim == 3:
                array[0, :, :] = gaussian_filter(array[0, :, :], sigma=sigma)
                array[1, :, :] = gaussian_filter(array[1, :, :], sigma=sigma)
                array[2, :, :] = gaussian_filter(array[2, :, :], sigma=sigma)
            else:
                array[:, :] = gaussian_filter(array[:, :], sigma=sigma)

        if self.color_mode == "HSV":
            array = np.ascontiguousarray(array.transpose(2, 1, 0))
            if array.shape[0] < self.sizey:
                stepx = self.sizex // array.shape[1]
                stepy = self.sizey // array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array, "HSV")

        elif self.color_mode in ["RGB", "R/G/B"]:
            array = np.ascontiguousarray(array.transpose(2, 1, 0))
            if array.shape[0] < self.sizey:
                stepx = self.sizex // array.shape[1]
                stepy = self.sizey // array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array, "RGB")

        else:  # mode == "BW"
            array *= float(self.bw_scale / 100)
            if array.shape[0] < self.sizey:
                stepx = self.sizex // array.shape[1]
                stepy = self.sizey // array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array.transpose())

        self.max_value = res.max()
        self.full_image = img0  # saving full res picture before resize
        img0 = img0.resize((self.sizex, self.sizey))
        img = ImageTk.PhotoImage(img0)
        return img

    def save_image(self, name):
        self.full_image.convert("RGB").save("images/{}.png".format(name))

    def set_minmax(self, pairx, pairy):
        self.minx, self.maxx = pairx
        self.miny, self.maxy = pairy

    def get_max(self):
        return self.max_value

    def set_color_mode(self, mode):
        self.color_mode = mode

    def set_function(self, f):
        self.active_function = f

    def set_function_R(self, f):
        self.function_R = f

    def set_function_G(self, f):
        self.function_G = f

    def set_function_B(self, f):
        self.function_B = f

    def set_slider_dict(self, sl_dict):
        self.slider_dict = sl_dict

    def new_random_seed(self):
        self.random_seed = random.randrange(0, 100000)
