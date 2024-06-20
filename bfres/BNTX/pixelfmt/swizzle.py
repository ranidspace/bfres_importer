# This file is part of botwtools.
#
# botwtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# botwtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with botwtools.  If not, see <https://www.gnu.org/licenses/>.
import logging; log = logging.getLogger(__name__)
import struct
import math


def countLsbZeros(val):
    cnt = 0
    while ((val >> cnt) & 1) == 0: cnt += 1
    return cnt


class Swizzle:
    def __init__(self, width, bpp, blkHeight=16):
        self.width = width
        self.bpp   = bpp

    def getOffset(self, x, y):
        return (y * self.width) + x


class BlockLinearSwizzle(Swizzle):
    def __init__(self, width, bpp, blockHeightLog2, blkHeight=16):
        self.width     = int((width  + 3) / 4)
        self.pitch     = ((width * bpp - 1) | (31)) + 1
        self.bpp       = bpp
        widthGobs      = math.ceil(width * bpp / 64.0)
        self.gobStride = 512 * blkHeight * widthGobs
        self.blockHeight = 1 << blockHeightLog2

    def getOffset(self, x, y):
        GOB_address = (0
                   + (y // (8 * self.blockHeight)) * self.gobStride
                   + (x * self.bpp // 64) * 512 * self.blockHeight
                   + (y % (8 * self.blockHeight) // 8) * 512)
        
        x *= self.bpp

        return (GOB_address + ((x % 64) // 32) * 256 + ((y % 8) // 2) * 64
               + ((x % 32) // 16) * 32 + (y % 2) * 16 + (x % 16))

        '''x <<= self.bppShift
        return (
            ((y >> self.bhShift) * self.gobStride) +
            ((x >> 6) << self.xShift) +
            (((y & self.bhMask) >> 3) << 9) +
            (((x & 0x3F) >> 5) << 8) +
            (((y & 0x07) >> 1) << 6) +
            (((x & 0x1F) >> 4) << 5) +
            ( (y & 0x01)       << 4) +
            (  x & 0x0F)
        )'''
