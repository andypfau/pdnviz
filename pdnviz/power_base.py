from abc import ABC
import warnings, copy



class PowerConfig:

    """Ambient temperature (for thermal calculations), in °C"""
    t_ambient: float = +20 # degrees C

    _warning_handler = None # type: callable[tuple[PowerBaseElement, str], None]


    @staticmethod
    def set_warning_handler(handler: "callable[tuple[PowerBaseElement, str], None]"):
        PowerConfig._warning_handler = handler


    @staticmethod
    def _warn(element: "PowerBaseElement", msg: str):
        if PowerConfig._warning_handler is not None:
            PowerConfig._warning_handler(element, msg)
        else:
            warnings.warn(f'{element}: {msg}')



class PowerBaseElement(ABC):


    def __init__(self, name):
        self.name = name
        self.clear_warnings()
    

    def _warn(self, msg: str, severe: bool = False):
        self._warnings.append(msg)
        PowerConfig._warn(self, msg)
        if severe:
            raise RuntimeError(msg)
    

    def clear_warnings(self):
        self._warnings = [] # type: list[str]
    

    def ok(self) -> bool:
        return len(self._warnings) == 0
    
    
    def get_warnings(self):
        return copy.copy(self._warnings)
