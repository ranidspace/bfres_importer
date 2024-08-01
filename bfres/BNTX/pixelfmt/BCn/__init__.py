#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DXT1/3/5 Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

################################################################
################################################################

from . import decompress_
from .. import TextureFormat

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

    def decompressDXT5(self, tex):
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