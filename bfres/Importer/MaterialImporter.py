import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
import struct

class MaterialImporter:
    """Imports material from FMDL."""

    def __init__(self, parent, fmdl):
        self.fmdl     = fmdl
        self.operator = parent.operator
        self.context  = parent.context


    def importMaterial(self, fmat):
        """Import specified material."""
        mat = bpy.data.materials.new(name=fmat.name)
        mat.use_nodes = True
        mat_wrap = PrincipledBSDFWrapper(mat, is_readonly=False)
        self._addCustomProperties(fmat, mat)

        for i, tex in enumerate(fmat.textures):
            if not bpy.data.images.get(tex['name']):
                log.info ("Texture %s missing",
                    tex['name'])
                continue

            log.info("Importing Texture %3d / %3d '%s'...",
                i+1, len(fmat.textures), tex['name'])

            image = bpy.data.images[tex['name']]
            sampler = tex['sampler']
            match sampler:
                case "_a0": # albedo (regular texture)
                    mat_wrap.base_color_texture.image = image

                case "_s0": # specular map
                    mat_wrap.specular_texture.image = image

                case "_r0": # roughness
                    mat_wrap.roughness_texture.image = image

                case "_m0": # metallness map
                    mat_wrap.metallic_texture.image = image

                case "_t0": # transmission map
                    mat_wrap.transmission_texture.image = image

                case "_n0": # normal map
                    mat_wrap.normalmap_texture.image = image
                
                case "_e0": # emission
                    mat_wrap.emission_strength_texture.image = image
                
                case "_op0": # opacity
                    mat_wrap.alpha_texture.image = image

                case _:
                    log.warning("Don't know what to do with texture: %s", tex['name'])
                    mtex = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    try:
                        mtex.image = image
                    except KeyError:
                        log.error("Texture not found: '%s'", tex['name'])
            
            # XXX Creates an error as theres no external file. Unsure if there's a better option to refresh the view after
            image.reload()

            '''param = "uking_texture%d_texcoord" % i
            param = fmat.shaderOptions.get(param, None)
            if param:
                mat.texture_slots[0].uv_layer = "_u"+param
                #log.debug("Using UV layer %s for texture %s",
                #    param, name)
            else:
                log.warning("No texcoord attribute for texture %d", i)'''

        return mat


    def _importTexture(self, fmat, tex):
        """Import specified texture to specified material."""
        # do we use the texid anymore?
        texid   = tex['name'].replace('.', '_') # XXX ensure unique
        texture = bpy.data.textures.new(name=texid, type ='IMAGE')
        try:
            texture.image = bpy.data.images[tex['name']]
        except KeyError:
            log.error("Texture not found: '%s'", tex['name'])
        return texture


    def _addCustomProperties(self, fmat, mat):
        """Add render/shader/material parameters and sampler list
        as custom properties on the Blender material object.
        """
        for name, param in fmat.renderInfo.items():
            val = param['vals']
            if param['count'] == 1: val = val[0]
            mat['renderInfo_'+name] = val

        for name, param in fmat.materialParams.items():
            mat['matParam_'+name] = {
                'type':   param['type']['name'],
                'offset': param['offset'],
                'data':   param['data'],
            }

        for name, val in fmat.shaderOptions.items():
            mat['shaderOption_'+name] = val

        mat['samplers']    = fmat.samplers
        mat['section_idx'] = fmat.header['section_idx']
