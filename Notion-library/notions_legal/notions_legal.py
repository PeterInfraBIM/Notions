from notions import NotionFrame, NotionType, NotionUnit, PerceptiveFrame
from enum import Enum
from dateutil import parser

class Gender(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class AgeClass(Enum):
    CHILD = "CHILD"
    ADULT = "ADULT"

class Person(Enum):
    WOMAN = "WOMAN"
    MAN = "MAN"
    GIRL = "GIRL"
    BOY = "BOY"

def init_date_of_birth():
    def converter_function(args):
        return {"date_of_birth": parser.parse(args['date_of_birth'])}
    
    def discriminator_function(args):
        return None
    
    NotionFrame(
        id="NF_Date_of_birth",
        parameter="date_of_birth",
        type=NotionType.DATE,
        unit=NotionUnit.DAY,
        derived_from=[],
        converter_code="""
    def converter_function(args):
        return {"date_of_birth": parser.parse(args['date_of_birth'])}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return None
    """,
        discriminator=discriminator_function
    )

def init_actual_date():
    def converter_function(args):
        return {"actual_date": parser.parse(args['actual_date'])}
    
    def discriminator_function(args):
        return None
    
    NotionFrame(
        id="NF_Actual_date",
        parameter="actual_date",
        type=NotionType.DATE,
        unit=NotionUnit.DAY,
        derived_from=[],
        converter_code="""
    def converter_function(args):
        return {"actual_date": parser.parse(args['actual_date'])}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return None
    """,
        discriminator=discriminator_function
    )

def init_legal_age():
    def converter_function(args):
        nv_date_of_birth = args["NF_Date_of_birth"]
        nv_actual_date = args["NF_Actual_date"]
        birth_date = nv_date_of_birth.property["date_of_birth"]
        actual_date = nv_actual_date.property["actual_date"]
        return {"legal_age": int((actual_date - birth_date).days//365.24)}
    
    def discriminator_function(args):
        legal_age = args["legal_age"]
        return AgeClass.CHILD if legal_age < 18 else AgeClass.ADULT
    
    NotionFrame(
        id="NF_Legal_age",
        parameter="legal_age",
        type=NotionType.DURATION,
        unit=NotionUnit.DAY,
        derived_from=["NF_Date_of_birth", "NF_Actual_date"],
        converter_code="""
    def converter_function(args):
        nv_date_of_birth = args["NF_Date_of_birth"]
        nv_actual_date = args["NF_Actual_date"]
        birth_date = nv_date_of_birth.property["date_of_birth"]
        actual_date = nv_actual_date.property["actual_date"]
        return {"age": int((actual_date - birth_date).days//365.24)}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        legal_age = args["legal_age"]
        return AgeClass.CHILD if legal_age < 18 else AgeClass.ADULT
    """,
        discriminator=discriminator_function
    )

def init_legal_gender():
    def converter_function(args):
        return {"legal_gender": args['legal_gender']}
    
    def discriminator_function(args):
        return args['legal_gender']
    
    NotionFrame(
        id="NF_Legal_gender",
        parameter="legal_gender",
        type=NotionType.ENUMERATION,
        unit=NotionUnit.NONE,
        derived_from=[],
        converter_code="""
    def converter_function(args):
        return {"legal_gender": args['legal_gender']}
    """,
        converter=converter_function,
        discriminator_code="""
    def discriminator_function(args):
        return args['legal_gender']
    """,
        discriminator=discriminator_function
    )

def init_legal():
    def discriminator_function(notion_frames, notion_values):
        nf_legal_age = notion_frames.get('NF_Legal_age')
        nv_legal_age = notion_values.get('NF_Legal_age')
        age_class = nf_legal_age.discriminator(nv_legal_age.property)
        nv_legal_gender = notion_values.get('NF_Legal_gender')
        gender = Gender(nv_legal_gender.property.get("legal_gender"))
        if gender.name is Gender.FEMALE.name:
            if age_class.name is AgeClass.ADULT.name:
                return Person.WOMAN
            return Person.GIRL
        else:
            if age_class.name is AgeClass.ADULT.name:
                return Person.MAN
            return Person.BOY
    
    PerceptiveFrame(
        id="PF_Legal",
        notion_frame_names=["NF_Legal_age", "NF_Legal_gender"],
        discriminator_code="""
    def discriminator_function(notion_frames, notion_values):
        nf_legal_age = notion_frames.get('NF_Legal_age')
        nv_legal_age = notion_values.get('NF_Legal_age')
        age_class = nf_legal_age.discriminator(nv_legal_age.property)
        nv_legal_gender = notion_values.get('NF_Legal_gender')
        gender = Gender(nv_legal_gender.property.get("legal_gender"))
        if gender.name is Gender.FEMALE.name:
            if age_class.name is AgeClass.ADULT.name:
                return Person.WOMAN
            return Person.GIRL
        else:
            if age_class.name is AgeClass.ADULT.name:
                return Person.MAN
            return Person.BOY
    """,
        discriminator=discriminator_function
    )

def init():
    init_date_of_birth()
    init_actual_date()
    init_legal_age()
    init_legal_gender()
    init_legal()
