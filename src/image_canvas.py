import numpy as np
from PIL import Image, ImageTk
from scipy.ndimage.filters import gaussian_filter
import src.userdef as user
import math
import random


use_global_image = False
# functionality works, but still needs refinement
# just set to True to test it
if use_global_image:
    imgStar = Image.open('starrynight.jpg')


def func(xx, yy, offx, offy, slider={}, f="", random_seed=0):
    '''Generic function that computes pixel values for canvas'''
    i = xx-offx
    j = yy-offy
    random.seed(random_seed)
    np.random.seed(random_seed)

    image = eval(f)
    if type(image).__module__ != 'numpy':
        print("Warning: your formula leads to invalid arrays.")
        if isinstance(image, int) or isinstance(image, float):
            print("Interpreting formula as a constant.")
            image = np.full((yy.shape[0], xx.shape[1]), image)
    return image


class Canvas:

    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey

        # Default values
        self.res = 30
        self.offx = 0
        self.offy = 0
        self.randomSeed = 0
        self.colorMode = "HSV"
        self.activeFunction = "i**2 + j**2"
        self.functionRed = "i**2 + j**2"
        self.functionGreen = "i**2 + j**2"
        self.functionBlue = "i**2 + j**2"
        self.sliderDict = {}
        self.randomModulation = False
        self.s_value = 200
        self.v_value = 200
        self.rgb_scale = 255
        self.bw_scale = 100
        self.sigma = 0

    def generateImage(self):
        resx = self.res*1600//100
        resy = self.res*900//100
        stepx = (self.maxx-self.minx)/resx
        stepy = (self.maxy-self.miny)/resy

        x = np.arange(self.minx, self.maxx, stepx)
        y = np.arange(self.miny, self.maxy, stepy)
        xx, yy = np.meshgrid(x, y, sparse=True)

        if self.colorMode != "R/G/B":
            res = func(xx, yy, self.offx, self.offy,
                       self.sliderDict, self.activeFunction,
                       self.randomSeed)
            res = res.transpose()

            res = res[:resx, :resy]
            if res.shape[1] > resy:  # fix potential floating error imprecision
                res = res[:, :-1]

            normalized = False
            if normalized:
                res = 256*res/np.max(res)

            if self.randomModulation:
                np.random.seed(self.randomSeed)
                randMat = np.random.rand(res.shape[0], res.shape[1])
                res = res*randMat

            if self.colorMode == "HSV":
                type0 = "uint8"
                array = np.zeros((3, resx, resy), type0)
                array[0, :, :] = res % (256*256*256)
                array[1, :, :] = np.full(
                    (res.shape[0], res.shape[1]), self.s_value, type0)
                array[2, :, :] = np.full(
                    (res.shape[0], res.shape[1]), self.v_value, type0)

                if use_global_image:
                    global imgStar
                    imgResized = imgStar.resize((resx, resy))
                    imgNp = np.asarray(imgResized, dtype="uint8")
                    np.add(array[0, :, :], imgNp[:, :, 0].transpose(
                    ), out=array[0, :, :], casting="unsafe")
                    np.add(array[1, :, :], imgNp[:, :, 1].transpose(
                    ), out=array[1, :, :], casting="unsafe")
                    np.add(array[2, :, :], imgNp[:, :, 2].transpose(
                    ), out=array[2, :, :], casting="unsafe")

            elif self.colorMode == "RGB":
                scale = self.rgb_scale
                max_value = min(scale, 256)

                array = np.zeros((3, resx, resy), 'uint8')
                array[0, :, :] = res % max_value
                array[1, :, :] = (res/max_value) % max_value
                array[2, :, :] = (res/(max_value*max_value)) % max_value

                if use_global_image:
                    imgResized = imgStar.resize((resx, resy))
                    imgNp = np.asarray(imgResized, dtype="uint8")
                    np.add(array[0, :, :], imgNp[:, :, 0].transpose(
                    ), out=array[0, :, :], casting="unsafe")
                    np.add(array[1, :, :], imgNp[:, :, 1].transpose(
                    ), out=array[1, :, :], casting="unsafe")
                    np.add(array[2, :, :], imgNp[:, :, 2].transpose(
                    ), out=array[2, :, :], casting="unsafe")

            else:  # BW
                array = res

        else:  # R/G/B
            scale = self.rgb_scale
            max_value = min(scale, 256)
            array = np.zeros((3, resx, resy), 'uint8')
            functions = [self.functionRed,
                         self.functionGreen, self.functionBlue]
            for channel in range(3):
                res = func(xx, yy, self.offx, self.offy, self.sliderDict,
                           functions[channel])
                res = res.transpose()

                res = res[:resx, :resy]
                if res.shape[1] > resy:  # fix potential floating error imprecision
                    res = res[:, :-1]

                if self.randomModulation:
                    randMat = np.random.rand(res.shape[0], res.shape[1])
                    res = res*randMat

                array[channel, :, :] = res % max_value

        sigma = self.sigma/100
        if sigma > 0:
            if array.ndim == 3:
                array[0, :, :] = gaussian_filter(
                    array[0, :, :], sigma=sigma)
                array[1, :, :] = gaussian_filter(
                    array[1, :, :], sigma=sigma)
                array[2, :, :] = gaussian_filter(
                    array[2, :, :], sigma=sigma)
            else:
                array[:, :] = gaussian_filter(array[:, :], sigma=sigma)

        if self.colorMode == "HSV":
            array = np.ascontiguousarray(array.transpose(2, 1, 0))
            if (array.shape[0] < self.sizey):
                stepx = self.sizex//array.shape[1]
                stepy = self.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array, 'HSV')

        elif self.colorMode in ["RGB", "R/G/B"]:
            array = np.ascontiguousarray(array.transpose(2, 1, 0))

            if (array.shape[0] < self.sizey):
                stepx = self.sizex//array.shape[1]
                stepy = self.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)

            img0 = Image.fromarray(array, 'RGB')
        else:  # mode == "BW"
            array *= float(self.bw_scale/100)
            if (array.shape[0] < self.sizey):
                stepx = self.sizex//array.shape[1]
                stepy = self.sizey//array.shape[0]
                array = np.repeat(array, stepx, axis=0)
                array = np.repeat(array, stepy, axis=1)
            img0 = Image.fromarray(array.transpose())

        self.max_value = res.max()
        self.fullImage = img0  # saving full res picture to output it

        ANTIALIAS = False
        if ANTIALIAS:
            img0 = img0.resize(
                (self.sizex, self.sizey), Image.ANTIALIAS)
        else:
            img0 = img0.resize((self.sizex, self.sizey))

        img = ImageTk.PhotoImage(img0)
        return img

    def saveImage(self, name):
        self.fullImage.convert('RGB').save(
            "Images/{}.png".format(name))

    def setMinMax(self, pairx, pairy):
        self.minx, self.maxx = pairx
        self.miny, self.maxy = pairy

    def getMax(self):
        return self.max_value

    def setRes(self, res):
        self.res = res

    def setOff(self, offx, offy):
        self.offx = offx
        self.offy = offy

    def setColorMode(self, mode):
        self.colorMode = mode

    def setFunction(self, f):
        self.activeFunction = f

    def setFunctionRed(self, f):
        self.functionRed = f

    def setFunctionGreen(self, f):
        self.functionGreen = f

    def setFunctionBlue(self, f):
        self.functionBlue = f

    def setSliderDict(self, sl_dict):
        self.sliderDict = sl_dict

    def setRandomMod(self, boolean):
        self.randomModulation = boolean

    def setSValue(self, s):
        self.s_value = s

    def setVValue(self, v):
        self.v_value = v

    def setRGBScale(self, scale):
        self.rgb_scale = scale

    def setBWScale(self, scale):
        self.bw_scale = scale

    def setSigma(self, sigma):
        self.sigma = sigma

    def newRandomSeed(self):
        self.randomSeed = random.randrange(0, 100000)
