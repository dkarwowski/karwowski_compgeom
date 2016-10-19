#!/usr/bin/env python

import ctypes as c

import pyglet
from pyglet.gl import *
from pyglet.window import mouse, key

from opengl import OpenGL, Mesh
from euclid import *

# set up a window
config = pyglet.gl.Config(sample_buffers=1, samples=4, depth_size=24)
window = pyglet.window.Window(1600, 900, config=config, resizable=False)

keys = key.KeyStateHandler()

# general settings
window.push_handlers(keys)
window.set_minimum_size(800, 450)
mouse_sensitivity = 0.005

# game objects
opengl = OpenGL()
meshes = [Mesh(opengl), Mesh(opengl)]

cam_pos = Vector3(1.2, 1.2, 1.2)
cam_at  = -cam_pos
cam_up  = Vector3(0, 0, 1)

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

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    global meshes
    for m in meshes:
        m.rot.z += dx * mouse_sensitivity

@window.event
def on_draw():
    global rotation, meshes
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for m in meshes:
        m.draw()

def update(dt):
    global cam_pos, cam_at, cam_up, opengl

    if keys[key.W]:
        cam_pos += cam_at * dt
    if keys[key.S]:
        cam_pos -= cam_at * dt

    opengl.view(cam_pos, cam_pos + cam_at, cam_up)

# generate meshes
meshes[0].vertices = [
        -0.5,  0.5, 0.1, 1.0, 0.0, 0.0,
        -0.5, -0.5, 0.2, 1.0, 0.0, 0.0,
         0.5, -0.5, 0.3, 1.0, 0.0, 0.0,
         0.5, -0.5, 0.3, 0.0, 1.0, 0.0,
         0.5,  0.5, 0.4, 0.0, 1.0, 0.0,
        -0.5,  0.5, 0.1, 0.0, 1.0, 0.0
        ]

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
