from pyjboss_api.core import Call, JbossConnection
from pyjboss_api.helpers import Payload

print("Establishing jboss connection")
jboss = JbossConnection('management', 'ManagementUserPassword')

print("Checking 'allowed-users' attribute of ['core-service']['management']['security-realm']['ManagementRealm']['authentication']['local'] ")
jboss.root['core-service']['management']['security-realm']['ManagementRealm']['authentication']['local'].attributes['allowed-users']

print("Checking read_attribute() operation on name 'map-groups-to-roles' on path ['core-service']['management']['security-realm']['ManagementRealm']")
res: Call = jboss.root['core-service']['management']['security-realm']['ManagementRealm'].operations.read_attribute(name='map-groups-to-roles')
res.raise_for_status()

print("Checking add() operation with name 'NewManagementRealm' on path ['core-service']['management']['security-realm']")
res: Call = jboss.root['core-service']['management']['security-realm'].add('NewManagementRealm')
res.raise_for_status()

print("Checking remove() operation on path ['core-service']['management']['security-realm']['NewManagementRealm']")
res: Call = jboss.root['core-service']['management']['security-realm']['NewManagementRealm'].operations.remove()

print("Checking for 'append' value on path subsystem.logging.periodic_rotating_file_handler.FILE: ", end='')
res = jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE.attributes['append']
print(str(res))

print("Shutting down Wildfly")
res = Call(jboss, Payload([], "shutdown"))
res.raise_for_status()