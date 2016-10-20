from euclid import *
from random import random

def ccw(a, b, c):
    return (b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)

class Vertex(Point3):
    def __init__(self, x, y, height):
        super(Point3, self).__init__(x, y, height)
        self.halfedge = None

    def __hash__(self):
        return hash((x, y, height))

    def halfedges(self):
        if not self.halfedge:
            return []

        res = [self.halfedge]
        current = self.halfedge.twin.next
        while current != res[0]:
            res += [current]
            current = current.twin.next
        return res

    def add_halfedge(self, new_he):
        hes = self.halfedges()
        insert = None
        if len(hes) == 1:
            insert = hes[0]
        elif len(hes) > 1:
            last = False
            for he in hes:
                curr = ccw(he.origin, he.twin.origin, new_he.origin) > 0
                if last and not curr:
                    insert = he.twin
                    break
                last = curr

        if insert:
            insert.next.prev = new_he.twin
            new_he.twin.next = insert.next
            insert.next = new_he
            new_he.prev = insert
        else:
            new_he.twin.next = new_he
            new_he.prev = new_he.twin
            self.halfedge = new_he

class Halfedge:
    def __init__(self, origin):
        self.origin = origin
        self.twin = None
        self.prev = None
        self.next = None

    def __str__(self):
        return "Halfedge(" + str(self.origin) + ")"

    def vertices(self):
        if not self.twin:
            return (self.origin)
        return (self.origin, self.twin.origin)

class Graph:
    def __init__(self, vertices=[]):
        self.vertices = [
                Vertex( 1,  1, random()),
                Vertex( 1, -1, random()),
                Vertex(-1, -1, random()),
                Vertex(-1,  1, random())
                ]
        self.add_edge(self.vertices[0], self.vertices[1])
        self.add_edge(self.vertices[1], self.vertices[2])
        self.add_edge(self.vertices[2], self.vertices[3])
        self.add_edge(self.vertices[3], self.vertices[0])
        self.add_edge(self.vertices[0], self.vertices[2])
        self._active_face = self.vertices[0].halfedge

    def add_vertex(self, vertex):
        if not self.vertices:
            raise NotImplemented

        first = self._active_face
        face = [first]
        curr  = first.next
        while first != curr:
            if not ccw(curr.origin, curr.twin.origin, vertex) >= 0:
                curr = first = curr.twin
                self._active_face = curr
                face = []
            face.append(curr)
            curr = curr.next

        for he in face:
            self.add_edge(he.origin, vertex)
        self.vertices.append(vertex)

    def add_edge(self, u, v):
        u_he = Halfedge(u)
        v_he = Halfedge(v)

        u_he.twin = v_he
        v_he.twin = u_he

        u.add_halfedge(u_he)
        v.add_halfedge(v_he)

    def gl_vertices(self):
        result = []

        seen = []
        expanded = [self._active_face]
        while expanded:
            temp = [expanded.pop()]

            if temp[0] in seen:
                continue

            while temp[-1].next != temp[0]: # ensure we don't redo the same one
                seen.append(temp[-1])
                temp.append(temp[-1].next)
                expanded.append(temp[-1].twin)

            print(len(temp), *temp)

            if len(temp) > 3:
                continue

            temp = [t.origin for t in temp]
            normal = (temp[1]-temp[0]).cross(temp[1]-temp[2]).normalize()
            color = [random(), random(), random()]

            for t in temp:
                result += [*t, *normal, *color]

        return result

if __name__=="__main__":
    g=Graph()
    print(g.gl_vertices())
    g.add_vertex(Vertex(0.4, 0.3, 0.1))
    print(g.gl_vertices())

