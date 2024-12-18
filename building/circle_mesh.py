#  give Python access to Blender's functionality
import bpy

# extend Python's math functionality
import math
# extend Python's print functionality
import pprint

def get_circle_vertex_coordinates(vert_count: int, radius: float) -> list[tuple[float]]:
    # initialize parameters
    angle_step = 2 * math.pi / vert_count
    z_step = 0.0

    # create a list of vertex coordinates
    vert_coordinates = list()

    # repeat code in a loop
    for i in range(vert_count):
        # calculate the current angle
        current_angle = i * angle_step

        # calculate coordinate
        x = radius * math.cos(current_angle)
        y = radius * math.sin(current_angle)

        # visualize what we are doing
        z = i * z_step
        # bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location=(x, y, z))

        vert_coordinates.append((x, y, 0))
    
    pprint.pprint(vert_coordinates)
    
    return vert_coordinates
    
    
# initialize parameters
vert_count = 24
radius = 2

# define lists for the verts, edges, and faces

vert_coordinates = get_circle_vertex_coordinates(vert_count, radius)

def get_circle_mesh(vert_count: int, vert_coordinates: list[tuple[float]]):

    vertices = vert_coordinates

    edges = []
    for i in range(vert_count):
        edges.append((i, (i + 1) % vert_count))
#    edges.append((vert_count - 1, 0))

    faces = []

    # create mesh data from the vertex, edge and face data
    mesh_data = bpy.data.meshes.new("circle_data")
    mesh_data.from_pydata(vertices, edges, faces)
    
    # create an object using the mesh data
    mesh_obj = bpy.data.objects.new("circle_obj", mesh_data)

    # link to the scene collection
    bpy.context.collection.objects.link(mesh_obj)
    
    return mesh_obj

mesh_obj = get_circle_mesh(vert_count, vert_coordinates)
#mesh_obj.location.z = radius
#mesh_obj.rotation_euler.x = math.radians(90)
#mesh_obj = get_circle_mesh(vert_count, vert_coordinates)
#mesh_obj.location.z = radius
#mesh_obj.rotation_euler.x = math.radians(90)
#mesh_obj.rotation_euler.z = math.radians(90)
                    