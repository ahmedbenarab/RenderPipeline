"""

RenderPipeline

Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from panda3d.core import SamplerState

from rpcore.loader import RPLoader
from rpcore.pluginbase.base_plugin import BasePlugin

from .apply_clouds_stage import ApplyCloudsStage

# Dynamic cloud generation is disabled for now
# from .cloud_voxel_stage import CloudVoxelStage

class Plugin(BasePlugin):

    name = "Volumetric Clouds"
    author = "tobspr <tobias.springer1@gmail.com>"
    description = ("This Plugin adds support or volumetric, raytraced clouds. "
                   "Right now this is pretty unoptimized and may consum a lot "
                   "of performance.")
    version = "alpha (!)"
    required_plugins = ("scattering",)

    def on_stage_setup(self):
        # self.generation_stage = self.create_stage(CloudVoxelStage)
        self.apply_stage = self.create_stage(ApplyCloudsStage)


    def on_pipeline_created(self):
        cloud_voxels = RPLoader.load_3d_texture(self.get_resource("slices/#.png"))
        cloud_voxels.set_wrap_w(SamplerState.WM_clamp)
        self.apply_stage.set_shader_input("CloudVoxels", cloud_voxels)

        noise_tex = RPLoader.load_texture(self.get_resource("noise.png"))
        noise_tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.apply_stage.set_shader_input("NoiseTex", noise_tex)