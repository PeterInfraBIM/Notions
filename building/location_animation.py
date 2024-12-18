# gice Python access to Blender's functionality
import bpy

# add a cube (pyramid) into the scene
bpy.ops.mesh.primitive_cube_add()

# get a reference to the currently active object
cube = bpy.context.active_object

cube.location = (-5.0, -5.0, -5.0)

# insert a key frame at frame one
start_frame = 1
cube.keyframe_insert("location", frame=start_frame) 

# change the location of the cube on the z-axis
cube.location = (5.0, 5.0, 5.0)

# insert a key frame  at the last frame
mid_frame = 90
cube.keyframe_insert("location", frame=mid_frame) 

# change the location of the cube on the z-axis
cube.location = (-5.0, -5.0, -5.0)

# insert a key frame  at the last frame
last_frame = 180
cube.keyframe_insert("location", frame=last_frame) 