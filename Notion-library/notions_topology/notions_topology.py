from notions import NotionFrame, NotionValue, NotionType, NotionUnit, PerceptiveFrame, PerceptiveFrameInstance
from enum import Enum

class OrientationClass(Enum):
    DEPARTURE = "DEPARTURE"
    ARRIVAL = "ARRIVAL"

class BoundaryClass(Enum):
    BOUNDS = "BOUNDS"
    IS_BOUNDED_BY = "IS_BOUNDED_BY"

class EnclosureClass(Enum):
    ENCLOSES = "ENCLOSE"
    IS_ENCLOSED_BY = "IS_ENCLOSED_BY"

class ConnectionClass(Enum):
    DOWN = "DOWN"
    UP = "UP"

class SelectionClass(Enum):
    SELECTS = "SELECTS"
    IS_SELECTED_BY = "IS_SELECTED_BY"

class ConfigurationManagementRelationClass(Enum):
    CONNECTION_CONNECTION_SELECTION = "CONNECTION_CONNECTION_SELECTION"
    CONNECTION_NODE_ENCLOSURE = "CONNECTION_NODE_ENCLOSURE"
    NODE_NODE_CONNECTION = "NODE_NODE_CONNECTION"
    NODE_NODE_ENCLOSURE = "NODE_NODE_ENCLOSURE"
    NODE_PORT_BOUNDARY = "NODE_PORT_BOUNDARY"
    PORT_PORT_CONNECTION = "PORT_PORT_CONNECTION"
    PORT_PORT_SELECTION = "PORT_PORT_SELECTION"
    SLOT_MODULE_SELECTION = "SLOT_MODULE_SELECTION"

class ConfigurationManagementNodeClass(Enum):
    NODE = "NODE"
    SLOT = "SLOT"
    MODULE = "MODULE"
    PORT = "PORT"
    CONNECTION = "CONNECTION"


def query_arcs(nodeId: str = None) -> list[PerceptiveFrameInstance]:
    arcs: list[PerceptiveFrameInstance] = []
    for pfi in PerceptiveFrameInstance.get_all_perceptive_frame_instances():
        for nv in pfi.get_all_notion_values():
            if nv.frame.id == "NF_Link":
                if not nodeId:
                    arcs.append(pfi)
                    break
                else:
                    if nv.property["link"] == nodeId:
                        arcs.append(pfi)
                        break
    return arcs

def init_link():
    def converter_function(args):
        return {"link": args["link"]}
    
    def discriminator_function(args):
        return None
    
    NotionFrame(
        id="NF_Link",
        parameter="link",
        type=NotionType.IRI, 
        unit=NotionUnit.NONE,
        derived_from=[],
        converter_code="""
    def converter_function(args):
        return {"link": args["link"]}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return None
    """,
        discriminator=discriminator_function
    )

def init_orientation():
    def converter_function(args):
        return {"orientation": args["orientation"]}
    
    def discriminator_function(args):
        return OrientationClass(args["orientation"])
    
    NotionFrame(
        id="NF_Orientation",
        parameter="orientation",
        type=NotionType.ENUMERATION, 
        unit=NotionUnit.NONE,
        derived_from=["NF_Link"],
        converter_code="""
    def converter_function(args):
        return {"orientation": args["orientation"]}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return OrientationClass(args["orientation"])
    """,
        discriminator=discriminator_function
    )

def init_boundary():
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"boundary": BoundaryClass.IS_BOUNDED_BY.name}
        else:
            return {"boundary": BoundaryClass.BOUNDS.name}
    
    def discriminator_function(args):
        return args["boundary"]
    
    NotionFrame(
        id="NF_Boundary",
        parameter="boundary",
        type=NotionType.ENUMERATION, 
        unit=NotionUnit.NONE,
        derived_from=["NF_Orientation"],
        converter_code="""
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"boundary": BoundaryClass.IS_BOUNDED_BY.name}
        else:
            return {"boundary": BoundaryClass.BOUNDS.name}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return args["boundary"]
    """,
        discriminator=discriminator_function
    )

def init_enclosure():
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"enclosure": EnclosureClass.IS_ENCLOSED_BY.name}
        else:
            return {"enclosure": EnclosureClass.ENCLOSES.name}
    
    def discriminator_function(args):
        return args["enclosure"]
    
    NotionFrame(
        id="NF_Enclosure",
        parameter="enclosure",
        type=NotionType.ENUMERATION, 
        unit=NotionUnit.NONE,
        derived_from=["NF_Orientation"],
        converter_code="""
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"enclosure": EnclosureClass.IS_ENCLOSED_BY.name}
        else:
            return {"enclosure": EnclosureClass.ENCLOSES.name}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return args["enclosure"]
    """,
        discriminator=discriminator_function
    )

def init_connection():
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"connection": ConnectionClass.DOWN.name}
        else:
            return {"connection": ConnectionClass.UP.name}
    
    def discriminator_function(args):
        return args["connection"]
    
    NotionFrame(
        id="NF_Connection",
        parameter="connection",
        type=NotionType.ENUMERATION, 
        unit=NotionUnit.NONE,
        derived_from=["NF_Orientation"],
        converter_code="""
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"connection": ConnectionClass.DOWN.name}
        else:
            return {"connection": ConnectionClass.UP.name}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return args["connection"]
    """,
        discriminator=discriminator_function
    )

def init_selection():
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"selection": SelectionClass.SELECTS.name}
        else:
            return {"selection": SelectionClass.IS_SELECTED_BY.name}
    
    def discriminator_function(args):
        return args["selection"]
    
    NotionFrame(
        id="NF_Selection",
        parameter="selection",
        type=NotionType.ENUMERATION, 
        unit=NotionUnit.NONE,
        derived_from=["NF_Orientation"],
        converter_code="""
    def converter_function(args):
        if args.get("orientation"):
            orientation = OrientationClass(args["orientation"])
        else:
            orientation = OrientationClass(args["NF_Orientation"].args["orientation"])
        if orientation.name is OrientationClass.DEPARTURE.name:
            return {"selection": SelectionClass.SELECTS.name}
        else:
            return {"selection": SelectionClass.IS_SELECTED_BY.name}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return args["selection"]
    """,
        discriminator=discriminator_function
    )

#-----------------------------------------------------------------------

def get_link(nv: NotionValue) -> str:
    dnvs: list[NotionValue] = nv.get_derived_notion_values()
    for dnv in dnvs:
        if dnv.frame.id == "NF_Link":
            return dnv.property["link"]
    return None

def get_config_mng_node_classification(nv: NotionValue):
    id = get_link(nv)
    p_frame: PerceptiveFrame = PerceptiveFrame.frames.get("PF_Config_Mng_Node")
    node_classification = p_frame.discriminator(None, None, id=id)
    return node_classification.name

def init_config_mng_relation():
    def discriminator_function(notion_frames, notion_values):
        if notion_values.get("NF_Enclosure"):
            enclosures = [nv for nv in notion_values.get("NF_Enclosure")]
            if enclosures:
                if enclosures[0].property.get("enclosure") == "IS_ENCLOSED_BY" and \
                    enclosures[1].property.get("enclosure") == "ENCLOSES":
                    return ConfigurationManagementRelationClass("NODE_NODE_ENCLOSURE")
                else:
                    return None
        if notion_values.get("NF_Boundary"):
            boundaries = [nv for nv in notion_values.get("NF_Boundary")]
            if boundaries:
                if boundaries[0].property.get("boundary") == "IS_BOUNDED_BY" and \
                    boundaries[1].property.get("boundary") == "BOUNDS":
                    return ConfigurationManagementRelationClass("NODE_PORT_BOUNDARY")
                else:
                    return None
        if notion_values.get("NF_Connection"):
            connections = [nv for nv in notion_values.get("NF_Connection")]
            if connections:
                if connections[0].property.get("connection") == "DOWN" and \
                    connections[1].property.get("connection") == "UP":
                    classification0 = get_config_mng_node_classification(connections[0])
                    classification1 = get_config_mng_node_classification(connections[1])
                    if classification0 == "PORT" and classification1 == "PORT":
                        return ConfigurationManagementRelationClass("PORT_PORT_CONNECTION")
                    else:
                        return ConfigurationManagementRelationClass("NODE_NODE_CONNECTION")
                else:
                    return None
        if notion_values.get("NF_Selection"):
            selections = [nv for nv in notion_values.get("NF_Selection")]
            if selections:
                if selections[0].property.get("selection") == "SELECTS" and \
                    selections[1].property.get("selection") == "IS_SELECTED_BY":
                    classification0 = get_config_mng_node_classification(selections[0])
                    classification1 = get_config_mng_node_classification(selections[1])
                    if classification0 == "PORT" and classification1 == "PORT":
                        return ConfigurationManagementRelationClass("PORT_PORT_SELECTION")
                    else:
                        return ConfigurationManagementRelationClass("SLOT_MODULE_SELECTION")
                else:
                    return None
                
    PerceptiveFrame(
        id="PF_Config_Mng_Relation",
        notion_frame_names=["NF_Enclosure", "NF_Boundary", "NF_Connection"],
        discriminator_code="""
def discriminator_function(notion_frames, notion_values):
    if notion_values.get("NF_Enclosure"):
        enclosures = [nv for nv in notion_values.get("NF_Enclosure")]
        if enclosures:
            if enclosures[0].property.get("enclosure") == "IS_ENCLOSED_BY" and \
                enclosures[1].property.get("enclosure") == "ENCLOSES":
                return ConfigurationManagementRelationClass("NODE_NODE_ENCLOSURE")
            else:
                return None
    if notion_values.get("NF_Boundary"):
        boundaries = [nv for nv in notion_values.get("NF_Boundary")]
        if boundaries:
            if boundaries[0].property.get("boundary") == "IS_BOUNDED_BY" and \
                boundaries[1].property.get("boundary") == "BOUNDS":
                return ConfigurationManagementRelationClass("NODE_PORT_BOUNDARY")
            else:
                return None
    if notion_values.get("NF_Connection"):
        connections = [nv for nv in notion_values.get("NF_Connection")]
        if connections:
            if connections[0].property.get("connection") == "DOWN" and \
                connections[1].property.get("connection") == "UP":
                classification0 = get_config_mng_node_classification(connections[0])
                classification1 = get_config_mng_node_classification(connections[1])
                if classification0 == "PORT" and classification1 == "PORT":
                    return ConfigurationManagementRelationClass("PORT_PORT_CONNECTION")
                else:
                    return ConfigurationManagementRelationClass("NODE_NODE_CONNECTION")
            else:
                return None
    if notion_values.get("NF_Selection"):
        selections = [nv for nv in notion_values.get("NF_Selection")]
        if selections:
            if selections[0].property.get("selection") == "SELECTS" and \
                selections[1].property.get("selection") == "IS_SELECTED_BY":
                classification0 = get_config_mng_node_classification(selections[0])
                classification1 = get_config_mng_node_classification(selections[1])
                if classification0 == "PORT" and classification1 == "PORT":
                    return ConfigurationManagementRelationClass("PORT_PORT_SELECTION")
                else:
                    return ConfigurationManagementRelationClass("SLOT_MODULE_SELECTION")
            else:
                return None
""",
        discriminator=discriminator_function
    )


def init_config_mng_node():
    def discriminator_function(notion_frames, notion_values, id):
        properties = dict()

        pfis = query_arcs(nodeId=id)
        for pfi in pfis:
            link_found = False
            for nv in pfi.notion_values:
                dnvs = pfi.get_all_notion_values()
                for dnv in dnvs:
                    if dnv.frame.id == "NF_Link":
                        if dnv.property["link"] == id:
                            link_found = True
                            properties[nv.frame.parameter] = nv.property[nv.frame.parameter]
                            break
                if link_found:
                    break

        if "boundary" in properties:
            if properties["boundary"] == "BOUNDS":
                return ConfigurationManagementNodeClass("PORT")
        if "selection" in properties:
            if properties["selection"] == "SELECTS":
                return ConfigurationManagementNodeClass("SLOT")
            if properties["selection"] == "IS_SELECTED_BY":
                return ConfigurationManagementNodeClass("MODULE")
        return ConfigurationManagementNodeClass("NODE")
                
    PerceptiveFrame(
        id="PF_Config_Mng_Node",
        notion_frame_names=[],
        discriminator_code="""
def discriminator_function(notion_frames, notion_values, id):
    properties = dict()

    pfis = query_arcs(nodeId=id)
    for pfi in pfis:
        link_found = False
        for nv in pfi.notion_values:
            dnvs = nv.get_derived_notion_values()
            for dnv in dnvs:
                if dnv.frame.id == "NF_Link":
                    if dnv.property["link"] == id:
                        link_found = True
                        properties[nv.frame.parameter] = nv.property[nv.frame.parameter]
                        break
            if link_found:
                break

    if "boundary" in properties:
        if properties["boundary"] == "BOUNDS":
            return ConfigurationManagementNodeClass("PORT")
    return ConfigurationManagementNodeClass("NODE")
""",
    discriminator=discriminator_function
)

#----------------------------------------------------------------------

def init():
    init_link()
    init_orientation()
    init_boundary()
    init_enclosure()
    init_connection()
    init_selection()
    init_config_mng_relation()
    init_config_mng_node()
