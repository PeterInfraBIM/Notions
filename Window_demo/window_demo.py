from ariadne import gql, QueryType, MutationType, ObjectType, InputType, EnumType, UnionType, make_executable_schema
from ariadne.asgi import GraphQL
import uvicorn
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD, Namespace, BNode
import uuid
from notions import NotionFrame, NotionValue, PerceptiveFrame, PerceptiveFrameInstance, NotionType, NotionUnit, create_notion_frame, create_perceptive_frame, create_perceptive_frame_instance, create_notion_value


class Transparancy(Enum):
    OPAQUE = "OPAQUE"
    SEMI_TRANSPARANT = "SEMI-TRANSPARANT"
    TRANSPARANT = "TRANSPARANT"


class Movable(Enum):
    FIXED = "FIXED"
    SHIFTABLE = "SHIFTABLE"
    ROTATABLE = "ROTATABLE"


class RotationAxis(Enum):
    HORIZONTAL_BOTTOM = "HORIZONTAL-BOTTOM"
    HORIZONTAL_TOP = "HORIZONTAL-TOP"
    VERTICAL_LEFT = "VERTICAL-LEFT"
    VERTICAL_RIGHT = "VERTICAL-RIGHT"


class RotationSide(Enum):
    INWARD = "INWARD"
    OUTWARD = "OUTWARD"


class Window:
    all_windows = dict()

    def __init__(self, windowInput: dict) -> None:
        self.windowId = windowInput["windowId"]
        self.width = windowInput["width"]
        self.height = windowInput["height"]
        self.bays = []
        for bayInput in windowInput["bayInput"]:
            self.bays.append(Bay(bayInput))
        Window.all_windows[self.windowId] = self
        

class Bay:
    def __init__(self, bayInput: dict) -> None:
        self.width = bayInput["width"]
        self.segments = []
        for segmentInput in bayInput["segmentInput"]:
            if segmentInput.get("fixed"):
                self.segments.append(FixedSegment(segmentInput))
            else:
                self.segments.append(RotatableSegment(segmentInput))

class Segment:
    def __init__(self, segmentInput: dict) -> None:
        pass


class FixedSegment(Segment):
    def __init__(self, segmentInput: dict)-> None:
        self.movable = Movable.FIXED.name
        self.height = segmentInput["fixed"]["height"]
        self.thickness = segmentInput["fixed"]["thickness"]
        self.transparancy = segmentInput["fixed"]["transparancy"]


class RotatableSegment(Segment):
    def __init__(self, segmentInput: dict) -> None:
        self.movable = Movable.ROTATABLE.name
        self.height = segmentInput["rotatable"]["height"]
        self.thickness = segmentInput["rotatable"]["thickness"]
        self.transparancy = segmentInput["rotatable"]["transparancy"]
        self.rotationParams = segmentInput["rotatable"]["rotationParams"]


class RotationParams:
    def __init__(self, axis: RotationAxis, side: RotationSide) -> None:
        self.axis = axis
        self.side = side

#######################################
# Topological Network
#######################################

class Node:
    def __init__(self, id: str = None, label: str = None) -> None:
        if id is None:
            id = f"{uuid.uuid4()}"
        self.id = id
        self.label = label
        self.has_parameter_type_set: PerceptiveFrame = None
        self.has_parameter_value_set: PerceptiveFrameInstance = None

class Module(Node):
    def __init__(self, id: str = None, label: str = None, portCount: int = 0) -> None:
        super().__init__(id=id, label=label)
        self.ports: list[Port] = []
        for i in range(portCount):
            self.ports.append(Port(id=self.id+"_"+str(i),label = self.label+f" Port{i}", portType = PortType.MODULE.name, owner = self))

class Slot(Node):
    def __init__(self, id: str, label: str, dimension: int, downPortCount: int = 0, upPortCount: int = 0, insidePortCount: int = 0, outsidePortCount: int = 0) -> None:
        super().__init__(id=id, label=label)
        self.network = None
        self.dimension: int = dimension
        self.downPorts: list[Port] = []
        for i in range(downPortCount):
            self.downPorts.append(Port(id=self.id+"_d"+str(i),label = self.label+f" DownPort{i}", portType = PortType.DOWN.name, owner = self))
        self.upPorts: list[Port] = []
        for i in range(upPortCount):
            self.upPorts.append(Port(id=self.id+"_u"+str(i),label = self.label+f" UpPort{i}", portType = PortType.UP.name, owner = self))
        self.insidePorts: list[Port] = []
        for i in range(insidePortCount):
            self.insidePorts.append(Port(id=self.id+"_i"+str(i),label = self.label+f" InsidePort{i}", portType = PortType.INSIDE.name, owner = self))
        self.outsidePorts: list[Port] = []
        for i in range(outsidePortCount):
            self.outsidePorts.append(Port(id=self.id+"_o"+str(i),label = self.label+f" OutsidePort{i}", portType = PortType.OUTSIDE.name, owner = self))

class PortType(Enum):
    DOWN = "DOWN"
    UP = "UP"
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"
    MODULE = "MODULE"

class Port(Node):
    def __init__(self, id: str, label: str, portType: PortType, owner: Node = None, feature: str = None) -> None:
        super().__init__(id=id, label=label)
        self.portType: PortType = portType
        self.owner: Node = owner
        self.feature = feature
    
class Connection:
    def __init__(self, downPort: Port = None, upPort: Port = None, insidePort: Port = None, outsidePort: Port = None, 
                 downFeature: str = None, upFeature: str = None, insideFeature: str = None, outsideFeature: str = None) -> None:
        self.id = f"{uuid.uuid4()}"
        self.downPort: Port = downPort
        self.upPort: Port = upPort
        self.insidePort: Port = insidePort
        self.outsidePort: Port = outsidePort
        if self.downPort:
            self.downPort.feature = downFeature
        if self.upPort:
            self.upPort.feature = upFeature
        if self.insidePort:
            self.insidePort.feature = insideFeature
        if self.outsidePort:
            self.outsidePort.feature = outsideFeature

class Aggregation:
    def __init__(self, part: Node, assembly: Node):
        self.id = f"{uuid.uuid4()}"
        self.part = part
        self.assembly = assembly

class TopologicalNetwork:
    def __init__(self, module: Module = None, slots: list[Slot] = [], aggregations: list[Aggregation] = [], connections: list[Connection] = [])-> None:
        self.module = module
        self.slots: list[Slot] = slots
        for slot in slots:
            slot.network = self
        self.aggregations: list[Aggregation] = aggregations
        self.connections: list[Connection] = connections

def init_size():
    global nf_size
    nf_size = create_notion_frame(
        id="NF_Size",
        parameter="size",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {"size": args['size']}
    """)

def init_gravitation_orientation():
    global nf_gravitation_orientation
    nf_gravitation_orientation = create_notion_frame(
        id="NF_GravitationOrientation",
        parameter="gravitation_orientation",
        type=NotionType.ENUMERATION,
        unit=NotionUnit.NONE,
        derivedFrom=[],
        converter="""
from enum import Enum
    
class GravitationOrientation(Enum):
    ALIGNED = \"ALIGNED\"
    PERPENDICULAR = \"PERPENDICULAR\"
    OTHER = \"OTHER\"

def converter_function(args):
    gravitation_orientation = GravitationOrientation(args['gravitation_orientation'])
    return {\"gravitation_orientation\": gravitation_orientation}
    """       
    )

def init_nf_width():
    global nf_width
    nf_length = create_notion_frame(
        id="NF_Width",
        parameter="width",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=["NF_Size", "NF_GravitationOrientation"],
        converter="""
def converter_function(args):
    size = args["NF_Size"].args["size"]
    return {"width": size}
    """)

def init_nf_height():
    global nf_height
    nf_height = create_notion_frame(
        id="NF_Height",
        parameter="height",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=["NF_Size", "NF_GravitationOrientation"],
        converter="""
def converter_function(args):
    size = args["NF_Size"].args["size"]
    return {"height": size}
    """)

def init_nf_thickness():
    global nf_thickness
    nf_thickness = create_notion_frame(
        id="NF_Thickness",
        parameter="thickness",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=["NF_Size"],
        converter="""
def converter_function(args):
    size = args["NF_Size"].args["size"]
    return {"thickness": size}
    """)

def init_nf_cavity():
    global nf_cavity
    nf_cavity = create_notion_frame(
        id="NF_Cavity",
        parameter="cavity",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=["NF_Size"],
        converter="""
def converter_function(args):
    size = args["NF_Size"].args["size"]
    return {"cavity": size}
    """)

def init_nf_glass_layers():
    global nf_glass_layers
    nf_glass_layers = create_notion_frame(
        id="NF_GlassLayers",
        parameter="glass_layers",
        type=NotionType.INTEGER,
        unit=NotionUnit.NONE,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {"glass_layers": args["glass_layers"]}
    """)

def init_nf_uw():
    global nf_uw
    nf_uw = create_notion_frame(
        id="NF_Uw",
        parameter="Uw",
        type=NotionType.FLOAT,
        unit=NotionUnit.U,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"Uw\": args['Uw']}
""")

def init_nf_ug():
    global nf_ug
    nf_ug = create_notion_frame(
        id="NF_Ug",
        parameter="Ug",
        type=NotionType.FLOAT,
        unit=NotionUnit.U,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"Ug\": args['Ug']}
""")
    
def init_nf_uf():
    global nf_uf
    nf_uf = create_notion_frame(
        id="NF_Uf",
        parameter="Uf",
        type=NotionType.FLOAT,
        unit=NotionUnit.U,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"Uf\": args['Uf']}
""")

def init_nf_up():
    global nf_up
    nf_up = create_notion_frame(
        id="NF_Up",
        parameter="Up",
        type=NotionType.FLOAT,
        unit=NotionUnit.U,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"Up\": args['Up']}
""")

def init_nf_uc():
    global nf_uc
    nf_uc = create_notion_frame(
        id="NF_Uc",
        parameter="Uc",
        type=NotionType.FLOAT,
        unit=NotionUnit.U,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"Uc\": args['Uc']}
""")

def init_nf_material():
    global nf_material
    nf_material = create_notion_frame(
        id="NF_Material",
        parameter="material",
        type=NotionType.STRING,
        unit=NotionUnit.NONE,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"material\": args['material']}
""")
    
def init_nf_specific_name():
    global nf_specific_name
    nf_specific_name = create_notion_frame(
        id="NF_SpecificName",
        parameter="specific_name",
        type=NotionType.STRING,
        unit=NotionUnit.NONE,
        derivedFrom=[],
        converter="""
def converter_function(args):
    return {\"specific_name\": args['specific_name']}
""")
    
def init_nf_offset():
    global nf_offset
    nf_offset = create_notion_frame(
        id="NF_Offset",
        parameter="offset",
        type=NotionType.INTEGER,
        unit=NotionUnit.MM,
        derivedFrom=["NF_SpecificName"],
        converter="""
from notions import NotionValue

def converter_function(args):
    print(args)
    for key, value in args.items():
        if isinstance(value, NotionValue):
            specific_name = value.args['specific_name']
            if specific_name == 'REY ECO CP 003':
                return {'offset': 38}
    return None
"""
    )


#######################################
# GraphQL schema
#######################################

type_defs = gql(
    '''
    type Query {
        window(windowId: ID!): Window
    }

    type Mutation {
        createWindow(windowInput: WindowInput!): Window!
        drawWindow(windowId: ID!): Boolean
        generateBuildingModule: TopologicalNetwork!
        generateWindowModule(windowId: ID!): TopologicalNetwork!
        generateGlassModule(windowId: ID!): TopologicalNetwork!
        generateEcoSystemModule(windowId: ID!): TopologicalNetwork
        generateCornerModule(windowId: ID!): TopologicalNetwork
        generateRDF(windowId: ID!, moduleId: String!): String!
    }

    type TopologicalNetwork {
        module: Module!
        slots: [Slot!]!
        connections: [Connection!]!
    }

    type Module {
        label: String!
        ports: [Port!]!
    }

    type Slot {
        network: TopologicalNetwork
        label: String!
        dimension: Int!
        downPorts: [Port!]!
        upPorts: [Port!]!
        insidePorts: [Port!]!
        outsidePorts: [Port!]!
    }

    type Port {
        index: Int!
        portType: PortType!
        feature: String
        owner: Slot!
        otherPort: Port
    }

    type Connection {
        network: TopologicalNetwork
        downPort: Port
        upPort: Port
        insidePort: Port
        outsidePort: Port
    }
    
    input WindowInput {
        windowId: ID!
        width: Int!
        height: Int!
        bayInput: [BayInput!]!
    }

    type Window {
        windowId: ID!
        width: Int!
        height: Int!
        bays: [Bay!]!
    }

    input BayInput {
        width: Int!
        segmentInput: [SegmentInput!]!
    }

    type Bay {
        width: Int!
        window: Window!
        segments: [Segment]!
    }

    input SegmentInput {
        fixed: FixedSegmentInput
        rotatable: RotatableSegmentInput
    }

    input FixedSegmentInput {
        height: Int!
        thickness: Int!
        transparancy: Transparancy!
    }

    input RotatableSegmentInput {
        height: Int!
        thickness: Int!
        transparancy: Transparancy!
        rotationParams: [RotationParamsInput!]!
    }

    type FixedSegment {
        movable: Movable!
        height: Int!
        thickness: Int!
        bay: Bay!
        transparancy: Transparancy!
    }

    type RotatableSegment {
        movable: Movable!
        height: Int!
        thickness: Int!
        bay: Bay!
        transparancy: Transparancy!
        rotationParams: [RotationParams!]!
    }

    input RotationParamsInput {
        axis: RotationAxis!
        side: RotationSide!
    }

    type RotationParams {
        axis: RotationAxis!
        side: RotationSide!
    }

    union Segment = FixedSegment | RotatableSegment

    enum Transparancy {
        OPAQUE
        SEMI_TRANSPARANT
        TRANSPARANT
    }

    enum Movable {
        FIXED
        SHIFTABLE
        ROTATABLE
    }

    enum RotationAxis {
        HORIZONTAL_BOTTOM
        HORIZONTAL_TOP
        VERTICAL_LEFT
        VERTICAL_RIGHT
    }

    enum RotationSide {
        INWARD
        OUTWARD
    }

    enum PortType {
        DOWN
        UP
        INSIDE
        OUTSIDE
        MODULE
    }
    '''
)

query = QueryType()
mutation = MutationType()
window = ObjectType("Window")
window_input = InputType("WindowInput")
bay = ObjectType("Bay")
bay_input = InputType("BayInput")
fixed_segment = ObjectType("FixedSegment")
rotatable_segment = ObjectType("RotatableSegment")
segment_input = InputType("SegmentInput")
rotatable_segment_input = InputType("RotatableSegmentInput")
module = ObjectType("Module")
topological_network = ObjectType("TopologicalNetwork")
slot = ObjectType("Slot")
port = ObjectType("Port")
connection = ObjectType("Connection")
transparency = EnumType(
    "Transparancy",
    {
        "OPAQUE": "O",
        "SEMI_TRANSPARANT": "S",
        "TRANSPARANT": "T",
    }
)
movable = EnumType(
    "Movable",
    {
        "FIXED": "F",
        "SHIFTABLE": "S",
        "ROTATABLE": "R",
    }
)
rotation_axis = EnumType(
    "RotationAxis",
    {
        "HORIZONTAL_BOTTOM": "HB",
        "HORIZONTAK_TOP": "HT",
        "VERTICAL_LEFT": "VL",
        "VERTICAL_RIGHT": "VR",
    }
)
rotation_axis = EnumType(
    "RotationSide",
    {
        "INWARD": "I",
        "OUTWARD": "O"
    }
)
port_type = EnumType(
    "PortType",
    {
        "DOWN": "D",
        "UP": "U",
        "INSIDE": "I",
        "OUTSIDE": "O"
    }
)
rotation_params = ObjectType("RotationParams")
segment = UnionType("Segment")

@segment.type_resolver
def resolve_segment_type(obj, *_):
    if isinstance(obj, FixedSegment):
        return "FixedSegment"
    if isinstance(obj, RotatableSegment):
        return "RotatableSegment"

#######################################
# Queries
#######################################
@query.field("window")
def resolve_query_window(*_, windowId: str):
    return Window.all_windows[windowId]

@topological_network.field("module")
def resolve_topological_network_module(obj, *_) -> Module :
    tn: TopologicalNetwork = obj
    return tn.module

@connection.field("downPort")
def resolve_port_down_port(obj, *_) -> Port:
    c: Connection = obj
    if c.downPort:
        if c.downPort.portType == "DOWN":
            return c.downPort
    return None

@connection.field("upPort")
def resolve_port_up_port(obj, *_) -> Port:
    c: Connection = obj
    if c.upPort:
        if c.upPort.portType == "UP":
            return c.upPort
    return None

@connection.field("insidePort")
def resolve_port_up_port(obj, *_) -> Port:
    c: Connection = obj
    if c.insidePort:
        if c.insidePort.portType == "INSIDE":
            return c.insidePort
    return None

@connection.field("outsidePort")
def resolve_port_up_port(obj, *_) -> Port:
    c: Connection = obj
    if c.outsidePort:
        if c.outsidePort.portType == "OUTSIDE":
            return c.outsidePort
    return None


@port.field("index")
def resolve_port_index(obj, *_) -> int:
    thisPort: Port = obj
    if isinstance(thisPort.owner, Slot):
        thisSlot: Slot = thisPort.owner
        if thisPort.portType == "UP":
            return thisSlot.upPorts.index(thisPort)
        if thisPort.portType == "DOWN":
            return thisSlot.downPorts.index(thisPort)
        if thisPort.portType == "INSIDE":
            return thisSlot.insidePorts.index(thisPort)
        if thisPort.portType == "OUTSIDE":
            return thisSlot.outsidePorts.index(thisPort)
    if isinstance(thisPort.owner, Module):
        thisModule: Module = thisPort.owner
        return thisModule.ports.index(thisPort)
    
@port.field("otherPort")
def resolve_port_other_port(obj, *_) -> Port:
    thisPort: Port = obj
    network: TopologicalNetwork = thisPort.owner.network
    for c in network.connections:
        if c.downPort == thisPort:
            return c.upPort
        elif c.upPort == thisPort:
            return c.downPort
    return None

@port.field("feature")
def resolve_port_feature(obj, *_) -> str:
    thisPort: Port = obj
    return thisPort.feature

#######################################
# Mutations
#######################################

@mutation.field("createWindow")
def resolve_mutation_create_window(*_, windowInput: object):
    print(windowInput)
    return Window(windowInput)

@mutation.field("generateBuildingModule")
def resolve_mutation_generate_building_module(*_) -> TopologicalNetwork:
    def generate_building_module() -> TopologicalNetwork:
        module = Module(
            id="a9a70e79-4a87-473c-82f3-2c7b2d2e1179", 
            label="BUILDING", portCount=0)

        slots: dict[str, Slot] = dict()
        slots["Required_Window"] = Slot(id="283d397d-4bb6-4107-931a-7cc28f650e59",dimension=2, label="2D slot Required Window", insidePortCount=4)
        slots["Required_Window"].has_parameter_type_set = create_perceptive_frame(
            id="5e834139-da06-4b58-be62-3a5b38518136",
            notionFrameIds=["NF_Width", "NF_Height", "NF_Uw", "NF_Material"]
        )
        slots["Required_Window"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "5b7f7e5d-8697-4eb2-bd49-275472f176b4",
            "perceptiveFrameId": slots["Required_Window"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Window"}]
            },{
                "notionFrameId": "NF_Width",
                "args": [],
                "derivedFrom": [{
                    "notionFrameId": "NF_Size",
                    "args": [{"key": "size", "value": "1200"}]
                }, {
                    "notionFrameId": "NF_GravitationOrientation",
                    "args": [{"key": "gravitation_orientation", "value": "PERPENDICULAR"}]
                }]
            },{
                "notionFrameId": "NF_Height",
                "args": [],
                "derivedFrom": [{
                    "notionFrameId": "NF_Size",
                    "args": [{"key": "size", "value": "1800"}]
                }, {
                    "notionFrameId": "NF_GravitationOrientation",
                    "args": [{"key": "gravitation_orientation", "value": "ALIGNED"}]
                }]
            }]
        })

        aggregations: list[Aggregation] = []
        for key, value in slots.items():
            aggregations.append(Aggregation(part=value.id, assembly=module.id))
        
        connections: list[Connection] = []

        return TopologicalNetwork(module=module, slots=[item for item in slots.values()], aggregations=aggregations, connections=connections)
    
    return generate_building_module()

@mutation.field("generateWindowModule")
def resolve_mutation_generate_window_module(*_, windowId: str) -> TopologicalNetwork: 
    def generate_window_module(w: Window) -> TopologicalNetwork:
        module = Module(id="b3f9149f-a726-4977-af2a-1821687be2e5",label="Offered_Window", portCount=4)
        module.has_parameter_type_set = create_perceptive_frame(
            id="4feef65d-7885-4773-bff1-da40c7acab1f",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Height", "NF_Uw", "NF_Material"]
        )
        module.has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "19052a87-d443-44c9-9192-df7228ca471a",
            "perceptiveFrameId": module.has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "REY ECO 32mm System"}]
            }]
        })

        slots: dict[str, Slot] = dict()
        slots["Required_Glazing"] = Slot(id="a6c0133c-d05f-4810-90c1-273a64fedeaa",dimension=2, label="2D slot GLAZING", downPortCount=4)
        slots["Required_Glazing"].has_parameter_type_set = create_perceptive_frame(
            id="72357296-50aa-49bf-8f10-a4ac790ea8dd",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Height", "NF_Ug"]
        )
        slots["Required_Glazing"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "db4f412d-ffce-4632-8ada-e7f28d60607c",
            "perceptiveFrameId": slots["Required_Glazing"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Glazing"}]
            }]
        })
        slots["Required_Top_Jamb"] = Slot(id="0172be31-3d17-4fc2-bb24-3507ab21e5e8",dimension=1, label="1D slot JAMB Top", downPortCount=2, upPortCount=1, outsidePortCount=1)
        slots["Required_Top_Jamb"].has_parameter_type_set = create_perceptive_frame(
            id="22a4133a-c7b4-4c14-b11c-7194fdfb0a96",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Uf"]
        )
        slots["Required_Top_Jamb"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "de13ce57-4b4b-4b0b-80c7-af225fb91656",
            "perceptiveFrameId": slots["Required_Top_Jamb"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Top_Jamb"}]
            }]
        })
        slots["Required_Bottom_Jamb"] = Slot(id="31d07757-a510-4aa0-9341-1b2fbab41cd0",dimension=1, label="1D slot JAMB Bottom", downPortCount=2, upPortCount=1, outsidePortCount=1)
        slots["Required_Bottom_Jamb"].has_parameter_type_set = create_perceptive_frame(
            id="9b74717c-70d5-4d60-ba42-4efafb75ceca",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Uf"]
        )
        slots["Required_Bottom_Jamb"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "b061fd04-5038-4005-b20a-65a36dc9df2a",
            "perceptiveFrameId": slots["Required_Bottom_Jamb"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Bottom_Jamb"}]
            }]
        })       
        slots["Required_Left_Sill"] = Slot(id="7dbc5958-a24a-4f76-b036-6bc1b900d4e2",dimension=1, label="1D slot SILL Left", downPortCount=2, upPortCount=1, outsidePortCount=1)
        slots["Required_Left_Sill"].has_parameter_type_set = create_perceptive_frame(
            id="17a42f2b-21da-46e9-84f4-2b62983a1d21",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Uf"]
        )
        slots["Required_Left_Sill"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "12c96e32-0a4d-40cd-8d7f-6c51b1d82be4",
            "perceptiveFrameId": slots["Required_Left_Sill"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Left_Sill"}]
            }]
        })       
        slots["Required_Right_Sill"] = Slot(id="0b35d00d-b4f5-4ee8-a02e-3c84cde27e39",dimension=1, label="1D slot SILL Right", downPortCount=2, upPortCount=1, outsidePortCount=1)
        slots["Required_Right_Sill"].has_parameter_type_set = create_perceptive_frame(
            id="dec0cff4-de1e-458d-8d2c-00c8dbec009a",
            notionFrameIds=["NF_SpecificName", "NF_Length", "NF_Uf"]
        ) 
        slots["Required_Right_Sill"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "34f1691a-3193-44cb-8bf7-b3c5ef5e6758",
            "perceptiveFrameId": slots["Required_Right_Sill"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Right_Sill"}]
            }]
        })         
        slots["Required_Top_Left_Joint"] = Slot(id="26c96058-0593-478d-9535-fed1f4fe877d",dimension=0, label="0D slot JOINT TL", upPortCount=2)
        slots["Required_Top_Left_Joint"].has_parameter_type_set = create_perceptive_frame(
            id="90ed72f3-fa98-4063-869a-f3da93a9456d",
            notionFrameIds=["NF_SpecificName"]
        )
        slots["Required_Top_Left_Joint"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "d9399ac1-f5ba-4b6b-9796-955b825bbc27",
            "perceptiveFrameId": slots["Required_Top_Left_Joint"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Top_Left_Joint"}]
            }]
        }) 
        slots["Required_Bottom_Left_Joint"] = Slot(id="4d2ed7ee-e6ff-4a04-b654-c0474080035d",dimension=0, label="0D slot JOINT BL", upPortCount=2)
        slots["Required_Bottom_Left_Joint"].has_parameter_type_set = create_perceptive_frame(
            id="a7bcfa2c-ff30-453d-8c34-371b7104ff44",
            notionFrameIds=["NF_SpecificName"]
        ) 
        slots["Required_Bottom_Left_Joint"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "8dd4721f-b4a0-401f-b560-d0d5b56c171d",
            "perceptiveFrameId": slots["Required_Bottom_Left_Joint"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Bottom_Left_Joint"}]
            }]
        }) 
        slots["Required_Top_Right_Joint"] = Slot(id="d759f0fb-0405-40ff-8bbf-393edfe60641",dimension=0, label="0D slot JOINT TR", upPortCount=2)
        slots["Required_Top_Right_Joint"].has_parameter_type_set = create_perceptive_frame(
            id="c68ba561-c546-4444-90d8-8672b06a88bc",
            notionFrameIds=["NF_SpecificName"]
        )
        slots["Required_Top_Right_Joint"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "5a275002-de28-4755-8e48-b44dcc5501d4",
            "perceptiveFrameId": slots["Required_Top_Right_Joint"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Top_Right_Joint"}]
            }]
        }) 
        slots["Required_Bottom_Right_Joint"] = Slot(id="55774a83-0acb-47bf-83cc-9bb7bac58b3c",dimension=0, label="0D slot JOINT BR", upPortCount=2)
        slots["Required_Bottom_Right_Joint"].has_parameter_type_set = create_perceptive_frame(
            id="b24f2d3a-136d-407b-87e3-1142da702495",
            notionFrameIds=["NF_SpecificName"]
        )
        slots["Required_Bottom_Right_Joint"].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "23d3c4bc-ea58-4f92-9885-d67e3daee8d8",
            "perceptiveFrameId": slots["Required_Bottom_Right_Joint"].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Required_Bottom_Right_Joint"}]
            }]
        }) 

        aggregations: list[Aggregation] = []
        for key, value in slots.items():
            aggregations.append(Aggregation(part=value.id, assembly=module.id))

        aggregations.append(Aggregation(part=slots["Required_Top_Jamb"].outsidePorts[0].id, 
                                        assembly=module.ports[0].id))
        aggregations.append(Aggregation(part=slots["Required_Right_Sill"].outsidePorts[0].id, 
                                        assembly=module.ports[1].id))
        aggregations.append(Aggregation(part=slots["Required_Bottom_Jamb"].outsidePorts[0].id, 
                                        assembly=module.ports[2].id))
        aggregations.append(Aggregation(part=slots["Required_Left_Sill"].outsidePorts[0].id, 
                                        assembly=module.ports[3].id))

        connections: list[Connection] = []
        connections.append(Connection(downPort=slots["Required_Glazing"].downPorts[0],upPort=slots["Required_Top_Jamb"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(downPort=slots["Required_Glazing"].downPorts[1],upPort=slots["Required_Bottom_Jamb"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(downPort=slots["Required_Glazing"].downPorts[2],upPort=slots["Required_Left_Sill"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(downPort=slots["Required_Glazing"].downPorts[3],upPort=slots["Required_Right_Sill"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(downPort=slots["Required_Top_Jamb"].downPorts[0],upPort=slots["Required_Top_Left_Joint"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Top_Jamb"].downPorts[1],upPort=slots["Required_Top_Right_Joint"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Bottom_Jamb"].downPorts[0],upPort=slots["Required_Bottom_Left_Joint"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Bottom_Jamb"].downPorts[1],upPort=slots["Required_Bottom_Right_Joint"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Left_Sill"].downPorts[0],upPort=slots["Required_Top_Left_Joint"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Left_Sill"].downPorts[1],upPort=slots["Required_Bottom_Left_Joint"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Right_Sill"].downPorts[0],upPort=slots["Required_Top_Right_Joint"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(downPort=slots["Required_Right_Sill"].downPorts[1],upPort=slots["Required_Bottom_Right_Joint"].upPorts[1],upFeature="cut 45°"))
        return TopologicalNetwork(module=module, slots=[item for item in slots.values()], aggregations=aggregations, connections=connections)

    w = Window.all_windows[windowId]
    return generate_window_module(w)


@mutation.field("generateGlassModule")
def resolve_mutation_generate_glass_module(*_, windowId: str) -> TopologicalNetwork:
    def generate_glass_module(w: Window) -> TopologicalNetwork:
        module = Module(id="74245516-1b5a-4674-862f-6d087305c462", label="Offered Glazing", portCount=4)
        module.has_parameter_type_set = create_perceptive_frame(
            id="85392696-8613-4dfb-99d1-d588abefbebb",
            notionFrameIds=["NF_SpecificName", "NF_Width", "NF_Height", "NF_Thickness", "NF_GlassLayers", "NF_Cavity", "NF_Ug"]
        )
        module.has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "19052a87-d443-44c9-9192-df7228ca471a",
            "perceptiveFrameId": module.has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "Scheuten Iso S+"}]
            }]
        })
        slots: dict[str, Slot] = dict()
        slots["Required_Cavity"] = Slot(id="bf05261e-042b-4f55-9e0b-b24b176b4fd3", dimension=2, label="2D slot CAVITY", insidePortCount=2)
        slots["Required_Cavity"].has_parameter_type_set = create_perceptive_frame(
            id="3984414f-30ad-49d3-a178-aa905840734b",
            notionFrameIds=["NF_SpecificName", "NF_Thickness", "NF_Uc"]
        )
        slots["Required_Glass_Plate_Outside"] = Slot(id="1adc305d-8b11-4e91-a01d-79856f756eae", dimension=2, label="2D slot GLASS PLATE OUTSIDE", downPortCount=4, outsidePortCount=1)
        slots["Required_Glass_Plate_Outside"].has_parameter_type_set = create_perceptive_frame(
            id="0f3c40eb-3ec6-4cb7-ac18-cfacde301373",
            notionFrameIds=["NF_SpecificName", "NF_Width", "NF_Height", "NF_Up"]
        )
        slots["Required_Glass_Plate_Inside"] = Slot(id="08420446-f092-4c67-8b9b-64c99963e16f", dimension=2, label="2D slot GLASS PLATE INSIDE", downPortCount=4, outsidePortCount=1)
        slots["Required_Glass_Plate_Inside"].has_parameter_type_set = create_perceptive_frame(
            id="879ce1a4-c9c1-4825-8b99-a92e2be67404",
            notionFrameIds=["NF_SpecificName", "NF_Width", "NF_Height", "NF_Up"]
        )
        
        aggregations: list[Aggregation] = []
        for key, value in slots.items():
            aggregations.append(Aggregation(part=value.id, assembly=module.id))

        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Outside"].downPorts[0].id, 
                                        assembly=module.ports[0].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Outside"].downPorts[1].id, 
                                        assembly=module.ports[1].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Outside"].downPorts[2].id, 
                                        assembly=module.ports[2].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Outside"].downPorts[3].id, 
                                        assembly=module.ports[3].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Inside"].downPorts[0].id, 
                                        assembly=module.ports[0].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Inside"].downPorts[1].id, 
                                        assembly=module.ports[1].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Inside"].downPorts[2].id, 
                                        assembly=module.ports[2].id))
        aggregations.append(Aggregation(part=slots["Required_Glass_Plate_Inside"].downPorts[3].id, 
                                        assembly=module.ports[3].id))
        
        connections: list[Connection] = []
        connections.append(Connection(outsidePort=slots["Required_Glass_Plate_Outside"].outsidePorts[0],insidePort=slots["Required_Cavity"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["Required_Glass_Plate_Inside"].outsidePorts[0],insidePort=slots["Required_Cavity"].insidePorts[1]))

        return TopologicalNetwork(module=module, slots=[item for item in slots.values()], aggregations=aggregations, connections=connections)


    w = Window.all_windows[windowId]
    return generate_glass_module(w)


@mutation.field("generateEcoSystemModule")
def resolve_mutation_generate_eco_system_module(*_, windowId: str) -> TopologicalNetwork:
    def generate_eco_system_module(w: Window) -> TopologicalNetwork:
        module = Module(id="8f2d4095-a42a-422d-8019-57000362a2d5", label="Offered Profile", portCount=4)
        module.has_parameter_type_set = create_perceptive_frame(
            id="16277c66-26c0-4dd9-9469-b6288801ce3b",
            notionFrameIds=["NF_SpecificName", "NF_Size", "NF_Uf"]
        )
        module.has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "854cb4a3-0a55-4193-9af0-999410f9135f",
            "perceptiveFrameId": module.has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_SpecificName",
                "args": [{"key": "specific_name", "value": "REY ECO CP 003"}]
            }]
        })
        module.ports[3].has_parameter_type_set = create_perceptive_frame(
            id="c64b6a2f-17f3-44c4-9472-46c0751be23e",
            notionFrameIds=["NF_Offset"]
        )
        print([nv.id for nv in module.has_parameter_value_set.notion_values if nv.frame.id == "NF_SpecificName"])
        module.ports[3].has_parameter_value_set = create_perceptive_frame_instance(perceptiveFrameInstanceInput={
            "id": "77eea101-705d-4a62-977d-e0bdca2e97ec",
            "perceptiveFrameId": module.ports[3].has_parameter_type_set.id,
            "notionValueInputs": [{
                "notionFrameId": "NF_Offset",
                "args": [],
                "derivedFromRef": [nv.id for nv in module.has_parameter_value_set.notion_values if nv.frame.id == "NF_SpecificName"]
            }]
        }
        )

        slots: dict[str, Slot] = dict()
        slots["GLASS HLD OUT"] = Slot(id="58aadd99-e749-48ae-b0b0-8dbfc6e6dd65", dimension=1, label="1D slot GLASS HLD OUT", upPortCount=1, insidePortCount=1)
        slots["GLASS HLD IN"] = Slot(id="9d2b5eaa-83c4-47ee-9c28-6006ec89ab0a", dimension=1, label="1D slot GLASS HLD IN", upPortCount=1, insidePortCount=1)
        slots["OUTER AL PROF"] = Slot(id="db2ec451-54ea-4470-a2b6-a3a0022f5066", dimension=1, label="1D slot OUTER AL PROF", outsidePortCount=3)
        slots["INNER AL PROF"] = Slot(id="d7daa9f8-c498-40b2-85ac-1acecbdbae58", dimension=1, label="1D slot INNER AL PROF", insidePortCount=1, outsidePortCount=3)
        slots["GLAZING BEAD"] = Slot(id="b8822679-5c91-4e82-81f4-6b706fbfbde0", dimension=1, label="1D slot GLAZING BEAD", insidePortCount=1, outsidePortCount=1)
        slots["ISOLATOR"] = Slot(id="4aafbfeb-1184-429c-b76d-bc39e7b46928", dimension=1, label="1D slot ISOLATOR", insidePortCount=2)
        slots["SPACER"] = Slot(id="3fe50ec7-8ddd-48cd-b4e7-c2ee55a09562", dimension=1, label="1D slot SPACER", insidePortCount=2)
        
        aggregations: list[Aggregation] = []
        for key, value in slots.items():
            aggregations.append(Aggregation(part=value.id, assembly=module.id))

        aggregations.append(Aggregation(part=slots["GLASS HLD OUT"].upPorts[0].id, 
                                        assembly=module.ports[0].id))
        aggregations.append(Aggregation(part=slots["GLASS HLD IN"].upPorts[0].id, 
                                        assembly=module.ports[1].id))
        aggregations.append(Aggregation(part=slots["INNER AL PROF"].insidePorts[0].id, 
                                        assembly=module.ports[2].id))
        
        connections: list[Connection] = []
        connections.append(Connection(outsidePort=slots["OUTER AL PROF"].outsidePorts[0],insidePort=slots["GLASS HLD OUT"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["INNER AL PROF"].outsidePorts[0],insidePort=slots["GLAZING BEAD"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["GLAZING BEAD"].outsidePorts[0],insidePort=slots["GLASS HLD IN"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["INNER AL PROF"].outsidePorts[1],insidePort=slots["SPACER"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["INNER AL PROF"].outsidePorts[2],insidePort=slots["ISOLATOR"].insidePorts[0]))
        connections.append(Connection(outsidePort=slots["OUTER AL PROF"].outsidePorts[1],insidePort=slots["SPACER"].insidePorts[1]))
        connections.append(Connection(outsidePort=slots["OUTER AL PROF"].outsidePorts[2],insidePort=slots["ISOLATOR"].insidePorts[1]))
     

        return TopologicalNetwork(module=module, slots=[item for item in slots.values()], aggregations=aggregations, connections=connections)


    w = Window.all_windows[windowId]
    return generate_eco_system_module(w)

@mutation.field("generateCornerModule")
def resolve_mutation_generate_corner_module(*_, windowId: str) -> TopologicalNetwork:
    def generate_corner_module(w: Window) -> TopologicalNetwork:
        module = Module(id="dcc67a6f-4352-44b5-b098-2009fbf331f3", label="Offered Joint", portCount=2)
        module.has_parameter_type_set = create_perceptive_frame(
            id="04ac5089-6471-46f5-9fbc-17b1b82a926a",
            notionFrameIds=["NF_SpecificName"]
        )
        return TopologicalNetwork(module=module, slots=[], aggregations=[], connections=[])

    w = Window.all_windows[windowId]
    return generate_corner_module(w)

@mutation.field("generateRDF")
def resolve_mutation_generate_RDF(*_, windowId: str, moduleId: str) -> str:
    def generateRDF(w: Window) -> str:
        def build_parameter_type_set(node: Node):
            if node.has_parameter_type_set:
                pf = URIRef(DATA + "#" + node.has_parameter_type_set.id)
                g.add((URIRef(DATA + "#" + node.id), URIRef(TN + "has_parameter_type_set"), pf))
                g.add((pf, RDF.type, URIRef(NT + "PerceptiveFrame")))
                g.add((pf, RDFS.label, Literal(f"{node.has_parameter_type_set.id}", datatype=XSD.string)))
                for frm in node.has_parameter_type_set.notion_frames:
                    g.add((pf, URIRef(NT + "frame"), URIRef(NT + frm)))

        def build_parameter_value_set(node: Node):
            def build_args(nv: URIRef, nvi: NotionValue):
                n = BNode()
                noargs = True
                for key, value in nvi.args.items():
                    if type(value)==str:
                        noargs = False
                        v.add((n, URIRef(NT + "key"), Literal(key, datatype=XSD.string)))
                        v.add((n, URIRef(NT + "value"), Literal(value, datatype=XSD.string)))
                        v.add((nv, RDFS.label, Literal(value, datatype=XSD.string)))
                if not noargs:
                    v.add((n, RDF.type, URIRef(NT + "Arg")))
                    v.add((nv, URIRef(NT + "args"), n))
                v.add((nv, URIRef(NT + "frame"),  URIRef(NT + nvi.frame.id)))

            if node.has_parameter_value_set:
                pfi = URIRef(VALUES + "#" + node.has_parameter_value_set.id)
                v.add((URIRef(DATA + "#" + node.id), URIRef(TN + "has_parameter_value_set"), pfi))
                v.add((pfi, RDF.type, URIRef(NT + "PerceptiveFrameInstance")))
                v.add((pfi, URIRef(NT + "perceptive_frame"), URIRef(DATA + "#" + node.has_parameter_value_set.perceptive_frame.id) ))
                for nvi in node.has_parameter_value_set.notion_values:
                    nv = URIRef(VALUES + "#" + f"{uuid.uuid4()}" )
                    v.add((nv, RDF.type, URIRef(NT + "NotionValue")))
                    v.add((nv, URIRef(NT + "frame"), URIRef(NT + nvi.frame.id)))
                    v.add((pfi, URIRef(NT + "notion_value"), nv))
                    build_args(nv, nvi)
                    # n = BNode()
                    # v.add((n, RDF.type, URIRef(NT + "Arg")))
                    # for key, value in nvi.args.items():
                    #     if type(value)==str:
                    #         v.add((n, URIRef(NT + "key"), Literal(key, datatype=XSD.string)))
                    #         v.add((n, URIRef(NT + "value"), Literal(value, datatype=XSD.string)))
                    #         v.add((nv, RDFS.label, Literal(value, datatype=XSD.string)))
                    # v.add((nv, URIRef(NT + "args"), n))
                    # v.add((nv, URIRef(NT + "frame"),  URIRef(NT + nvi.frame.id)))
                    # v.add((pfi, URIRef(NT + "notion_value"), nv))
                    dnvs = nvi.get_derived_notion_values()
                    for dnv in dnvs:
                        dn = BNode()
                        v.add((dn, RDF.type, URIRef(NT + "NotionValue")))
                        v.add((dn, URIRef(NT + "frame"), URIRef(NT + dnv.frame.id)))
                        v.add((nv, URIRef(NT + "derived_from_nv"), dn))
                        build_args(dn, dnv)

        tn = Graph()
#        g.parse("C:\\Users\\peter\\Documents\\Development\\Notions\\topology_network.ttl")
#        tn.parse("http://infrabim.nl/kip/topology_network")
        tn.parse("C:/Users/peter/Documents/Development/Notions/Window_demo/topology_network.ttl")
        tn.parse("C:/Users/peter/TBCFreeWorkspace/Notions/nt.ttl")
        g = Graph(bind_namespaces="rdflib")
        v = Graph(bind_namespaces="rdflib")
        TN=Namespace("http://infrabim.nl/kip/topology_network#")
        g.bind("tn", TN)
        v.bind("tn", TN)
        NT=Namespace("http://infrabim.nl/kip/notions/nt#")
        g.bind("nt", NT)
        v.bind("nt", NT)
        DATA=Namespace(f"http://infrabim.nl/kip/demo/{moduleId}")
        g.bind(moduleId, DATA) 
        g.bind("", DATA+"#")
        VALUES=Namespace(f"http://infrabim.nl/kip/demo/{moduleId}_values")
        v.bind("values", VALUES)
        v.bind("", VALUES+"#")

        if moduleId == "building":
            nw:TopologicalNetwork = resolve_mutation_generate_building_module()        
        elif moduleId == "window":
            nw:TopologicalNetwork = resolve_mutation_generate_window_module(windowId=windowId)
        elif moduleId == "glass":
            nw:TopologicalNetwork = resolve_mutation_generate_glass_module(windowId=windowId)
        elif moduleId == "eco_system":
            nw:TopologicalNetwork = resolve_mutation_generate_eco_system_module(windowId=windowId)
        elif moduleId == "corner":
            nw:TopologicalNetwork = resolve_mutation_generate_corner_module(windowId=windowId)

        module = URIRef(DATA + "#" + f"{nw.module.id}")
        g.add((module, RDF.type, URIRef(TN + "Module")))
        g.add((module, RDFS.label, Literal(f"{nw.module.label}", datatype=XSD.string)))
        build_parameter_type_set(nw.module)
        build_parameter_value_set(nw.module)

        port_index = 0
        for p in nw.module.ports:
            port = URIRef(DATA + "#" + f"{p.id}")
            g.add((port, RDF.type, URIRef(TN + "ModulePort")))
            g.add((port, RDFS.label, Literal(p.label, datatype=XSD.string)))

            g.add((module, URIRef(TN + "has_port"), port))
            port_index += 1

            build_parameter_type_set(p)
            build_parameter_value_set(p)


        for s in nw.slots:
            slot = URIRef(DATA + "#" + f"{s.id}")
            g.add((slot, RDF.type, URIRef(TN + "Slot")))
            g.add((slot, RDFS.label, Literal(f"{s.label}", datatype=XSD.string)))
            g.add((slot, URIRef(TN + "dimension"), Literal(f"{s.dimension}", datatype=XSD.int)))
            build_parameter_type_set(s)
            build_parameter_value_set(s)


            for p in s.downPorts:
                port = URIRef(DATA + "#" + f"{p.id}")
                g.add((port, RDF.type, URIRef(TN + "DownPort")))
                g.add((port, RDFS.label, Literal(p.label, datatype=XSD.string)))

                g.add((slot, URIRef(TN + "has_down_port"), port))
                port_index += 1

            port_index = 0
            for p in s.upPorts:
                port = URIRef(DATA + "#" + f"{p.id}")
                g.add((port, RDF.type, URIRef(TN + "UpPort")))
                g.add((port, RDFS.label, Literal(p.label, datatype=XSD.string)))

                g.add((slot, URIRef(TN + "has_up_port"), port))
                port_index += 1
            
            port_index = 0
            for p in s.insidePorts:
                port = URIRef(DATA + "#" + f"{p.id}")
                g.add((port, RDF.type, URIRef(TN + "InsidePort")))
                g.add((port, RDFS.label, Literal(p.label, datatype=XSD.string)))

                g.add((slot, URIRef(TN + "has_inside_port"), port))
                port_index += 1

            port_index = 0
            for p in s.outsidePorts:
                port = URIRef(DATA + "#" + f"{p.id}")
                g.add((port, RDF.type, URIRef(TN + "OutsidePort")))
                g.add((port, RDFS.label, Literal(p.label, datatype=XSD.string)))

                g.add((slot, URIRef(TN + "has_outside_port"), port))
                port_index += 1
        
        for l in nw.aggregations:
            link = URIRef(DATA + "#" + f"{uuid.uuid4()}")
            g.add((link, RDF.type, URIRef(TN + "Aggregation")))
            g.add((link, URIRef(TN + "part"), URIRef(DATA + "#" + l.part)))
            g.add((link, URIRef(TN + "assembly"), URIRef(DATA + "#" +l.assembly)))

        for l in nw.connections:
            link = URIRef(DATA + "#" + f"{uuid.uuid4()}")
            g.add((link, RDF.type, URIRef(TN + "Connection")))
            if l.downPort:
                g.add((link, URIRef(TN + "down"), URIRef(DATA + "#" + l.downPort.id)))
            if l.upPort:
                g.add((link, URIRef(TN + "up"), URIRef(DATA + "#" +l.upPort.id)))
            if l.insidePort:
                g.add((link, URIRef(TN + "inside"), URIRef(DATA + "#" +l.insidePort.id)))
            if l.outsidePort:
                g.add((link, URIRef(TN + "outside"), URIRef(DATA + "#" +l.outsidePort.id)))

        v.serialize(format='turtle', 
                    destination=f"C:/Users/peter/Documents/Development/Notions/Window_demo/{moduleId}_values.ttl")
        g.serialize(format='turtle',
                    destination=f"C:/Users/peter/Documents/Development/Notions/Window_demo/{moduleId}.ttl")
        return g.serialize(format='turtle')

    w = Window.all_windows[windowId]
    return generateRDF(w) 

@mutation.field("drawWindow")
def resolve_mutation_draw_window(*_, windowId: str):
    def draw_rotations(xstart, ystart, bwidth, s):
        if s.movable == Movable.ROTATABLE.name:
            for r in s.rotationParams:
                match r["axis"]:
                    case "HORIZONTAL_TOP":
                        xpoints = np.array([xstart,          xstart+bwidth/2, xstart+bwidth ])
                        ypoints = np.array([ystart+s.height, ystart,          ystart+s.height])
                        plt.plot(xpoints, ypoints, linestyle = 'dotted')
                    case "HORIZONTAL_BOTTOM":
                        xpoints = np.array([xstart, xstart+bwidth/2, xstart+bwidth ])
                        ypoints = np.array([ystart, ystart+s.height, ystart])
                        plt.plot(xpoints, ypoints, linestyle = 'dotted')
                    case "VERTICAL_LEFT":
                        xpoints = np.array([xstart, xstart+bwidth, xstart])
                        ypoints = np.array([ystart, ystart+s.height/2, ystart+s.height])
                        plt.plot(xpoints, ypoints, linestyle = 'dotted') 
                    case "VERTICAL_RIGHT":
                        xpoints = np.array([xstart+bwidth, xstart, xstart+bwidth])
                        ypoints = np.array([ystart, ystart+s.height/2, ystart+s.height])
                        plt.plot(xpoints, ypoints, linestyle = 'dotted')                     

    w = Window.all_windows[windowId]

    # Draw window
    xpoints = np.array([0, 0,        w.width,  w.width, 0])
    ypoints = np.array([0, w.height, w.height, 0,       0])
    plt.plot(xpoints, ypoints)

    xstart = 0
    for b in w.bays:
        ystart = 0
        for s in b.segments:
            xpoints = np.array([xstart, xstart,   xstart+ b.width,  xstart + b.width, xstart])
            ypoints = np.array([ystart, w.height, w.height,         ystart,           ystart])
            plt.plot(xpoints, ypoints)
            draw_rotations(xstart, ystart, b.width, s)
            ystart += s.height
        xstart += b.width
       
    plt.show()
    return True

schema = make_executable_schema(
    type_defs, query, mutation, window, segment, rotatable_segment, rotatable_segment_input, rotation_params, module, topological_network, connection, port
)

app = GraphQL(schema, debug=True)

def main():
    init_size()
    init_gravitation_orientation()
    init_nf_width()
    init_nf_height()
    init_nf_thickness()
    init_nf_glass_layers()
    init_nf_cavity()
    init_nf_uw()
    init_nf_ug()
    init_nf_uf()
    init_nf_up()
    init_nf_uc()
    init_nf_material()
    init_nf_specific_name()
    init_nf_offset()
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()