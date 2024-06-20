import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC5(TextureFormat, BCn):
    id = 0x1E
    bytesPerPixel = 16


    def decode(self, tex):
        decode   = self.decodePixel
        bpp      = self.bytesPerPixel
        data     = tex.data
        width    = (tex.width  + 3) // 4
        height   = (tex.height + 3) // 4
        pixels   = bytearray(width * height * 64)
        swizzle  = tex.swizzle.getOffset
        is_snorm = tex.fmt_dtype.name == 'SNorm'

        for y in range(height):
            for x in range(width):
                offs    = swizzle(x, y)
                redbits, ralph = self.calcAlpha(data[offs : offs+8])
                grnbits, galph = self.calcAlpha(data[offs+8 : offs+16])

                if is_snorm:
                    for ty in range(4):
                        for tx in range(4):
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r = self.decodeAlphaSigned(redbits, ralph)
                            g = self.decodeAlphaSigned(grnbits, galph)
                            pixels[out : out+4] = (0, g, r, 255)
                            redbits >>= 3
                            grnbits >>= 3
                            continue
                else:
                    for ty in range(4):
                        for tx in range(4):
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r = self.decodeAlpha(redbits, ralph)
                            g = self.decodeAlpha(grnbits, galph)
                            pixels[out : out+4] = (0, g, r, 255)
                            redbits >>= 3
                            grnbits >>= 3

        return pixels, self.depth


    def calcAlpha(self, alpha):
            alpha0 = alpha[0]
            alpha1 = alpha[1]
            bits = (alpha[0] | (alpha[1] << 8 ) |
            (alpha[2] << 16) | (alpha[3] << 24) |
            (alpha[4] << 32) | (alpha[5] << 40) |
            (alpha[6] << 48) | (alpha[7] << 56)) >> 16
            return bits, (alpha0, alpha1)
    
    def decodeAlpha(self, bits, alpha):
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
    
    def decodeAlphaSigned(self, bits, alpha):
        code = bits & 0x07
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

def ToUnsigned8(v):
    if v > 127:
        return 127

    elif v < -128:
        return 128

    elif v < 0:
        return v + 256

    return v

def ToSigned8(v):
    if v > 255:
        return -1

    elif v < 0:
        return 0

    elif v > 127:
        return v - 256

    return v