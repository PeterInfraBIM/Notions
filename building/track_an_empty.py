# give Python access to Blender's functionality
import bpy

def set_end_frame(frame_count: int) -> None:
    """set the end frame"""
    bpy.context.scene.frame_end = frame_count

def set_fps(fps: int) -> None:
    """set the fps"""
    bpy.context.scene.render.fps = fps

def create_row(cube_count: int, location_offset: float) -> None:
    """create a row of cubes along the Y-axis"""
    for i in range(cube_count):
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, i*location_offset, 0))
        
def create_empty() -> object:
    """create an empty for tracking"""
    bpy.ops.object.empty_add()
    empty = bpy.context.active_object
    insert_keyframe(empty, "location", frame=1)
    return empty

def animate(object: object, cube_count: int, location_offset: float, frame_count: int) -> None :
    """animate the location property of the object"""
    insert_keyframe(object, "location", frame=1)
    object.location.y = cube_count * location_offset
    insert_keyframe(object, "location", frame=frame_count)

def insert_keyframe(object: object, channel: str, frame: int) -> None :
    """insert keyframe"""
    object.keyframe_insert(channel, frame=frame)
    
def set_y_location(object: object, y: float) -> None :
    object.location.y = y
    
def create_camera(start_location: tuple[float], track_to: object) -> object :
    """add a camera into the scene"""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.location = start_location
    insert_keyframe(camera, "location", frame=1)
    bpy.ops.object.constraint_add(type='TRACK_TO')
    camera.constraints["Track To"].target = track_to
    return camera


# create parameters
cube_count = 10
location_offset = 3
frame_count = 250
fps = 30

set_end_frame(frame_count)
set_fps(fps)

create_row(cube_count, location_offset)

empty = create_empty()
animate(empty, cube_count, location_offset, frame_count)
camera = create_camera(start_location=(15.0, 0.0, 2.0), track_to=empty)
animate(camera, cube_count, location_offset, frame_count)
