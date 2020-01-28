from core.modules import InputModule
from core.config_file import ConfigFile

class HCSR04(InputModule):
    """
    Distance measuring using the HC-SR04 sensor.
    """

    def __init__(self):
        super(HCSR04, self).__init__()
        from modules.input.HCSR04.dep.hcsr04 import HCSR04 as HCSR04_drv
        self.sensor = HCSR04_drv(self.config().get("pin_echo"), self.config().get("pin_trigger"), self.config().get("samples"))

    def get_id():
        return 1

    def get(self):
        return InputModule.uint16_to_bytearray(self.sensor.measure())

    def decode(array):
        s = "\t\"HCSR04\":\n\t{\n"
        s += "\t\t\"distance_cm\": " + str(InputModule.bytearray_to_uint16(array, 0)) + "\n\t}"
        return s

    def test(self):
        self.get()

    def get_config_definition():
        return (
            "input_hcsr04",
            "Adds support for the HCSR04 distance sensor.",
            (
                ("pin_echo", "20", "Defines the echo pin.", ConfigFile.VariableType.uint),
                ("pin_trigger", "21", "Defines the trigger pin.", ConfigFile.VariableType.uint),
                ("samples", "20", "Defines how many samples should be taken.", ConfigFile.VariableType.uint),
            )
        )
