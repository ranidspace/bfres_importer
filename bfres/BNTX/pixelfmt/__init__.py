import logging; log = logging.getLogger(__name__)
from .base import TextureFormat, fmts, types
from . import rgb, BCn
from . import formatinfo

for cls in TextureFormat.__subclasses__():
    fmts[cls.id] = cls