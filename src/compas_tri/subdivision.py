from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from copy import deepcopy

from compas.utilities import pairwise


__all__ = []


def trimesh_subdivide(mesh, k=1):
    """Subdivide a trimesh - same topology as Loop subdivision without geometry smoothing.

    Parameters
    ----------
    mesh : Mesh
            The trimesh object that will be subdivided.
    k : int, optional
            The number of levels of subdivision.

    """

    for _ in range(k):
        new_vkeys = {}
        for fkey in list(mesh.faces()):
            existing_vkeys = deepcopy(mesh.face_vertices(fkey))
            mesh.delete_face(fkey)
            for u, v in pairwise(existing_vkeys + existing_vkeys[:1]):
                if (v, u) not in new_vkeys:
                    x, y, z = mesh.edge_midpoint(u, v)
                    new_vkeys[(u, v)] = mesh.add_vertex(
                        attr_dict={'x': x, 'y': y, 'z': z})
            a, b, c = existing_vkeys
            ab = new_vkeys[(a, b)] if (
                a, b) in new_vkeys else new_vkeys[(b, a)]
            bc = new_vkeys[(b, c)] if (
                b, c) in new_vkeys else new_vkeys[(c, b)]
            ca = new_vkeys[(c, a)] if (
                c, a) in new_vkeys else new_vkeys[(a, c)]
            mesh.add_face([ab, bc, ca])
            mesh.add_face([ab, b, bc])
            mesh.add_face([bc, c, ca])
            mesh.add_face([ca, a, ab])
