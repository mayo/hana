#!/usr/bin/env python

import codecs
import os
import shutil
import pathspec

from hana import errors

#TODO: build in file watcher, server... hana-level plugins, as opposed to processing plugins?
#TODO: setup logging

class Hana():

    def __init__(self, configuration=None, output_directory=None):
        # Load configuration first, any parameters override config
        if configuration:
            self._load_configuration(configuration)

        self._output = output_directory

        # Validate configuration
        self._validate_configuration()

        self.files = {}
        self.plugins = []
        self.metadata = {}

    def _load_configuration(config_file):
        #TODO: load config
        pass

    def _validate_configuration(self):
        if not self._output or not os.path.isdir(self._output):
            raise errors.HanaMissingOutputDirectoryError()

    @ property
    def output(self):
        return self._output

    def plugin(self, plugin, pattern=None):
        if isinstance(pattern, str):
            pattern = [pattern]

        self.plugins.append((plugin, pattern))

    def build(self, clean=False):
        if clean:
            self._clean_output_dir()

        self._process()

        self._write()

    def _clean_output_dir(self):
        shutil.rmtree(self._output)
        os.mkdir(self._output)

    def _process(self):
        for plugin, patterns in self.plugins:
            files = self.files
            keys = None

            # Make a file subset
            if patterns:
                match = pathspec.PathSpec.from_lines('gitwildmatch', patterns).match_file
                files = { k:files[k] for k in files if match(k) }
                keys = set(files.keys())

            # Execute plugin with file subset
            plugin(files, self)

            # Update master file list
            #TODO: there has to be a better way
            if patterns:
                new_keys = set(files.keys())

                deleted_keys = keys - new_keys
                new_keys = new_keys - keys

                for k in deleted_keys:
                    del self.files[k]

                for k in new_keys:
                    self.files[k] = files[k]

    def _write(self):
        for filename, f in self.files.iteritems():
            output_path = os.path.join(self._output, filename)

            def makedirs(path, dir):
                if not dir:
                    return

                if os.path.isdir(os.path.join(self._output, path, dir)):
                    return

                makedirs(*os.path.split(path))

                if os.path.isdir(os.path.join(self._output, path)) or path == '':
                    dirpath = os.path.join(self._output, path, dir)
                    os.mkdir(dirpath)
                    return

            makedirs(*os.path.split(os.path.dirname(filename)))

            print 'w%s %s' % ('b' if f.is_binary else 't', output_path)
            if not f.is_binary:
                codecs.open(output_path, 'w', 'utf-8').write(f['contents'])
            else:
                open(output_path, 'wb').write(f['contents'])


#class FileSystemLoader():
#    def __init__(self, source_path):
#        self._source_path = source_path
#
#    def get_files(self):
#        out_files = {}
#
#        for path, dirs, files in os.walk(self._source_path):
#            for f in files:
#                source = os.path.join(path, f)
#                filepath = os.path.relpath(source, self._source_path)
#
#                out_files[filepath] = MetaFile(source)
#
#        return out_files


#TODO: fileset to make filtering more easier. Filter files based on glob pattern, so in plugins:
#files.filter(glob) returns iterator/generator with matches
#TODO: support dictionary/list-like iteration so behave like current implementation
class FileSet():

    def __init__(self, basepath):
        self.files = {}

    #def push
    #TODO: verify base path, resolve relative paths
    def add(self, f):
        pass

    #def pop
    #TODO: verify base path, resolve relative paths
    def remove(self, f):
        pass

    def __iter__(self):
        pass

#TODO: create source-less file that has _loaded set to true to avoid loading

# NEW NOTES AS OF Sept 13
# - there should be no such things as output_file. There should be source_file (if one is present) and filename, which is used for everything else. Initially, MetaFile that is source file backed will have filename set to source_file.

class MetaFile(dict):
    READ_ONLY_KEYS = [] #'filename']

    def __init__(self, filename, *args, **kwargs):
        self._is_binary = None

        kwargs['filename'] = filename

        super(MetaFile, self).update(*args, **kwargs)

        self._loaded = False

    def __setitem__(self, key, value):
        if key in MetaFile.READ_ONLY_KEYS:
            raise AttributeError('{} is a read only key'.format(key))

        #TODO: set _loaded when contents is assigned

        super(MetaFile, self).__setitem__(key, value)

    def __getitem__(self, key):
        if key == 'contents' and not self._loaded:
            self._get_contents()

        return super(MetaFile, self).__getitem__(key)

    def __hash__(self):
        return hash(self['filename'])

    @property
    def is_binary(self):
        #TODO: if source file is not defined, but we have content, use that instead of reading a file. If neither exists, treat it as binary
        #NOTE: once using contents, this should not be cached as contents can change on the fly
        if self._is_binary is None:

            with open(self['filename'], 'rb') as fin:
                CHUNKSIZE = 1024

                while 1:
                    chunk = fin.read(CHUNKSIZE)
                    if '\0' in chunk:
                        self._is_binary = True
                        break

                    if len(chunk) < CHUNKSIZE:
                        break

                    self._is_binary = False

        return self._is_binary

    def _get_contents(self):
        #TODO: raise if 'filename' is not defined
        print 'r%s %s' % ('b' if self.is_binary else 't', self['filename'])
        if self.is_binary:
            self['contents'] = open(self['filename'], 'r').read()
        else:
            self['contents'] = codecs.open(self['filename'], 'r', 'utf-8').read()

        self._loaded = True

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self['filename'], dict(self))

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

