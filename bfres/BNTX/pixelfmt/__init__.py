import logging; log = logging.getLogger(__name__)
from .base import TextureFormat, fmts, types
from . import rgb, BCn
from .formatinfo import formats, blk_dims, BCn_formats, bpps

for cls in TextureFormat.__subclasses__():
    fmts[cls.id] = cls

def torgb8(data, height, width, fmt):
    bpp = fmt.bytesPerPixel
    result = bytearray(width * height * 8)
    offs = 0
    for i in range(width*height):
        pos = i*4
        r,g,b,a = fmt.decodePixel(data[offs:offs+bpp])
        result[pos]   = r
        result[pos+1] = g
        result[pos+2] = b
        result[pos+3] = a
        offs += bpp
    return bytes(result)

def decode(texture):
    '''Returns rgba8 texture bytes from data'''
    if (texture.fmt_id >> 8) in fmts:
        format_ = fmts[texture.fmt_id >> 8]()
        data = torgb8(texture.mipData, texture.height, texture.width, format_)
    
    else: # XXX this could definitely all be put into the same fmts list like it was before this commit
        match texture.fmt_id >> 8:
            case 0x0B:
                data = texture.mipData
                format_ = 'rgba8'

            case 0x1a:
                data = BCn.decompressDXT1(texture.mipData, texture.width, texture.height)
                format_ = 'rgba8'

            case 0x1b:
                data = BCn.decompressDXT3(texture.mipData, texture.width, texture.height)
                format_ = 'rgba8'

            case 0x1c:
                data = BCn.decompressDXT5(texture.mipData, texture.width, texture.height)
                format_ = 'rgba8'

            case 0x1d:
                data = BCn.decompressBC4(texture.mipData, texture.width, texture.height, 0 if texture.fmt_id & 3 == 1 else 1)
                format_ = 'rgba8'

            case 0x1e:
                data = BCn.decompressBC5(texture.mipData, texture.width, texture.height, 0 if texture.fmt_id & 3 == 1 else 1)
                format_ = 'rgba8'

            case _:
                raise TypeError("No decoder for textue format " +
                str(texture.fmt_id), texture.fmt_name)
    return data