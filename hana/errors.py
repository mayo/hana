
class HanaError(Exception): pass
class HanaMissingSourceDirectoryError(HanaError): pass
class HanaMissingOutputDirectoryError(HanaError): pass
class HanaPluginError(HanaError): pass
