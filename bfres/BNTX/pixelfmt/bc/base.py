import logging; log = logging.getLogger(__name__)
import struct
from ..base import TextureFormat


def unpackRGB565(pixel):
    r = (((pixel) << 3) & 0xf8) | (((pixel) >>  2) & 0x07)
    g = (((pixel) >> 3) & 0xfc) | (((pixel) >>  9) & 0x03)
    b = (((pixel) >> 8) & 0xf8) | (((pixel) >> 13) & 0x07)
    return r, g, b, 0xFF


def clamp(val):
    if val > 1: return 0xFF
    if val < 0: return 0
    return int(val * 0xFF)

def ToUnsigned8(v):
        """Converts to a unsigned 8 bit integer (0 to 255)"""
        if v > 127:
            return 127

        elif v < -128:
            return 128

        elif v < 0:
            return v + 256

        return v

def ToSigned8(v):
        """Converts to a signed 8 bit integer (-128 to 127)"""
        if v > 255:
            return -1

        elif v < 0:
            return 0

        elif v > 127:
            return v - 256

        return v

class BCn:
    def decodeTile(self, data, offs):
        clut = []
        try:
            c0, c1, idxs = struct.unpack_from('HHI', data, offs)
        except:
            log.error("BC: Failed to unpack tile data from offset 0x%X: %s",
                offs, data[offs:offs+8])
            raise
        clut.append(unpackRGB565(c0))
        clut.append(unpackRGB565(c1))
        clut.append(self.calcCLUT2(clut[0], clut[1], c0, c1))
        clut.append(self.calcCLUT3(clut[0], clut[1], c0, c1))

        idxshift = 0
        output = bytearray(4*4*4)
        out = 0
        for ty in range(4):
            for tx in range(4):
                i = (idxs >> idxshift) & 3
                output[out : out+4] = clut[i]
                idxshift += 2
                out += 4
        return output


    def calcCLUT2(self, lut0, lut1, c0, c1):
        r = int((2 * lut0[0] + lut1[0]) / 3)
        g = int((2 * lut0[1] + lut1[1]) / 3)
        b = int((2 * lut0[2] + lut1[2]) / 3)
        return r, g, b, 0xFF


    def calcCLUT3(self, lut0, lut1, c0, c1):
        r = int((lut0[0] + 2 * lut1[0]) // 3)
        g = int((lut0[1] + 2 * lut1[1]) // 3)
        b = int((lut0[2] + 2 * lut1[2]) // 3)
        return r, g, b, 0xFF

    def decodeAlphaSigned(self, code, alpha):
            # used by BC3, BC4, BC5 SNORM textures
            # a0, a1 are color endpoints
            # the palette consists of (a0, a1, 6 more colors)
            # those 6 colors are a gradient from a0 to a1
            # code from BNTX-Editor translated to python
            if code == 0:
                ACOMP = alpha[0]

            elif code == 1:
                ACOMP = alpha[1]

            elif ToSigned8(alpha[0]) > ToSigned8(alpha[1]):
                ACOMP = ToUnsigned8((ToSigned8(alpha[0]) * (8 - code) + (ToSigned8(alpha[1]) * (code - 1))) // 7)

            elif code < 6:
                ACOMP = ToUnsigned8((ToSigned8(alpha[0]) * (6 - code) + (ToSigned8(alpha[1]) * (code - 1))) // 5)

            elif code == 6:
                ACOMP = 0x80

            else:
                ACOMP = 0x7f
            return ACOMP
    
    def decodeAlpha(self, bits, alpha):
        # used by BC3, BC4, BC5 UNORM textures
        # View above function's comment
        code = bits & 0x07
        if code == 0:
            ACOMP = alpha[0]
        elif code == 1:
            ACOMP = alpha[1]

        elif alpha[0] > alpha[1]:
            ACOMP = (alpha[0] * (8 - code) + (alpha[1] * (code - 1))) // 7

        elif code < 6:
            ACOMP = (alpha[0] * (6 - code) + (alpha[1] * (code - 1))) // 5

        elif code == 6:
            ACOMP = 0

        else:
            ACOMP = 255
        return ACOMP