
###############################################################################
# Name:         imgio
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019-12-07
# Version:      [0.2.1]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import numpy as np
from PIL import Image as PilImageModule
from imageio import imread, imwrite
imsave = imwrite

def shape2size(shape):
    """ im_arr.shape: {h, w, c}
        PIL.Image.size: {w, h}
    """
    size = (shape[1], shape[0])
    return size

def shape2mode(shape):
    if len(shape) < 3:
        return "L"
    elif shape[2] == 3:
        return "RGB"  # 无法区分BGR (OpenCV)
    elif shape[2] == 4:
        return "RGBA"
    else:
        raise Exception("未知的图像类型")

def guess_mode(im_arr):
    """ 一种预测图像mode的简单方式 """
    if im_arr.ndim < 3:
        return "L"
    else:
        return shape2mode(im_arr.shape)


class ImageConverter:
    """ 内部使用numpy::array存储数据
        mode: "1", "L", "P", "RGB", "BGR", "RGBA", "YUV", "LAB"
    """
    def mode(self):
        return self._img.mode

    def width(self):
        return self._img.width()

    def height(self):
        return self._img.height()

    #####################################################################
    def convert(self, mode):
        if mode == self._img.mode:
            return
        self._img = self._img.convert(mode)

    # IO
    def open(self, path_file):
        self._img = PilImageModule.open(path_file, "r")

    def save(self, path_file):
        # with open(path_file, "wb") as fp:
        self._img.save(path_file)

    # def load(self, arg=None, **kwargs):
    #     if arg is None:
    #         self._img = None  # PIL::Image
    #     elif len(kwargs) == 0 and isPath(arg):
    #         self.open(arg)
    #     elif len(kwargs) == 1 and isinstance(arg, np.ndarray):
    #         self.from_numpy(arg, mode=kwargs["mode"])
    #     elif len(kwargs) == 2 and isinstance(arg, (bytes, bytearray)):
    #         self.from_bytes(arg, kwargs["mode"], kwargs["size"])
    #     else:
    #         raise Exception(f"Unkown arguments to load: 【arg:{arg}, kwargs:{kwargs}】")

    def from_bytes(self, data, mode, **kwargs):
        """ mode: "1", "L", "P", "RGB", "RGBA", "CMYK"...
        """
        if "size" in kwargs:
            size = kwargs["size"]
        elif "shape" in kwargs:
            size = shape2size(kwargs["shape"])
        else:
            raise Exception("必须传入size或shape参数")

        self._img = PilImageModule.frombytes(mode, size, data)

    def to_bytes(self):
        return self._img.tobytes()

    def from_numpy(self, im_arr, mode):
        """ 这里设定mode为显式参数，因为无法通过channel完全确定mode：
            * 2dim: "1", "L", "P", "I", "F"
            * 3dim: "RGB", "BGR"
            * 4dim: "RGBA", "CMYK", "YCbCr"
        """
        if mode == "BGR":
            self.from_opencv(im_arr)
            return
        self._img = PilImageModule.fromarray(im_arr, mode)

    def to_numpy(self):
        im = np.asarray(self._img)
        return im

    def from_qtimg(self, qt_img, type="QPixmap"):
        if type == "QPixmap":
            self._img = PilImageModule.fromqpixmap(qt_img)
        elif type == "QImage":
            self._img = PilImageModule.fromqimage(qt_img)
        else:
            raise Exception(f"Unkown type 【{type}】")

    def to_qtimg(self, type="QPixmap"):
        if type == "QPixmap":
            return self._img.toqpixmap()
        elif type == "QImage":
            return self._img.toqimage()
        else:
            raise Exception(f"Unkown type 【{type}】")

    # def from_opencv(self, im_arr, cv_mode="BGR"):
    #     if len(im_arr.shape) < 3:
    #         assert len(cv_mode) == 1, f"当前nadrray的维度与参数cv_mode【{cv_mode}】不匹配"
    #     elif cv_mode == "RGB":
    #         pass
    #     elif cv_mode == "BGR":
    #         im_arr = bgr2rgb(im_arr)
    #         cv_mode = "RGB"
    #     else:
    #         raise Exception("敬请期待")
    #     self.from_numpy(im_arr, cv_mode)

    # def to_opencv(self):
    #     # opencv 不处理 ndim>3 的图像
    #     im_arr = self.to_numpy()
    #     if len(im_arr.shape) >= 3:  # 保存为3维数据
    #         if self.mode != "RGB":
    #             # im_arr = np.delete(im_arr, -1, axis=1)
    #             self._img.convert("RGB")
    #         im_arr = rgb2bgr(im_arr)
    #     return im_arr

    def from_pillow(self, pil_img):
        self._img = pil_img

    def to_pillow(self):
        return self._img


converter = ImageConverter()  # 全局转换器对象，用于图片格式转换

def ndarray2pixmap(im_arr, mode=None):
    if mode is None:
        mode = guess_mode(im_arr)

    converter.from_numpy(im_arr, mode)
    pixmap = converter.to_qtimg()
    return pixmap

def pixmap2ndarray(pixmap):
    converter.from_qtimg(pixmap)
    im_arr = converter.to_numpy()
    return im_arr

def ndarray2bytes(im_arr, mode=None):
    if mode is None:
        mode = guess_mode(im_arr)

    converter.from_numpy(im_arr, mode)
    bytes_ = converter.to_bytes()
    return bytes_

def bytes2ndarray(data, mode, **kwargs):
    """ kwargs:
            - size: (w, h)
            - shape: (h, w, ...)
    """
    if "size" in kwargs:
        size = kwargs["size"]
    elif "shape" in kwargs:
        size = shape2size(kwargs["shape"])
    else:
        raise Exception("必须传入size或shape参数")

    converter.from_bytes(data, mode, size)
    im_arr = converter.to_numpy()
    return im_arr

def pillow2ndarray(pil_img):
    im_arr = np.asarray(pil_img)
    return im_arr

    # converter.from_pillow(pil_img)
    # im_arr = converter.to_numpy()
    # return im_arr

def ndarray2pillow(im_arr, mode=None):
    if mode is None:
        mode = guess_mode(im_arr)

    converter.from_numpy(im_arr, mode)
    return converter._img

def convert_mode(im_arr, mode_to, mode_from=None):
    if mode_from is None:
        mode_from = guess_mode(im_arr)

    if mode_to == mode_from:
        return im_arr
    else:
        converter.from_numpy(im_arr, mode_from)
        converter.convert(mode_to)
        im_arr2 = converter.to_numpy()
        return im_arr2


#####################################################################
def deprecated():

    def opencv2rgb(color_space):
        if color_space == "GRAY":
            raise Exception("敬请期待")

        elif color_space == "BGR":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif color_space == "HSV":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
        elif color_space == "LAB":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_LAB2RGB)
        elif color_space == "YUV":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_YUV2RGB)
        elif color_space == "YCrCb":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_YCrCb2RGB)  # COLOR_BGR2YCR_CB
        else:
            raise Exception("未知的图像色彩空间")

        return img_rgb
