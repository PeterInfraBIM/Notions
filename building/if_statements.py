# give Python access to Blender's functionality
import bpy

# give Python access to Blender's mesh editing functionality
import bmesh

# extend Python's functionality to generate random numbers
import random

def get_random_color() -> object:
    """generate a random color"""
    red = random.random()
    green = random.random()
    blue = random.random()
    alpha = 1.0
    color = (red, green, blue, alpha)
    return color

def generate_random_color_materials(object: object, count: int) -> None:
    """generate random color materials"""
    for i in range(count):
        # create a new material
        mat = bpy.data.materials.new(f"material_{i}")
        mat.diffuse_color = get_random_color()
        
        # add the material to the object
        object.data.materials.append(mat)

def add_ico_sphere(subdivisions: int) -> object :
    """add an ico sphere"""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions)
    return bpy.context.active_object

def assign_materials_to_faces(obj: object) -> None:
    """assign materials to faces"""
    # turn on Edit mode
    bpy.ops.object.editmode_toggle()

    # deselect all faces
    bpy.ops.mesh.select_all(action='DESELECT')

    # get geometry data from the mesh object
    bmesh_obj = bmesh.from_edit_mesh(obj.data)
    
    material_count = len(obj.data.materials)

    # iterate through each face of the mesh
    for face in bmesh_obj.faces:

        # set the active material
        obj.active_material_index = random.randint(0, material_count)

        # select the face and assign the active material
        face.select = True
        bpy.ops.object.material_slot_assign()
        face.select = False

    # turn OFF Edit mode
    bpy.ops.object.editmode_toggle()

# add ico_sphere
ico_object = add_ico_sphere(subdivisions=3)

# create a variable for holding the number of materials to create
material_count = 30

# create and assign materials to the object
generate_random_color_materials(ico_object, material_count)

# assign materials to faces
assign_materials_to_faces(ico_object)

