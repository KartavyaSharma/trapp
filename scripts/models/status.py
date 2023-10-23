from enum import Enum, EnumMeta

class MethaStatus(EnumMeta):
    
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True

class BaseStatus(Enum, metaclass=EnumMeta):
    pass

class Status(BaseStatus):
    INIT = "Applied"
    ASSESSMENT = "Assessment"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"