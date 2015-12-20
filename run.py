#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import struct


class ColorSwatch_v1():
    __rawdata = []
    __typename = ""

    def __init__(self, file):
        self.rawdata = struct.unpack(">5H", file.read(10))
        self.typename = self.colorTypeName()

    def colorTypeName(self):
        try:
            return {0: "RGB", 1: "HSB",
                    2: "CMYK", 7: "Lab",
                    8: "Grayscale"}[self.rawdata[0]]
        except IndexError:
            print
            self.rawdata[0]

    def __strCMYK(self):
        rgb8bit = map(lambda a: (65535 - a) / 655.35, self.rawdata[1:])
        return "{name} ({typename}): {0}% {1}% {2}% {3}%".format(*rgb8bit, **self.__dict__)

    def __strRGB(self):
        rgb8bit = map(lambda a: int(a / 256), self.rawdata[1:4])
        return "{name} ({typename}): R: {0:<3.0f} G: {1:<3.0f} B: {2:<3.0f}".format(*rgb8bit, **self.__dict__)

    def __strGrayscale(self):
        gray = self.rawdata[1] / 100.
        return "{name} ({typename}): {0}%".format(gray, **self.__dict__)

    def __str__(self):
        return {0: self.__strRGB, 1: "HSB",
                2: self.__strCMYK, 7: "Lab",
                8: self.__strGrayscale}[self.rawdata[0]]()


class ColorSwatch_v2(ColorSwatch_v1):
    def __init__(self, file):
        super(ColorSwatch_v2, self).__init__(file)
        namelen, = struct.unpack(">I", file.read(4))
        cp = file.read(2 * namelen)
        self.name = cp[0:-2].decode('utf-16-be')  # skip last whitespace


if len(sys.argv) < 1:
    print("No file in arg")
else:
    with open(sys.argv[1], "rb") as file:
        # Read colors for version 1
        version_bytes = file.read(2)
        ver, = struct.unpack(">H", version_bytes)
        if (ver != 1):
            raise TypeError("Probably not a adobe aco file")
        count = file.read(2)
        count, = struct.unpack(">H", count)
        colors_v1 = file.seek(count * 10, 1)

        # Read colors for version 2
        version_bytes = file.read(2)
        ver, = struct.unpack(">H", version_bytes)
        count = file.read(2)
        count, = struct.unpack(">H", count)
        for _ in range(count):
            swatch = ColorSwatch_v2(file)
            print(str(swatch))
