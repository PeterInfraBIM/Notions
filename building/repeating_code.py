# give Python access to Blender's functionality
import bpy

# extend Python's math functionality
import math

# create variables used in the loop
radius_step = 0.1
current_radius = 0.1
number_hexagons = 50
current_z_rotation = 0
z_rotation_step = 5

for i in range(1, number_hexagons):
    # add a hexagon mesh into the scene
    current_radius = radius_step * i
    bpy.ops.mesh.primitive_circle_add(vertices=6, radius=current_radius)

    # get a reference to the currently active object
    hexagon_mesh = bpy.context.active_object

    # rotate mesh about the x-axis
    degrees = -90
    hexagon_mesh.rotation_euler.x = math.radians(degrees)
    
     # rotate mesh about the z-axis
    current_z_rotation = i * z_rotation_step;
    hexagon_mesh.rotation_euler.z = math.radians(current_z_rotation)

    # convert mesh into a curve
    bpy.ops.object.convert(target='CURVE')

    # add bevel to curve
    hexagon_mesh.data.bevel_depth = 0.05
    hexagon_mesh.data.bevel_resolution = 16

    # shade smooth
    bpy.ops.object.shade_smooth()
