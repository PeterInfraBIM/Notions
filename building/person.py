from enum import Enum

class Gender(Enum):
    XX = 0
    XY = 1

class Notion:
    def __init__(self) -> None:
        self.name = None
        self.domain = None
    def __repr__(self) -> str:
        return f"domain: {self.domain}"


class NotionGender(Notion):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Gender"
        self.domain = Gender
        self.is_female = lambda n: n == Gender.XX
        self.is_male = lambda n: n == Gender.XY

class NotionAge(Notion):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Age"
        self.domain = float
        self.is_child = lambda a: a < 18
        self.is_adult = lambda a: a >= 18

class Anything:
    def __init__(self) -> None:
        self.notions = dict()
    def add_notion(self, notion: Notion):
        self.notions[notion.name] = {
            "notion": notion,
            "value": None
        }
    def set_value(self, notion: Notion, value: Gender):
        self.notions.get(notion.name)["value"] = value


def main():
    # Create an instance of Anything
    person = Anything()
    # Create notion frame for gender
    gender = NotionGender()
    # Create notion frame for age
    age = NotionAge()

    # Add gender notion frame to the anything instance
    person.add_notion(gender)
    # Add age notion frame to the anything instance
    person.add_notion(age)

    # Set a gender notion value
    person.set_value(gender, Gender.XX)
    # Set an age notion value
    person.set_value(age, 16)

    # Present available notion frames
    print(f"Notions: {person.notions}")
    # Query the notion frame
    print(f"Is woman? {gender.is_female(person.notions.get(gender.name)["value"])}")
    print(f"Is child? {age.is_child(person.notions.get(age.name)["value"])}")
    print(f"Is girl? {gender.is_female(person.notions.get(gender.name)["value"]) and age.is_child(person.notions.get(age.name)["value"])}")


main()



