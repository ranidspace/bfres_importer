#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DXT1/3/5 Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

################################################################
################################################################

from . import decompress_
from .. import TextureFormat
import numpy as np

class BC1(TextureFormat):
    id = 0x1a
    bytesPerPixel = 4
    depth = 8

    def decompress(self, tex):
        data = tex.mipData
        width = tex.width
        height = tex.height
        if not isinstance(data, bytes):
            try:
                data = bytes(data)

            except:
                print("Couldn't decompress data")
                return b''

        csize = ((width + 3) // 4) * ((height + 3) // 4) * 8
        if len(data) < csize:
            print("Compressed data is incomplete")
            return b''

        data = data[:csize]
        return decompress_.decompressDXT1(data, width, height)
    
class BC2(TextureFormat):
    id = 0x1b
    bytesPerPixel = 4
    depth = 8

    def decompress(self, tex):
        data = tex.mipData
        width = tex.width
        height = tex.height
        if not isinstance(data, bytes):
            try:
                data = bytes(data)

            except:
                print("Couldn't decompress data")
                return b''

        csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
        if len(data) < csize:
            print("Compressed data is incomplete")
            return b''

        data = data[:csize]
        return decompress_.decompressDXT3(data, width, height)
    
class BC3(TextureFormat):
    id = 0x1c
    bytesPerPixel = 4
    depth = 8

    def decompress(self, tex):
        data = tex.mipData
        width = tex.width
        height = tex.height
        if not isinstance(data, bytes):
            try:
                data = bytes(data)

            except:
                print("Couldn't decompress data")
                return b''

        csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
        if len(data) < csize:
            print("Compressed data is incomplete")
            return b''

        data = data[:csize]
        return decompress_.decompressDXT5(data, width, height)

class BC4(TextureFormat):
    id = 0x1d
    bytesPerPixel = 4
    depth = 8

    def decompress(data, tex):
        data = tex.mipData
        width = tex.width
        height = tex.height
        SNORM = 0 if tex.header['fmt_dtype'] == 1 else 1
        if not isinstance(data, bytes):
            try:
                data = bytes(data)

            except:
                print("Couldn't decompress data")
                return b''

        csize = ((width + 3) // 4) * ((height + 3) // 4) * 8
        if len(data) < csize:
            print("Compressed data is incomplete")
            return b''

        data = data[:csize]
        return decompress_.decompressBC4(data, width, height, SNORM)
    
    def decodePixels(self, data):
        rgba = np.empty(len(data)*4)
        rgba[0::4] = rgba[1::4] = rgba[2::4] = np.frombuffer(data, dtype='B') / 255
        rgba[3::4] = 1
        return rgba

class BC5(TextureFormat):
    id = 0x1e
    bytesPerPixel = 4
    depth = 8

    def decompress(self, tex):
        data = tex.mipData
        width = tex.width
        height = tex.height
        SNORM = 0 if tex.header['fmt_dtype'] == 1 else 1
        if not isinstance(data, bytes):
            try:
                data = bytes(data)

            except:
                print("Couldn't decompress data")
                return b''

        csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
        if len(data) < csize:
            print("Compressed data is incomplete")
            return b''

        data = data[:csize]
        return decompress_.decompressBC5(data, width, height, SNORM)
    
    def decodePixels(self, data):
        r = data[0].astype(np.float32) / 255
        g = data[1].astype(np.float32) / 255
        x = r * 2 - 1
        y = g * 2 - 1
        z = abs(1 - x**2 - y**2)**0.5
        rgba = np.empty(data.size*2, dtype=np.float32)
        rgba[0::4] = r
        rgba[1::4] = g
        rgba[2::4] = np.real((z + 1) * 0.5)
        rgba[3::4] = 1
        return rgba