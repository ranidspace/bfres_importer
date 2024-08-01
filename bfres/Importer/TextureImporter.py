import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import struct
import os
import os.path
import numpy as np
import time

class TextureImporter:
    """Imports texture images from BNTX archive."""

    def __init__(self, parent):
        self.parent   = parent
        self.operator = parent.operator
        self.context  = parent.context


    def importTextures(self, bntx):
        """Import textures from BNTX."""
        images = {}
        for i, tex in enumerate(bntx.textures):
            log.info("Importing texture %3d/%3d '%s' (%s)...",
                i+1, len(bntx.textures), tex.name,
                type(tex.format_).__name__)

            image = bpy.data.images.new(name=tex.name,
                width=tex.width, height=tex.height)
            # image.use_alpha = True

            offs   = 0
            r,g,b,a = 0,0,0,0
            ctype = [0, 255, r, g, b, a]
            compSelect = tex.channel_types

            start_time = time.time()
            for i in range(100):
                pixels = tex.format_.decodePixels(tex.pixels)
            print("--- %s seconds ---" % (time.time() - start_time))

            image.pixels = pixels

            # save to file
            if self.operator.dump_textures:
                base, ext = os.path.splitext(self.parent.path)
                dirPath = "%s/%s" % (base, bntx.name)
                os.makedirs(dirPath, exist_ok=True)
                image.filepath_raw = "%s/%s.png" % (
                    dirPath, tex.name)
                image.file_format = 'PNG'
                log.info("Saving image to %s", image.filepath_raw)
                image.save()

            image.update()
            image.pack()
            images[tex.name] = image
        return images
