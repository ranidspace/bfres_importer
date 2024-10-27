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

        if fmat.header['shader_name'] == 'Hoian_UBER':
            mat_wrap.base_color = fmat.materialParams['albedo_color']['data'][:3]
            mat_wrap.roughness = fmat.materialParams['roughness']['data']
            mat_wrap.metallic = fmat.materialParams['metalness']['data']
            mat_wrap.alpha = fmat.materialParams['opacity']['data']
            mat_wrap.emission_strength = fmat.materialParams['emission_intensity']['data']
            mat_wrap.emission_color = fmat.materialParams['emission_color']['data'][:3]
            if fmat.shaderOptions.get('enable_taransmission') and self.operator.enable_sss:
                mat_wrap.node_principled_bsdf.inputs['Subsurface Weight'].default_value  = fmat.materialParams['transmission_rate']['data']
                mat_wrap.node_principled_bsdf.inputs['Subsurface Radius'].default_value  = fmat.materialParams['transmission_color_backlight']['data'][:3]
                
        i = 0
        for fragSamplerKey, texSampler in fmat.fragSamplers.items():
            i += 1
            sampler = fragSamplerKey
            texName = texSampler['textureName']

            if not bpy.data.images.get(texName):
                log.info ("Texture %s missing",
                    texName)
                continue

            image = bpy.data.images[texName]

            match sampler:
                case "_a0": # albedo (regular texture)
                    if fmat.shaderOptions.get('emission_color_type') == '1':
                        mat_wrap.emission_color_texture.image = image
                    textureHelper = mat_wrap.base_color_texture

                case "_s0": # specular map
                    textureHelper = mat_wrap.specular_texture

                case "_r0": # roughness
                    textureHelper = mat_wrap.roughness_texture

                case "_m0": # metallness map
                    textureHelper = mat_wrap.metallic_texture

                case "_t0": # transmission map, actually subsurface
                    mtex = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    mtex.label = f"{texName}"
                    mtex.image = image
                    image.colorspace_settings.is_data = True
                    if fmat.shaderOptions.get('enable_taransmission') and self.operator.enable_sss:
                        mat.node_tree.links.new(mtex.outputs['Color'], mat_wrap.node_principled_bsdf.inputs['Subsurface Scale'])
                    continue

                case "_n0": # normal map
                    textureHelper = mat_wrap.normalmap_texture
                
                case "_e0": # emission
                    textureHelper = mat_wrap.emission_strength_texture
                
                case "_op0": # opacity
                    textureHelper = mat_wrap.alpha_texture

                case _:
                    log.warning("Don't know what to do with texture: %s", texName)
                    mtex = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    mtex.label = f"{sampler} {texName}"
                    try:
                        mtex.image = image
                    except KeyError:
                        log.error("Texture not found: '%s'", texName)
                    continue

            textureHelper.image = image
            # add mapping here, the helper has locrotscale attributes
            
            # XXX Creates an error as theres no external file. Unsure if there's a better option to refresh the view after
            image.reload()
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

        mat['samplers']    = fmat.samplerInfoList
        mat['section_idx'] = fmat.header['section_idx']
