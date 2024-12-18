import math

class Domain:
    def __init__(self, name) -> None:
        self.name = name

class IntegerDomain(Domain):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.intervals = dict()
    
class Interval:
    pass

class IntegerInterval(Interval):
    def __init__(self, lower_bound: int = None, upper_bound: int = None) -> None:
        super().__init__()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


