import logging; log = logging.getLogger(__name__)
from ...BinaryStruct import BinaryStruct, BinaryObject
from ...BinaryStruct.Padding import Padding
from ...BinaryStruct.StringOffset import StringOffset
from ...BinaryStruct.Switch import Offset32, Offset64, String
from ...BinaryFile import BinaryFile
from ...FRES.FresObject import FresObject
from ...FRES.Dict import Dict
import struct


shaderParamTypes = {
    # http://mk8.tockdom.com/wiki/FMDL_(File_Format)#Material_Parameter
    0x04: {'fmt':'i',  'name':'sptr',  'outfmt':'%08X'},
    0x08: {'fmt':'I',  'name':'ptr',   'outfmt':'%08X'},
    0x0C: {'fmt':'f',  'name':'float', 'outfmt':'%f'},
    0x0D: {'fmt':'2f', 'name':'Vec2f', 'outfmt':'%f, %f'},
    0x0E: {'fmt':'3f', 'name':'Vec3f', 'outfmt':'%f, %f, %f'},
    0x0F: {'fmt':'4f', 'name':'Vec4f', 'outfmt':'%f, %f, %f, %f'},
    0x1E: {'fmt':'I5f','name':'texSRT', # scale, rotation, translation
        'outfmt':'mode=%d XS=%f YS=%f rot=%f X=%f Y=%f'},
}


class ShaderAssign(BinaryStruct):
    fields = (
        String(  'name'),  Padding(4),
        String(  'name2'), Padding(4),
        Offset64('vtx_attr_names'), # -> offsets of attr names
        Offset64('vtx_attr_dict'),
        Offset64('tex_attr_names'),
        Offset64('tex_attr_dict'),
        Offset64('shader_option_vals'), # names from dict
        Offset64('shader_option_dict'), Padding(4),
        ('B',    'num_vtx_attrs'),
        ('B',    'num_tex_attrs'),
        ('H',    'num_shader_options'),
    )

class Header(BinaryStruct):
    """FMAT header."""
    magic  = b'FMAT'
    fields = (
        ('4s',   'magic'), # 0x00
        ('I',    'size'),  # 0x04
        ('I',    'size2'), # 0x08
        Padding(4), # 0x0C
        String(  'name'),  # 0x10
        Padding(4), # 0x14
        Offset64('render_info_offs'), # 0x18
        Offset64('render_info_dict_offs'), # 0x20
        Offset64('shader_assign_offs'), # 0x28 -> name offsets
        Offset64('unk30_offs'), # 0x30
        Offset64('tex_ref_array_offs'), # 0x38
        Offset64('unk40_offs'), # 0x40
        Offset64('sampler_info_offs'), # 0x48
        Offset64('sampler_dict_offs'), # 0x50
        Offset64('mat_param_array_offs'), # 0x58
        Offset64('mat_param_dict_offs'), # 0x60
        Offset64('mat_param_data_offs'), # 0x68
        Offset64('user_data_offs'), # 0x70
        Offset64('user_data_dict_offs'), # 0x78
        Offset64('volatile_flag_offs'), # 0x80
        Offset64('user_offs'), # 0x88
        Offset64('sampler_slot_offs'), # 0x90
        Offset64('tex_slot_offs'), # 0x98
        ('I',    'mat_flags'), # 0xA0
        ('H',    'section_idx'), # 0xA4
        ('H',    'render_info_cnt'), # 0xA6
        ('B',    'tex_ref_cnt'), # 0xA8
        ('B',    'sampler_cnt'), # 0xA9
        ('H',    'mat_param_cnt'), # 0xAA
        ('H',    'mat_param_data_size'), # 0xAC
        ('H',    'raw_param_data_size'), # 0xAE
        ('H',    'user_data_cnt'), # 0xB0
        ('H',    'unkB2'), # 0xB2; usually 0 or 1
        ('I',    'unkB4'), # 0xB4
    )
    size = 0xB8

class ShaderReflection(BinaryStruct):
    fields = (
        String('shader_name'),  Padding(4),
        String('shader_name2'), Padding(4),
        Offset64('render_info_offs'), # 
        Offset64('render_info_dict_offs'), # 
        Offset64('mat_param_array_offs'), # 
        Offset64('mat_param_dict_offs'), # 
        Offset64('vtx_attr_dict'),
        Offset64('tex_attr_dict_offs'), # 
        Offset64('shader_option_dict_offs'), # 
        ('H',    'render_info_cnt'), #
        ('H',    'mat_param_cnt'), # 
        ('H',    'mat_param_data_size'), # 
        ('I',    'unk58'),
        ('Q',    'reserved3')
    )

class ShaderAssign10(BinaryStruct):
    fields = (
        Offset64('shader_refl'),
        Offset64('vtx_attr_names'), # -> offsets of attr names
        Offset64('vtx_attr_indx'),
        Offset64('tex_attr_names'),
        Offset64('tex_attr_indx'),
        Offset64('bool_shader_option_vals'), # names from dict
        Offset64('shader_option_vals'), 
        Offset64('shader_option_indx_array'),
        Padding(4),
        ('B',    'num_vtx_attrs'),
        ('B',    'num_tex_attrs'),
        ('H',    'num_bool_shader_options'),
        ('H',    'num_shader_options'),
    )

class Header10(BinaryStruct):
    """FMAT header."""
    magic  = b'FMAT'
    fields = (
        ('4s',   'magic'), # 0x00
        ('I',   'visibility'), # 0x04
        String(  'name'),  # 0x08
        Padding(4), # 0x14
        Offset64('shader_assign_offs'), # 0x10; material_shader_data
        Offset64('unk18_offs'), # 0x18; user_texture_view_array
        Offset64('tex_ref_array_offs'), # 0x20; texture_name_array
        Offset64('unk28_offs'), # 0x28; sampler_array
        Offset64('sampler_info_offs'), # 0x30; sampler_info_array
        Offset64('sampler_dict_offs'), # 0x38; sampler_dictionary
        Offset64('render_info_value_offs'), # 0x40; render_info_value_array
        Offset64('render_info_cnt_offs'), # 0x48; render_info_value_count_array
        Offset64('render_info_off_offs'), # 0x50; render_info_value_offset_array
        Offset64('mat_param_data_offs'), # 0x58; shader_option_value_array
        Offset64('unk60_offs'), # 0x60; shader_option_ubo_offset_array
        Padding(8), # 0x68
        Offset64('user_data_offs'), # 0x70; user_data_array
        Offset64('user_data_dict_offs'), # 0x78; user_data_dictionary
        Offset64('volatile_flag_offs'), # 0x80; shader_option_convert_flags_array
        Offset64('user_offs'), # 0x88; user_pointer
        Offset64('sampler_slot_offs'), # 0x90; user_sampler_descriptor_slot_array
        Offset64('tex_slot_offs'), # 0x98; user_texture_descriptor_slot_array
        ('H',    'section_idx'), # 0xA0
        ('B',    'sampler_cnt'), # 0xA2
        ('B',    'tex_ref_cnt'), # 0xA3
        Padding(2), # 0xA4
        ('H',    'user_data_cnt'), # 0xA6
        ('H',    'unka8'), # 0xA8; unknown size
        ('H',    'unkaa'), # 0xAA; user shading model option ubo size
       ('I',    'reserved2'), # 0xAC; reserve2
    )
    size = 0xB0

class SamplerInfo(BinaryStruct):
    """ResGfxSamplerInfo."""
    fields = (
        ('B',    'wrap_mode_u'),        # 0x00
        ('B',    'wrap_mode_v'),        # 0x01
        ('B',    'wrap_mode_w'),        # 0x02
        ('B',    'compare_op'),         # 0x03
        ('B',    'border_color'),       # 0x04
        ('B',    'max_anisotropy'),     # 0x05
        ('H',    'sampler_options'),    # 0x06; bitstruct, 2,2,2,1,1,2,6x
        ('f',    'lod_clamp_min'),      # 0x08
        ('f',    'lod_clamp_max'),      # 0x0C
        ('f',    'lod_bias'),           # 0x10
        Padding(4),                     # 0x14
        Padding(4),                     # 0x18
        Padding(4),                     # 0x1C
    )
    size = 0xF0


class FMAT(FresObject):
    """A material object in an FRES."""
    Header = Header
    Header10 = Header10

    def __init__(self, fres):
        self.fres         = fres
        self.header       = None
        self.headerOffset = None
        self.name         = None


    def __str__(self):
        return "<FMAT(%s, @%s) at 0x%x>" %(
            str(self.name),
            '?' if self.headerOffset is None else hex(self.headerOffset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        dicts = ('render_info', 'sampler', 'mat_param', 'user_data')

        res = []
        # Dump dicts
        #for i, name in enumerate(dicts):
        #    d = getattr(self, name+'_dict')
        #    if i == 0: name = '  '+name
        #    if d is None:
        #        res.append(name+": <none>")
        #    else:
        #        res.append(name+': '+ d.dump())

        # Dump render info
        res.append("Render info:")
        res.append("  \x1B[4mParam                           "+
            "│Type    │Cnt│Value\x1B[0m")
        for name, param in self.renderInfo.items():
            res.append("  %-32s│%-8s│%3d│%s" % (
                name, param['type'], param['count'], param['vals']))

        # Dump material params
        res.append("Material params:")
        res.append("  \x1B[4mParam                                   "+
            "│Type  │Size│Offset│Idx0│Idx1│Unk00│Unk14│Data\x1B[0m")
        for name, param in self.materialParams.items():
            res.append("  %-40s│%6s│%4d│%06X│%4d│%4d│%5d│%5d│%s" % (
                name,
                param['type']['name'],
                param['size'],    param['offset'],
                param['idxs'][0], param['idxs'][1],
                param['unk00'],   param['unk14'],
                param['data']))

        # Dump texture list
        res.append("Textures:")
        res.append("  \x1B[4mIdx│Slot│Name\x1B[0m")
        for i, tex in enumerate(self.textureSamplers):
            res.append("  %3d│%4d│%s" % (
                i, tex['slot'], tex['name']))

        # Dump sampler list
        res.append("Samplers:")
        res.append("  \x1B[4mIdx│Slot│Data\x1B[0m")
        for i, smp in enumerate(self.samplerInfoList):
            res.append("  %3d│%4d│%s" % (
                i, smp['slot'], smp['data']))

        # Dump shader option list
        res.append("Shader Options:")
        for name, val in self.shaderOptions.items():
            res.append("  %-45s: %4s" % (name, val))

        # Dump tex/vtx attrs
        res.append("Texture Attributes: " + (', '.join(self.fragSamplers)))
        res.append("Vertex  Attributes: " + (', '.join(self.vtxAttrs)))

        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        log.debug("Reading FMAT from 0x%06X", offset)
        self.headerOffset = offset
        if self.fres.header['version'] == (0, 10):
            self.header = self.fres.read(Header10(), offset)
            self._readShaderAssign()
            self._readDicts()
            self._readRenderInfo10()
            self._readMaterialParams10()
        else:
            self.header = self.fres.read(Header(), offset)
            self._readShaderAssign()
            self._readDicts()
            self._readRenderInfo()
            self._readMaterialParams()
        self.name   = self.header['name']

        self._readTextureSamplers()
        self._readSamplerInfoArray()

        return self


    def _readDicts(self):
        """Read the dicts."""
        dicts = ('render_info', 'sampler', 'mat_param', 'user_data')
        for name in dicts:
            offs = self.header[name + '_dict_offs']
            if offs: data = self._readDict(offs, name)
            else:    data = None
            setattr(self, name + '_dict', data)


    def _readDict(self, offs, name):
        """Read a Dict."""
        d = Dict(self.fres).readFromFRES(offs)
        return d

    def _readRenderInfo10(self):
        self.renderInfo = {}
        types   = ('s32', 'float', 'str')
        base    = self.header['render_info_offs']
        valBase = self.header['render_info_value_offs']
        cntBase = self.header['render_info_cnt_offs']
        offBase = self.header['render_info_off_offs']
        for i in range(self.header['render_info_cnt']):
            name, typ = self.fres.read('QB7x', base + (i*16))
            name = self.fres.readStr(name)
            cnt = self.fres.read('H', cntBase + (i*2))
            offs = self.fres.read('H', offBase+(i*2))
            
            try: typeName = types[typ]
            except IndexError: typeName = '0x%X' % typ
            
            self._readInfo(name, types, typ, offs, cnt, valBase, ['i','f','Q'])

    def _readRenderInfo(self):
        """Read the render params list."""
        self.renderInfo = {}
        types = ('float[2]', 'float', 'str')
        base  = self.header['render_info_offs']

        for i in range(self.header['render_info_cnt']):
            name, offs, cnt, typ, pad = self.fres.read(
                'QQHHI', base + (i*24))
            name = self.fres.readStr(name)

            if pad != 0:
                log.warning("FRES: FMAT Render info '%s' padding=0x%X",
                    name, pad)
            try: typeName = types[typ]
            except IndexError: typeName = '0x%X' % typ

            self._readInfo(name, types, typ, offs, cnt, 0, ['2f','f','Q'])

    def _readInfo(self, name, types, typ, offs, cnt, base, fmt):
        param = {
                'name':  name,
                'count': cnt,
                'type':  types[typ],
                'vals':  [],
            }
        
        for j in range(cnt):
            offset = base + offs 
            if   typ == 2:
                offs2 = self.fres.read('Q', offset + j*8)
                val  = self.fres.readStr(offs2)
            elif typ == 0 or typ == 1: val=self.fres.read(fmt[typ],  offset + j*4)
            else:
                log.warning("FMAT Render param '%s' unknown type 0x%X",
                    name, typ)
                val = '<unknown>'
            param['vals'].append(val)

        if name in self.renderInfo:
            log.warning("FMAT: Duplicate render param '%s'", name)
        self.renderInfo[name] = param

        
    def _readMaterialParams10(self):
        self.materialParams = {}

        array_offs = self.header['mat_param_array_offs']
        data_offs  = self.header['mat_param_data_offs']
        for i in range(self.header['mat_param_cnt']):
            # unk0: always 0; unk14: always -1s
            # idx0, idx1: both always == i
            unk0, name, offset, typ = \
                self.fres.read('QQHB', array_offs + (i*0x18))
            
            name = self.fres.readStr(name)
            typ = shaderParamTypes[typ]
            if unk0:
                log.debug("Material param '%s' unk0=0x%X", name, unk0)
            data = self.fres.read(typ['fmt'], data_offs + offset)

            if name in self.materialParams:
                log.warning("Duplicate material param '%s'", name)

            self.materialParams[name] = {
                'name':   name,
                'data':   data,
                'type':   typ,
                'offset': offset,
            }

    def _readMaterialParams(self):
        """Read the material param list."""
        self.materialParams = {}
        #print("FRES: FMAT Material params:")

        array_offs = self.header['mat_param_array_offs']
        data_offs  = self.header['mat_param_data_offs']
        for i in range(self.header['mat_param_cnt']):
            # unk0: always 0; unk14: always -1
            # idx0, idx1: both always == i
            unk0, name, type, size, offset, unk14, idx0, idx1 = \
                self.fres.read('QQBBHiHH', array_offs + (i*32))

            name = self.fres.readStr(name)
            type = shaderParamTypes[type]
            if unk0:
                log.debug("Material param '%s' unk0=0x%X", name, unk0)
            if unk14 != -1:
                log.debug("Material param '%s' unk14=%d", name, unk14)
            if idx0 != i or idx1 != i:
                log.debug("Material param '%s' idxs=%d, %d (expected %d)",
                    name, idx0, idx1, i)

            data = self.fres.read(size, data_offs + offset)

            #log.debug("%-38s %-5s %s", name, type['name'],
            #    type['outfmt'] % data)

            if name in self.materialParams:
                log.warning("Duplicate material param '%s'", name)

            self.materialParams[name] = {
                'name':   name,
                'type':   type,
                'size':   size,
                'offset': offset,
                'idxs':   (idx0, idx1),
                'unk00':  unk0,
                'unk14':  unk14,
                'data':   data,
            }


    def _readTextureSamplers(self):
        """Read the sampler list and return the texture associated with it"""
        self.textureSamplers = {}
        for i in range(self.header['tex_ref_cnt']):
            offs = self.header['tex_ref_array_offs'] + (i*8)
            offs = self.fres.read('Q', offs)
            texName = self.fres.readStr(offs)
            slot = self.fres.read('q',
                self.header['tex_slot_offs'] + (i*8))
            texSamplerName = self.sampler_dict.nodes[i+1].name
            #log.debug("%3d (%2d): %s", i, slot, name)
            self.textureSamplers[texSamplerName] = ({'textureName':texName, 'textureSampler':texSamplerName,'slot':slot})

        assign = self.shader_assign
        self.fragSamplers = {}
        for i in range(assign['num_tex_attrs']):
            offs = self.fres.read('Q', assign['tex_attr_names']+(i*8))
            samplerName = self.fres.readStr(offs)
            if assign['tex_attr_indx'] == 0:
                fragSamplerName = self.tex_attribute_dict.nodes[i+1].name
                self.fragSamplers[fragSamplerName] = self.textureSamplers[samplerName]
            else:
                idx  = self.fres.read('B', assign['tex_attr_indx']+(i))
                fragSamplerName = self.tex_attribute_dict.nodes[idx+1].name
                self.fragSamplers[fragSamplerName] = self.textureSamplers[samplerName]

    def _readSamplerInfoArray(self):
        """Read the sampler list."""
        self.samplerInfoList = []
        for i in range(self.header['sampler_cnt']):
            samplerinfo = SamplerInfo()
            data = samplerinfo.readFromFile(self.fres.file,
                self.header['sampler_info_offs'] + (i*0x20))
            slot = self.fres.read('q',
                self.header['sampler_slot_offs'] + (i*8))
            #log.debug("%3d (%2d): %s", i, slot, data)
            self.samplerInfoList.append({'slot':slot, 'data':data})
            # XXX no idea what to do with this data


    def _readShaderAssign(self):
        """Read the shader assign data."""
        if self.fres.header['version'] == (0, 10):
            assign = ShaderAssign10()
        else:
            assign = ShaderAssign()
        assign = assign.readFromFile(self.fres.file,
            self.header['shader_assign_offs'])
        self.shader_assign = assign
        

        if self.fres.header['version'] == (0, 10):
            shaderrefl = ShaderReflection()
            shaderrefl = shaderrefl.readFromFile(self.fres.file,
                assign['shader_refl'])
            self.shader_assign.update(shaderrefl)
            self.header.update(shaderrefl)

        self.vtxAttrs = []
        for i in range(assign['num_vtx_attrs']):
            offs = self.fres.read('Q', assign['vtx_attr_names']+(i*8))
            name = self.fres.readStr(offs)
            self.vtxAttrs.append(name)
        
        self.tex_attribute_dict = self._readDict(
                assign['tex_attr_dict_offs'], "texture_attributes")

        self.shader_option_dict = self._readDict(
                assign['shader_option_dict_offs'], "shader_options")
        self.shaderOptions = {}
            #log.debug("material params:")
        if self.fres.header['version'] == (0, 10):
            bools = self.fres.read('I', assign['bool_shader_option_vals'])
            for i in range(assign['num_bool_shader_options']):
                name = self.shader_option_dict.nodes[i+1].name
                val  = bool(bools & 1 << i != 0)
                if name in self.shaderOptions:
                    log.warning("FMAT: duplicate shader_option '%s'", name)
                if name != '':
                    self.shaderOptions[name] = val

            for i in range(assign['num_shader_options']-assign['num_bool_shader_options']):
                name = self.shader_option_dict.nodes[assign['num_bool_shader_options']+i+1].name
                offs = self.fres.read('Q', assign['shader_option_vals']+(i*8))
                val  = self.fres.readStr(offs)  # WHY ARE THESE STORED AS STRINGS
                #log.debug("%-40s: %s", name, val)
                if name in self.shaderOptions:
                    log.warning("FMAT: duplicate shader_option '%s'", name)
                if name != '':
                    self.shaderOptions[name] = val
        else:
            for i in range(assign['num_shader_options']):
                name = self.shader_option_dict.nodes[i+1].name
                offs = self.fres.read('Q', assign['shader_option_vals']+(i*8))
                val  = self.fres.readStr(offs)
                #log.debug("%-40s: %s", name, val)
                if name in self.shaderOptions:
                    log.warning("FMAT: duplicate shader_option '%s'", name)
                if name != '':
                    self.shaderOptions[name] = val