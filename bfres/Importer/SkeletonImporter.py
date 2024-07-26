import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import struct
import math
from mathutils import Matrix, Vector

class SkeletonImporter:
    """Imports skeleton from FMDL."""

    def __init__(self, parent, fmdl):
        self.fmdl     = fmdl
        self.operator = parent.operator
        self.context  = parent.context


    def importSkeleton(self, fskl):
        """Import specified skeleton."""
        name = self.fmdl.name

        # This is completely stupid. We basically automate the UI
        # to create the bones manually.
        # There is a better way (which still involves the UI, but
        # less so), but it of course doesn't work. (The created
        # bones fail to actually exist.)
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        # Create armature and object
        amt = bpy.data.armatures.new(name=name+'.Armature')
        armObj = bpy.data.objects.new(name=name, object_data=amt)
        
        bpy.context.scene.collection.objects.link(armObj)
        bpy.context.view_layer.objects.active = armObj

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        boneObjs = {}
        for i, bone in enumerate(fskl.bones):
            boneObj = amt.edit_bones.new(name=bone.name)
            boneObjs[i] = boneObj
            boneObj.use_relative_parent = True
            boneObj.use_local_location = True

            boneObj.length = 0.1
            if bone.parent:
                boneObj.parent = boneObjs[bone.parent_idx]
                boneObj.matrix = bone.parent.matrix @ bone.computeTransform()
            else:
                boneObj.matrix = bone.computeTransform()
            bone.matrix = boneObj.matrix

        if self.operator.connect_bones:  # XXX This gives bad results, needs a full rewrite
            for boneObj in amt.edit_bones:
                if boneObj.parent:
                    if (len(boneObj.parent.children) == 1 or self.checknames(boneObj, amt.edit_bones)) and boneObj.parent.head != boneObj.head:
                        boneObj.parent.tail = boneObj.head


        bpy.ops.object.mode_set(mode='OBJECT')
        return armObj

    def checknames(self, bone, armature):
        for i, c in enumerate(bone.name):
            if c.isdigit():
                c = int(c)
                num = int(bone.name[i])
                oneless = bone.name[0:i]+str(num-1)+bone.name[i+1:]
                if bone.parent.name == oneless:
                    return True
        return False
