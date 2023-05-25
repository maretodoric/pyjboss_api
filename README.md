# pyjboss_api
This is python module that allows you to connect to WildFly api and read/write resources in more pythonic way. Inspired by rafaelbgil pyjboss (https://github.com/rafaelbgil/pyjboss).
Module is still work in progress and actual compatability is yet to be tested.

Tested Wildfly Versions:

| Version                           | Status    |
| --------------------------------- | --------- |
| wildfly-10.1.0.Final (Standalone) | Supported |
| wildfly-22.0.1.Final (Standalone) | Supported |

## Installation
Currently, module is only available from git, so to install from git, run following command.
```bash
pip3 install git+https://github.com/maretodoric/pyjboss_api
```

Alternatively, if you would like to run in Python Virtual Environment (recommended)
```bash
python3 -m venv pyjboss
cd pyjboss
source bin/activate
pip3 install git+https://github.com/maretodoric/pyjboss_api
```

## Usage

### Importing module
Import JbossConnection class from module
```python
from pyjboss_api import JbossConnection
```

### Making connection to WIldfly API
Make connection to Wildfly API. Module supports plan http and https with option to ignore SSL validation (for self-signed certificates).
JbossConnection class accepts two required positional arguments which are username and password, and additional arguments for IP Address/Hostname, port, SSL or SSL Verification. Below are few examples.
```python
# If Wildfly is running locally
jboss = JbossConnection('username', 'password')

# Connect to Wildfly running remotely
jboss = JbossConnection('username', 'password', address='192.168.0.100')

# ... If https is used
jboss = JbossConnection('username', 'password', address='192.168.0.100', ssl=True)

# ... If self-signed certificate is used and you would wish to ignore it
jboss = JbossConnection('username', 'password', address='192.168.0.100', ssl=True, ssl_verify=False)

# In case Wildfly management interface is listening on port other than 9990, use 'port' argument
jboss = JbossConnection('username', 'password', port=9993)
```

When initially making connection and if connection is remote, it may take some time for it to establish. This is due to initial calls to Wildfly API to determine list of resources, their models and values as everything is built recursively upon establishing connection.

### Making changes
When using jboss-cli to make adjustments, traditionally you specify address and operation like this:

```bash
bash jboss-cli.sh --command="/subsystem=logging/periodic-rotating-file-handler=FILE:write-attribute(name=suffix,value='.yyyy-MM-dd-HH')"
```

So first part, before colon (`:`) is path to a resource, then we have operation name we want to execute under that resource and in parenthesis we have arguments to operation.

In python, with this module, you can do it in few ways
```python
# Using attribute-based path
jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE.attributes['suffix'] = '.yyyy-MM-dd-HH'

# Using dictionary-based path
jboss.root['subsystem']['logging']['periodic-rotating-file-handler']['FILE'].attributes['suffix'] = '.yyyy-MM-dd-HH'

# Using operation function - you can reach the operation same way as dict-based above
jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE.operations.write_attribute(name="suffix", value=".yyyy-MM-dd-HH")

# Using Call, Addresses and Payload helpers to manually form payload - Call, Addresses and Payload will be explained later
from pyjboss_api.core import Call
from pyjboss_api.helpers import Addresses, Payload
Call(jboss, Payload("/subsystem=logging/periodic-rotating-file-handler=FILE", "write-attribute", name="suffix", value=".yyyy-MM-dd-HH"))
```

As you may have noticed, difference between attribute-based path and dictionary-based path is that dict-based retains native wildfly path names, while attribute-based is easier in case you're writing code from interactive terminal as it supports auto-completion and all dashes (`-`) are converted to underscores (`_`).

Also, if you're calling write_attribute function (write-attribute operation), you're required - just like in Wildfly interactive console or CLI - to specify name of attribute you're changing as well as it's value.

As for using Call, Addresses and Payload, in few cases when it's difficult to comprehand all the paths or there `might` be a bug somewhere in path (hopefully not), you can 'manually override' it by combining python functions with native Wildfly path and calls.

### Reading attributes
You can also get values from attributes same way as you would read any other attribute, just call it
```python
# Using attribute-based path
jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE.attributes['suffix']
# returns: '.yyyy-MM-dd-HH'

# Using dictionary-based path
jboss.root['subsystem']['logging']['periodic-rotating-file-handler']['FILE'].attributes['suffix'] = '.yyyy-MM-dd-HH'
# returns: '.yyyy-MM-dd-HH'

# Using operation function - you can reach the operation same way as dict-based above
jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE.operations.read_attribute(name='suffix')
# returns instance of Call class containing result - will be explained in next example

# Using Call, Addresses and Payload helpers to manually form payload - Call, Addresses and Payload will be explained later
from pyjboss_api.core import Call
from pyjboss_api.helpers import Addresses, Payload
res = Call(jboss, Payload("/subsystem=logging/periodic-rotating-file-handler=FILE", "read-attribute", name="suffix"))
res.success # Contains boolean value representing if call was successful or not - same reply you would get when calling from jboss-cli
res.result # Contains result from previous operation, in our case: '.yyyy-MM-dd-HH'
res.reload_required # Contains boolean value representing if Wildfly server needs to be reloaded
res # Just calling result of Call class, you get some descripting info about it, example: JbossResult(success=True,result=.yyyy-MM-dd-HH,reload_required=False)
```

### Reading resource
As you might've guessed it, due to some resources have `operations` attribute, you can access operation `read-resource` (or `read_resource` in python) which will allow you to get that resource and everything underneath it. You might want this in order to programatically search for specific settings that you may want to change.
```python
# Command below returns instance of Call class, which as previously discussed contains if call was successfully executed as well as result
res = jboss.root.subsystem.logging.operations.read_resource()
res.result # would return something like:
# {'add-logging-api-dependencies': True, 'use-deployment-logging-config': True, 'async-handler': None, 'console-handler': {'CONSOLE': None}, 'custom-formatter': None, 'custom-handler': None, 'file-handler': None, 'log-file': {'server.log': None, 'server.log.2023-03-07T13': None, 'server.log.2023-03-08T11': None, 'server.log.2023-03-08T12': None, 'server.log.2023-03-08T13': None, 'server.log.2023-03-08T14': None, 'server.log.2023-03-08T15': None, 'server.log.2023-03-08T16': None, 'server.log.2023-03-08T23': None, 'server.log.2023-03-09T00': None, 'server.log.2023-03-09T13': None, 'server.log.2023-03-09T14': None, 'server.log.2023-03-09T16': None, 'server.log.2023-03-10T16': None, 'server.log.2023-03-11T17': None, 'server.log.2023-03-11T22': None, 'server.log.2023-03-13T16': None, 'server.log.2023-05-22T16': None}, 'logger': {'org.jboss.as.config': None, 'sun.rmi': None, 'com.zentity.gateway.api.security.LoggingFilter': None, 'org.apache.http.wire': None, 'PoolingHttpClientConnectionManager': None, 'com.arjuna': None}, 'logging-profile': None, 'pattern-formatter': {'PATTERN': None, 'COLOR-PATTERN': None}, 'periodic-rotating-file-handler': {'FILE': None}, 'periodic-size-rotating-file-handler': None, 'root-logger': {'ROOT': None}, 'size-rotating-file-handler': None, 'syslog-handler': None}

# You can also pass arguments to operation, for example to recursively get resource:
res = jboss.root.subsystem.logging.operations.read_resource(recursive=True)
# res = {'add-logging-api-dependencies': True, 'use-deployment-logging-config': True, 'async-handler': None, 'console-handler': {'CONSOLE': {'autoflush': True, 'enabled': True, 'encoding': None, 'filter': None, 'filter-spec': None, 'formatter': '%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n', 'level': 'INFO', 'name': 'CONSOLE', 'named-formatter': 'COLOR-PATTERN', 'target': 'System.out'}}, 'custom-formatter': None, 'custom-handler': None, 'file-handler': None, 'log-file': None, 'logger': {'org.jboss.as.config': {'category': 'org.jboss.as.config', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'DEBUG', 'use-parent-handlers': True}, 'sun.rmi': {'category': 'sun.rmi', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'WARN', 'use-parent-handlers': True}, 'com.zentity.gateway.api.security.LoggingFilter': {'category': 'com.zentity.gateway.api.security.LoggingFilter', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'DEBUG', 'use-parent-handlers': True}, 'org.apache.http.wire': {'category': 'org.apache.http.wire', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'DEBUG', 'use-parent-handlers': True}, 'PoolingHttpClientConnectionManager': {'category': 'PoolingHttpClientConnectionManager', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'DEBUG', 'use-parent-handlers': True}, 'com.arjuna': {'category': 'com.arjuna', 'filter': None, 'filter-spec': None, 'handlers': None, 'level': 'WARN', 'use-parent-handlers': True}}, 'logging-profile': None, 'pattern-formatter': {'PATTERN': {'color-map': None, 'pattern': '%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n'}, 'COLOR-PATTERN': {'color-map': None, 'pattern': '%K{level}%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n'}}, 'periodic-rotating-file-handler': {'FILE': {'append': True, 'autoflush': True, 'enabled': True, 'encoding': None, 'file': {'path': 'server.log', 'relative-to': 'jboss.server.log.dir'}, 'filter': None, 'filter-spec': None, 'formatter': '%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n', 'level': 'ALL', 'name': 'FILE', 'named-formatter': 'PATTERN', 'suffix': '.yyyy-MM-dd-HH'}}, 'periodic-size-rotating-file-handler': None, 'root-logger': {'ROOT': {'filter': None, 'filter-spec': None, 'handlers': ['CONSOLE', 'FILE'], 'level': 'INFO'}}, 'size-rotating-file-handler': None, 'syslog-handler': None}
```

### Creating resource
Some paths support creating a resource, like in previous example our `periodic-rotating-file-handler` logging handler. If you wish to add such resource (handler in our case) you can do so like this
```python
jboss.root.subsystem.logging.periodic_rotating_file_handler.add("FILE_TWO")
```

Actually, above example **WILL FAIL**! But will not raise exception! Why? Because you want to see what failed. Let's grab result into a variable and read it
```python
res = jboss.root.subsystem.logging.periodic_rotating_file_handler.add("FILE_TWO")
res.result
# Returns something like: 'WFLYCTL0155: file may not be null'
```

This gives us information that we need to add some arguments in order to create this resource, let's try that
```python
res = jboss.root.subsystem.logging.periodic_rotating_file_handler.add("FILE_TWO", file="server_two.log")
res.result
# Returns in this case: 'WFLYCTL0097: Wrong type for file. Expected [OBJECT] but was STRING'
```

This errors tells us that we used string (server_two.log) for `file` attribute when it should be object. When looking at Wildfly documentation, we see that `file` attribute should be a dict (or `object`) containing `relative-to` and `path` attributes with `path` being required one. Another required argument needs to be `suffix` so we should apply that too. So in ordeer to properly create our `FILE_TWO` we need to run following:
```python
res = jboss.root.subsystem.logging.periodic_rotating_file_handler.add('FILE_TWO', file={'path': 'server_two.log'}, suffix='.yyyy-MM-dd')
res.success # Returns True
res.result # Returns None as expected
```

### Removing resource
Some resources can be removed from a model, like example above - `FILE_TWO` handler for `periodic-rotating-file-handler` model. We can do it like this
```python
jboss.root.subsystem.logging.periodic_rotating_file_handler.FILE_TWO.operations.remove()
```
This will also remove `FILE_TWO` attribute from it's parent, so you won't be able to call it anymore (which removes possible confusion later on).
When removing resource, always use this approach as it removes the attribute from parent. Removing resource by simply using `Call` class would leave the attribute, hopefully that will be changed in future.

### Handling warnings
Sometimes when you make changes, some changes require you to restart or reload server. When this happens, warning will be raised displaying message wherever the code is executed from. Warnings are also raised when exception is occurred while running instance of `Call`. You can suppress the warning by doing one of following:
```python
import warnings

# To silent ALL warnings
from pyjboss_api.exceptions import PyJbossAPIWarnings
warnings.filterwarnings(action='ignore', category=PyJbossAPIWarnings)

# To silent warnings related to server reload
from pyjboss_api.exceptions import ReloadServer
warnings.filterwarnings(action='ignore', category=ReloadServer)

# To silent warnings related to exceptions raised while running a Call
from pyjboss_api.exceptions import CallRaisedException
warnings.filterwarnings(action='ignore', category=CallRaisedException)
```

## Classes explained
### Class: JbossConnection
Main class to initiate connection to Wildfly server

#### Parameters
| Name        | Type         | Description                                           | Default    |
| ----------- | ------------ | ----------------------------------------------------- | ---------- |
| username    | String       | Username used to authenticate with Wildfly API        | *required* |
| password    | String       | Password used to authenticate with Wildfly API        | *required* |
| address     | String       | IP Address or FQDN to connect to                      | localhost  |
| port        | Int          | Port used when connecting to                          | 9990       |
| ssl         | Boolean      | If we need to use **https** instead of **http**       | False      |
| ssl_verify  | Boolean      | Wheather to validate SSL Cert or not (if self-signed) | True       |

#### Attributes
| Name            | Description                                                             |
| --------------- | ----------------------------------------------------------------------- |
| address         | Final URL used for connection                                           |
| last_payload    | JSON string of previous payload that was executed                       |
| last_call       | Instance of `Call` class of previously run command                      |
| root            | Instance of `RootPath`, this is where all paths are recursively created |
| reload_required | Attribute holding a boolean value if server needs to be reloaded        |

#### Methods
| Name     | Arguments | Return Value | Description            |
| -------- | --------- | -------------| ---------------------- |
| reload() | None      | None         | Reloads Wildfly Server |

### Class: Call
This class is called every time some call to Wildfly API needs to be executed. It's nothing but a helper to run requests.post method and contains some attributes that hold values from a call.

#### Parameters
| Name        | Type                       | Description                                                                                                                                    | Default    |
| ----------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| client      | JbossConnection            | Instance of JbossConnection, this is needed since we extract address and credentials from it, as well as we save call to two of it's arguments | *required* |
| payload     | Union[dict, list, Payload] | Instance of Payload class helper or dict/list containing a payload                                                                             | *required* |

#### Attributes
| Name            | Description                                                                                                            |
| --------------- | ---------------------------------------------------------------------------------------------------------------------- |
| payload         | JSON String of payload used to run this call                                                                           |
| reload_required | Boolean value representing if server stated that the reload is required                                                |
| exception       | Exception class and all it's attributes **if** exception is raised during call                                         |
| request         | This is not available if exception is raised, otherwise contains response object from requests module of executed call |
| success         | Boolean value as a reply from Wildfly API indicating if call was successful, False if exception is raised              |
| result          | Result as a reply from Wildfly API, can be either string, bool, dict, list - depending on reply                        |

#### Methods
| Name                      | Arguments | Return Value                                      | Description                                                                         |
| ------------------------- | --------- | ------------------------------------------------- | ----------------------------------------------------------------------------------- |
| raise_for_status()        | None      | None                                              | Raises instance of `FailedApiCall` if attribute `success` is not `True`             |
| return_success_or_raise() | None      | Value from `success` attribute or raise exception | raise_for_status() internally, otherwise returns value from `success` argument      |
| return_result_or_raise()  | None      | Value from `result` attribute or raise exception  | Runs raise_for_status() internally, otherwise returns value from `result` argument  |

### Class: Addresses
This class is helper to form proper address payload or address string based on parameters provided. Number of parameters MUST be either 1 (string representing full path, example: `/subsystem=logging/`) or even number that can be used to form a path (example: `Addresses('subsystem', 'logging')`)

#### Attributes
| Name        | Description                                                                |
| ----------- | -------------------------------------------------------------------------- |
| addresses   | List of dict - that's the format Wildfly API accepts as a path to resource |
| str_address | String representing path like in native jboss-cli                          |

#### Methods
| Name                  | Arguments             | Return Value   | Description                                                                       |
| --------------------- | --------------------- | -------------- | --------------------------------------------------------------------------------- |
| add_path(dir, subdir) | Parts of address path | None           | Append directory (Model) and subdirectory (Resource) to current path              |
| get_jmespath_filter() | None                  | String         | Can be used as jmespath filter - used internally while recursively creating paths |
| to_dict()             | None                  | List[Dict]     | Returns list of dict in Wildfly API friendly format to use when making a call     |

#### Class: Payload
Helper class to form a json payload that is required to be send to Wildfly API

#### Parameters
| Name       | Type             | Description                                                                                                                 | Default    |
| ---------- | -----------------| --------------------------------------------------------------------------------------------------------------------------- | ---------- |
| address    | Union[Addresses, str, dict] | Accepts instance of Addresses or string/dict to form instance itself. If not passed, can be manually added later | None       |
| operation  | String                      | Name of operation that we need to execute                                                                        | *required* |
| \*\*kwargs | Union[dict, str]            | Key-Value pairs of arguments passed to operation that will be executed                                           | *required* |

#### Attributes
| Name        | Description                                              |
| ----------- | -------------------------------------------------------- |
| address   | As explained in parameters - holds the address for payload |
| operation | As explained in parameters - holds the name of operation   |
| payload   | Contains final payload (dict) that will be used            |