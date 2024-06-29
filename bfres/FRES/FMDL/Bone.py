import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryStruct.Flags import Flags
from bfres.BinaryStruct.Vector import Vec3f, Vec4f
from bfres.BinaryFile import BinaryFile
from bfres.FRES.FresObject import FresObject
from bfres.FRES.Dict import Dict
from .Attribute import Attribute, AttrStruct
from .Buffer    import Buffer
from .FVTX      import FVTX
from .LOD       import LOD
from .Vertex    import Vertex
import struct
from enum import IntEnum
import math
import mathutils # Blender


class BoneStruct(BinaryStruct):
    """The bone data in the file."""
    fields = (
        String('name'),
        ('5I', 'unk04'),
        ('H',  'bone_idx'),
        ('h',  'parent_idx'),
        ('h',  'smooth_mtx_idx'),
        ('h',  'rigid_mtx_idx'),
        ('h',  'billboard_idx'),
        ('H',  'udata_count'),
        Flags('flags', {
            'VISIBLE': 1,
            'RESERVED0': 11,
            'EULER':   1, # use euler rotn, not quaternion
            'RESERVED1': 3,
            'BB_MODE': (3, lambda v: Bone.BillboardMode(v)),
            'RESERVED2': 4,
            'SEG_SCALE_COMPENSATE': 1, # Segment scale
                # compensation. Set for bones scaled in Maya whose
                # scale is not applied to child bones.
            'UNIFORM_SCALE': 1, # Scale uniformly.
            'SCALE_VOL_1': 1, # Scale volume by 1.
            'NO_ROTATION': 1,
            'NO_TRANSLATION': 1,
            # same as previous but for hierarchy of bones
            'GRP_UNIFORM_SCALE': 1,
            'GRP_SCALE_VOL_1':   1,
            'GRP_NO_ROTATION':   1,
            'GRP_NO_TRANSLATION':1,
        }),
        Vec3f('scale'),
        Vec4f('rot'),
        Vec3f('pos'),
    )
    size = 80

class BoneStruct10(BinaryStruct):
    """The bone data in the file."""
    fields = (
        String('name'), Padding(4), # 0x00
        ('3Q', 'unk08'), # 0x08
        ('H',  'bone_idx'), # 0x20
        ('h',  'parent_idx'), # 0x22
        ('h',  'smooth_mtx_idx'), # 0x24
        ('h',  'rigid_mtx_idx'), # 0x26
        ('h',  'billboard_idx'), # 0x28
        ('H',  'udata_count'),  # 0x2A
        Flags('flags', {
            'RESERVED0': 12,
            'VISIBLE': 1,
            'RESERVED1': 3,
            'BB_MODE': (3, lambda v: Bone.BillboardMode(v)),
            'RESERVED2': 4,

            'SEG_SCALE_COMPENSATE': 1,
            'UNIFORM_SCALE': 1, # Scale uniformly.
            'SCALE_VOL_1': 1, # Scale volume by 1.
            'NO_ROTATION': 1,
            'NO_TRANSLATION': 1,

            'GRP_UNIFORM_SCALE': 1,
            'GRP_SCALE_VOL_1':   1,
            'GRP_NO_ROTATION':   1,
            'GRP_NO_TRANSLATION': 1,
        }),
        Vec3f('scale'),
        Vec4f('rot'),
        Vec3f('pos'),
    )
    size = 0x58


class Bone(FresObject):
    """A bone in an FSKL."""
    _struct = BoneStruct
    _struct10 = BoneStruct10

    class BillboardMode(IntEnum):
        BB_None = 0,
        Child = 1,
        World_Vec = 2,
        World_Point = 3,
        Screen_Vec = 4,
        Screen_Point = 5,
        Y_Vec = 6,
        Y_Point = 7,

    def __init__(self, fres):
        self.fres   = fres
        self.offset = None
        self.parent = None # to be set by FSKL on read


    def __str__(self):
        return "<Bone(@%s) at 0x%x>" %(
            '?' if self.offset is None else hex(self.offset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        flags = []
        for name in sorted(self.flags.keys()):
            if name != '_raw':
                val = self.flags[name]
                if val: flags.append(name)
        flags = ', '.join(flags)
        rotD  = ' (%3d, %3d, %3d, %3d°)' % tuple(map(math.degrees, self.rot))

        res  = []
        res.append("Bone #%3d '%s':" % (self.bone_idx, self.name))
        res.append("Position: %#5.2f, %#5.2f, %#5.2f" % tuple(self.pos))
        res.append("Rotation: %#5.2f, %#5.2f, %#5.2f, %#5.2f" % tuple(self.rot) + rotD)
        res.append("Scale:    %#5.2f, %#5.2f, %#5.2f" % tuple(self.scale))
        res.append("Unk04: 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X" %
            self.unk04)
        res.append("Parent     Idx: %3d" % self.parent_idx)
        res.append("Smooth Mtx Idx: %3d" % self.smooth_mtx_idx)
        res.append("Rigid  Mtx Idx: %3d" % self.rigid_mtx_idx)
        res.append("Billboard  Idx: %3d" % self.billboard_idx)
        res.append("Udata count:    %3d" % self.udata_count)
        res.append("Flags: %s" % flags)
        #res = ', '.join(res)
        return '\n'.join(res).replace('\n', '\n  ')
        #return res


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        #log.debug("Reading Bone from 0x%06X", offset)
        self.offset = offset
        if self.fres.header['version'] == (0, 10):
            data = self.fres.read(BoneStruct10(), offset)
        else:
            data = self.fres.read(BoneStruct(), offset)

        self.name           = data['name']
        self.pos            = data['pos']
        self.rot            = data['rot']
        self.scale          = data['scale']
        self.bone_idx       = data['bone_idx']
        self.parent_idx     = data['parent_idx']
        self.smooth_mtx_idx = data['smooth_mtx_idx']
        self.rigid_mtx_idx  = data['rigid_mtx_idx']
        self.billboard_idx  = data['billboard_idx']
        self.udata_count    = data['udata_count']
        self.flags          = data['flags']

        return self


    def computeTransform(self):
        """Compute final transformation matrix."""
        L = mathutils.Vector(self.pos[0:3])
        R = mathutils.Euler(self.rot[0:3])
        S = mathutils.Vector(self.scale[0:3])
        M = mathutils.Matrix.LocRotScale(L,R,S)
        '''if self.flags['SEG_SCALE_COMPENSATE']:
            # apply inverse of parent's scale
            if self.parent:
                S[0] *= 1 / self.parent.scale[0]
                S[1] *= 1 / self.parent.scale[1]
                S[2] *= 1 / self.parent.scale[2]
            else:
                log.warning("Bone '%s' has flag SEG_SCALE_COMPENSATE but no parent", self.name)'''
        M = mathutils.Matrix.LocRotScale(L,R,S)
        # Rotate on the X axis because nintendo things are Y axis up
        if not self.parent:
            M = mathutils.Matrix.Rotation(math.radians(90), 4, (1,0,0)) @ M
        return M

        L = mathutils.Matrix.Translation(L).to_4x4().transposed()
        Sm = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()
        Sm[0][0] = S[0]
        Sm[1][1] = S[1]
        Sm[2][2] = S[2]
        S = Sm
        log.debug(R)
        log.debug(self._fromEulerAngles(R))
        log.debug(self._fromEulerAngles(R).to_matrix())
        R = self._fromEulerAngles(R).to_matrix().to_4x4().transposed()
        log.debug(R)
        if self.parent:
            P = self.parent.computeTransform()#.to_4x4()
        else:
            P = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()
        M = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()

        # Apply transformations. (order is important!)
        M = M * R
        M = M * L

        #log.debug("Final bone transform %s: %s", self.name, M)
        return M


    def _fromAxisAngle(self, axis, angle):
        return mathutils.Quaternion((
            math.cos(angle / 2),
            axis[0] * math.sin(angle / 2),
            axis[1] * math.sin(angle / 2),
            axis[2] * math.sin(angle / 2),
        ))

    def _fromEulerAngles(self, rot):
        x = self._fromAxisAngle((1,0,0), rot[0])
        y = self._fromAxisAngle((0,1,0), rot[1])
        z = self._fromAxisAngle((0,0,1), rot[2])
        #q = x * y * z
        q = z * y * x
        if q.w < 0: q *= -1
        return q
