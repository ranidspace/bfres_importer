#!/usr/bin/env python3
"""BFRES importer/decoder for Blender.

This script can also run from the command line without Blender,
in which case it just prints useful information about the BFRES.
"""

bl_info = {
    "name": "Nintendo BFRES format",
    "description": "Import-Export BFRES models",
    "author": "RenaKunisaki",
    "version": (0, 1, 0),
    "blender": (4, 1, 0),
    "location": "File > Import-Export",
    "warning": "This add-on is under development.",
    "wiki_url": "https://github.com/RenaKunisaki/bfres_importer/wiki",
    "tracker_url": "https://github.com/RenaKunisaki/bfres_importer/issues",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

# Reload the package modules when reloading add-ons in Blender with F8.
print("BFRES MAIN")
if "bpy" in locals():
    import importlib
    names = ('BinaryStruct', 'FRES', 'FMDL', 'Importer', 'Exporter',
    'YAZ0')
    for name in names:
        ls = locals()
        if name in ls:
            importlib.reload(ls[name])

import bpy
from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        axis_conversion,
        )


# fix up import path (why is this necessary?) 
# developer number 2 note: i think it has to do with importing packages from different directories. It gives a "no module named" error if anyone else wants to fix it
import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# set up debug log
from .bfres import logger
bfres.logger.setup('bfres')
log = bfres.logger.logging.getLogger()

class ImportBFRES(bpy.types.Operator, ImportHelper):
    """Load a BFRES model file"""
    bl_idname    = "import_scene.nxbfres"
    bl_label     = "Import NX BFRES"
    bl_options   = {'UNDO'}

    directory: StringProperty()  # type: ignore

    filename_ext = ".bfres"

    filter_glob: StringProperty(
        default="*.sbfres;*.bfres;*.fres;*.szs;*.zs",
        options={'HIDDEN'},
    )  # type: ignore

    files: CollectionProperty(name="File Path",
            type=bpy.types.OperatorFileListElement,
            ) # type: ignore
    
    ui_tab: EnumProperty(
            items=(('MAIN', "Main", "Main basic settings"),
                  ),
            name="ui_tab",
            description="Import options categories",
            ) # type: ignore

    import_tex_file: BoolProperty(
        name="Import .Tex File",
        description="Import textures from .Tex file with same name.",
        default=True)
    
    component_selector: BoolProperty(
        name="Use Component Selector",
        description="If textures have the wrong colours, turn this off",
        default=True)

    dump_textures: BoolProperty(name="Dump Textures",
        description="Export textures to PNG.",
        default=False)

    dump_debug: BoolProperty(name="Dump Debug Info",
        description="Create `fres-SomeFile-dump.txt` files for debugging.",
        default=False)

    smooth_faces: BoolProperty(name="Smooth Faces",
        description="Set smooth=True on generated faces.",
        default=False)
    
    first_lod: BoolProperty(name="First LOD",
        description="Only import the first, most detailed LOD.",
        default=True)

    connect_bones: BoolProperty(name="Auto Connect Bones",
        description="Attempt to connect bones together",
        default=False)

    save_decompressed: BoolProperty(name="Save Decompressed Files",
        description="Keep decompressed FRES files.",
        default=False)

    parent_ob_name: StringProperty(name="Name of a parent object to which FSHP mesh objects will be added.")

    mat_name_prefix: StringProperty(name="Text prepended to material names to keep them unique.")

    def draw(self, context):
        pass

    def execute(self, context):
        #user_preferences = context.user_preferences
        #addon_prefs = user_preferences.addons[self.bl_idname].preferences
        #print("PREFS:", user_preferences, addon_prefs)
        keywords = self.as_keywords(ignore=("filter_glob", "directory", "ui_tab", "filepath", "files"))

        import os
        from bfres.Importer import Importer

        log.info("Attempting To Import Linked files")
        if self.import_tex_file:
            texpath, ext = os.path.splitext(self.filepath)
            texpath = texpath + '.Tex' + ext
            if os.path.exists(texpath):
                log.info("Importing linked file: %s", texpath)
                importer = Importer(self, context)
                importer.run(texpath, **keywords)     
    
        log.info("importing: %s", self.properties.filepath)
        importer = Importer(self, context)
        return importer.run(self.properties.filepath, **keywords)

class BFRES_PT_import_textures(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Textures"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_nxbfres"
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "import_tex_file")
        sub = layout.column()
        sub.enabled = operator.import_tex_file
        sub.prop(operator, "dump_textures")
        sub.prop(operator, "component_selector")

class BFRES_PT_import_mesh(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Model"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_nxbfres"
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "smooth_faces")
        layout.prop(operator, "first_lod")
        layout.prop(operator, "connect_bones")

class BFRES_PT_import_misc(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Misc"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_nxbfres"
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "save_decompressed")
        layout.prop(operator, "dump_debug")



def menu_func_import(self, context):
    self.layout.operator(ImportBFRES.bl_idname, text="Nintendo Switch BFRES (.bfres/.szs)")

#def menu_func_export(self, context):
#    self.layout.operator(ExportBFRES.bl_idname, text="Nintendo Switch BFRES (.bfres)")


classes = (
    ImportBFRES,
    BFRES_PT_import_textures,
    BFRES_PT_import_mesh,
    BFRES_PT_import_misc,
    #ExportBFRES,
)

# define Blender functions
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    #bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    #bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


# define main function, for running script outside of Blender.
# this currently doesn't work.
'''def main():
    if len(sys.argv) < 2:
        print("Usage: %s file" % sys.argv[0])
        return

    InPath = sys.argv[1]
    InFile = None

    # try to decompress the input to a temporary file.
    file  = BinaryFile(InPath, 'rb')
    magic = file.read(4)
    file.seek(0) # rewind
    if magic in (b'Yaz0', b'Yaz1'):
        print("Decompressing YAZ0...")

        # create temp file and write it
        InFile = tempfile.TemporaryFile()
        YAZ0.decompressFile(file, InFile)
        InFile.seek(0)
        InFile = BinaryFile(InFile)
        file.close()
        file = None

    elif magic == b'FRES':
        print("Input already decompressed")
        InFile = BinaryFile(file)

    else:
        file.close()
        file = None
        raise TypeError("Unsupported file type: "+str(magic))

    # decode decompressed file
    print("Decoding FRES...")
    fres = FRES.FRES(InFile)
    fres.decode()
    print("FRES contents:\n" + fres.dump())'''


if __name__ == '__main__':
    # main()
    register()