"""This script contains helper methods to managing importing texture into specific slots."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2020, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
# * Neither the name of the NIF File Format Library and Tools
#   project nor the names of its contributors may be used to endorse
#   or promote products derived from this software without specific
#   prior written permission.
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


from pyffi.formats.nif import NifFormat

from io_scene_nif.modules.nif_import.geometry.vertex import Vertex
from io_scene_nif.modules.nif_import.property.texture.loader import TextureLoader
from io_scene_nif.utils.util_logging import NifLog

# dictionary of texture files, to reuse textures
DICT_TEXTURES = {}

# TODO [property][texture] Move IMPORT_EMBEDDED_TEXTURES as a import property
IMPORT_EMBEDDED_TEXTURES = False

"""Names (ordered by default index) of shader texture slots for Sid Meier's Railroads and similar games."""
EXTRA_SHADER_TEXTURES = [
    "EnvironmentMapIndex",
    "NormalMapIndex",
    "SpecularIntensityIndex",
    "EnvironmentIntensityIndex",
    "LightCubeMapIndex",
    "ShadowTextureIndex"]


class TextureSlotManager:

    def __init__(self):
        self.texture_loader = TextureLoader()

    def create_texture_slot(self, b_mat, image_texture):
        b_mat_texslot = b_mat.texture_slots.add()
        try:
            b_mat_texslot.texture = self.texture_loader.import_texture_source(image_texture.source)
            uv_layer_name = image_texture.uv_set
        except:
            b_mat_texslot.texture = self.texture_loader.import_texture_source(image_texture)
            uv_layer_name = 0
        b_mat_texslot.use = True

        # Influence mapping

        # Mapping
        b_mat_texslot.texture_coords = 'UV'
        b_mat_texslot.uv_layer = Vertex.get_uv_layer_name(uv_layer_name)
        return b_mat_texslot

    def update_diffuse_slot(self, b_mat_texslot):
        # Influence mapping
        b_mat_texslot.texture.use_alpha = False

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = True

    def update_bump_slot(self, b_mat_texslot):
        # Influence mapping
        b_mat_texslot.texture.use_normal_map = False  # causes artifacts otherwise.

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = False
        b_mat_texslot.use_map_normal = True
        b_mat_texslot.use_map_alpha = False

    def update_normal_slot(self, b_mat_texslot):
        # Influence mapping
        b_mat_texslot.texture.use_normal_map = True  # causes artifacts otherwise.

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = False
        b_mat_texslot.use_map_normal = True
        b_mat_texslot.use_map_alpha = False

    def update_glow_slot(self, b_mat_texslot):
        # Influence mapping
        b_mat_texslot.texture.use_alpha = False

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = False
        b_mat_texslot.use_map_emit = True

    def update_gloss_slot(self, b_mat_texslot):
        # Influence mapping
        b_mat_texslot.texture.use_alpha = False

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = False
        b_mat_texslot.use_map_specular = True
        b_mat_texslot.use_map_color_spec = True

    def update_decal_slot(self, b_mat_texslot):
        # self.update_decal_slot(b_mat_texslot)
        # TODO [property][texture] Add support for decal slots
        NifLog.warn("This functionality is not currently supported")
        pass

    def update_decal_slot_0(self, b_mat_texslot):
        self.update_decal_slot(b_mat_texslot)
        # TODO [property][texture] Add support for decal slots

    def update_decal_slot_1(self, b_mat_texslot):
        self.update_decal_slot(b_mat_texslot)
        # TODO [property][texture] Add support for decal slots

    def update_detail_slot(self, b_mat_texslot):
        self.update_decal_slot(b_mat_texslot)
        # TODO [property][texture] Add support for decal slots

    def update_decal_slot_2(self, b_mat_texslot):
        self.update_decal_slot(b_mat_texslot)

    def update_dark_slot(self, b_mat_texslot):
        self.update_decal_slot(b_mat_texslot)
        b_mat_texslot.blend_type = 'DARK'

    def update_reflection_slot(self, b_mat_texslot):
        # Influence mapping

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = True
        b_mat_texslot.use_map_emit = True
        b_mat_texslot.use_map_mirror = True

    def update_environment_slot(self, b_mat_texslot):
        # Influence mapping

        # Influence
        # TODO [property][texture][flag][alpha] Figure out if this texture has alpha
        # if self.nif_import.ni_alpha_prop:
        #     b_mat_texslot.use_map_alpha = True

        b_mat_texslot.use_map_color_diffuse = True
        b_mat_texslot.blend_type = 'ADD'

    @staticmethod
    def get_b_blend_type_from_n_apply_mode(n_apply_mode):
        # TODO [material] Check out n_apply_modes
        if n_apply_mode == NifFormat.ApplyMode.APPLY_MODULATE:
            return "MIX"
        elif n_apply_mode == NifFormat.ApplyMode.APPLY_REPLACE:
            return "COLOR"
        elif n_apply_mode == NifFormat.ApplyMode.APPLY_DECAL:
            return "OVERLAY"
        elif n_apply_mode == NifFormat.ApplyMode.APPLY_HILIGHT:
            return "LIGHTEN"
        elif n_apply_mode == NifFormat.ApplyMode.APPLY_HILIGHT2:  # used by Oblivion for parallax
            return "MULTIPLY"
        else:
            NifLog.warn("Unknown apply mode (%i) in material, using blend type 'MIX'".format(n_apply_mode))
            return "MIX"
