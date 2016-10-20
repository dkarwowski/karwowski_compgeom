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
opengl.orthographic()
meshes = [
        Mesh(opengl, pos=Vector3(-0.85, 0, 0), scale=0.5),
        Mesh(opengl, pos=Vector3(0.85, 0, 0), scale=0.5)
        ]

cam_pos = Vector3(0, -1.0, 1.0)
cam_at  = Vector3(0, 1.0, -0.5)
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

    # draw ui
    glClear(GL_DEPTH_BUFFER_BIT)
    opengl.orthographic(scale=window.height)
    opengl.view(
            pos=Vector3(window.width/2, window.height/2, 1),
            at=Vector3(window.width/2, window.height/2, 0),
            up=Vector3(0, 1, 0))
    v = [
            99.5, 99.5, 0, 0.9, 0.9, 0.9,
            99.5,  9.5, 0, 0.9, 0.9, 0.9,
             9.5, 99.5, 0, 0.9, 0.9, 0.9
            ]
    mesh = Mesh(opengl, vertices=v, pos=Vector3(window.width/2, window.height/2, 0))
    mesh.draw()
    opengl.view(cam_pos, cam_pos + cam_at, cam_up)
    opengl.orthographic(scale=1.0)

def update(dt):
    global cam_pos, cam_at, cam_up, opengl

    if keys[key.W]:
        cam_pos += cam_at.normalized() * dt
    if keys[key.S]:
        cam_pos -= cam_at.normalized() * dt
    if keys[key.A]:
        cam_pos -= cam_at.cross(cam_up).normalized() * dt
    if keys[key.D]:
        cam_pos += cam_at.cross(cam_up).normalized() * dt

    opengl.view(cam_pos, cam_pos + cam_at, cam_up)

# generate meshes
meshes[0].vertices = [
        -1.0,  1.0, 0.2, 1.0, 0.0, 0.0,
        -1.0, -1.0, 0.3, 1.0, 0.0, 0.0,
         1.0, -1.0, 0.4, 1.0, 0.0, 0.0,

         1.0, -1.0, 0.4, 0.0, 1.0, 0.0,
         1.0,  1.0, 0.5, 0.0, 1.0, 0.0,
        -1.0,  1.0, 0.2, 0.0, 1.0, 0.0,

        -1.0,  1.0, 0.2, 0.3, 0.3, 0.3,
        -1.0,  1.0, 0.0, 0.3, 0.3, 0.3,
        -1.0, -1.0, 0.0, 0.3, 0.3, 0.3,

        -1.0,  1.0, 0.2, 0.3, 0.3, 0.3,
        -1.0, -1.0, 0.0, 0.3, 0.3, 0.3,
        -1.0, -1.0, 0.3, 0.3, 0.3, 0.3,

        -1.0, -1.0, 0.3, 0.3, 0.3, 0.3,
        -1.0, -1.0, 0.0, 0.3, 0.3, 0.3,
         1.0, -1.0, 0.0, 0.3, 0.3, 0.3,

        -1.0, -1.0, 0.3, 0.3, 0.3, 0.3,
         1.0, -1.0, 0.0, 0.3, 0.3, 0.3,
         1.0, -1.0, 0.4, 0.3, 0.3, 0.3,

         1.0, -1.0, 0.4, 0.3, 0.3, 0.3,
         1.0, -1.0, 0.0, 0.3, 0.3, 0.3,
         1.0,  1.0, 0.0, 0.3, 0.3, 0.3,

         1.0, -1.0, 0.4, 0.3, 0.3, 0.3,
         1.0,  1.0, 0.0, 0.3, 0.3, 0.3,
         1.0,  1.0, 0.5, 0.3, 0.3, 0.3,

         1.0,  1.0, 0.5, 0.3, 0.3, 0.3,
         1.0,  1.0, 0.0, 0.3, 0.3, 0.3,
        -1.0,  1.0, 0.0, 0.3, 0.3, 0.3,

         1.0,  1.0, 0.5, 0.3, 0.3, 0.3,
        -1.0,  1.0, 0.0, 0.3, 0.3, 0.3,
        -1.0,  1.0, 0.2, 0.3, 0.3, 0.3
        ]
meshes[1].vertices = meshes[0].vertices

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()

