from enum import Enum, auto
import json
import yaml

class ConfigType(Enum):
    Json = auto() # JSON (RFC-8259)
    Yaml = auto() # YAML (YAML 1.2)

class ConfigContext():
    # Unparsed string contain the config file's contents.
    # JSON, YAML are considered the legal formats.
    raw_config = str()

    # De-serialized parsed data from the config file.
    # Library users may use this property to modify,
    # or access directly the keys and values.
    parsed_config = {}


    def __init__(self, cfgtype: ConfigType):
        """
        Manages serialized and de-serialized configuration data,
        it's useful in several scenarios. YAML and JSON serialization 
        is the only legal configuration format supported.

        The usage of JSON isn't supported and you're encouraged to use
        the YAML because it has more features than JSON.
        """

        self.cfgtype = cfgtype  # This property is useful while selection
                                # of de-serialization format.

    def parse(self, data: str):
        """
        Parses the data based on the de-serialization format,
        the format must be explictly specified.
        Note that, you cannot provide any other serialized format
        other than the format specfied on the initalization.
        """

        self.parsed_config = (
            self._parse_yaml 
                if self.cfgtype == ConfigType.Yaml 
                else 
            self._parse_json 
                if self.cfgtype == ConfigType.Json 
                else 
            None)(data)

    def _parse_json(self, _data) -> dict:
        json.loads(_data)

    def _parse_yaml(self, _data) -> dict:
        yaml.load(_data, Loader=yaml.CLoader)