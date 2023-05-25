class PyJbossAPIWarnings(Warning):
    pass

class ReloadServer(PyJbossAPIWarnings):
    pass

class CallRaisedException(PyJbossAPIWarnings):
    pass

class PyJbossException(Exception):
    pass

class EntryAlreadyExists(PyJbossException):
    def __init__(self, entry: object) -> None:
        arg = "%s already exists under %s" % (entry.name, entry.Address.str_address)
        super().__init__(arg)

class EntryMissing(PyJbossException):
    def __init__(self, entry: object) -> None:
        arg = "Resource under address: %s is mising." % (entry.Address.str_address)
        super().__init__(arg)

class FailedToAddEntry(PyJbossException):
    def __init__(self, entry: object, call: object) -> None:
        arg = "Failed to add %s to %s - %s" % (entry.__name__, entry.parent.name, call)
        super().__init__(arg)

class FailedApiCall(PyJbossException):
    def __init__(self, call: object):
        self.payload = call.payload
        self.result = call.result
        self.call = call
        arg = "Call with payload %s failed! Result: %s" % (call.payload, call.result)
        super().__init__(arg)

class MissingArgument(PyJbossException):
    def __init__(self, missing_arg_name: str):
        super().__init__("Missing required argument: %s" % missing_arg_name)

class MissingResourceDefinition(PyJbossException):
    def __init__(self, definition: str) -> None:
        arg = "Missing Resource definition. Please define resource with: '%s' variable." % definition
        super().__init__(arg)

class UnsupportedOperation(PyJbossException):
    def __init__(self, op: str) -> None:
        super().__init__(f"Unsupported operation '{op}' for this Directory/Resource")