import OpenGL.GL as GL
import pygame
import numpy
import math

vertex_shader = """
#version 330

in vec2 position;
in vec2 coord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 texcoord;

void main()
{
    vec4 pos = vec4(position.xy, 1.0f, 1.0f);
    gl_Position = projection * view * model * pos;
    texcoord = coord;
}
"""

fragment_shader = """
#version 330
in vec2 texcoord;
uniform vec4 color;
uniform sampler2D tex;

void main()
{
   gl_FragColor = vec4((color.rgb * texture(tex, texcoord).rgb), color.a);
}
"""
vertices = [
     0.5,  0.5,   1.0, 1.0,   # Top Right
     0.5, -0.5,   1.0, 0.0,   # Bottom Right
    -0.5,  0.5,   0.0, 1.0,   # Top Left 
     0.5, -0.5,   1.0, 0.0,   # Bottom Right
    -0.5, -0.5,   0.0, 0.0,   # Bottom Left
    -0.5,  0.5,   0.0, 1.0    # Top Left 
]
vertices = numpy.array(vertices, dtype=numpy.float32)


def identity4x4():
    m = [0.0 for _ in range(16)]
    m[0] = m[5] = m[10] = m[15] = 1.0
    return m


def translation4x4(x, y, z=0.0):
    m = identity4x4()
    m[12] = x
    m[13] = y
    m[14] = z
    return m


def transform4x4(translation, rotation, scaling):
    m = translation4x4(*translation)
    r = math.radians(rotation)
    s = math.sin(r)
    c = math.cos(r)
    m[0] = scaling[1] * c
    m[1] = scaling[1] * s
    m[4] = scaling[0] * (-s)
    m[5] = scaling[0] * c
    if len(scaling) == 3:
        m[10] = scaling[2]

    return m


def ortho4x4(left, right, bottom, top, near, far):
    m = identity4x4()
    m[0] = 2.0 / (right - left)
    m[5] = 2.0 / (top - bottom)
    m[10] = -2.0 / (far - near)
    m[12] = -((right + left) / float(right - left))
    m[13] = -((top + bottom) / float(top - bottom))
    m[14] = -((far + near) / float(far - near))
    return m


def create_texture(filename):
    # Load and create a texture 
    texture = GL.glGenTextures(1);
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture); # All upcoming GL_TEXTURE_2D operations now have effect on this texture object
    # Set the texture wrapping parameters
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT);   # Set texture wrapping to GL_REPEAT (usually basic wrapping method)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT);
    # Set texture filtering parameters
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR);
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR);
    # Load image, create texture and generate mipmaps
    image = pygame.image.load(filename);
    width, height = image.get_size()
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, width, height, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGB", 1));
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D);
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0); # Unbind texture when done, so we won't accidentily mess up our texture.

    return texture


def create_object(shader):
    # Create a new VAO (Vertex Array Object) and bind it
    vertex_array_object = GL.glGenVertexArrays(1)
    GL.glBindVertexArray( vertex_array_object )

    # Generate buffers to hold our vertices
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)

    # Get the position of the 'position' in parameter of our shader and bind it.
    position = GL.glGetAttribLocation(shader, 'position')
    GL.glEnableVertexAttribArray(position)

    coord = GL.glGetAttribLocation(shader, 'coord')
    GL.glEnableVertexAttribArray(coord)

    # Describe the 'position' data layout in the buffer
    GL.glVertexAttribPointer(position, 2, GL.GL_FLOAT, False, 16, GL.GLvoidp(0))
    GL.glVertexAttribPointer(coord, 2, GL.GL_FLOAT, False, 16, GL.GLvoidp(8))

    # Send the data over to the buffer
    GL.glBufferData(GL.GL_ARRAY_BUFFER, 96, vertices, GL.GL_STATIC_DRAW)

    # Unbind the VAO first (Important)
    GL.glBindVertexArray(0)

    # Unbind other stuff
    GL.glDisableVertexAttribArray(position)
    GL.glDisableVertexAttribArray(coord)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    return vertex_array_object


def create_shader(vertex_shader_code, fragment_shader_code):
    vshader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(vshader, vertex_shader_code)
    GL.glCompileShader(vshader)

    if not GL.glGetShaderiv(vshader, GL.GL_COMPILE_STATUS):
        raise RuntimeError(GL.glGetShaderInfoLog(vshader))

    fshader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(fshader, fragment_shader_code)
    GL.glCompileShader(fshader)

    if not GL.glGetShaderiv(fshader, GL.GL_COMPILE_STATUS):
        raise RuntimeError(GL.glGetShaderInfoLog(fshader))
    
    program = GL.glCreateProgram()
    GL.glAttachShader(program, vshader)
    GL.glAttachShader(program, fshader)
    GL.glLinkProgram(program)

    if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
        raise RuntimeError(GL.glGetProgramInfoLog(program))

    return program


def clear(color=None):
    if color is not None:
        GL.glClearColor(*color)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)


def display(shader, vertex_array_object, texture, color, model, view, projection):
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    GL.glUseProgram(shader)
    loc = GL.glGetUniformLocation(shader, "color")
    GL.glUniform4f(loc, *color)

    loc = GL.glGetUniformLocation(shader, "model")
    GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, model)

    loc = GL.glGetUniformLocation(shader, "view")
    GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, view)

    loc = GL.glGetUniformLocation(shader, "projection")
    GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, projection)

    GL.glBindVertexArray( vertex_array_object )
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
    GL.glBindVertexArray( 0 )
    
    GL.glUseProgram(0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)


def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512), pygame.OPENGL|pygame.DOUBLEBUF)
    GL.glClearColor(0.5, 0.5, 0.5, 1.0)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);
    GL.glBlendEquation(GL.GL_FUNC_ADD);
    GL.glViewport(0, 0, 512, 512)

    texture = create_texture('container.jpg')
    shader = create_shader(vertex_shader, fragment_shader)
    vertex_array_object = create_object(shader)
    clock = pygame.time.Clock()
    pos = 250, 250
    angle = 0
    model1 = transform4x4((250.0, 256.0), 0.0, (250.0, 250.0))
    model2 = transform4x4(pos, angle, (200.0, 200.0))
    view = transform4x4((0.0, 0.0), 0.0, (1.0, 1.0))
    projection = ortho4x4(0, 512, 0, 512, -1, 1)
    
    while True:     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos[0], 512-event.pos[1]
                if event.button == 4:
                    angle = (angle + 10.0) % 360.0
                if event.button == 5:
                    angle = (angle - 10.0) % 360.0
                model2 = transform4x4(pos, angle, (200.0, 200.0))

        yellow = 1.0, 0.0, 0.0, 1.0
        red = 1.0, 1.0, 1.0, 0.75
        clear()
        display(shader, vertex_array_object, texture, yellow, model1, view, projection)
        display(shader, vertex_array_object, texture, red, model2, view, projection)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
