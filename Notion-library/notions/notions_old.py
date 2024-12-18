from enum import Enum

class ConfigurationManagementClass(Enum):
    CONNECTION_CONNECTION_SELECTION = "CONNECTION_CONNECTION_SELECTION"
    CONNECTION_NODE_ENCLOSURE = "CONNECTION_NODE_ENCLOSURE"
    NODE_NODE_CONNECTION = "NODE_NODE_CONNECTION"
    NODE_NODE_ENCLOSURE = "NODE_NODE_ENCLOSURE"
    NODE_PORT_BOUNDARY = "NODE_PORT_BOUNDARY"
    PORT_PORT_CONNECTION = "PORT_PORT_CONNECTION"
    PORT_PORT_SELECTION = "PORT_PORT_SELECTION"
    SLOT_MODULE_SELECTION = "SLOT_MODULE_SELECTION"


class NotionType(Enum):
    NONE = "NONE"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DURATION = "DURATION"
    ENUMERATION = "ENUMERATION"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    IRI = "IRI"
    STRING = "STRING"


class NotionUnit(Enum):
    NONE = "NONE"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class NotionFrame:
    frames = dict()

    def __init__(self, id: str, parameter: str, type: NotionType, unit: NotionUnit, 
                 derived_from: list[str],
                 converter_code: str, converter: callable, 
                 discriminator_code: str, discriminator: callable) -> None:
        self.id = id
        self.parameter = parameter
        self.type = type
        self.unit = unit
        if len(derived_from) > 0:
            nfs = [NotionFrame.get_notion_frame(nf_id) for nf_id in derived_from]
            dnfs = self.find_derived_frames(nfs)
            nfs += dnfs
            keys = [nf.id for nf in nfs]
            values = [nf for nf in nfs]
            self.derived_from = {key: value for key, value in zip(keys, values)}
        else:
            self.derived_from = dict()
        self.converter_code = converter_code
        self.converter = converter
        self.discriminator_code = discriminator_code
        self.discriminator = discriminator
        NotionFrame.frames[id] = self

    def find_derived_frames(self, nfs: list[object]) -> list[object]:
        def get_df(nf, dnfs):
            if nf.derived_from:
                for dnf in nf.derived_from.values():
                    dnfs.update(get_df(dnf, dnfs))
            else:
                dnfs.add(nf)
                return dnfs
        dnfs = set()
        for nf in nfs:
            if nf.derived_from.values():
                tmp = get_df(nf, dnfs)
                if tmp:
                    dnfs.update(tmp)
        return list(dnfs)

    def get_notion_frame(id: str) -> object:
        ### get notion frame by id ###
        return NotionFrame.frames.get(id)
    
    def get_all_notion_frames() -> list[object]:
        ### get all notion frames ###
        return [nf for nf in NotionFrame.frames.values()]


class NotionValue:
    values = dict()

    def __init__(self, id: str, frame: NotionFrame, args: dict) -> None:
        self.id = id
        self.frame = frame
        self.args = args
        self.property = self.frame.converter(args)
        self.classification = self.frame.discriminator(self.property)
        NotionValue.values[id] = self

    def get_derived_notion_values(self) -> list[object]:
        if self.frame.derived_from:
            return [value for value in self.args.values() if isinstance(value, NotionValue)]
        return []

    def get_notion_value(id: str) -> object:
        ### get notion value by id ###
        return NotionValue.values.get(id)
    
    def get_all_notion_values() -> list[object]:
        ### get all notion values ###
        return [nv for nv in NotionValue.values.values()]
    
    def __repr__(self) -> str:
        return f"NotionValue(id=\"{self.id}\", frame=\"{self.frame.id}\", args={self.args}, property={self.property}, classification={self.classification})"


class PerceptiveFrame:
    frames = dict()

    def __init__(self, id: str, notion_frame_names: list[str], discriminator_code: str, discriminator: callable) -> None:
        self.id = id
        nfs = [NotionFrame.get_notion_frame(nf_name) for nf_name in notion_frame_names]
        keys = [nf.id for nf in nfs]
        values = [nf for nf in nfs]
        self.notion_frames = {key: value for key, value in zip(keys, values)}
        self.discriminator_code = discriminator_code
        self.discriminator = discriminator
        PerceptiveFrame.frames[id] = self
    
    def get_perceptive_frame(id: str) -> object:
        ### get perceptive_frame by id ###
        return PerceptiveFrame.frames[id]
    
    def get_all_perceptive_frames() -> list[object]:
        ### get all perceptive_frames ###
        return [pf for pf in PerceptiveFrame.frames.values()]


class PerceptiveFrameInstance:
    values = dict()

    def __init__(self, id: str, perceptiveFrameId: str, notion_value_ids: list[str]) -> None:
        self.id = id
        self.perceptive_frame = None
        if perceptiveFrameId:
            self.perceptive_frame = PerceptiveFrame.get_perceptive_frame(perceptiveFrameId)
        self.notion_values = self.get_all_notion_values(notion_value_ids)
        PerceptiveFrameInstance.values[id] = self
    
    def get_all_notion_values(self, notion_value_ids):
        nvs = [NotionValue.get_notion_value(id) for id in notion_value_ids]
        dnvs = [nv.get_derived_notion_values() for nv in nvs]
        for index in range(len(dnvs)):
            for dnv in dnvs[index]:
                nvs.append(dnv)
        return [nv for nv in nvs]

    def get_perceptive_frame_instance(id: str) -> object:
        ### get perceptive_frame_instance by id ###
        return PerceptiveFrameInstance.values.get(id)
    
    def get_all_perceptive_frame_instances() -> list[object]:
        ### get all perceptive_frame_instances ###
        return [pfi for pfi in PerceptiveFrameInstance.values.values()]
