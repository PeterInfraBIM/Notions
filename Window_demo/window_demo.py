from ariadne import gql, QueryType, MutationType, ObjectType, InputType, EnumType, UnionType, make_executable_schema
from ariadne.asgi import GraphQL
import uvicorn
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt

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
class TopologicalNetwork:
    def __init__(self, slots: list[object] = [], connections: list[object] = [])-> None:
        self.slots: list[Slot] = slots
        for slot in self.slots:
            slot.network = self
        self.connections: list[Connection] = connections
        for connection in self.connections:
            connection.network = self

class Slot:
    def __init__(self, label: str, dimension: int, downPortCount: int = 0, upPortCount: int = 0) -> None:
        self.network = None
        self.label: str = label
        self.dimension: int = dimension
        self.downPorts: list[Port] = []
        for i in range(downPortCount):
            self.downPorts.append(Port(portType = PortType.DOWN.name, slot = self))
        self.upPorts: list[Port] = []
        for i in range(upPortCount):
            self.upPorts.append(Port(portType = PortType.UP.name, slot = self))

class PortType(Enum):
    DOWN = "DOWN"
    UP = "UP"

class Port:
    def __init__(self, portType: PortType, slot: Slot = None, feature: str = None) -> None:
        self.portType: PortType = portType
        self.slot: Slot = slot
        self.feature = feature
    
class Connection:
    def __init__(self, downPort: Port, upPort: Port, downFeature: str = None, upFeature: str = None) -> None:
        self.network = None
        self.downPort: Port = downPort
        self.upPort: Port = upPort
        self.downPort.feature = downFeature
        self.upPort.feature = upFeature

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
        generateTopologicalNetwork(windowId: ID!): TopologicalNetwork!
    }

    type TopologicalNetwork {
        slots: [Slot!]!
        connections: [Connection!]!
    }

    type Slot {
        network: TopologicalNetwork
        label: String!
        dimension: Int!
        downPorts: [Port!]!
        upPorts: [Port!]!
    }

    type Port {
        index: Int!
        portType: PortType!
        feature: String
        slot: Slot!
        otherPort: Port
    }

    type Connection {
        network: TopologicalNetwork
        downPort: Port!
        upPort: Port!
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
port = ObjectType("Port")
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
        "UP": "U"
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

@port.field("index")
def resolve_port_index(obj, *_) -> int:
    thisPort: Port = obj
    thisSlot: Slot = thisPort.slot
    if thisPort.portType == "UP":
        return thisSlot.upPorts.index(thisPort)
    if thisPort.portType == "DOWN":
        return thisSlot.downPorts.index(thisPort)

@port.field("otherPort")
def resolve_port_other_port(obj, *_) -> Port:
    thisPort: Port = obj
    network: TopologicalNetwork = thisPort.slot.network
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

@mutation.field("generateTopologicalNetwork")
def resolve_mutation_generate_topological_network(*_, windowId: str): 
    def generateTopologicalNetwork(w: Window) -> TopologicalNetwork:
        slots: dict[str, Slot] = dict()
        slots["Glas"] = Slot(dimension=2, label="Glas", downPortCount=4)
        slots["Bovendorpel"] = Slot(dimension=2, label="Bovendorpel", downPortCount=2, upPortCount=1)
        slots["Onderdorpel"] = Slot(dimension=2, label="Onderdorpel", downPortCount=2, upPortCount=1)
        slots["Zijstijl links"] = Slot(dimension=2, label="Zijstijl links", downPortCount=2, upPortCount=1)
        slots["Zijstijl rechts"] = Slot(dimension=2, label="Zijstijl rechts", downPortCount=2, upPortCount=1)
        slots["Verbinding links-boven"] = Slot(dimension=2, label="Verbinding links-boven", upPortCount=2)
        slots["Verbinding links-onder"] = Slot(dimension=2, label="Verbinding links-onder", upPortCount=2)
        slots["Verbinding rechts-boven"] = Slot(dimension=2, label="Verbinding rechts-boven", upPortCount=2)
        slots["Verbinding rechts-onder"] = Slot(dimension=2, label="Verbinding rechts-onder", upPortCount=2)

        connections: list[Connection] = []
        connections.append(Connection(slots["Glas"].downPorts[0],slots["Bovendorpel"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(slots["Glas"].downPorts[1],slots["Onderdorpel"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(slots["Glas"].downPorts[2],slots["Zijstijl links"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(slots["Glas"].downPorts[3],slots["Zijstijl rechts"].upPorts[0],upFeature="shrink 37 mm"))
        connections.append(Connection(slots["Bovendorpel"].downPorts[0],slots["Verbinding links-boven"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(slots["Bovendorpel"].downPorts[1],slots["Verbinding rechts-boven"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(slots["Onderdorpel"].downPorts[0],slots["Verbinding links-onder"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(slots["Onderdorpel"].downPorts[1],slots["Verbinding rechts-onder"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(slots["Zijstijl links"].downPorts[0],slots["Verbinding links-boven"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(slots["Zijstijl links"].downPorts[1],slots["Verbinding links-onder"].upPorts[0],upFeature="cut 45°"))
        connections.append(Connection(slots["Zijstijl rechts"].downPorts[0],slots["Verbinding rechts-boven"].upPorts[1],upFeature="cut 45°"))
        connections.append(Connection(slots["Zijstijl rechts"].downPorts[1],slots["Verbinding rechts-onder"].upPorts[1],upFeature="cut 45°"))
        return TopologicalNetwork([item for item in slots.values()], connections)

    w = Window.all_windows[windowId]
    return generateTopologicalNetwork(w)

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
    type_defs, query, mutation, window, segment, rotatable_segment, rotatable_segment_input, rotation_params, port
)

app = GraphQL(schema, debug=True)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()