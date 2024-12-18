import bpy
import bmesh

obj_name = "my_shape"

mesh_data = bpy.data.meshes.new(f"{obj_name}_data")

mesh_obj = bpy.data.objects.new(obj_name, mesh_data)

bpy.context.scene.collection.objects.link(mesh_obj)

bm = bmesh.new()

vert_coords = [
    (1.0, 1.0, 0.0),
    (1.0, -1.0, 0.0),
    (-1.0, -1.0, 0.0),
    (-1.0, 1.0, 0.0),
    (0.0, 0.0, 1.0)
]

for coord in vert_coords:
    bm.verts.new(coord)

bm.verts.ensure_lookup_table()

face_vert_indices = [
    (0, 1, 2, 3),
    (4, 1, 0),
    (4, 2, 1),
    (4, 3, 2),
    (4, 0, 3)
]

for vert_indices in face_vert_indices:
    bm.faces.new([bm.verts[index] for index in vert_indices])

bm.to_mesh(mesh_data)

mesh_data.update()

bm.free()

