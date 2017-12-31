
class HanaError(Exception):
    pass

class HanaPluginError(HanaError):
    pass

class InvalidPluginsDirectory(HanaError):
    pass

class PluginNotFoundError(HanaPluginError):
    pass
