import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp, ToSigned8


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
                red     = (data[offs], data[offs+1])
                redCh   = struct.unpack('Q', data[offs+2 : offs+10])[0]
                green     = (data[offs+8], data[offs+9])
                greenCh = struct.unpack('Q', data[offs+10 : offs+18])[0]

                if is_snorm:
                    for ty in range(4):
                        for tx in range(4):
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            shift = ty * 12 + tx * 3
                            r   = (redCh   >> shift) & 7
                            g   = (greenCh >> shift) & 7

                            r = self.decodeAlphaSigned(r, red)
                            g = self.decodeAlphaSigned(g, green)

                            r = ToSigned8(r) + 128
                            g = ToSigned8(g) + 128
                            b = self.calcBlue(r,g)
                            pixels[out : out+4] = (b, g, r, 255)
                else:
                    for ty in range(4):
                        for tx in range(4):
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            shift = ty * 12 + tx * 3
                            r   = (redCh   >> shift) & 7
                            g   = (greenCh >> shift) & 7
                            r = self.decodeAlpha(r, red)
                            g = self.decodeAlpha(g, green)
                            b = self.calcBlue(r,g)
                            pixels[out : out+4] = (b, g, r, 255)

        return pixels, self.depth
    
    def calcBlue(self, r, g):
        x = (2 * (r/255)) - 1
        y = (2 * (g/255)) - 1
        z = (1 - x**2 - y**2)**0.5
        b = (z + 1)*0.5
        return int(b.real * 255 + 0.5) # add 0.5 to round it properly as int just truncates
    
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
    