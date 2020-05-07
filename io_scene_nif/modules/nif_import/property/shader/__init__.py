"""This script contains helper methods to import shader property data."""

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

from abc import ABC

from io_scene_nif.utils.util_logging import NifLog


class BSShader(ABC):

    @staticmethod
    def import_uv_offset(b_mat, shader_prop):
        for texture_slot in b_mat.texture_slots:
            if texture_slot:
                texture_slot.offset.x = shader_prop.uv_offset.u
                texture_slot.offset.y = shader_prop.uv_offset.v

    @staticmethod
    def import_uv_scale(b_mat, shader_prop):
        for texture_slot in b_mat.texture_slots:
            if texture_slot:
                texture_slot.scale.x = shader_prop.uv_scale.u
                texture_slot.scale.y = shader_prop.uv_scale.v

    @staticmethod
    def import_clamp(b_mat, shader_prop):
        clamp = shader_prop.texture_clamp_mode
        for texture_slot in b_mat.texture_slots:
            if texture_slot:
                if clamp == 3:
                    texture_slot.texture.image.use_clamp_x = False
                    texture_slot.texture.image.use_clamp_y = False
                if clamp == 2:
                    texture_slot.texture.image.use_clamp_x = False
                    texture_slot.texture.image.use_clamp_y = True
                if clamp == 1:
                    texture_slot.texture.image.use_clamp_x = True
                    texture_slot.texture.image.use_clamp_y = False
                if clamp == 0:
                    texture_slot.texture.image.use_clamp_x = True
                    texture_slot.texture.image.use_clamp_y = True

    @staticmethod
    def set_alpha_bsshader(b_mat, shader_property):
        NifLog.debug("Alpha prop detected")
        b_mat.use_transparency = True
        b_mat.alpha = (1 - shader_property.alpha)
        b_mat.transparency_method = 'Z_TRANSPARENCY'  # enable z-buffered transparency
        return b_mat

    @staticmethod
    def import_flags(b_mat, flags):
        for name in flags._names:
            sf_index = flags._names.index(name)
            if flags._items[sf_index]._value == 1:
                b_mat.niftools_shader[name] = True
