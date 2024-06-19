import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import struct
from .MaterialImporter import MaterialImporter
from .SkeletonImporter import SkeletonImporter
from .LodImporter      import LodImporter


class ModelImporter:
    """Mixin class for importing the geometric models."""

    def _importModel(self, fmdl):
        """Import specified model."""
        # create a parent if we don't have one.
        fmdl_obj = None
        '''if self.operator.parent_ob_name is None:
            fmdl_obj = bpy.data.objects.new(name=fmdl.name, object_data=None)
            self._add_object_to_group(fmdl_obj, fmdl.name)
            bpy.context.scene.collection.objects.link(fmdl_obj)''' #Fix Later
        # import the skeleton
        self.fmdl = fmdl
        self.skelImp  = SkeletonImporter(self, fmdl)
        self.armature = self.skelImp.importSkeleton(fmdl.skeleton)

        # import the materials.
        self.matImp = MaterialImporter(self, fmdl)
        for i, fmat in enumerate(fmdl.fmats):
            log.info("Importing material %3d / %3d...",
                i+1, len(fmdl.fmats))
            self.matImp.importMaterial(fmat)

        # create the shapes.
        for i, fshp in enumerate(fmdl.fshps):
            log.info("Importing shape %3d / %3d '%s'...",
                i+1, len(fmdl.fshps), fshp.name)
            self._importShape(fmdl, fshp, self.armature)


    def _importShape(self, fmdl, fshp, parent):
        """Import FSHP.

        fmdl: FMDL to import from.
        fshp: FSHP to import.
        parent: Object to parent the LOD models to.
        """
        fvtx = fmdl.fvtxs[fshp.header['fvtx_idx']]
        if self.operator.first_lod == True:
            lod = fshp.lods[0]
            lodImp  = LodImporter(self)
            meshObj = lodImp._importLod(fvtx, fmdl, fshp, lod, 0)
            meshObj.parent = parent
        else:
            for ilod, lod in enumerate(fshp.lods):
                log.info("Importing LOD %3d / %3d...",
                    ilod+1, len(fshp.lods))

                lodImp  = LodImporter(self)
                meshObj = lodImp._importLod(fvtx, fmdl, fshp, lod, ilod)
                meshObj.parent = parent
