A fork of an blender addon to import BFRES models on newer versions of blender and with different versions of BFRES

The original version only worked with BFRES version 3.5, or BOTW

This addon is currently in heavy development and large portions of it do not work yet.

Big thank you to Watertoon for the BFRES v10 structs, and Syroot and KillzXGaming as i reference their code here a lot

# Progress
- Model Versions:
    - [x] BFRES 5.3 (BOTW, MK8DX, ARMS; Breaks often, give me a heads up)
    - [X] BFRES 10 (Splatoon 3, Mario Wonder, TOTK)
    - [ ] BFRES 8/9 (Basically everything else; Planned)
- Importing into Blender
    - [x] Models
    - [x] Textures
    - [ ] Materials
        - Basic PBR samplers (albedo, normal, roughness, etc) apply correctly
        - Does not yet read material attributes or shader settings
        - Textures use default mapping to the first UV map only
    - [x] Bones 
        - Bones import but they're disconnected (but properly parented!). 
        - A very rudamentary "Auto Connect" is included
    - [ ] Animations
        - Not planned, but may happen

# Original readme below this header
Nintendo BFRES importer (and eventually exporter) for Blender.

Imports models from games such as Breath of the Wild.

Currently only supports Switch formats (and probably not very well).

Based on https://github.com/Syroot/io_scene_bfres

Very much in development and may be full of bugs and rough corners.

# What works:
- Importing models, with their skeletons and textures, from `.bfres` and `.sbfres` files (at least `Animal_Fox` works)
    - Includes cases where textures are in a separate `.Tex.sbfres` file in the same directory
    - Textures are embedded in the `.blend` file
    - Each LOD (level of detail) model is imported as a separate object, which might look strange when all of them are visible.
    - Materials' render/shader/material parameters are stored as Blender custom properties on the material objects.
    - Text files in the FRES are embedded into the blend file.

# What's broken:
- Specular intensity is way too high (models are shinier than they should be)
- `npc_zelda_miko` is weird, needs investigation
- Decompressing is slow
    - Progress indicator sucks, but I don't think Blender provides any way to do a better one
- `Animal_Bee`'s UV map is all wrong
- The addon preferences don't show up and I have no idea why
- Some texture formats might not decode correctly
- Extra files in the FRES, which are neither text nor a supported format, are discarded
    - The game probably never does this, but it's technically possible

# What's not even started yet:
- Animations
- Exporting
    - Exports as a `.dat` file containing Python code, which might be useful for some scripts
    - Eventually will export a `bfres` file
- WiiU files

# Why another importer?
I wanted to convert to a common format such as Collada, which any 3D editor could then use, but Blender seems to have issues with every suitable format. ¯\\\_(ツ)\_/¯

Syroot's importer didn't work for me, and as far as I know, didn't support skeletons. Since I'd already made a convertor, it was easier to build an importer from that.
