import logging
import os

import pathspec

from hana.errors import HanaPluginError
from hana.core import FSFile

class FileLoader(object):
    def __init__(self, source_path, ignore_patterns=(), source_file_keyword=None):
        self._source_path = source_path
        self.ignore_patterns = ignore_patterns
        self.source_file_keyword = source_file_keyword
        self.logger = logging.getLogger(self.__module__)

        if not os.path.isdir(self._source_path):
            raise SourceDirectoryError()

    def __call__(self, files, hana):
        ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', self.ignore_patterns)

        for path, _, sfiles in os.walk(self._source_path):
            for f in sfiles:
                source = os.path.join(path, f)

                if ignore_spec.match_file(f):
                    continue

                filepath = os.path.relpath(source, self._source_path)

                if filepath in files:
                    raise FileExistsError("File {} already exists".format(filepath))

                metadata = {}

                if self.source_file_keyword:
                    metadata[self.source_file_keyword] = source

                files.add(filepath, FSFile(source, **metadata))

class FileLoaderError(HanaPluginError):
    pass

class FileExistsError(FileLoaderError):
    pass

class SourceDirectoryError(FileLoaderError):
    pass

