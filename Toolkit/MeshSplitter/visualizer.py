



from panda3d.core import *
from random import random


load_prc_file("../../Config/configuration.prc")
load_prc_file_data("", "show-frame-rate-meter #t")
load_prc_file_data("", "gl-debug #t")
# load_prc_file_data("", "notify-level-glgsg debug")

import direct.directbase.DirectStart

import sys
sys.path.insert(0, "../../")

from Native.RSNative import StaticGeometryHandler, SGNode, SGRenderNode
from Code.Util.MovementController import MovementController


controller = MovementController(base)
controller.set_initial_position(Vec3(3), Vec3(0))
controller.setup()


vtx_shader = """
#version 150


uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;

uniform sampler2D DatasetTex;
uniform isamplerBuffer DynamicStripsTex;

uniform samplerBuffer DrawnObjectsTex;

out vec4 col;

float rand(float co){
    return fract(sin(dot(co, 12.9898)) * 43758.5453);
}

void main() {
    
    int strip_offs = gl_InstanceID;
    int vtx_idx = gl_VertexID;

    int object_id = texelFetch(DynamicStripsTex, strip_offs * 2 + 1).x;
    int strip_id = texelFetch(DynamicStripsTex, strip_offs * 2 + 2).x;



    // Read transform from object data
    int dobj_offs = 1 + 5 * object_id;

    vec4 mt0 = texelFetch(DrawnObjectsTex, dobj_offs + 1).rgba;
    vec4 mt1 = texelFetch(DrawnObjectsTex, dobj_offs + 2).rgba;
    vec4 mt2 = texelFetch(DrawnObjectsTex, dobj_offs + 3).rgba;
    vec4 mt3 = texelFetch(DrawnObjectsTex, dobj_offs + 4).rgba;

    mat4 transform = mat4(mt0, mt1, mt2, mt3); 

    // 2 for bounds, 1 for visibility
    int data_offs = 2 + 1 + vtx_idx * 2;

    vec4 data0 = texelFetch(DatasetTex, ivec2(data_offs + 0, strip_id), 0).bgra;
    vec4 data1 = texelFetch(DatasetTex, ivec2(data_offs + 1, strip_id), 0).bgra;

    vec4 vtx_pos = vec4(data0.xyz, 1);

    col = vec4(rand(strip_id), 1.0 - (strip_id % 32 / 32.0), (strip_id % 4) / 4.0, 1);
    col.w = 1.0;

    vec3 nrm = normalize(vec3(data0.w, data1.xy));
    col.xyz = nrm;

    //col.xyz = vec3( (dot(nrm, vec3(1, 0, 0))) < 0.5 ? 1.0 : 0.0);
    vtx_pos = transform * vtx_pos;


    gl_Position = p3d_ModelViewProjectionMatrix * vtx_pos;    
} """


frag_shader = """
#version 150

in vec4 col;
out vec4 result;

void main() {

    result = col;
}
"""

shader = Shader.make(Shader.SL_GLSL, vtx_shader, frag_shader)


# This is usually done by the pipeline
handler = StaticGeometryHandler()


# Load model
model_dataset = handler.load_dataset("model.rpsg")

for x in xrange(10):
    for y in xrange(10):

        node = SGNode("test", handler, model_dataset)
        np = render.attach_new_node(node)

        np.set_scale(0.2)
        np.set_pos(x*0.5, y*0.5, 0)



base.camLens.setNearFar(0.01, 1000.0)
base.camLens.setFov(120)

# np.set_scale(0.5)
collect_shader = Shader.load_compute(Shader.SL_GLSL, "collect_objects.compute.glsl")


finish_node = SGRenderNode(handler, collect_shader)
finish_np = render.attach_new_node(finish_node)
finish_np.set_shader(shader, 1000)

def update(task):
    cpos = base.camera.getPos(render)
    cdir = base.camera.getQuat(render).getForward()
    finish_np.set_shader_input("cameraPosition", cpos)
    finish_np.set_shader_input("cameraDirection", cdir)

    return task.cont

base.addTask(update, "update")

base.run()

sys.exit(0)





