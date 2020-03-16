"""This script contains classes to help import morph animations as shape keys."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2019, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import bpy
from pyffi.formats.nif import NifFormat

from io_scene_nif.modules.nif_import import animation
from io_scene_nif.modules.nif_import.animation import Animation
from io_scene_nif.utils import util_math
from io_scene_nif.utils.util_global import EGMData
from io_scene_nif.utils.util_logging import NifLog


class MorphAnimation(Animation):

    def __init__(self):
        super().__init__()
        animation.FPS = bpy.context.scene.render.fps

    def import_morph_controller(self, n_node, b_obj, v_map):
        """Import NiGeomMorpherController as shape keys for blender object."""

        n_morphCtrl = util_math.find_controller(n_node, NifFormat.NiGeomMorpherController)
        if n_morphCtrl:
            b_mesh = b_obj.data
            morphData = n_morphCtrl.data
            if morphData.num_morphs:
                # get name for base key
                keyname = morphData.morphs[0].frame_name.decode()
                if not keyname:
                    keyname = 'Base'

                # insert base key at frame 1, using relative keys
                sk_basis = b_obj.shape_key_add(keyname)

                # get base vectors and import all morphs
                baseverts = morphData.morphs[0].vectors

                shape_action = self.create_action(b_obj.data.shape_keys, b_obj.name + "-Morphs")
                
                for idxMorph in range(1, morphData.num_morphs):
                    # get name for key
                    keyname = morphData.morphs[idxMorph].frame_name.decode()
                    if not keyname:
                        keyname = 'Key %i' % idxMorph
                    NifLog.info("Inserting key '{0}'".format(keyname))
                    # get vectors
                    morph_verts = morphData.morphs[idxMorph].vectors
                    self.morph_mesh(b_mesh, baseverts, morph_verts, v_map)
                    shape_key = b_obj.shape_key_add(keyname, from_mix=False)

                    # first find the keys
                    # older versions store keys in the morphData
                    morph_data = morphData.morphs[idxMorph]
                    # newer versions store keys in the controller
                    if not morph_data.keys:
                        try:
                            if n_morphCtrl.interpolators:
                                morph_data = n_morphCtrl.interpolators[idxMorph].data.data
                            elif n_morphCtrl.interpolator_weights:
                                morph_data = n_morphCtrl.interpolator_weights[idxMorph].interpolator.data.data
                        except KeyError:
                            NifLog.info("Unsupported interpolator '{0}'".format(type(n_morphCtrl.interpolator_weights[idxMorph].interpolator)))
                            continue
                        
                    # get the interpolation mode
                    interp = self.get_b_interp_from_n_interp( morph_data.interpolation)
                    fcu = self.create_fcurves(shape_action, "value", (0,), flags=n_morphCtrl.flags, keyname=shape_key.name)
                    
                    # set keyframes
                    for key in morph_data.keys:
                        self.add_key(fcu, key.time, (key.value,), interp)

    def import_egm_morphs(self, b_obj, v_map, n_verts):
        """Import all EGM morphs as shape keys for blender object."""
        # TODO [morph][egm] if there is an egm, the assumption is that there is only one mesh in the nif
        b_mesh = b_obj.data
        sym_morphs = [list(morph.get_relative_vertices()) for morph in EGMData.data.sym_morphs]
        asym_morphs = [list(morph.get_relative_vertices()) for morph in EGMData.data.asym_morphs]

        # insert base key at frame 1, using absolute keys
        sk_basis = b_obj.shape_key_add("Basis")
        b_mesh.shape_keys.use_relative = False

        morphs = ([(morph, "EGM SYM %i" % i) for i, morph in enumerate(sym_morphs)] +
                  [(morph, "EGM ASYM %i" % i) for i, morph in enumerate(asym_morphs)])

        for morph_verts, key_name in morphs:
            # convert tuples into vector here so we can simply add in morph_mesh()
            morphvert_out = []
            for u in morph_verts:
                v = NifFormat.Vector3()
                v.x, v.y, v.z = u
                morphvert_out.append(v)
            self.morph_mesh(b_mesh, n_verts, morphvert_out, v_map)
            # TODO [animation] unused variable is it required
            shape_key = b_obj.shape_key_add(key_name, from_mix=False)

    def morph_mesh(self, b_mesh, baseverts, morphverts, v_map):
        """Transform a mesh to be in the shape given by morphverts."""
        # for each vertex calculate the key position from base
        # pos + delta offset
        # length check disabled
        # as sometimes, oddly, the morph has more vertices...
        # assert(len(baseverts) == len(morphverts) == len(v_map))
        for bv, mv, b_v_index in zip(baseverts, morphverts, v_map):
            # pyffi vector3
            v = bv + mv
            # if applytransform:
            # v *= transform
            b_mesh.vertices[b_v_index].co = v.as_tuple()
