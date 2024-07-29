import logging; log = logging.getLogger(__name__)
from ..BinaryStruct import BinaryStruct, BinaryObject
from ..BinaryStruct.Padding import Padding
from ..BinaryStruct.StringOffset import StringOffset
from ..BinaryStruct.Switch import Offset32, Offset64, String
from ..BinaryFile import BinaryFile
from .FresObject import FresObject
import tempfile


class BufferSection(BinaryStruct):
    """Defines the buffer offsets and sizes."""
    fields = (
        ('I', 'unk00'),       # 0x00
        ('I', 'size'),        # 0x04
        Offset64("buf_offs"), # 0x08
        Padding(16),          # 0x10
    )
    size = 0x20
