# give Python access to Blender's functionality
import bpy

# extend Python's math functionality
import math

# add a cube into the scene
bpy.ops.mesh.primitive_cube_add()

# get a reference to the current active object
cube = bpy.context.active_object

# insert key frame at one
start_frame = 1
cube.keyframe_insert("rotation_euler", frame=start_frame)

# change the rotation of the cube around the z-axis
degrees = 90
radians = math.radians(degrees)
cube.rotation_euler.z = radians

# insert key frame at the middle
mid_frame = 90
cube.keyframe_insert("rotation_euler", frame=mid_frame)

# change the rotation of the cube around the x-axis
degrees = 90
radians = math.radians(degrees)
cube.rotation_euler.x = radians

# insert key frame at the last frame
end_frame = 180
cube.keyframe_insert("rotation_euler", frame=end_frame)