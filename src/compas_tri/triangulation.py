from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh

from compas_singular.topology import is_adjacency_two_colorable
from compas_singular.datastructures import mesh_vertex_2_coloring, mesh_face_2_coloring, quad_mesh_polyedge_subcolor

from compas.geometry import Polyline


__all__ = [
    'triangulation_double',
    'triangulation_simple_two_directions',
    'triangulation_simple_one_direction',
    'triremesh_two_color_quadmesh'
]


def triangulation_double(mesh):
    """Double triangulation of a quad mesh by adding four edges per face. Mesh gets directly modified.

    Parameters
    ----------
    mesh : Mesh
            The quad mesh data structure.

    """

    new_faces = {}
    for fkey in mesh.faces():
        new_faces[fkey] = []
        x, y, z = mesh.face_centroid(fkey)
        w = mesh.add_vertex(x=x, y=y, z=z)
        for u, v in mesh.face_halfedges(fkey):
            new_faces[fkey].append((u, v, w))

    for fkey, faces in new_faces.items():
        mesh.delete_face(fkey)
        for face in faces:
            mesh.add_face(face)


def triangulation_simple_two_directions(mesh, color=0):
    """Simple continuous triangulation of a quad mesh in two directions by adding only one edge per face. Quad mesh must have vertex two coloring. Mesh gets directly modified.

    Parameters
    ----------
    mesh : Mesh
            The quad mesh data structure.
    color : bool
            Pick one of the two color directions.

    """

    vertex2color = mesh_vertex_2_coloring(mesh)

    new_faces = {}
    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        if vertex2color[a] != color:
            a, b, c, d = b, c, d, a
        face0 = (a, b, c)
        face1 = (c, d, a)
        new_faces[fkey] = (face0, face1)

    for fkey, faces in new_faces.items():
        mesh.delete_face(fkey)
        for face in faces:
            mesh.add_face(face)


def triangulation_simple_one_direction(mesh, color=0):
    """Simple continuous triangulation of a quad mesh in one direction by adding only one edge per face. Quad mesh must have face two coloring. Mesh gets directly modified.

    Parameters
    ----------
    mesh : Mesh
            The quad mesh data structure.
    color : bool
            Pick one of the two color directions.

    """

    vertex2color = mesh_vertex_2_coloring(mesh)
    face2color = mesh_face_2_coloring(mesh)

    new_faces = {}
    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        if abs(vertex2color[a] - face2color[fkey]) != color:
            a, b, c, d = b, c, d, a
        face0 = (a, b, c)
        face1 = (c, d, a)
        new_faces[fkey] = (face0, face1)

    for fkey, faces in new_faces.items():
        mesh.delete_face(fkey)
        for face in faces:
            mesh.add_face(face)


def triremesh_two_color_quadmesh(mesh, color=0, color2=0):

    remesh = Mesh()

    graph = quadmesh_polyedge_graph_subcolor(mesh, color=color)

    pkey2color = is_adjacency_two_colorable(graph.adjacency)

    # vertices
    new_polyedges = {}
    for pkey, polyedge in mesh.polyedges(data=True):
        if pkey in pkey2color and pkey2color[pkey] == color2:
            n = len(polyedge)
            polyline = Polyline([mesh.vertex_coordinates(vkey)
                                 for vkey in polyedge])
            new_polyline = Polyline([polyline.point(i / n)
                                     for i in range(n + 1)])
            new_polyedge = []
            for x, y, z in new_polyline:
                vkey = remesh.add_vertex(attr_dict={'x': x, 'y': y, 'z': z})
                new_polyedge.append(vkey)
                new_polyedges[pkey] = new_polyedge
        else:
            new_polyedge = []
            for vkey in polyedge:
                x, y, z = mesh.vertex_coordinates(vkey)

                vkey = remesh.add_vertex(attr_dict={'x': x, 'y': y, 'z': z})
                new_polyedge.append(vkey)
            new_polyedges[pkey] = new_polyedge

    # faces
    for pkey0 in mesh.polyedges():
        if pkey0 in pkey2color and pkey2color[pkey0] != color2:
            vkeys0 = new_polyedges[pkey0]
            n = len(vkeys0)
            for pkey1 in graph.neighbors(pkey0):
                vkeys1 = new_polyedges[pkey1]
                print(mesh.polyedge_vertices(pkey0)[0], mesh.polyedge_vertices(pkey1)[
                      0], mesh.polyedge_vertices(pkey1)[-1], mesh.halfedge[mesh.polyedge_vertices(pkey0)[0]])
                if not (mesh.has_edge((mesh.polyedge_vertices(pkey0)[0], mesh.polyedge_vertices(pkey1)[0])) or mesh.has_edge((mesh.polyedge_vertices(pkey0)[0], mesh.polyedge_vertices(pkey1)[-1]))):
                    print('!', mesh.polyedge_vertices(pkey0))
                    print('!!', mesh.polyedge_vertices(pkey1))
                # if mesh.has_edge((mesh.polyedge_vertices(pkey0)[0], mesh.polyedge_vertices(pkey1)[0])):
                    #vkeys1 = list(reversed(vkeys1))
                    # exception if polyedge is closed
                for i in range(n):
                    remesh.add_face([vkeys0[i], vkeys1[i], vkeys1[i + 1]])
                    if i < n - 1:
                        remesh.add_face(
                            [vkeys0[i], vkeys1[i + 1], vkeys0[i + 1]])
                    # is orientation of faces consistent?

    return remesh
