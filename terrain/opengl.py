from ctypes import c_char_p, c_char, cast, pointer, POINTER, sizeof, create_string_buffer
from pyglet.gl import *
from euclid import *

class OpenGL:
    _default_vert = """
    #version 130

    in vec3 position;
    in vec3 normal;
    in vec3 color;

    out vec3 Color;
    out vec3 Normal;
    out vec3 FragPos;

    uniform mat4 normsub;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 proj;

    void main()
    {
        gl_Position = proj * view * model * vec4(position, 1.0);
        FragPos = vec3(model * vec4(position, 1.0));
        Color = color;
        Normal = mat3(normsub) * normal;
    }
    """

    _default_frag = """
    #version 130

    in vec3 FragPos;
    in vec3 Color;
    in vec3 Normal;

    out vec4 outColor;

    uniform vec3 viewPos;
    uniform vec3 lightPos;
    uniform vec3 lightColor;

    void main()
    {
        float ambientStrength = 0.2f;
        vec3 ambient = ambientStrength * lightColor;

        vec3 norm = normalize(Normal);
        vec3 lightDir = normalize(lightPos - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * lightColor;

        float specularStrength = 0.5f;
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16);
        vec3 specular = specularStrength * spec * lightColor;

        vec3 result = (ambient + diffuse + specular) * Color;
        outColor = vec4(result, 1.0);
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
        glValidateProgram(self.shader)
        glUseProgram(self.shader)

        self.normmat_uni = glGetUniformLocation(self.shader, b'normsub')
        self.model_uni = glGetUniformLocation(self.shader, b'model')
        self.view_uni  = glGetUniformLocation(self.shader, b'view')
        self.proj_uni  = glGetUniformLocation(self.shader, b'proj')

        self.view_pos = glGetUniformLocation(self.shader, b'viewPos')
        self.light_color = glGetUniformLocation(self.shader, b'lightColor')
        self.light_pos = glGetUniformLocation(self.shader, b'lightPos')

        glEnable(GL_DEPTH_TEST)
        self.perspective()
        self.view()
        self.model()
        self.light()

    def view(self, pos=Vector3(1, 1, 1), at=Vector3(0, 0, 0), up=Vector3(0, 0, 1)):
        view_mat = Matrix4.new_look_at(pos, at, up)
        view_gl  = (GLfloat * len(view_mat[:]))(*view_mat[:])
        glUniformMatrix4fv(self.view_uni, 1, GL_FALSE, view_gl)
        view_pos_gl = (GLfloat * len(pos[:]))(*pos)
        glUniform3fv(self.view_pos, 1, view_pos_gl)

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
        norm_mat = model_mat.inverse().transposed()
        norm_gl = (GLfloat * len(norm_mat[:]))(*norm_mat[:])
        glUniformMatrix4fv(self.normmat_uni, 1, GL_FALSE, norm_gl)

    def light(self, pos=Vector3(0, -0.2, 2), color=(1.0, 1.0, 1.0)):
        light_pos_gl = (GLfloat * len(pos[:]))(*pos)
        light_color_gl = (GLfloat * len(color))(*color)
        glUniform3fv(self.light_pos, 1, light_pos_gl)
        glUniform3fv(self.light_color, 1, light_color_gl)

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

        self.swap_vertices(self.vertices)

    def swap_vertices(self, vertices):
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
        self.gl.model(pos=self.pos, rotz=self.rotz, scale=self.scale)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices)//9)
        glBindVertexArray(0)
