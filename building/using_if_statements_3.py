import bpy

def change_name(obj, item):
    print("In change name...", obj.name)
    obj.name = f"obj.{item['name']}.{item['index']:03d}"
    obj.data.name = f"mesh.{item['name']}.{item['index']:03d}"
    item['index'] += 1

count = 10
x_offset = 3
z_offset = 3

for i in range(count):
    bpy.ops.mesh.primitive_cube_add(location=(i * x_offset, 0, 0))
    bpy.ops.mesh.primitive_ico_sphere_add(location=(i * x_offset, 0, z_offset))
    bpy.ops.mesh.primitive_monkey_add(location=(i * x_offset, 0, 2 * z_offset))


dict = {
    "cube": {
        "name": "cube",
        "index": 0
    },
    "ico": {
        "name": "ico",
        "index": 0
    },
    "monkey": {
        "name": "monkey",
        "index": 0
    }
}

for obj in bpy.data.objects:
    if "Cube" in obj.name:
        change_name(obj, dict["cube"])
    elif "Ico" in obj.name:
        change_name(obj, dict["ico"])
    elif "Suzanne" in obj.name:
        change_name(obj, dict["monkey"])
    