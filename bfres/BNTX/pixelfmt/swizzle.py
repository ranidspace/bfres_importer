# This file is a modified file from
# https://github.com/aboood40091/BNTX-Editor/
# Which is licensed under GPL-3

import logging; log = logging.getLogger(__name__)
import struct
import math

def DIV_ROUND_UP(n, d):
    return (n + d - 1) // d

def round_up(x, y):
    return ((x - 1) | (y - 1)) + 1


def pow2_round_up(x):
    x -= 1
    x |= x >> 1
    x |= x >> 2
    x |= x >> 4
    x |= x >> 8
    x |= x >> 16

    return x + 1
    
def deswizzle(width, height, blkWidth, blkHeight, bpp, tileMode, blockHeightLog2, data):
    '''Function which returns deswizzled image data'''
    # Modified from https://github.com/aboood40091/BNTX-Editor/ which is under a GPL-3.0 License
    blockHeight = 1 << blockHeightLog2

    width = DIV_ROUND_UP(width, blkWidth)
    height = DIV_ROUND_UP(height, blkHeight)
    
    if tileMode == 1:
        pitch = width * bpp

        # If wii u support is added this depends on if the header of the texture is "NX" or not
        pitch = round_up(pitch, 32)

        surfSize = pitch * height

    else:
        pitch = round_up(width * bpp, 64)
        surfSize = pitch * round_up(height, blockHeight * 8)


    result = bytearray(surfSize)

    for y in range(height):
        for x in range(width):
            if tileMode == 1:
                pos = y * pitch + x * bpp

            else:
                pos = getAddrBlockLinear(x, y, width, bpp, 0, blockHeight)

            pos_ = (y * width + x) * bpp

            if pos + bpp <= surfSize:
                result[pos_:pos_ + bpp] = data[pos:pos + bpp]

    return result




def getAddrBlockLinear(x, y, image_width, bytes_per_pixel, base_address, blockHeight):
    image_width_in_gobs = DIV_ROUND_UP(image_width * bytes_per_pixel, 64)
    GOB_address = (base_address
                   + (y // (8 * blockHeight)) * 512 * blockHeight * image_width_in_gobs
                   + (x * bytes_per_pixel // 64) * 512 * blockHeight
                   + (y % (8 * blockHeight) // 8) * 512)

    x *= bytes_per_pixel

    Address = (GOB_address + ((x % 64) // 32) * 256 + ((y % 8) // 2) * 64
               + ((x % 32) // 16) * 32 + (y % 2) * 16 + (x % 16))

    return Address