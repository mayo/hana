import codecs
import datetime
import hashlib
import itertools
import logging
import os.path
import sys
import yaml

import pathspec
import pkg_resources

from hana import errors

class Hana(object):

    def __init__(self, configuration=None, metadata=dict()):
        self._setup_logging()

        self.logger = logging.getLogger(self.__module__)

        self.config = {}
        self.metadata = metadata

        # Load configuration first, any parameters override config
        if configuration:
            self.config = self._load_configuration(configuration)

        self._process_config()

        self.plugins = []

        self.files = FileSet()

    def _setup_logging(self):
        logger = logging.getLogger('hana')
        if not logger.handlers:
            formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")

            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)

    def _load_configuration(self, config_file):
        self.logger.info('Loading configuration from "%s"', config_file)
        return yaml.safe_load(open(config_file))

    def _process_config(self):
        # Logging
        logging_cfg = self.config.get('logging')
        if logging_cfg:
            for logger_name, logger_config in logging_cfg.items():
                level = logger_config.get('level').upper()
                logging.getLogger(logger_name).setLevel(level)
                self.logger.debug('Setting %s log level to: %s', logger_name, level)

        # Metadata
        metadata = self.config.get('metadata')
        if metadata:
            self.metadata.update(metadata)

        # Plugins
        plugins_directory = self.config.get('plugins_directory')
        if plugins_directory:
            abs_plugins_dir = os.path.abspath(plugins_directory)

            if not os.path.isdir(abs_plugins_dir):
                raise errors.InvalidPluginsDirectory()

            sys.path.insert(0, abs_plugins_dir)
            #self._setup_plugins(plugins_directory)

        build_steps = self.config.get('build')
        if build_steps:
            plugins = set([])

            for plugin in build_steps:
                if isinstance(plugin, str):
                    plugins.add(plugin)

                elif isinstance(plugin, dict):
                    plugins.add(next(iter(plugin)))

                else:
                    #TODO: plugin error
                    raise RuntimeError('Invalid plugin configuration')

            self._load_plugins(plugins)


    def _load_plugins(self, plugins):
        self.logger.info('Loading plugins')

        plugins = set(plugins)

        for plugin in plugins:
            self.load_plugin(plugin)


    def load_plugin(self, plugin):
        parts = plugin.split(':', 1)
        module_path = None
        import_name = None

        if len(parts) < 2:
            module_path = parts[0]
            import_name = parts[0].split('.')[-1]
        else:
            module_path, import_name = parts

        try:
            self.logger.info('Loading plugin %s from %s', import_name, module_path)
            mod = __import__(module_path, None, None, [import_name])
            return getattr(mod, import_name)
        except ImportError as err:
            self.logger.exception('Error loading plugin %s', plugin)
            raise RuntimeError("Couldn't load plugin {}".format(plugin))


    def plugin(self, plugin, pattern=None):
        if isinstance(pattern, str):
            pattern = [pattern]

        self.plugins.append((plugin, pattern))

    def build(self):
        self.metadata['_hana_build_time'] = datetime.datetime.utcnow()

        for plugin, patterns in self.plugins:
            filter = self.files.filter()

            if patterns:
                filter.patterns(*patterns)
            plugin(filter, self)

class FileSet(object):

    def __init__(self, parent=None):
        self._files = {}
        self._parent = parent

    def __iter__(self):
        #TODO: is this right? changed for py3
        return iter(self._files.items())

    def __len__(self):
        return len(self._files)

    def __contains__(self, filename):
        return filename in self._files

    def __getitem__(self, key):
        return self._files[key]

    def filenames(self):
        """Return all filenames
        """
        return self._files.keys()

    def filter(self):
        """Return FileSetFilter
        """
        return FileSetFilter(self)

    def add(self, filename, f):
        self._files[filename] = f

    def remove(self, filename):
        self._files.pop(filename)

    def rename(self, filename, new_name):
        self._files[new_name] = self._files.pop(filename)


class FileSetFilter(object):
    ORDER_ASC = 'asc'
    ORDER_DESC = 'desc'

    def __init__(self, file_set):
        self.file_set = file_set

        self._patterns = []
        self._metadata = []
        self._limit = None
        self._order = []

    def _flatten(self, mdlist):
        return set(itertools.chain(*mdlist))

    def __iter__(self):
        counter = 0
        files = self.file_set
        self._patterns = self._flatten(self._patterns)
        matcher = pathspec.PathSpec.from_lines('gitwildmatch', self._patterns)

        if self._order:
            #TODO: implement
            pass
            # files = sorted(files, ...)

        for filename, hfile in files:
            if self._limit and counter >= self._limit:
                # Limit reached, end iteration
                return

            if self._patterns and not matcher.match_file(filename):
                # If patterns defined and file doesn't match skip
                continue

            if self._metadata:
                skip = False
                for k, v in self._metadata:
                    if not k in hfile:
                        skip = True
                        continue

                    if not hfile[k] == v:
                        skip = True
                        continue

                if skip:
                    continue

            counter += 1
            yield filename, hfile

    def patterns(self, *patterns):
        # Check to allow arg expansion when it's empty
        if patterns:
            self._patterns.append(patterns)

        return self

    def metadata(self, key, value):
        #NOTE: simple metadata matching key:value supporting "and" when specified multiple times
        #TODO: implement "key between" (times, dates)
        #TODO: inplement "key contains value" (lists, dictionaries)
        #TODO: logic "key == x or key == y" etc.
        #TODO: more complex logic: [ [ 'title' == 'x' | title == 'y' ] & published_on < 1234 ]
        #                          [ [ KEY('title) == 'x' | KEY(title) == 'y' ] & 
        tup = key, value
        self._metadata.append(tup)

        return self

    def limit(self, limit=None):
        self._limit = limit
        return self

    def order(self, key, direction):
        #TODO: implement
        pass

class File(dict):

    def __init__(self, *args, **kwargs):
        super(File, self).__init__()
        super(File, self).update(*args, **kwargs)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, dict(self))

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
                                "got {:d}".format(len(args)))

            other = dict(args[0])

            for key in other:
                self[key] = other[key]

        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    def sha1sum(self):
        return self.hashsum(hashlib.sha1).hexdigest()

    def hashsum(self, hash_algo):
        if self.is_binary:
            return hash_algo(self['contents'])
        else:
            return hash_algo(codecs.encode(self['contents'], 'utf-8'))


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

        return super(FSFile, self).__getitem__(key)

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
                    if b'\0' in chunk:
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
        return '<{} {} {}>'.format(self.__class__.__name__, self.filename, dict(self))

