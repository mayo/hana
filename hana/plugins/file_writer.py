import codecs
from hana.errors import HanaPluginError
import logging
import os
import shutil


class FileWriter():
    def __init__(self, deploy_path, clean=False):
        self._deploy_path = deploy_path
        self.clean = clean
        self.logger = logging.getLogger(self.__module__)

        if not os.path.isdir(self._deploy_path):
            raise DeployDirectoryError()

    def _clean_output_dir(self):
        #TODO: see if we can avoid removing the dir itself
        shutil.rmtree(self._deploy_path)
        self._create_output_dir()

    def _create_output_dir(self):
        os.mkdir(self._deploy_path)

    def __call__(self, files, hana):
        if self.clean and os.path.isdir(self._deploy_path):
            self._clean_output_dir()

        if not os.path.isdir(self._deploy_path):
            self._create_output_dir()

        for filename, f in files:
            output_path = os.path.join(self._deploy_path, filename)

            def makedirs(path, dir):
                if not dir:
                    return

                if os.path.isdir(os.path.join(self._deploy_path, path, dir)):
                    return

                makedirs(*os.path.split(path))

                if os.path.isdir(os.path.join(self._deploy_path, path)) or path == '':
                    dirpath = os.path.join(self._deploy_path, path, dir)
                    os.mkdir(dirpath)
                    return

            makedirs(*os.path.split(os.path.dirname(filename)))

            self.logger.debug('Writing {} ({})'.format(output_path, 'binary' if f.is_binary else 'text'))
            if not f.is_binary:
                codecs.open(output_path, 'w', 'utf-8').write(f['contents'])
            else:
                open(output_path, 'wb').write(f['contents'])



class FileLoaderError(HanaPluginError): pass
class DeployDirectoryError(FileLoaderError): pass


