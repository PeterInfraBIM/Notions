import bpy
import bmesh
import math
from enum import Enum
from bpybb.utils import clean_scene

class Ref(Enum):
    REF = 0
    NOREF = 1

class Dim(Enum):
    DIM_0 = 0
    DIM_1 = 1
    DIM_2 = 2
    DIM_3 = 3

class SideInside(Enum):
    SIDE = 0
    INSIDE = 1

class Metatop(Enum):
    BOUNDARY = 0
    ENCLOSURE = 1

class Inclusion(Enum):
    INCLUSIVE = 0
    EXCLUSIVE = 1

class Shelter(Enum):
    INTERIOR = 0
    EXTERIOR = 1

class FaceOrient(Enum):
    HORIZ = 0
    NON_HORIZ = 1

class HorFaceSideOrient(Enum):
    UP = 0
    DOWN = 1

class HumanPassage(Enum):
    CLOSED = 0
    CONTROLLABLE = 1
    OPEN = 2

class VisualTransparency(Enum):
    CLOSED = 0
    CONTROLLABLE = 1
    OPEN = 2


class Anything:
    def __init__(self, id: str) -> None:
        self.id = id
        self.notions = dict()
        self.repr = dict()

    def __repr__(self) -> str:
        self.repr["id"] = self.id
        self.repr["notions"] = self.notions
        return str(self.repr)

class Network(Anything):
    def __init__(self, id: str, ref: Ref = None) -> None:
        super().__init__(id)
        if ref:
            self.notions["ref"] = ref
    
    def set_source(self, source: object) -> None :
        if self.notions.get("ref") == Ref.REF:
            self.source = source

    def set_target(self, target: object) -> None :
        if self.notions.get("ref") == Ref.REF:
            self.target = target
    
    def set_translation(self, translation: tuple[float]) -> None :
        if self.notions.get("ref") == Ref.REF:
            self.translation = translation
            source_object = bpy.data.objects[self.source.id]
            source_object.location.x +=  self.translation[0]
            source_object.location.y +=  self.translation[1]
            source_object.location.z +=  self.translation[2]

    def set_metatop(self, metatop: Metatop = Metatop.ENCLOSURE, inclusion: Inclusion = Inclusion.EXCLUSIVE) -> None :
        if self.notions.get("ref") == Ref.REF:
            source_object = bpy.data.objects[self.source.id]
            bpy.context.view_layer.objects.active = source_object
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            source_object.modifiers["Solidify"].thickness = 0.2
            source_object.modifiers["Solidify"].offset = 0

            target_object = bpy.data.objects[self.target.id]
            bpy.context.view_layer.objects.active = target_object
            bpy.ops.object.modifier_add(type='BOOLEAN')
            target_object.modifiers["Boolean"].solver = 'FAST'
            target_object.modifiers["Boolean"].object = source_object
            bpy.ops.object.modifier_apply(modifier="Boolean")
            bpy.context.view_layer.objects.active = source_object
            bpy.ops.object.modifier_remove(modifier="Solidify")

    def __repr__(self) -> str:
        if self.notions.get("ref") == Ref.REF:
            self.repr["source"] = self.source.id
            self.repr["target"] = self.target.id
            self.repr["translation"] = self.translation
        return super().__repr__()

class Topology(Network):
    def __init__(self, id: str, ref = Ref.NOREF, dim: Dim = None, side_inside: SideInside = None) -> None:
        super().__init__(id, ref)
        self.dimensions = None
        if dim:
            self.notions["dim"] = dim
        if side_inside:
            self.notions["side_inside"] = side_inside

    def create_geometry(self, dimensions: tuple[float] = None):
        if self.notions.get("ref") == Ref.NOREF:
            if dimensions:
                self.dimensions = dimensions
            if self.notions.get("side_inside") == SideInside.INSIDE:
                if self.notions.get("dim") == Dim.DIM_0:
                    vertices = [(0.0, 0.0, 0.0)]
                    mesh_data = bpy.data.meshes.new("vertex_mesh_data")
                    mesh_data.from_pydata(vertices, [], [])
                    mesh_obj = bpy.data.objects.new("vertex_object", mesh_data)
                    bpy.context.collection.objects.link(mesh_obj)
                if self.notions.get("dim") == Dim.DIM_1:
                    x = 1.0
                    if self.dimensions[0]:
                        x = self.dimensions[0]
                    vertices = [
                        (0.0, 0.0, 0.0),
                        (x, 0.0, 0.0)
                    ]
                    edges = [
                        (0, 1)
                    ]
                    mesh_data = bpy.data.meshes.new("edge_mesh_data")
                    mesh_data.from_pydata(vertices, edges, [])
                    mesh_obj = bpy.data.objects.new("edge_object", mesh_data)
                    bpy.context.collection.objects.link(mesh_obj)
                if self.notions.get("dim") == Dim.DIM_2:
                    x = 1.0
                    y = 1.0
                    if self.dimensions[0]:
                        x = self.dimensions[0]
                    if self.dimensions[1]:
                        y = self.dimensions[1]
                    vertices = [
                        (0.0, 0.0, 0.0),
                        (x, 0.0, 0.0),
                        (x, y, 0.0),
                        (0.0, y, 0.0)
                    ]
                    edges = []
                    faces = [
                        (0, 1, 2, 3)
                    ]
                    mesh_data = bpy.data.meshes.new("face_mesh_data")
                    mesh_data.from_pydata(vertices, edges, faces)
                    mesh_obj = bpy.data.objects.new(self.id, mesh_data)
                    bpy.context.collection.objects.link(mesh_obj)
                    if self.notions.get("face_orient") == FaceOrient.NON_HORIZ:
                        mesh_obj.rotation_euler.x = math.radians(90)
                        bpy.ops.object.select_pattern(pattern='face*')
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if self.notions.get("dim") == Dim.DIM_3:
                    vertices = [
                        (0.0, 0.0, 0.0),
                        (0.0, 1.0, 0.0),
                        (1.0, 1.0, 0.0),
                        (1.0, 0.0, 0.0),
                        (0.0, 0.0, 1.0),
                        (0.0, 1.0, 1.0),
                        (1.0, 1.0, 1.0),
                        (1.0, 0.0, 1.0),
                    ]
                    edges = []
                    faces = [
                        (0, 1, 2, 3),
                        (7, 6, 5, 4), 
                        (4, 5, 1, 0),
                        (7, 4, 0, 3), 
                        (6, 7, 3, 2),
                        (5, 6, 2, 1),
                    ]
                    mesh_data = bpy.data.meshes.new("volume_mesh_data")
                    mesh_data.from_pydata(vertices, edges, faces)
                    mesh_obj = bpy.data.objects.new("volume_object", mesh_data)
                    bpy.context.collection.objects.link(mesh_obj)

class BuildingArchitecture(Topology):
    def __init__(self,
                 id,
                 ref=Ref.NOREF,
                 dim: Dim = None, 
                 side_inside: SideInside = None, 
                 shelter: Shelter = None, 
                 face_orient: FaceOrient = None, 
                 hor_face_side_orient: HorFaceSideOrient = None, 
                 human_passage: HumanPassage = None, 
                 visual_transparency: VisualTransparency = None) -> None:
        super().__init__(id, ref, dim, side_inside)
        if shelter:
            self.notions["shelter"] = shelter
        if face_orient:
            self.notions["face_orient"] = face_orient
        if hor_face_side_orient:
            self.notions["hor_face_side_orient"] = hor_face_side_orient
        if human_passage:
            self.notions["human_passage"] = human_passage
        if visual_transparency:
            self.notions["visual_transparency"] = visual_transparency


def separete_frame_part(window, profile, id, vert_list):
    window.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
 
    bm = bmesh.from_edit_mesh(window.data)
    # bm.from_mesh(window.data)
    
    bpy.ops.mesh.select_mode(type="VERT")
    bm.verts.ensure_lookup_table()
    print(len(bm.verts), vert_list[id], vert_list[(id+1)%4])
    bm.verts[vert_list[id]].select = True
    bm.verts[vert_list[(id+1)%4]].select = True

    bpy.ops.mesh.select_mode(type="EDGE")
    bm.edges.ensure_lookup_table()
    bm.edges[id].select = True
 
    bpy.ops.mesh.separate(type='SELECTED')
    for obj in bpy.context.selected_objects:
        if obj.name != "window_001":
            obj.name = f"frame_00{id}"

    # bm.to_mesh(window.data)
    # window.data.update()
    bmesh.update_edit_mesh(window.data)
    bm.free()

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    

def create_window() -> None :
    # Create frame profile
    bpy.ops.mesh.primitive_plane_add()
    profile = bpy.context.active_object
    profile.name = "profile_001"
    bpy.ops.transform.resize(value=(0.070, 0.070, 1))
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.convert(target='CURVE')

    # Create window plane
    bpy.ops.mesh.primitive_plane_add()
    window = bpy.context.active_object
    window.name = "window_001"
    bpy.ops.transform.resize(value=(1, 0.6, 1))
    bpy.ops.object.transform_apply(scale=True)
    
    vert_list = [0, 1, 3, 2]
    for id in range(len(vert_list)):
        separete_frame_part(window, profile, id, vert_list)
    for id in range(4):
        obj = bpy.data.objects[f'frame_00{id}']
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bpy.ops.mesh.select_mode(type="VERT")
        bm.verts.ensure_lookup_table()
        if id%2 == 0:
            bm.verts[0].co.y += 0.07
            bm.verts[1].co.y -= 0.07
        else:
            bm.verts[0].co.x -= 0.07
            bm.verts[1].co.x += 0.07
        bmesh.update_edit_mesh(obj.data)
        bm.free()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target='CURVE')
        bpy.context.object.data.bevel_mode = 'OBJECT'
        bpy.context.object.data.bevel_object = profile
        bpy.context.view_layer.objects.active = obj
        bpy.context.object.data.use_fill_caps = True
        bpy.ops.object.convert(target="MESH")
        obj.select_set(False)        
    
   

def main():
    clean_scene()

    # vertex = Topology(id="vertex", dim=Dim.DIM_0, side_inside=SideInside.INSIDE)
    # vertex.create_geometry()
    # print(vertex)

    # edge = Topology(id="edge", dim=Dim.DIM_1, side_inside=SideInside.INSIDE)
    # edge.create_geometry(dimensions=(2.0,))
    # print(edge)

    # face = Topology(id="face", dim=Dim.DIM_2, side_inside=SideInside.INSIDE)
    # face.create_geometry()
    # print(face)

    # volume = Topology(id="volume", dim=Dim.DIM_3, side_inside=SideInside.INSIDE)
    # volume.create_geometry()
    # print(volume)

    # window = BuildingArchitecture(
    #     id="#window_001",
    #     dim=Dim.DIM_2, 
    #     side_inside=SideInside.INSIDE, 
    #     face_orient=FaceOrient.NON_HORIZ, 
    #     visual_transparency=VisualTransparency.CONTROLLABLE
    # )
    # window.create_geometry(dimensions=(2.0, 1.2))

    # door = BuildingArchitecture(
    #     id="#door_001",
    #     dim=Dim.DIM_2, 
    #     side_inside=SideInside.INSIDE, 
    #     face_orient=FaceOrient.NON_HORIZ, 
    #     human_passage=HumanPassage.CONTROLLABLE
    # )
    # door.create_geometry(dimensions=(0.9, 2.1))

    # wall = BuildingArchitecture(
    #     id="#wall_001",
    #     dim=Dim.DIM_2, 
    #     side_inside=SideInside.INSIDE, 
    #     face_orient=FaceOrient.NON_HORIZ
    # )
    # wall.create_geometry(dimensions=(4.0, 2.6))

    # link_window2wall = BuildingArchitecture(id="#link_window2wall_001", ref=Ref.REF)
    # link_window2wall.set_source(window)
    # link_window2wall.set_target(wall)
    # link_window2wall.set_translation((1.5, 0.0, 0.9))
    # link_window2wall.set_metatop(metatop=Metatop.ENCLOSURE, inclusion=Inclusion.EXCLUSIVE)

    # link_door2wall = BuildingArchitecture(id="#link_door2wall_001", ref=Ref.REF)
    # link_door2wall.set_source(door)
    # link_door2wall.set_target(wall)
    # link_door2wall.set_translation((0.2, 0.0, 0.02))
    # link_door2wall.set_metatop(metatop=Metatop.ENCLOSURE, inclusion=Inclusion.EXCLUSIVE)

    create_window()

main()
