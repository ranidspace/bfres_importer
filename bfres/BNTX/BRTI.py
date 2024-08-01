import logging; log = logging.getLogger(__name__)
from ..BinaryStruct import BinaryStruct, BinaryObject
from ..BinaryStruct.Padding import Padding
from ..BinaryStruct.StringOffset import StringOffset
from ..BinaryStruct.Switch import Offset32, Offset64, String
from ..BinaryFile import BinaryFile
from ..Common import StringTable
from enum import IntEnum
from .pixelfmt import TextureFormat
from .pixelfmt.swizzle import deswizzle, DIV_ROUND_UP, pow2_round_up
from .pixelfmt.formatinfo import formats, bpps, blk_dims

class Header(BinaryStruct):
    """BRTI object header."""
    magic  = b'BRTI'
    fields = (
        ('4s',   'magic'), # Header
        ('I',    'length'),
        ('Q',    'length2'),
        ('B',    'flags'),  # Texture Info
        ('B',    'dimensions'),
        ('H',    'tile_mode'),
        ('H',    'swizzle_size'),
        ('H',    'mipmap_cnt'),
        ('H',    'multisample_cnt'),
        ('H',    'reserved1A'),
        ('B',    'fmt_dtype', lambda v: BRTI.TextureDataType(v)),
        ('B',    'fmt_type',  lambda v: TextureFormat.get(v)()),
        Padding(2),   #end of format
        ('I',    'access_flags'),
        ('i',    'width'),
        ('i',    'height'),
        ('i',    'depth'),
        ('I',    'array_cnt'),
        ('I',    'texture_layout'),
        ('I',    'texture_layout2'),
        Padding(20),
        ('I',    'data_len'),
        ('I',    'alignment'),
        ('4B',   'channel_types',lambda v:tuple(v)),
        ('i',    'tex_type'),
        String(  'name'),
        Padding(4),
        Offset64('parent_offset'),
        Offset64('ptrs_offset'),
    )


class BRTI:
    """A BRTI in a BNTX."""
    Header = Header

    class ChannelType(IntEnum):
        Zero  = 0
        One   = 1
        Red   = 2
        Green = 3
        Blue  = 4
        Alpha = 5

    class TextureType(IntEnum):
        Image1D = 0
        Image2D = 1
        Image3D = 2
        Cube    = 3
        CubeFar = 8

    class TextureDataType(IntEnum):
        UNorm  = 1
        SNorm  = 2
        UInt   = 3
        SInt   = 4
        Single = 5
        SRGB   = 6
        UHalf  = 10

    def __init__(self):
        self.file       = None
        self.mipOffsets = []


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append("BRTI Name:     '%s'" % self.name)
        res.append("Length:          0x%06X / 0x%06X" % (
            self.header['length'], self.header['length2']))
        res.append("Flags:           0x%02X" % self.header['flags'])
        res.append("Dimensions:      0x%02X" % self.header['dimensions'])
        res.append("Tile Mode:       0x%04X" % self.header['tile_mode'])
        res.append("Swiz Size:       0x%04X" % self.header['swizzle_size'])
        res.append("Mipmap Cnt:      0x%04X" % self.header['mipmap_cnt'])
        res.append("Multisample Cnt: 0x%04X" % self.header['multisample_cnt'])
        res.append("Reserved 1A:     0x%04X" % self.header['reserved1A'])
        res.append("Fmt Data Type:   %2d %s" % (
            int(self.header['fmt_dtype']),
            self.header['fmt_dtype'].name))
        res.append("Fmt Type:        %2d %s" % (
            self.header['fmt_type'].fmt_id,
            type(self.header['fmt_type']).__name__))
        res.append("Access Flags:    0x%08X" % self.header['access_flags'])
        res.append("Width x Height:  %5d/%5d" % (self.width, self.height))
        res.append("Depth:           %3d" % self.header['depth'])
        res.append("Array Cnt:       %3d" % self.header['array_cnt'])
        res.append("Block Height:    %8d" % self.header['texture_layout'])
        res.append("Unk38:           %04X %04X" % (
            self.header['unk38'], self.header['unk3A']))
        res.append("Unk3C:           %d, %d, %d, %d, %d" % (
            self.header['image_size'], self.header['unk40'],
            self.header['unk44'], self.header['unk48'],
            self.header['unk4C']))
        res.append("Data Len:        0x%08X" % self.header['data_len'])
        res.append("Alignment:       0x%08X" % self.header['alignment'])
        res.append("Channel Types:   %s, %s, %s, %s" % (
            self.header['channel_types'][0].name,
            self.header['channel_types'][1].name,
            self.header['channel_types'][2].name,
            self.header['channel_types'][3].name))
        res.append("Texture Type:    0x%08X" % self.header['tex_type'])
        res.append("Parent Offs:     0x%08X" % self.header['parent_offset'])
        res.append("Ptrs Offs:       0x%08X" % self.header['ptrs_offset'])
        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFile(self, file:BinaryFile, offset=0):
        """Decode objects from the file."""
        self.file            = file
        self.header          = self.Header().readFromFile(file, offset)
        self.name            = self.header['name']
        self.format_         = self.header['fmt_type']
        self.width           = self.header['width']
        self.height          = self.header['height']
        self.tile_mode       = self.header['tile_mode']
        self.channel_types   = self.header['channel_types']

        self.fmt_id          = self.format_.id
        self.bpp             = bpps[self.fmt_id]

        if (self.fmt_id) in blk_dims:
            self.blkWidth, self.blkHeight = blk_dims[self.fmt_id]
        else:
            self.blkWidth, self.blkHeight = 1, 1
        self.blockHeightLog2 = self.header['texture_layout'] & 7

        log.info("Reading texture %s (%s)", self.name, type(self.format_).__name__)

        self._readMipmaps()
        self._readData()
        self.pixels = self.format_.decompress(self)
        return self


    def _readMipmaps(self):
        """Read the mipmap images."""
        for i in range(self.header['mipmap_cnt']):
            offs  = self.header['ptrs_offset'] + (i*8)
            entry = self.file.read('I', offs) #- base
            self.mipOffsets.append(entry)


    def _readData(self):
        """Read the raw image data."""
        base = self.file.read('Q', self.header['ptrs_offset'])
        self.data = self.file.read(self.header['data_len'], base)

        linesPerBlockHeight = (1 << self.blockHeightLog2) * 8
        blockHeightShift = 0
        mipOffset = self.mipOffsets[0]

        size = DIV_ROUND_UP(self.width, self.blkWidth) * DIV_ROUND_UP(self.height, self.blkHeight) * self.bpp

        if pow2_round_up(DIV_ROUND_UP(self.height, self.blkHeight)) < linesPerBlockHeight:
            blockHeightShift += 1

        result = deswizzle(
            self.width, self.height, self.blkWidth, self.blkHeight, self.bpp, self.tile_mode,
            max(0, self.blockHeightLog2 - blockHeightShift), self.data,
        )

        self.mipData = result[:size]
            