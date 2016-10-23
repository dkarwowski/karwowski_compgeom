#!/usr/bin/env python

import ctypes as c

import pyglet
from pyglet.gl import *
from pyglet.window import mouse, key
from random import random

from .opengl import ShaderLoader, Mesh, Camera
from .euclid import *
from .geometry import Graph, Vertex

# set up a window
config = pyglet.gl.Config(sample_buffers=1, samples=4, depth_size=24)
window = pyglet.window.Window(1600, 900, config=config, resizable=False)

keys = key.KeyStateHandler()

# general settings
window.push_handlers(keys)
window.set_minimum_size(800, 450)
mouse_sensitivity = 0.005

# game objects
shader = ShaderLoader.get_shader()
glUseProgram(shader.handle)
meshes = [
        Mesh(shader, pos=Vector3(-0.85, 0, 0), scale=0.5),
        Mesh(shader, pos=Vector3(0.85, 0, 0), scale=0.5),
        ]
graphs = [
        Graph(),
        Graph()
        ]

graphs[0].add_edge(graphs[0].vertices[0], graphs[0].vertices[2])
graphs[1].add_edge(graphs[1].vertices[1], graphs[1].vertices[3])

cam = Camera(Vector3(0, -1.0, 1.0), Vector3(0, 1.0, -0.5), Vector3(0, 0, 1))
cam.set_ortho(1.0, window.width/window.height, 0.1, 10.0)
proj_gl = cam.get_proj()
glUniformMatrix4fv(shader.uni('proj'), 1, GL_FALSE, proj_gl)

light_pos = Vector3(0, -0.2, 2)
light_pos_gl = (GLfloat * len(light_pos[:]))(*light_pos)
glUniform3fv(shader.uni('lightPos'), 1, light_pos_gl)
light_color = (1.0, 1.0, 1.0)
light_color_gl = (GLfloat * len(light_color))(*light_color)
glUniform3fv(shader.uni('lightColor'), 1, light_color_gl)

glEnable(GL_DEPTH_TEST)

@window.event
def on_mouse_press(x, y, button, modifiers):
    global window
    # add check that depends on where x & y is
    window.set_exclusive_mouse(True)

@window.event
def on_mouse_release(x, y, button, modifiers):
    global window
    # add check that depends on where x & y is
    window.set_exclusive_mouse(False)

    p = Vertex(random()*2 - 1, random()*2 - 1, random())
    graphs[0].add_vertex(p.copy())
    graphs[1].add_vertex(p.copy())
    meshes[0].set_vertices(graphs[0].gl_vertices())
    meshes[1].set_vertices(graphs[1].gl_vertices())

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    global meshes, mouse_sensitivity
    for m in meshes:
        m.rotz += dx * mouse_sensitivity

@window.event
def on_draw():
    global meshes

    # draw 3d
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for m in meshes:
        m.draw()

def update(dt):
    global cam, shader

    if keys[key.W]:
        cam.pos += cam.at.normalized() * dt
    if keys[key.S]:
        cam.pos -= cam.at.normalized() * dt
    if keys[key.A]:
        cam.pos -= cam.at.cross(cam.up).normalized() * dt
    if keys[key.D]:
        cam.pos += cam.at.cross(cam.up).normalized() * dt

    view_gl = cam.get_view()
    glUniformMatrix4fv(shader.uni('view'), 1, GL_FALSE, view_gl)
    view_pos_gl = cam.get_view_pos()
    glUniform3fv(shader.uni('viewPos'), 1, view_pos_gl)

# generate meshes
meshes[0].vertices = graphs[0].gl_vertices()
meshes[1].vertices = graphs[1].gl_vertices()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()

