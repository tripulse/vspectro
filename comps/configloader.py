from enum import Enum, auto
import logging
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

        self.cfgtype = cfgtype
        logging.info(f"Set the Configuration Parser type to {repr(cfgtype)}")

    def parse(self, data: str):
        """
        Parses the data based on the de-serialization format,
        the format must be explictly specified.
        Note that, you cannot provide any other serialized format
        other than the format specfied on the initalization.
        """

        if self.cfgtype == ConfigType.Yaml:
            self.parsed_config = self._parse_yaml(data)
        elif self.cfgtype == ConfigType.Json:
            self.parsed_config = self._parse_json(data)
        else:
            logging.error("No supported configuration type found!")

    def _parse_json(self, _data) -> dict:
        try:
            return json.loads(_data)
        except json.JSONDecodeError as decode_err:
            logging.exception("Cannot decode JSON data!", stack_info= True)

    def _parse_yaml(self, _data) -> dict:
        try:
            return yaml.load(_data, Loader=yaml.CLoader)
        except yaml.YAMLError as decode_err:
            logging.exception("Cannot decode YAML data!", stack_info= True)