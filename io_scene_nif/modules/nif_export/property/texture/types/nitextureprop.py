"""This modules contains helper methods to export nitextureproperty type nodes"""

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

from io_scene_nif.modules.nif_export.block_registry import block_store
from io_scene_nif.modules.nif_export.property.texture import TextureSlotManager, TextureWriter
from io_scene_nif.utils.util_global import NifOp
from io_scene_nif.utils.util_logging import NifLog


class NiTextureProp(TextureSlotManager):

    __instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if NiTextureProp.__instance:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            NiTextureProp.__instance = self

    @staticmethod
    def get():
        """ Static access method. """
        if not NiTextureProp.__instance:
            NiTextureProp()
        return NiTextureProp.__instance

    def export_texturing_property(self, flags=0x0001, applymode=None, b_mat=None):
        """Export texturing property."""

        self.determine_texture_types(b_mat)

        texprop = NifFormat.NiTexturingProperty()

        texprop.flags = flags
        texprop.apply_mode = applymode
        texprop.texture_count = 7

        self.export_texture_shader_effect(texprop)
        self.export_nitextureprop_tex_descs(texprop)

        # search for duplicate
        for n_block in block_store.block_to_obj:
            if isinstance(n_block, NifFormat.NiTexturingProperty) and n_block.get_hash() == texprop.get_hash():
                return n_block

        # no texturing property with given settings found, so use and register
        # the new one
        return texprop

    def export_nitextureprop_tex_descs(self, texprop):

        if self.base_mtex:
            texprop.has_base_texture = True
            self.texture_writer.export_tex_desc(texdesc=texprop.base_texture,
                                                uvlayers=self.dict_mesh_uvlayers,
                                                b_mat_texslot=self.base_mtex)
            # check for texture flip definition
            try:
                fliptxt = Blender.Text.Get(basemtex.texture.name)
            except NameError:
                pass
            else:
                # texture slot 0 = base
                # TODO [animation] FIXME Heirarchy
                # self.texture_anim.export_flip_controller(fliptxt, self.base_mtex.texture, texprop, 0)
                pass

        if self.glow_mtex:
            texprop.has_glow_texture = True
            self.texture_writer.export_tex_desc(texdesc=texprop.glow_texture,
                                                uvlayers=self.dict_mesh_uvlayers,
                                                b_mat_texslot=self.glow_mtex)

        if self.bump_mtex:
            if NifOp.props.game not in self.USED_EXTRA_SHADER_TEXTURES:
                texprop.has_bump_map_texture = True
                self.texture_writer.export_tex_desc(texdesc=texprop.bump_map_texture,
                                                    uvlayers=self.dict_mesh_uvlayers,
                                                    b_mat_texslot=self.bump_mtex)
                texprop.bump_map_luma_scale = 1.0
                texprop.bump_map_luma_offset = 0.0
                texprop.bump_map_matrix.m_11 = 1.0
                texprop.bump_map_matrix.m_12 = 0.0
                texprop.bump_map_matrix.m_21 = 0.0
                texprop.bump_map_matrix.m_22 = 1.0

        if self.normal_mtex:
            shadertexdesc = texprop.shader_textures[1]
            shadertexdesc.is_used = True
            shadertexdesc.texture_data.source = TextureWriter.export_source_texture(n_texture=self.normal_mtex.texture)

        if self.gloss_mtex:
            if NifOp.props.game not in self.USED_EXTRA_SHADER_TEXTURES:
                texprop.has_gloss_texture = True
                self.texture_writer.export_tex_desc(texdesc=texprop.gloss_texture,
                                                    uvlayers=self.dict_mesh_uvlayers,
                                                    b_mat_texslot=self.gloss_mtex)
            else:
                shadertexdesc = texprop.shader_textures[2]
                shadertexdesc.is_used = True
                shadertexdesc.texture_data.source = TextureWriter.export_source_texture(n_texture=self.gloss_mtex.texture)

        if self.dark_mtex:
            texprop.has_dark_texture = True
            self.texture_writer.export_tex_desc(texdesc=texprop.dark_texture,
                                                uvlayers=self.dict_mesh_uvlayers,
                                                b_mat_texslot=self.dark_mtex)

        if self.detail_mtex:
            texprop.has_detail_texture = True
            self.texture_writer.export_tex_desc(texdesc=texprop.detail_texture,
                                                uvlayers=self.dict_mesh_uvlayers,
                                                b_mat_texslot=self.detail_mtex)

        if self.ref_mtex:
            if NifOp.props.game not in self.USED_EXTRA_SHADER_TEXTURES:
                NifLog.warn("Cannot export reflection texture for this game.")
                # tex_prop.hasRefTexture = True
                # self.export_tex_desc(texdesc=tex_prop.refTexture, uvlayers=uvlayers, mtex=refmtex)
            else:
                shadertexdesc = texprop.shader_textures[3]
                shadertexdesc.is_used = True
                shadertexdesc.texture_data.source = TextureWriter.export_source_texture(n_texture=self.ref_mtex.texture)

    def export_texture_effect(self, b_mat_texslot=None):
        """Export a texture effect block from material texture mtex (MTex, not Texture)."""
        texeff = NifFormat.NiTextureEffect()
        texeff.flags = 4
        texeff.rotation.set_identity()
        texeff.scale = 1.0
        texeff.model_projection_matrix.set_identity()
        texeff.texture_filtering = NifFormat.TexFilterMode.FILTER_TRILERP
        texeff.texture_clamping = NifFormat.TexClampMode.WRAP_S_WRAP_T
        texeff.texture_type = NifFormat.EffectType.EFFECT_ENVIRONMENT_MAP
        texeff.coordinate_generation_type = NifFormat.CoordGenType.CG_SPHERE_MAP
        if b_mat_texslot:
            texeff.source_texture = TextureWriter.export_source_texture(b_mat_texslot.texture)
            if NifOp.props.game == 'MORROWIND':
                texeff.num_affected_node_list_pointers += 1
                texeff.affected_node_list_pointers.update_size()
        texeff.unknown_vector.x = 1.0
        return block_store.register_block(texeff)

    def export_texture_shader_effect(self, tex_prop):
        # export extra shader textures
        if NifOp.props.game == 'SID_MEIER_S_RAILROADS':
            # sid meier's railroads:
            # some textures end up in the shader texture list there are 5 slots available, so set them up
            tex_prop.num_shader_textures = 5
            tex_prop.shader_textures.update_size()
            for mapindex, shadertexdesc in enumerate(tex_prop.shader_textures):
                # set default values
                shadertexdesc.is_used = False
                shadertexdesc.map_index = mapindex

            # some texture slots required by the engine
            shadertexdesc_envmap = tex_prop.shader_textures[0]
            shadertexdesc_envmap.is_used = True
            shadertexdesc_envmap.texture_data.source = TextureWriter.export_source_texture(filename="RRT_Engine_Env_map.dds")

            shadertexdesc_cubelightmap = tex_prop.shader_textures[4]
            shadertexdesc_cubelightmap.is_used = True
            shadertexdesc_cubelightmap.texture_data.source = TextureWriter.export_source_texture(filename="RRT_Cube_Light_map_128.dds")

        elif NifOp.props.game == 'CIVILIZATION_IV':
            # some textures end up in the shader texture list there are 4 slots available, so set them up
            tex_prop.num_shader_textures = 4
            tex_prop.shader_textures.update_size()
            for mapindex, shadertexdesc in enumerate(tex_prop.shader_textures):
                # set default values
                shadertexdesc.is_used = False
                shadertexdesc.map_index = mapindex
