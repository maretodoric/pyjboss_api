### BELOW ARE HELPERS / ALIASES TO OPERATION VALUES TO PASS IN Payload
ADD = "add"
READ_RESOURCE = "read-resource"

def WRITE_ATTRIBUTE(name: str, value):
    return {"operation": "write-attribute", "name": name, "value": value}

def READ_ATTRIBUTE(name: str):
    return {"operation": "read-attribute", "name": name}
