#Berry engine with Python and OpenGL
import moderngl as gl
import glfw
import time
import numpy
class model:
    def __init__(self, data=(-0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
                             0.0, 0.5, 0.0, 0.0, 1.0, 0.0,
                             0.5, -0.5, 0.0, 0.0, 0.0, 1.0)):
        self.data=numpy.array(data, dtype='float32')
    def swap(self, data):
        self.data=numpy.array(data, dtype='float32')
class light_source:
    def __init__(self, pos=[0.15, 0.15, 0.08], color=[0.2, 0.2, 0.2]):
        self.pos=pos
        self.color=color
class camera:
    def __init__(self, pos=[1.0, 1.0, 1.0]):
        self.x=pos[0]
        self.y=pos[1]
        self.z=pos[2]
class instance:
    def get_speed(self, speed):
        final=speed/self.fps
        return final
    def bind_light(self, light):
        self.light=light
    def bind_camera(self, cam):
        self.camera=cam
    def bind_model(self, obj):
        self.model=obj
    def __init__(self, vsync=0, show_fps=False, req=330, frag_num=0):
        self.req=req
        self.mouse=None
        self.key_pressed=None
        self.vsync=vsync
        self.light_source=light_source()
        self.scale=[1.0, 1.0, 1.0]
        self.camera=camera()
        self.alive=True
        self.show_fps=show_fps
        self.model=model()
        self.fps=60
        self.frame=0
        self.vshade='''#version 330
in vec3 in_pos;
in vec3 in_color;
out vec3 pos;
out vec3 color;
uniform mat4 matrix;
void main(){
    color=in_color;
    pos=in_pos;
    vec4 transform=vec4(in_pos, 1.0f)*matrix;
    gl_Position=vec4(transform);
}'''
        self.shaders='''#version 330
in vec3 pos;
in vec3 color;
uniform vec3 u_light;
uniform vec3 u_light_pos;
uniform mat4 matrix;
void main(){
    vec3 light=u_light;
    vec4 light_pos=vec4(u_light_pos, 1.0f)*matrix;
    vec3 dist=vec3(0.0f, 0.0f, 0.0f);
    dist.xyz=abs(pos.xyz-light_pos.xyz);
    float total=sqrt(pow(dist.x, 2.0f)+pow(dist.y, 2.0f)+pow(dist.z, 2.0f));
    float ambient=0.7f;
    light/=total;
    vec3 result=abs(color*light*ambient);
    gl_FragColor=vec4(result, 1.0f);
}'''
    def create_window(self, name='Berry Engine Viewport', x=640, y=480, fullscreen=False):
        self.name=name
        if not glfw.init():
            self.alive=False
            return
        if fullscreen == True:
            self.win=glfw.create_window(x, y, name, glfw.get_primary_monitor(), None)
        else:
            self.win=glfw.create_window(x, y, name, None, None)
        glfw.make_context_current(self.win)
        self.ctx=gl.create_context(require=self.req)
        if not self.win:
            glfw.terminate()
            self.alive=False
            return
    def start(self):
        self.start=time.time()
        self.vbo=self.ctx.buffer(self.model.data)
        self.prog=self.ctx.program(vertex_shader=self.vshade, fragment_shader=self.shaders)
        self.mat=self.prog['matrix']
        self.light_pos=self.prog['u_light_pos']
        self.light=self.prog['u_light']
        self.light_pos.write(numpy.array(self.light_source.pos, dtype='float32'))
        self.light.write(numpy.array(self.light_source.color, dtype='float32'))
        self.mat.write(numpy.array([1.0, 0.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0, 0.0,
                                    0.0, 0.0, 1.0, 0.0,
                                    0.0, 0.0, 0.0, 1.0], dtype='float32'))
        self.vao=self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_pos', 'in_color')
        glfw.set_cursor_pos_callback(self.win, self.mouse_input)
        glfw.set_key_callback(self.win, self.keystroke)
    def render(self, clear=(0.0, 0.0, 0.0, 1.0)):
        glfw.swap_interval(self.vsync)
        if self.alive == False:
            glfw.terminate()
            return
        if not glfw.window_should_close(self.win):
            self.ctx.clear(*clear)
            self.vao.render(gl.TRIANGLES)
            self.frame+=1
            try:
                self.fps=self.frame/(time.time()-self.start)
            except:
                pass
            if time.time()-self.start >= 1:
                self.start=time.time()
                self.frame=0
            if self.show_fps:
                glfw.set_window_title(self.win, self.name+' FPS:'+str(int(self.fps)))
            self.mat.write(numpy.array([self.camera.x*self.scale[0], 0.0, 0.0, 0.0,
                                        0.0, self.camera.y*self.scale[1], 0.0, 0.0,
                                        0.0, 0.0, self.camera.z*self.scale[2], 0.0,
                                        0.0, 0.0, 0.0, 1.0], dtype='float32'))
            glfw.swap_buffers(self.win)
            glfw.poll_events()
            return
        self.alive=False
        glfw.terminate()
    def mouse_input(self, win, mx, my):
        self.mouse=[mx, my]
    def keystroke(self, win, key, scancode, action, mods):
        self.key_pressed=key
    def close(self):
        self.alive=False
        glfw.terminate()
