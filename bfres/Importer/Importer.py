import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import os
import os.path
import tempfile
import shutil
import struct
import math
import zstandard
from ..Exceptions import UnsupportedFileTypeError
from ..BinaryFile import BinaryFile
from .. import YAZ0, FRES, BNTX
from .ModelImporter import ModelImporter
from .TextureImporter import TextureImporter


class Importer(ModelImporter):
    def __init__(self, operator, context):
        self.operator = operator
        self.context  = context

        # Keep a link to the add-on preferences.
        #self.addon_prefs = #context.user_preferences.addons[__package__].preferences


    @staticmethod
    def _add_object_to_group(ob, group_name):
        # Get or create the required group.
        group = bpy.data.objects[group_name]

        # Link the provided object to it.
        ob.parent = group
        return group


    def run(self, path, **keywords):
        """Perform the import."""
        self.wm   = bpy.context.window_manager
        self.path = path
        return self.unpackFile(path)


    def unpackFile(self, file):
        """Try to unpack the given file.

        file: A file object, or a path to a file.

        If the file format is recognized, will try to unpack it.
        If the file is compressed, will first decompress it and
        then try to unpack the result.
        Raises UnsupportedFileTypeError if the file format isn't
        recognized.
        """
        if type(file) is str: # a path
            file = BinaryFile(file)
        self.file = file

        # read magic from header
        file.seek(0) # rewind
        magic = file.read(4)
        file.seek(0) # rewind
        match magic:
            case b'Yaz0' | b'Yaz1': # Compressed YAZ file
                r = self.decompressYaz(file)
                return self.unpackFile(r)
            
            case b'(\xb5/\xfd': # Compressed ZSTD file
                r = self.decompressZS(file)
                return self.unpackFile(r)
            
            case b'FRES':
                return self._importFres(file)

            case b'BNTX':
                return self._importBntx(file)
            case _:
                raise UnsupportedFileTypeError(magic)

    def decompressZS(self, file):
        filecontents = file.read(file.size, 0)
        decompressed = zstandard.decompress(filecontents)
        result = tempfile.TemporaryFile()
        result.write(decompressed)
        result.seek(0)
        return BinaryFile(result)

    def decompressYaz(self, file):
        """Decompress given file.

        Returns a temporary file.
        """
        log.debug("Decompressing input file...")
        result = tempfile.TemporaryFile()

        # make progress callback to update UI
        progress = 0
        def progressCallback(cur, total):
            nonlocal progress
            pct = math.floor((cur / total) * 100)
            if pct - progress >= 1:
                self.wm.progress_update(pct)
                progress = pct
            print("\rDecompressing... %3d%%" % pct, end='')
        self.wm.progress_begin(0, 100)

        # decompress the file
        decoder = YAZ0.Decoder(file, progressCallback)
        for data in decoder.bytes():
            result.write(data)
        self.wm.progress_end()
        print("") # end status line
        result.seek(0)

        if self.operator.save_decompressed: # write back to file
            path, ext = os.path.splitext(file.name)
            # 's' prefix indicates compressed;
            # eg '.sbfres' is compressed '.bfres'
            if ext.startswith('.s'): ext = '.'+ext[2:]
            else: ext = '.out'
            log.info("Saving decompressed file to: %s", path+ext)
            with open(path+ext, 'wb') as save:
                shutil.copyfileobj(result, save)
            result.seek(0)

        return BinaryFile(result)


    def _importFres(self, file):
        """Import FRES file."""
        self.fres = FRES.FRES(file)
        self.fres.decode()

        if self.operator.dump_debug:
            with open('./fres-%s-dump.txt' % self.fres.name, 'w') as f:
                f.write(self.fres.dump())
            #print("FRES contents:\n" + self.fres.dump())

        # decode embedded files
        for file in self.fres.embeds:
            self._importFresEmbed(file)

        # import the models.
        for i, model in enumerate(self.fres.models):
            log.info("Importing model    %3d / %3d...",
                i+1, len(self.fres.models))
            self._importModel(model)

        return {'FINISHED'}


    def _importFresEmbed(self, file):
        """Import embedded file from FRES."""
        if file.name.endswith('.txt'): # embed into blend file
            obj = bpy.data.texts.new(name=file.name)
            obj.write(file.data.decode('utf-8'))
        else: # try to decode, may be BNTX
            try:
                self.unpackFile(file.toTempFile())
            except UnsupportedFileTypeError as ex:
                log.debug("Embedded file '%s' is of unsupported type '%s'",
                    file.name, ex.magic)


    def _importBntx(self, file):
        """Import BNTX file."""
        self.bntx = BNTX.BNTX(file)
        self.bntx.decode()
        if self.operator.dump_debug:
            with open('./fres-%s-bntx-dump.txt' % self.bntx.name, 'w') as f:
                f.write(self.bntx.dump())

        imp = TextureImporter(self)
        imp.importTextures(self.bntx)

        return {'FINISHED'}
