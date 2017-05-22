#!/usr/bin/env python

import os
import shutil

from hana import errors

#TODO: build in file watcher, server... hana-level plugins, as opposed to processing plugins?

class Hana():

    def __init__(self, configuration=None, source=None, output=None, plugins=[], file_loader=None):
        # Load configuration first, any parameters override config
        if configuration:
            self._load_configuration(configuration)

        self._source = source
        self._output = output
        self._file_loader = file_loader

        if file_loader:
            self._file_loader = file_loader
        else:
            self._file_loader = FileSystemLoader(self._source)

        # Validate configuration
        self._validate_configuration()

        self.files = {}
        self.plugins = plugins

    def _load_configuration(config_file):
        #TODO: load config
        pass

    def _validate_configuration(self):
        if not self._source or not os.path.isdir(self._source):
            raise errors.HanaMissingSourceDirectoryError()

        if not self._output or not os.path.isdir(self._output):
            raise errors.HanaMissingOutputDirectoryError()

    #TODO: should we support filter natively?
    def use(self, plugin):
        self.plugins.append(plugin)

        return self

    def build(self, clean=False):
        if clean:
            self._clean_output_dir()

        self._find_files()

        self._process()

        self._write()


    def _clean_output_dir(self):
        shutil.rmtree(self._output)
        os.mkdir(self._output)

    def _find_files(self):
        self.files = self._file_loader.get_files()


    def _process(self):
        for plugin in self.plugins:
            plugin(self.files, self)

    def _write(self):
        for filename, f in self.files.iteritems():
            output_path = os.path.join(self._output, filename)

            def makedirs(path, dir):
                if not dir:
                    return

                if os.path.isdir(os.path.join(path, dir)):
                    return

                if os.path.isdir(path) or path == '':
                    dirpath = os.path.join(self._output, path, dir)
                    os.mkdir(dirpath)
                    return

                makedirs(*os.path.split(path))

            makedirs(*os.path.split(os.path.dirname(filename)))

            open(output_path, 'w').write(f.contents)

class FileSystemLoader():
    def __init__(self, source_path):
        self._source_path = source_path

    def get_files(self):
        out_files = {}

        for path, dirs, files in os.walk(self._source_path):
            for f in files:
                source = os.path.join(path, f)
                filepath = os.path.relpath(source, self._source_path)

                out_files[filepath] = File(source)

        return out_files


class File():

    def __init__(self, source_file):
        self.metadata = {}

        self._source_file = source_file
        self._contents = None

    @property
    def contents(self):
        if self._contents is None:
            self._contents = open(self._source_file).read()

        return self._contents

    def __repr__(self):
        return self._source_file

