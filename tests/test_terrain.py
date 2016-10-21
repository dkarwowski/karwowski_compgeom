from terrain.euclid import *
from terrain.geometry import *
import pytest

def test_ccw_ccw():
    assert ccw(Vector3(0, 1, 0), Vector3(0, 0, 0), Vector3(1, 0, 0)) > 0

def test_ccw_cw():
    assert ccw(Vector3(1, 0, 0), Vector3(0, 0, 0), Vector3(0, 1, 0)) < 0

def test_ccw_colinear():
    assert ccw(Vector3(0, 0, 0), Vector3(0, 1, 0), Vector3(0, 2, 0)) == 0

def test_vertex_add_halfedge_none():
    v = Vertex(1, 2, 3)
    u = Vertex(2, 3, 4)
    v_he = Halfedge(v)
    u_he = Halfedge(u)
    v_he.twin = u_he
    u_he.twin = v_he
    v.add_halfedge(v_he)
    u.add_halfedge(u_he)
    assert v_he.twin == u_he
    assert v_he.prev == u_he
    assert v_he.next == u_he
    assert u_he.twin == v_he
    assert u_he.prev == v_he
    assert u_he.next == v_he
    assert v_he in v.halfedges and len(v.halfedges) == 1
    assert u_he in u.halfedges and len(u.halfedges) == 1

def test_vertex_add_halfedge_one():
    v = Vertex(0, 0, 3)
    u = Vertex(1, 0, 3)
    w = Vertex(0, 1, 3)
    vu_he = Halfedge(v)
    uv_he = Halfedge(u)
    vu_he.twin = uv_he
    uv_he.twin = vu_he
    v.add_halfedge(vu_he)
    u.add_halfedge(uv_he)

    vw_he = Halfedge(v)
    wv_he = Halfedge(w)
    vw_he.twin = wv_he
    wv_he.twin = vw_he
    v.add_halfedge(vw_he)
    assert len(v.halfedges) == 2
    assert vu_he in v.halfedges and vw_he in v.halfedges
    assert uv_he.next == vw_he
    assert vw_he.prev == uv_he
    assert vu_he.prev == wv_he
    assert wv_he.next == vu_he
    assert wv_he.next.origin == wv_he.twin.origin

    w.add_halfedge(wv_he)
    assert vw_he.prev == uv_he
    assert wv_he.next == vu_he
    assert vw_he.next == wv_he
    assert wv_he.prev == vw_he
    assert vw_he.next.origin == vw_he.twin.origin

def test_vertex_add_halfedge_acute():
    v = Vertex(0, 0, 3)
    u = Vertex(1, 0, 3)
    w = Vertex(0, 1, 3)
    vu_he = Halfedge(v)
    uv_he = Halfedge(u)
    vu_he.twin = uv_he
    uv_he.twin = vu_he
    v.add_halfedge(vu_he)
    u.add_halfedge(uv_he)
    vw_he = Halfedge(v)
    wv_he = Halfedge(w)
    vw_he.twin = wv_he
    wv_he.twin = vw_he
    v.add_halfedge(vw_he)
    w.add_halfedge(wv_he)

    x = Vertex(1, 1, 3)
    vx_he = Halfedge(v)
    xv_he = Halfedge(x)
    vx_he.twin = xv_he
    xv_he.twin = vx_he
    v.add_halfedge(vx_he)
    assert len(v.halfedges) == 3
    #assert v.halfedges.index(vx_he) == 1
    assert xv_he.next.origin == xv_he.twin.origin
    assert xv_he.next == vu_he
    assert vu_he.prev == xv_he
    assert vx_he.prev == wv_he
    assert wv_he.next == vx_he

