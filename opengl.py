from ctypes import c_char_p, c_char, cast, pointer, POINTER, sizeof
from pyglet.gl import *
from euclid import *

class OpenGL:
    _default_vert = """
    #version 130

    in vec3 position;
    in vec3 color;

    out vec3 Color;

    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 proj;

    void main()
    {
        gl_Position = proj * view * model * vec4(position, 1.0);
        Color = color;
    }
    """

    _default_frag = """
    #version 130

    in vec3 Color;

    out vec4 outColor;

    void main()
    {
        outColor = vec4(Color, 1.0);
    }
    """

    def __init__(self, vertpath=None, fragpath=None):
        vert = OpenGL._default_vert
        frag = OpenGL._default_frag

        if vertpath:
            with open(vertpath, 'r') as v:
                vert = v.read()
        if fragpath:
            with open(fragpath, 'r') as f:
                frag = f.read()

        self.vshader = glCreateShader(GL_VERTEX_SHADER)
        vert = c_char_p(bytes(vert, 'utf8'))
        glShaderSource(self.vshader, 1, cast(pointer(vert), POINTER(POINTER(c_char))), None)
        glCompileShader(self.vshader)

        self.fshader = glCreateShader(GL_FRAGMENT_SHADER)
        frag = c_char_p(bytes(frag, 'utf8'))
        glShaderSource(self.fshader, 1, cast(pointer(frag), POINTER(POINTER(c_char))), None)
        glCompileShader(self.fshader)

        self.shader = glCreateProgram()
        glAttachShader(self.shader, self.vshader)
        glAttachShader(self.shader, self.fshader)
        glBindFragDataLocation(self.shader, 0, b'outColor')
        glLinkProgram(self.shader)
        glUseProgram(self.shader)

        self.model_uni = glGetUniformLocation(self.shader, b'model')
        self.view_uni  = glGetUniformLocation(self.shader, b'view')
        self.proj_uni  = glGetUniformLocation(self.shader, b'proj')

        glEnable(GL_DEPTH_TEST)

    def view(self, pos, at, up):
        view_mat = Matrix4.new_look_at(pos, at, up)
        view_gl  = (GLfloat * len(view_mat[:]))(*view_mat[:])
        glUniformMatrix4fv(self.view_uni, 1, GL_FALSE, view_gl)

    def proj(self, fov=math.pi/2, ratio=16/9, fnear=0.1, ffar=10.0):
        proj_mat = Matrix4.new_perspective(fov, ratio, fnear, ffar)
        proj_gl  = (GLfloat * len(proj_mat[:]))(*proj_mat[:])
        glUniformMatrix4fv(self.proj_uni, 1, GL_FALSE, proj_gl)

    def model(self, pos=Matrix4.new_identity(), rot=0, scale=1.0):
        model_mat = pos.new_scale(scale, scale, scale).new_rotatez(rot)
        model_gl  = (GLfloat * len(model_mat[:]))(*model_mat[:])
        glUniformMatrix4fv(self.model_uni, 1, GL_FALSE, model_gl)

