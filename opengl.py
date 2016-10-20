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
        self.perspective()
        self.view()
        self.model()

    def view(self, pos=Vector3(1, 1, 1), at=Vector3(0, 0, 0), up=Vector3(0, 0, 1)):
        view_mat = Matrix4.new_look_at(pos, at, up)
        view_gl  = (GLfloat * len(view_mat[:]))(*view_mat[:])
        glUniformMatrix4fv(self.view_uni, 1, GL_FALSE, view_gl)

    def perspective(self, fov=math.pi/2, ratio=16/9, fnear=0.1, ffar=10.0):
        proj_mat = Matrix4.new_perspective(fov, ratio, fnear, ffar)
        proj_gl  = (GLfloat * len(proj_mat[:]))(*proj_mat[:])
        glUniformMatrix4fv(self.proj_uni, 1, GL_FALSE, proj_gl)

    def orthographic(self, scale=1.0, ratio=16/9, fnear=0.1, ffar=10.0):
        ortho_mat = Matrix4.new_orthographic(scale, ratio, fnear, ffar)
        ortho_gl  = (GLfloat * len(ortho_mat[:]))(*ortho_mat[:])
        glUniformMatrix4fv(self.proj_uni, 1, GL_FALSE, ortho_gl)

    def model(self, pos=Vector3(0, 0, 0), rotz=0, scale=1.0):
        model_mat = Matrix4()\
                .translate(*pos[:])\
                .rotatez(rotz)\
                .scale(scale, scale, scale)
        model_gl  = (GLfloat * len(model_mat[:]))(*model_mat[:])
        glUniformMatrix4fv(self.model_uni, 1, GL_FALSE, model_gl)


class Mesh:
    def __init__(self, gl, vertices=[], pos=Vector3(0, 0, 0), rotz=0, scale=1):
        self.gl = gl
        self.vertices = vertices

        self.glsetup = False
        self.vao = GLuint()
        self.vbo = GLuint()
        #self.ebo = GLuint()

        self.pos = pos
        self.rotz = rotz
        self.scale = scale

    def _setup_gl(self):
        if not self.vertices:
            return

        self.glsetup = True
        glGenVertexArrays(1, pointer(self.vao))
        glGenBuffers(1, pointer(self.vbo))
        #glGenBuffers(1, pointer(self.ebo))

        glBindVertexArray(self.vao)
        # bind buffer data
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        verts_gl = (GLfloat * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, sizeof(verts_gl), verts_gl, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), 0)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), 3 * sizeof(GLfloat))

        glBindVertexArray(0)

    def draw(self):
        if not self.glsetup:
            self._setup_gl()
        if not self.glsetup:
            return

        glBindVertexArray(self.vao)
        self.gl.model(pos=self.pos, rotz=self.rotz, scale=self.scale)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices)//6)
        glBindVertexArray(0)
