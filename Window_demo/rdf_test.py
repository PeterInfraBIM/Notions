import uvicorn
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD, Namespace
from ariadne import gql, make_executable_schema, QueryType, ObjectType, EnumType, InterfaceType
from ariadne.asgi import GraphQL
from enum import Enum

class Node:
    def __init__(self, id:str, label:str):
        self.id: str = id
        self.label: str = label

class Module(Node):
    def __init__(self, id:str, label:str, port_ids:list[str], slot_ids:list[str]):
        super().__init__(id=id, label=label)
        self.port_ids: list[str] = port_ids
        self.slot_ids: list[str] = slot_ids

class Slot(Node):
    def __init__(self, id:str, label:str, dimension:int, port_ids:list[str]):
        super().__init__(id=id, label=label)
        self.dimension: int = dimension
        self.port_ids: list[str] = port_ids

class PortType(Enum):
    DOWN = 0
    UP = 1
    INSIDE = 2
    OUTSIDE = 3
    MODULE = 4

class Port(Node):
    def __init__(self, id:str, label:str, type: PortType):
        super().__init__(id=id, label=label)
        self.type: PortType = type

type_defs = gql(
    '''
    type Query {
        "Get all modules"
        allModules: [Module!]!
        "Get a module by ID"
        moduleById(id: ID!): Module
        "Get a slot by ID"
        slotById(id: ID!): Slot
    }

    type Module {
        "Global identifier"
        id: ID!
        "Readable identifier"
        label: String!
        "Number of available public ports"
        portCount: Int!
        "Public port identifiers"
        portIds: [ID!]!
        "Public port objects"
        ports: [ModulePort!]!
        "Number of local slots"
        slotCount: Int!
        "Local slot identifiers"
        slotIds: [ID!]!
        "Local slots"
        slots: [Slot!]!
        "Selecting slot identifier"
        selectingSlotId: ID
        "Selecting slot object"
        selectingSlot: Slot
    }

    type Slot {
        "Global identifier"
        id: ID!
        "Readable identifier"
        label: String!
        "Dimension: 0D, 1D, 2D or 3D"
        dimension: Int!
        "Number of available ports"
        portCount: Int!
        "Port identifiers"
        portIds: [ID!]!
        "Port objects"
        ports: [SlotPort!]!
        "Selected implementation module identifier"
        selectedModuleId: ID
        "Selected implementation module"
        selectedModule: Module
        "Enclosing module identifier"
        enclosedByModuleId: ID
        "Enclosing module object"
        enclosedByModule: Module
    }

    interface Port {
        "Global identifier"
        id: ID!
        "Readable identifier"
        label: String!
        "Port type: Module, Up, Down, Inside, Outside"
        type: PortType!
    }

    type SlotPort implements Port {
        "Global identifier"
        id: ID!
        "Readable identifier"
        label: String!
        "Port type: Module, Up, Down, Inside, Outside"
        type: PortType!
        "Connected port identifier"
        connectedToPortId: ID
        "Connected port object"
        connectedToPort: SlotPort
        "Selected module port identifier"
        selectedModulePortId: ID
        "Selected module port object"
        selectedModulePort: ModulePort
    }

    type ModulePort implements Port {
        "Global identifier"
        id: ID!
        "Readable identifier"
        label: String!
        "Port type: Module, Up, Down, Inside, Outside"
        type: PortType!
        "Subport identifiers"
        subPortIds: [ID!]!
        "Subport objects"
        subPorts: [SlotPort!]!
    }

    enum PortType {
        DOWN
        UP
        INSIDE
        OUTSIDE
        MODULE
    }

    ''')

query = QueryType()
module = ObjectType("Module")
slot = ObjectType("Slot")
port = InterfaceType("Port")
module_port = ObjectType("ModulePort")
slot_port = ObjectType("SlotPort")
port_type = EnumType(
    "PortType",
    {
        "DOWN": 0,
        "UP": 1,
        "INSIDE": 2,
        "OUTSIDE": 3,
        "MODULE": 4
    }
)

def get_all_modules() -> list[Module]:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?sub ?tag
        WHERE {
            ?sub rdf:type tn:Module ;
                rdfs:label ?tag ;
                .
        }
    """

    all_modules:list[Module] = []

    for r in g.query(q):
        module_id = r["sub"]
        module = get_module_by_id(module_id)
        all_modules.append(module)
        set_module_port_ids(module)
        set_module_slot_ids(module)

    return all_modules


def get_module_by_id(id:str) -> Module:
    q1 = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?tag
        WHERE {
            """ f'<{id}>' """ rdf:type tn:Module ;
                rdfs:label ?tag ;
                .
        }
    """
    module: Module = None
    for r in g.query(q1):
        port_ids = []
        slot_ids = []
        module = Module(id=id, label=r["tag"], port_ids=port_ids, slot_ids=slot_ids)

    return module


def set_module_port_ids(module: Module) -> None:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?port
        WHERE { """ f'<{module.id}>' """ rdf:type tn:Module ;
                tn:has_port ?port ;
                .
        }
    """
    port_ids = []
    for r in g.query(q):
        port_ids.append(r["port"])
    module.port_ids = port_ids
    return


def set_module_slot_ids(module: Module) -> None :
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?slot
        WHERE { """f"<{module.id}>" """rdf:type tn:Module .
                ?aggregation tn:assembly """f"<{module.id}>" """ ;
                    tn:part ?slot
                .
        }
    """
    slot_ids = []
    for r in g.query(q):
        slot_ids.append(r["slot"])
    module.slot_ids = slot_ids
    return


def get_port_by_id(port_id: str) -> Port:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?tag ?port
        WHERE { {
                """f'<{port_id}>'""" rdf:type tn:Port ;
                    rdf:type ?port ;
                    rdfs:label ?tag ;
                    .
            } UNION {
                """f'<{port_id}>'""" rdf:type tn:UpPort ;
                        rdf:type ?port ;
                        rdfs:label ?tag ;
                        .
            } UNION {
                """f'<{port_id}>'""" rdf:type tn:DownPort ;
                        rdf:type ?port ;
                        rdfs:label ?tag ;
                        .
            } UNION {
                """f'<{port_id}>'""" rdf:type tn:InsidePort ;
                        rdf:type ?port ;
                        rdfs:label ?tag ;
                        .
            } UNION {
                """f'<{port_id}>'""" rdf:type tn:OutsidePort ;
                        rdf:type ?port ;
                        rdfs:label ?tag ;
                        .
            }
        }
    """

    port: Port = None
    for r in g.query(q):
        label = r["port"]
        print(label[label.index('#')+1:])
        port_type: PortType = None
        match label[label.index('#')+1:]:
            case 'DownPort':
                port_type = PortType.DOWN
            case 'UpPort':
                port_type = PortType.UP
            case 'OutsidePort':
                port_type = PortType.OUTSIDE
            case 'InsidePort':
                port_type = PortType.INSIDE
            case 'Port':
                port_type = PortType.MODULE
    
        port = Port(port_id, r["tag"], port_type)  

    return port

def get_slot_by_id(slot_id: str) -> Slot:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?tag ?dimension
        WHERE {
            """f'<{slot_id}>'""" rdf:type tn:Slot ;
                rdfs:label ?tag ;
                tn:dimension ?dimension
                .
        }
    """

    slot: Slot = None

    for r in g.query(q):
        slot = Slot(id=slot_id, label=r["tag"], dimension=int(r["dimension"]), port_ids=[])

    if slot is not None:
        set_slot_port_ids(slot)

    return slot

def set_slot_port_ids(slot: Slot) -> None:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT  ?dport ?uport ?iport ?oport ?label
        WHERE { 
            { <"""f'{slot.id}'"""> rdf:type tn:Slot ;
                tn:has_down_port ?dport .
				?dport rdfs:label ?label ;
            } UNION {
                <"""f'{slot.id}'"""> rdf:type tn:Slot ;
                tn:has_up_port ?uport .
				?uport rdfs:label ?label ;
            } UNION {
                <"""f'{slot.id}'"""> rdf:type tn:Slot ;
                tn:has_inside_port ?iport .
				?iport rdfs:label ?label ;
            } UNION {
                <"""f'{slot.id}'"""> rdf:type tn:Slot ;
                tn:has_outside_port ?oport .
				?oport rdfs:label ?label ;
            }
        }
    """
    port_ids = []
    for r in g.query(q):
        if r["dport"] is not None:
            port_ids.append(r["dport"])
        if r["uport"] is not None:
            port_ids.append(r["uport"])
        if r["iport"] is not None:
            port_ids.append(r["iport"])
        if r["oport"] is not None:
            port_ids.append(r["oport"])
    slot.port_ids = port_ids
    return

def get_connected_to_port_id(this_port: Port) -> str:
    match this_port.type.name:
        case 'DOWN':
            p1 = "tn:down"
            p2 = "tn:up"
        case 'UP':
            p1 = "tn:up"
            p2 = "tn:down"
        case 'INSIDE':
            p1 = "tn:inside"
            p2 = "tn:outside"
        case 'OUTSIDE':
            p1 = "tn:outside"
            p2 = "tn:inside"
        case 'MODULE':    
            p1 = "tn:port"
            p2 = "tn:port"

    q = """
    PREFIX tn: <http://infrabim.nl/kip/topology_network#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
    SELECT ?other_port ?connection
    WHERE {
        ?connection rdf:type tn:Connection ;
            """ f'{p1} <{this_port.id}>' """ ;
            """ f'{p2}' """ ?other_port ;
            .
    }
    """
    for r in g.query(q):
        return r["other_port"]
    return None

def get_connected_to_port(this_port: Port) -> Port:
    port_id = get_connected_to_port_id(this_port)
    if port_id is not None:
        return get_port_by_id(port_id)
    return None

def get_selected_module_id(slot: Slot) -> str:
    q = """
    PREFIX tn: <http://infrabim.nl/kip/topology_network#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
    SELECT ?selected_module ?selection
    WHERE {
        ?selection rdf:type tn:Selection ;
        tn:selecting_slot """f'<{slot.id}>'""" ;
        tn:selected_module ?selected_module ;
            .
    }
    """

    for r in g.query(q):
        return r["selected_module"]
    return None


def get_selected_module(slot: Slot) -> Module:
    module_id = get_selected_module_id(slot)

    if module_id is not None:
        return get_module_by_id(module_id)
    return None

def get_selecting_slot_id(module: Module) -> str:
    q = """
    PREFIX tn: <http://infrabim.nl/kip/topology_network#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
    SELECT ?selecting_slot ?selection
    WHERE {
        ?selection rdf:type tn:Selection ;
        tn:selected_module """f'<{module.id}>'""" ;
        tn:selecting_slot ?selecting_slot ;
            .
    }
    """

    for r in g.query(q):
        return r["selecting_slot"]
    return None

def get_selecting_slot(module: Module) -> Slot:
    slot_id = get_selecting_slot_id(module)
    if slot_id is not None:
        return get_slot_by_id(slot_id)
    return None


def get_enclosed_by_module_id(slot: Slot) -> str:
    q = """
    PREFIX tn: <http://infrabim.nl/kip/topology_network#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
    SELECT ?module ?aggregation
    WHERE {
        ?aggregation rdf:type tn:Aggregation ;
        tn:part """f'<{slot.id}>'""" ;
        tn:assembly ?module ;
            .
    }
    """

    for r in g.query(q):
        return r["module"]
    return None    

def get_enclosed_by_module(slot: Slot) -> Module:
    module_id = get_enclosed_by_module_id(slot)

    if module_id is not None:
        return get_module_by_id(module_id)
    return None

def get_selected_module_port_id(port: Port) -> str :
    q = """
    PREFIX tn: <http://infrabim.nl/kip/topology_network#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
    SELECT ?selected_module_port ?selection
    WHERE {
        ?selection rdf:type tn:Selection ;
        tn:selecting_slot_port """f'<{port.id}>'""" ;
        tn:selected_module_port ?selected_module_port ;
            .
    }
    """

    for r in g.query(q):
        return r["selected_module_port"]
    return None

def get_selected_module_port(port: Port) -> Port :
    module_id = get_selected_module_port_id(port)
    if module_id is not None:
        return get_port_by_id(module_id)
    return None

def get_sub_port_ids(module_port: Port) -> list[str]:
    q = """
        PREFIX tn: <http://infrabim.nl/kip/topology_network#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
        SELECT ?slot_port
        WHERE { """f"<{module_port.id}>" """rdf:type tn:Port .
                ?aggregation tn:assembly """f"<{module_port.id}>" """ ;
                    tn:part ?slot_port
                .
        }
    """
    slot_port_ids = []
    for r in g.query(q):
        slot_port_ids.append(r["slot_port"])
    return slot_port_ids

def get_sub_ports(module_port: Port) -> list[Port]:
    sub_ports: list[Port] = []
    sub_port_ids = get_sub_port_ids(module_port)
    for id in sub_port_ids:
        sub_ports.append(get_port_by_id(id))
    return sub_ports

@port.type_resolver
def resolve_port_type(obj, *_):
    port: Port = obj
    if port.type == PortType.MODULE:
        return "ModulePort"
    else: 
        return "SlotPort"

#######################################
# Queries
#######################################
@query.field("allModules")
def resolve_query_all_modules(*_) -> list[Module]:
    all_modules = get_all_modules()
    return all_modules

@query.field("moduleById")
def resolve_query_module_by_id(*_, id) -> Module:
    module = get_module_by_id(id)
    set_module_port_ids(module)
    set_module_slot_ids(module)
    return module

@query.field("slotById")
def resolve_query_slot_by_id(*_, id) -> Slot:
    slot = get_slot_by_id(id)
    set_slot_port_ids(slot)
    return slot

@module.field("portCount")
def resolve_module_port_count(obj, *_) -> int:
    module: Module = obj
    return len(module.port_ids)

@module.field("portIds")
def resolve_module_port_ids(obj, *_) -> int:
    module: Module = obj
    return module.port_ids

@module.field("ports")
def resolve_module_ports(obj, *_) -> list[Port]:
    def sort_func(port:Port):
        return port.label

    module: Module = obj
    ports:list[Port] = []
    for port_id in module.port_ids:
        ports.append(get_port_by_id(port_id))
        
    ports.sort(key=sort_func)

    return ports

@module.field("slotCount")
def resolve_module_slot_count(obj, *_) -> int:
    module: Module = obj
    return len(module.slot_ids)

@module.field("slotIds")
def resolve_module_slot_ids(obj, *_) -> int:
    module: Module = obj
    return module.slot_ids

@module.field("slots")
def resolve_module_slots(obj, *_) -> list[Slot]:
    def sort_func(slot:Slot):
        return slot.label

    module: Module = obj
    slots:list[Slot] = []
    for slot_id in module.slot_ids:
        slots.append(get_slot_by_id(slot_id))
    slots.sort(key=sort_func)

    return slots

@module.field("selectingSlotId")
def resolve_module_selecting_slot_id(obj, *_) -> str:
    module: Module = obj
    return get_selecting_slot_id(module)

@module.field("selectingSlot")
def resolve_module_selecting_slot(obj, *_) -> Slot:
    module: Module = obj
    return get_selecting_slot(module)

@slot.field("portCount")
def resolve_module_port_count(obj, *_) -> int:
    slot: Slot = obj
    return len(slot.port_ids)

@slot.field("portIds")
def resolve_slot_port_ids(obj, *_) -> int:
    slot: Slot = obj
    return slot.port_ids

@slot.field("ports")
def resolve_slot_ports(obj, *_) -> list[Port]:
    def sort_func(port:Port):
        return port.label
    
    slot: Slot = obj
    ports: list[Port] = []
    for port_id in slot.port_ids:
        ports.append(get_port_by_id(port_id))
    ports.sort(key=sort_func)

    return ports

@slot.field("selectedModuleId")
def resolve_slot_selected_modul_id(obj, *_) -> str:
    slot: Slot = obj
    return get_selected_module_id(slot)

@slot.field("selectedModule")
def resolve_slot_selected_module(obj, *_) -> Module:
    slot: Slot = obj
    selected_module = get_selected_module(slot)
    return selected_module

@slot.field("enclosedByModuleId")
def resolve_slot_enclosed_by_module_id(obj, *_) -> str:
    slot: Slot = obj
    return get_enclosed_by_module_id(slot)

@slot.field("enclosedByModule")
def resolve_slot_enclosed_by_module_id(obj, *_) -> Module:
    slot: Slot = obj
    return get_enclosed_by_module(slot)

@port.field("type")
def resolve_port_type(obj, *_) :
    port: Port = obj
    return port.type.value

@slot_port.field("connectedToPortId")
def resolve_slot_port_connected_to_port_id(obj, *_) -> str:
    this_port: Port = obj
    return get_connected_to_port_id(this_port)

@slot_port.field("connectedToPort")
def resolve_slot_port_connected_to_port(obj, *_) -> Port:
    this_port: Port = obj
    other_port = get_connected_to_port(this_port)
    return other_port

@slot_port.field("selectedModulePortId")
def resolve_slot_port_selected_module_port_id(obj, *_) -> str:
    this_port: Port = obj
    return get_selected_module_port_id(this_port)

@slot_port.field("selectedModulePort")
def resolve_slot_port_selected_module_port(obj, *_) -> Port:
    this_port: Port = obj
    selected_module_port = get_selected_module_port(this_port)
    return selected_module_port

@module_port.field("subPortIds")
def resolve_module_port_sub_port_ids(obj, *_) -> list[str]:
    module_port: Port = obj
    sub_port_ids = get_sub_port_ids(module_port)
    return sub_port_ids

@module_port.field("subPorts")
def resolve_module_port_sub_ports(obj, *_) -> list[Port]:
    module_port: Port = obj
    sub_ports = get_sub_ports(module_port)
    return sub_ports

# Create a Graph
g = Graph()
g.parse("Notions/Window_demo/topology_network.ttl")
g.parse("Notions/Window_demo/window_glass_selection.ttl")
g.parse("Notions/Window_demo/window_module.ttl")
g.parse("Notions/Window_demo/glass_module.ttl")
g.parse("Notions/Window_demo/eco_system.ttl")

# TN=Namespace("http://infrabim.nl/kip/topology_network#")
# g.bind("tn", TN)

schema = make_executable_schema(
    type_defs, query, module, slot, port, module_port, slot_port, port_type
)

app = GraphQL(schema, debug=True)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
