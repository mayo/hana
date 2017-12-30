import codecs
from hana import errors
import importlib
import logging
import pathspec
import pkg_resources
import sys
import yaml

#TODO: this probably shouldn't be here
root_logger = logging.getLogger()

if not root_logger.handlers:
    root_logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)


class Hana():

    def __init__(self, configuration=None):
        self.logger = logging.getLogger(self.__module__)

        # Load configuration first, any parameters override config
        if configuration:
            self._load_configuration(configuration)

        # Validate configuration
        self._validate_configuration()

        self.plugins = []
        self.metadata = {}

        self.files = FileSet()

    def _load_configuration(self, config_file):
        self.logger.info('Loading configuration from "{}"'.format(config_file))
        config = yaml.safe_load(open(config_file))

        if 'plugin_path' in config:
            #TODO: add plugin path on path
            pass

        plugins = config.get('plugins')
        if plugins:
            self._load_plugins(plugins)

    def _validate_configuration(self):
        #TODO
        pass

    def _load_plugins(self, plugins):
        self.logger.info('Loading plugins')
        target = None
        package = None

        # Collect all entrypoints for plugins
        available_plugins = { e.name: e for e in pkg_resources.iter_entry_points(group='hana.plugins') }

        # Collect configured plugins
        wanted_plugins = set([ p.keys()[0] for p in plugins ])

        # Fail early for missing plugins
        missing_plugins = wanted_plugins - set(available_plugins.keys())
        if missing_plugins:
            raise errors.PluginNotFoundError('Missing plugins: "{}" not found'.format(missing_plugins))

        # Iterate plugins and make new instances
        for plugin_spec in plugins:
            plugin_name, plugin_config = plugin_spec.items()[0]

            # Get the plugin callable
            plugin = available_plugins[plugin_name].load()

            # Initialize the plugin if requested or if parameters passed
            if plugin_config.get('init', False) or 'parameters' in plugin_config:
                plugin = plugin(**plugin_config.get('parameters'))

            self.plugin(plugin, plugin_config.get('patterns'))

    def plugin(self, plugin, pattern=None):
        if isinstance(pattern, str):
            pattern = [pattern]

        self.plugins.append((plugin, pattern))

    def build(self):
        self._process()

    def _process(self):
        for plugin, patterns in self.plugins:
            plugin(self.files.filter(patterns), self)

#TODO: fileset to make filtering more easier. Filter files based on glob pattern, so in plugins:
#files.filter(glob) returns iterator/generator with matches
#TODO: this is not ideal and error prone, as it sub-calls .add, etc. This should really return a proxy that's smart enough to iterate through matching items, rather than recursively call action methods.
class FileSet():

    def __init__(self, parent=None):
        self._files = {}
        self._parent = parent

    def __iter__(self):
        return self._files.iteritems()

    def __len__(self):
        return len(self._files)

    def __contains__(self, filename):
        return filename in self._files

    def __getitem__(self, key):
        return self._files[key]

    def filenames(self):
        """Return all filenames
        """

        return self._files.iterkeys()

    def filter(self, patterns):
        """Return FileSet with subset of files
        """

        if not patterns:
            return self

        fm = FileSet(self)

        match = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

        for filename, f in self:
            if match.match_file(filename):
                fm.add(filename, f)

        return fm

    #TODO: verify base path, resolve relative paths
    def add(self, filename, f):
        self._files[filename] = f

        if self._parent:
            self._parent.add(filename, f)

    #TODO: verify base path, resolve relative paths
    def remove(self, filename):
        self._files.pop(filename)

        if self._parent:
            self._parent.remove(filename)

    def rename(self, filename, new_name):
        self._files[new_name] = self._files.pop(filename)

        if self._parent:
            self._parent.rename(filename, new_name)

#TODO: finish me
class FileSetProxy(object):
    def __init__(self, file_manager, patterns):
        self._file_manager = file_manager
        self._patterns = patterns



class File(dict):

    def __init__(self, *args, **kwargs):
        super(File, self).update(*args, **kwargs)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict(self))

    @property
    def is_binary(self):
        # If we don't have any content, treat it as binary and try to do detection later
        if not self['contents']:
            return True

        return '\0' in self['contents']

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))

            other = dict(args[0])

            for key in other:
                self[key] = other[key]

        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]


class FSFile(File):

    def __init__(self, filename, *args, **kwargs):
        super(FSFile, self).__init__(*args, **kwargs)

        if not filename:
            raise

        self._is_binary = None
        self.loaded = False
        self.filename = filename

    def __getitem__(self, key):
        if key == 'contents' and not self.loaded:
            self._get_contents()

        return super(File, self).__getitem__(key)

    # Override is_binary to avoid loading files unnecesarily
    @property
    def is_binary(self):
        # If the file is already loaded, it may have been processed
        if self.loaded:
            #TODO: call super.is_binary?
            self._is_binary = None
            return '\0' in self['contents']

        if self._is_binary is None:
            with open(self.filename, 'rb') as fin:
                CHUNKSIZE = 1024

                while True:
                    chunk = fin.read(CHUNKSIZE)
                    if '\0' in chunk:
                        self._is_binary = True
                        break

                    if len(chunk) < CHUNKSIZE:
                        break

                    self._is_binary = False

        return self._is_binary

    def _get_contents(self):
        if self.is_binary:
            self['contents'] = open(self.filename, 'rb').read()

        else:
            self['contents'] = codecs.open(self.filename, 'r', 'utf-8').read()

        self.loaded = True

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.filename, dict(self))

