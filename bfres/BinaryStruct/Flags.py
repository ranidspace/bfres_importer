import logging; log = logging.getLogger(__name__)
from .BinaryObject import BinaryObject
import struct


class Flags(BinaryObject):
    """A set of bitflags."""
    def __init__(self, name, flags, fmt='I'):
        self.name   = name
        self._flags = flags
        self.fmt    = fmt
        self.size   = struct.calcsize(fmt)


    def readFromFile(self, file, offset=None):
        val = file.read(self.fmt, offset)
        res = {'_raw':val}
        offs = 0
        for name, length in self._flags.items():
            if name[:8] != "RESERVED":
                if type(length) == tuple:
                    func = length[1]
                    length = length[0]
                    mask = ((1 << length) - 1) << offs
                    res[name] = func((val & mask) >> offs)
                else:
                    mask = ((1 << length) - 1) << offs
                    res[name] = (val & mask) >> offs
            offs += length
        return res
