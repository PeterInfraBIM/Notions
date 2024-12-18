import bpy

verts = [
    (-1.0, -1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (1.0, 1.0, -1.0),
    (1.0, -1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (-1.0, 1.0, 1.0),
    (1.0, 1.0, 1.0),
    (1.0, -1.0, 1.0),
]
faces = [
    (0, 1, 3), (1, 2, 3),
    (7, 6, 4), (4, 6, 5),
    (4, 5, 0), (0, 5, 1),
    (7, 4, 3), (3, 4, 0),
    (6, 7, 2), (2, 7, 3),
    (5, 6, 1), (1, 6, 2),
]
edges = []

mesh_data = bpy.data.meshes.new("cube_data")
mesh_data.from_pydata(verts, edges, faces)

mesh_obj = bpy.data.objects.new("cube_object", mesh_data)

bpy.context.collection.objects.link(mesh_obj)