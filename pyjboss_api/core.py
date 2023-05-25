import pdb
from json import dumps as jdumps
from typing import Union
from urllib.parse import quote_plus
from warnings import warn

from jmespath import search as jpsearch
from requests import post
from requests.auth import HTTPDigestAuth
from requests.exceptions import ConnectionError, JSONDecodeError

from .exceptions import CallRaisedException, FailedApiCall, ReloadServer, UnsupportedOperation
from .helpers import Addresses, Payload, pyattr
from .logger import log
from .operations import ADD, READ_ATTRIBUTE, READ_RESOURCE, WRITE_ATTRIBUTE

ATTR_TYPES = {
    "BOOLEAN": bool,
    "OBJECT": dict
}

class JbossConnection(object):
    def __init__(self, username: str, password: str, address: str = 'localhost', port: int = 9990, ssl: bool = False, ssl_verify: bool = True):
        '''
        Initiate connection to WildFly API

        You can use it like this if you're connecting to standard port (9990) without ssl:
            >>> from pyjboss_api import JbossConnection
            >>> jboss = Connect('localhost', 'management', 'secret')
        or, if you have SSL management connection listening on different port:
            >>> from pyjboss_api import JbossConnection
            >>> jboss = Connect('localhost', 'management', 'secret', jboss_port=9993, jboss_ssl=True)

        :param username (required): Username with admin privileges
        :param password (required): Password of user you're connecting with
        :param address (optional, default: 'localhost'): IP Address or hostname of WIldFly server
        :param port (optional, default: 9990): Port where WildFly API is listening to
        :param ssl (optional, False): If WildFly API is listening on SSL protocol, use it
        :param ssl_verify (optional, True): If jboss_ssl is set to True, then this parameter determins if we need to verify ssl certificate or not.
        '''

        # Make sure parameters are of valid type
        assert isinstance(address, str)
        assert isinstance(username, str)
        assert isinstance(password, str)
        assert isinstance(port, int)
        assert isinstance(ssl, bool)
        assert isinstance(ssl_verify, bool)

        # Connection parameters
        self.address = "%s://%s:%s/management" % ("https" if ssl else "http", address, port)
        self.username = username
        self.password = password
        self.ssl_verify = ssl_verify

        # Variables holding previous call result
        self.last_payload = None
        self.last_call = None

        # Make first call
        log.debug(f"Making first call to jboss controller at: {self.address}")
        init_call = Call(self, READ_ATTRIBUTE("server-state"))
        if init_call.exception:
            raise ConnectionError("Failed to start establish initial connection to WildFly API. Raised exception: %s. Call result: %s" % (init_call.exception, init_call))

        # Load resource descriptions so we can build models on top of them
        log.debug("Extracting resource descriptions...")
        self._resource_description = Call(self, Payload(operation='read-resource-description', recursive=True, operations=True))
        self._resource_description.raise_for_status()

        # Load initial values - this will come in handy so we don't call read-resource for every applicable resource
        log.debug("Extracting initial values for resources...")
        self._initial_values = Call(self, Payload([], READ_RESOURCE, recursive=True)).result

        # Start building model
        log.debug("Building a model.")
        self.root = RootPath(self, self._resource_description.result)

    def reload(self):
        log.debug("Asked to reload.")
        Call(self, Payload(operation="reload")).raise_for_status()

    @property
    def reload_required(self):
        res = Call(self, READ_ATTRIBUTE("server-state"))
        return res.reload_required
    
    @reload_required.setter
    def reload_required(self, value: bool):
        if value == True:
            warn("Server reload required", ReloadServer)

class Call(object):
    def __init__(self, client: JbossConnection, payload: Union[dict, list, Payload]):
        self.client = client
        address = client.address
        user = client.username
        password = client.password
        ssl_verify = client.ssl_verify

        # Turn payload to json string
        if isinstance(payload, (dict, list)):
            payload = jdumps(payload)
        elif isinstance(payload, Payload):
            payload = jdumps(payload.to_dict())
        else:
            raise TypeError("Received payload type: %s but we need dict, list or instance of Payload class" % type(payload))
        self.payload = payload

        # Create headers and authentication token
        headers = {'content-type': 'application/json'}
        authentication = HTTPDigestAuth(username=user, password=password)
        
        # Memorize last payload and call result
        client.last_payload = payload
        client.last_call = self

        self.reload_required = False
        self.exception = None
        try:
            log.debug(f"Running call with payload: {payload}")
            res = post(address, auth=authentication, headers=headers, data=payload, verify=ssl_verify)
            self.request = res
            log.debug(f"Call completed with status code: {res.status_code}")
            res = res.json()
        except JSONDecodeError as e:
            log.exception(e)
            self.exception = type(e).__name__
            self.success = False
            self.result = "Received response is not JSON. Status code: %s, text: %s" % (res.status_code, res.text)
            warn(self.result, CallRaisedException)
        except ConnectionError as e:
            log.exception(e)
            self.exception = type(e).__name__
            self.success = False
            self.result = "Cannot connect to host url %s." % (address)
            warn(self.result, CallRaisedException)
        except Exception as e:
            log.exception(e)
            self.exception = type(e).__name__
            self.success = False
            self.result = "Exception (%s) occurred. Error: %s" % (type(e).__name__, str(e))
            warn(self.result, CallRaisedException)
        else:
            self.success = True if res['outcome'] == "success" else False
            self.result = res['result'] if 'result' in res else res['failure-description'] if 'failure-description' in res else None
            if 'response-headers' in res and 'process-state' in res['response-headers'] and res['response-headers']['process-state'] == 'reload-required':
                self.reload_required = True
                client.reload_required = True

    def raise_for_status(self):
        if not self.success:
            raise FailedApiCall(self)
        
    def return_success_or_raise(self):
        '''
        Call this to raise Exception if call ended with exception, otherwise will return success response.
        '''
        return self.raise_for_status() if self.exception else self.success
    
    def return_result_or_raise(self):
        '''
        Call this to raise Exception if call ended with exception, otherwise will return result response.
        '''
        return self.raise_for_status() if self.exception else self.result
    
    def __repr__(self):
        return "JbossResult(success=%s,result=%s,reload_required=%s)" % (self.success, self.result, self.reload_required)

class RootPath(dict):
    def __init__(self, connection: JbossConnection, children: dict, address = "/"):
        self._connection = connection
        self._dict = {}

        for child in children['children']:
            if children['children'][child].get('model-description'):
                _child = Model(self._connection, children['children'][child], "%s%s" % (address, child))
                setattr(self, pyattr(child), _child)
                self._dict[child] = _child

        super().__init__(**self._dict)

class ResourceAttributes:
    def __init__(self, child):
        self._connection = child._connection
        self._attributes = child._child['attributes']
        self._address = child._address
        self._keys = child._child['attributes'].keys()

    def __getitem__(self, key):
        return Call(self._connection, Payload(self._address, **READ_ATTRIBUTE(key))).return_result_or_raise()

    def __setitem__(self, key, value):
        if self._attributes[key]['type']['TYPE_MODEL_VALUE'] in ATTR_TYPES:
            _type = ATTR_TYPES[self._attributes[key]['type']['TYPE_MODEL_VALUE']]
            if not isinstance(value, _type):
                raise ValueError(f"Value passed must be type of {_type}, not {type(value)}")
        return Call(self._connection, Payload(self._address, **WRITE_ATTRIBUTE(key, value))).raise_for_status()

    def __repr__(self):
        return "ResourceAttributes(%s)" % { k:self[k] for k in self._attributes.keys()}

class ResourceOperations:
    def __init__(self, child):
        self._list = []

        for op in child._child['operations']:
            setattr(self, pyattr(op), Operation(op, child, child._child['operations'][op]))
            self._list.append(op)
    
    def __repr__(self) -> str:
        return f"Operations({self._list})"
    

class Model(dict):
    def __init__(self, connection: JbossConnection, child, address: str, initial_run = True):
        self._address = address
        self._connection = connection
        self._child = child
        self.description = child['description'] if 'description' in child else None
        self._dict = {}
        self._expandable = False

        try: child['model-description']
        except: pdb.set_trace()
        # Recursively create resources under this Model
        for subdir in child['model-description'].keys():
            _child = child['model-description'][subdir]
            # Sometime resource can be expanded, make sure we accomodate those
            if subdir == '*':
                self._expandable = True
                _address = address.split("/")
                _resource = _address.pop(-1)
                _address = Addresses("/".join(_address))
                if initial_run:
                    jmespath_filter = _address.get_jmespath_filter() # + f'."{_resource}"'
                    _children = jpsearch(jmespath_filter, self._connection._initial_values)
                else:
                    _children = Call(self._connection, Payload(_address, READ_RESOURCE)).result

                if _children and _children[_resource]:
                    for subdir in _children[_resource]:
                        _subdir = Resource(self._connection, _child, "%s=%s" % (address, quote_plus(subdir)), self)
                        setattr(self, pyattr(subdir), _subdir)
                        self._dict[subdir] = _subdir
            else:
                _subdir = Resource(self._connection, _child, "%s=%s" % (address, quote_plus(subdir)), self)
                setattr(self, pyattr(subdir), _subdir)
                self._dict[subdir] = _subdir
        super().__init__(**self._dict)

    def add(self, name: str, **kwargs):
        __doc__ = self._child['model-description']['*']['operations']['add']['description'] if self._expandable else None
        if self._expandable:
            _res = Call(self._connection, Payload(f"{self._address}={name}", ADD, **{ k.replace("_", "-"): kwargs.get(k) for k in kwargs }))
            if _res.success:
                _resource = Resource(connection = self._connection, child = self._child['model-description']['*'], address = "%s=%s" % (self._address, quote_plus(name)), parent = self, initial_run = False)
                setattr(self, pyattr(name), _resource)
                self._dict.__setitem__(name, _resource)
                self.__setitem__(name, _resource)
            return _res
        else:
            raise UnsupportedOperation("add")

    def __repr__(self):
        return f"Model({self._address}, Children={[ k for k in self._dict.keys()]})"

class Resource(dict):
    def __init__(self, connection: JbossConnection, child, address: str, parent: Model, initial_run = True):
        self._address = Addresses(address)
        self._connection = connection
        self._child = child
        self._parent = parent
        self._dict = {}

        # Recursively create any models below this resource
        for child in self._child['children']:
            if self._child['children'][child].get('model-description'):
                _child = Model(self._connection, self._child['children'][child], "%s/%s" % (self._address.str_address, child), initial_run)
                setattr(self, pyattr(child), _child)
                self._dict[child] = _child

        # Load dict
        super().__init__(**self._dict)
        
        self.attributes = ResourceAttributes(self)
        self.operations = ResourceOperations(self)

    def __repr__(self):
        return f"Resource({self._address.str_address}, {self.attributes}, Children={[ k for k in self._dict.keys()]})"

class Operation:
    def __init__(self, name: str, child: Resource, op_prop: dict):
        self._name = name
        self._connection = child._connection
        self._address = child._address
        self._doc = op_prop['description']
        self._props = list(op_prop['request-properties'].keys())
        self._op_prop = op_prop
        self._child = child
        self._parent = child._parent

    def __call__(self, **kwargs):
        log.debug(f"Running operation '{self._name} with kwargs: {kwargs}")
        res = Call(self._connection, Payload(self._address, self._name, **{ k.replace("_", "-"): kwargs.get(k) for k in kwargs }))
        if self._name == 'remove' and res.success:
            delattr(self._parent, self._address.str_address.split("=")[-1])
            self._parent._dict.__delitem__(self._address.str_address.split("=")[-1])
            self._parent.__delitem__(self._address.str_address.split("=")[-1])
        return res
    
    @property
    def __doc__(self):
        return self._doc
    
    def __repr__(self):
        return f"Operation(name={self._name}, kwargs={self._props})"