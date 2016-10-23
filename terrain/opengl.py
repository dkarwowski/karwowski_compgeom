from ctypes import c_char_p, c_char, cast, pointer, POINTER, sizeof, create_string_buffer
from pyglet.gl import *
from euclid import *

class Shader:
    def __init__(self, handle):
        self.handle = handle
        self.uniforms = dict()

    def uni(self, var):
        return self.uniforms.setdefault(
            var,
            glGetUniformLocation(self.handle, bytes(var, 'utf8'))
        )

class ShaderLoader:
    shaders = dict()

    def _get_shader(cls, vertpath='3d.vert', fragpath='3d.frag'):
        vpath = "./resources/shaders/" + vertpath
        fpath = "./resources/shaders/" + fragpath
        if (vpath, fpath) in cls.shaders:
            return cls.shaders[(vpath, fpath)]

        vshader = cls._load_shader(vpath, GL_VERTEX_SHADER)
        fshader = cls._load_shader(fpath, GL_FRAGMENT_SHADER)

        shader = glCreateProgram()
        glAttachShader(shader, vshader)
        glAttachShader(shader, fshader)

        glLinkProgram(shader)

        success = GLint()
        glGetProgramiv(shader, GL_LINK_STATUS, pointer(success))
        if success.value != GL_TRUE:
            logsize = GLint()
            glGetProgramiv(shader, GL_INFO_LOG_LENGTH, pointer(logsize))
            log = create_string_buffer(logsize.value)
            glGetProgramInfoLog(shader, logsize.value, 0, log)
            print("link error:", log.value)

        glValidateProgram(shader)
        glGetProgramiv(shader, GL_VALIDATE_STATUS, pointer(success))
        if success.value != GL_TRUE:
            logsize = GLint()
            glGetProgramiv(shader, GL_INFO_LOG_LENGTH, pointer(logsize))
            log = create_string_buffer(logsize.value)
            glGetProgramInfoLog(shader, logsize.value, 0, log)
            print("valid error:", log.value)

        s = Shader(shader)
        cls.shaders[(vpath, fpath)] = s
        return s
    get_shader = classmethod(_get_shader)

    def _load_shader(cls, path, shader_type):
        with open(path) as source:
            shader = glCreateShader(shader_type)

            buff = c_char_p(bytes(source.read(), 'utf8'))
            glShaderSource(shader, 1, cast(pointer(buff), POINTER(POINTER(c_char))), None)

            glCompileShader(shader)

            success = GLint()
            glGetShaderiv(shader, GL_COMPILE_STATUS, pointer(success))
            if success.value != GL_TRUE:
                logsize = GLint()
                glGetShaderiv(shader, GL_INFO_LOG_LENGTH, pointer(logsize))
                log = create_string_buffer(logsize.value)
                glGetShaderInfoLog(shader, logsize.value, 0, log)
                print("compile error:", log.value)

            return shader
        return None
    _load_shader = classmethod(_load_shader)

class Camera:
    def __init__(self, pos, to, up):
        self.pos = pos
        self.to  = to
        self.up  = up

        self.is_persp = False
        self.proj = Matrix4()

    def set_persp(self, fov, aspect, z_near, z_far):
        self.proj = Matrix4.new_perspective(fov, aspect, z_near, z_far)
        self.is_persp = True

    def set_ortho(self, scale, aspect, z_near, z_far):
        self.proj = Matrix4.new_orthographic(scale, aspect, z_near, z_far)
        self.is_persp = False

    def get_proj(self):
        proj_gl = (GLfloat * len(self.proj[:]))(*self.proj[:])
        return proj_gl

    def get_view(self):
        view_mat = Matrix4.new_look_at(self.pos, self.to + self.pos, self.up)
        view_gl  = (GLfloat * len(view_mat[:]))(*view_mat[:])
        return view_gl

    def get_view_pos(self):
        view_pos_gl = (GLfloat * len(self.pos[:]))(*self.pos)
        return view_pos_gl

class Mesh:
    def __init__(self, shader, vertices=[], pos=Vector3(0, 0, 0), rotz=0, scale=1):
        self.shader = shader
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

        self.set_vertices(self.vertices)

    def set_vertices(self, vertices):
        self.vertices = vertices
        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        verts_gl = (GLfloat * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, sizeof(verts_gl), verts_gl, GL_STATIC_DRAW)
        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), 0)
        # normals
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), 3 * sizeof(GLfloat))
        # colors
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), 6 * sizeof(GLfloat))

        glBindVertexArray(0)

    def draw(self):
        if not self.glsetup:
            self._setup_gl()
        if not self.glsetup:
            return

        glBindVertexArray(self.vao)

        model_mat = Matrix4()\
                .translate(*self.pos)\
                .rotatez(self.rotz)\
                .scale(*((self.scale,) * 3))
        model_gl = (GLfloat * len(model_mat[:]))(*model_mat[:])
        glUniformMatrix4fv(self.shader.uni('model'), 1, GL_FALSE, model_gl)

        norm_mat = model_mat.inverse().transposed()
        norm_gl  = (GLfloat * len(norm_mat[:]))(*norm_mat[:])
        glUniformMatrix4fv(self.shader.uni('norm'), 1, GL_FALSE, norm_gl)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices)//9)

        glBindVertexArray(0)
