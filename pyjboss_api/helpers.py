import re
from typing import Optional, Union

from urllib.parse import unquote_plus, quote_plus

class Addresses:
    def __init__(self, *paths):
        self.addresses = []
        _path = []
        self.str_address = ""

        if len(paths) == 1 and paths[0].startswith("/"):
            path: str = paths[0].lstrip("/")

            # This fixes situation when resource is named '/'
            path = f"={quote_plus('/')}".join(re.split('=/', path)).replace("=", "/")
            
            paths = [ unquote_plus(p) for p in path.split("/") ]

        if len(paths) == 1:
            pass
        elif not (len(paths) % 2) == 0:
            raise ValueError("Incorrect number of paths. Must be even number")
        for path in paths:
            _path.append(path)
            if len(_path) == 2:
                self.addresses.append({ _path[0]: _path[1] })
                self.str_address = self.str_address + "/" + _path[0] + "=" + _path[1]
                _path = []

    def add_path(self, directory: str, subdirectory: str):
        self.addresses.append({ directory: subdirectory })

    def get_jmespath_filter(self):
        # This returns root path
        if not self.addresses:
            return '@'
        
        _pattern = ''
        for i in self.addresses:
            if _pattern:
                _pattern = _pattern + "."
            for k,v in i.items():
                _pattern = _pattern + f'"{k}"."{v}"'
        return _pattern

    def to_dict(self):
        return self.addresses
    
    def __repr__(self):
        return f"Address({self.str_address})"
    
    def __str__(self):
        return self.str_address

class Payload:
    def __init__(self, address: Optional[Union[Addresses, str, dict]] = None, operation: Optional[str] = None, **kwargs):
        self.payload = {}
        if address:
            self.address = address
        if operation:
            self.operation = operation
        if kwargs:
            for kwarg in kwargs:
                self.add_key_value(kwarg, kwargs[kwarg])

    def add_key_value(self, key, value):
        self.payload[key] = value

    def to_dict(self):
        return self.payload

    @property
    def operation(self):
        return self.payload['operation'] if 'operation' in self.payload else None
    
    @operation.setter
    def operation(self, value):
        self.payload['operation'] = value

    @property
    def address(self):
        return self.payload['address'] if 'address' in self.payload else None
    
    @address.setter
    def address(self, value):
        if isinstance(value, Addresses):
            self.payload["address"] = value.to_dict()
        elif isinstance(value, str):
            self.payload["address"] = Addresses(value).to_dict()
        elif isinstance(value, dict):
            self.payload["address"] = Addresses(**value).to_dict()
        else:
            raise TypeError("Address argument type invalid. Must be instance of Addresses class or str, dict.")

def pyattr(attr: str):
    '''
    Helper to return python-friendly attribute name
    '''
    return attr.replace("-", "_")