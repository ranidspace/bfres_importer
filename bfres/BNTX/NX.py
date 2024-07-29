import logging; log = logging.getLogger(__name__)
from ..BinaryStruct import BinaryStruct, BinaryObject
from ..BinaryStruct.Padding import Padding
from ..BinaryStruct.Switch import Offset32, Offset64


class NX(BinaryStruct):
    """A 'NX' texture in a BNTX."""
    magic  = b'NX  '
    fields = (
        ('4s',   'magic'),
        ('I',    'num_textures'),
        Offset64('tex_table_offset'),
        Offset64('tex_data_offset'),
        Offset64('tex_dict_offset'),
        ('I',    'tex_mem_pool_offset'),
    )
