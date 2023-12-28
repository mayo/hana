import pytest
import hana
import hana.plugins.file_loader
import hana.plugins.file_writer

#TODO: test absolute paths
#TODO: test relative paths
def test_validation():
    with pytest.raises(hana.plugins.file_loader.SourceDirectoryError):
        b = hana.Hana()
        b.plugin(hana.plugins.file_loader.FileLoader(source_path='nonexistent_directory'))
        b.build()

def test_simple():
    b = hana.Hana()

    b.plugin(hana.plugins.file_loader.FileLoader(source_path='test/simple'))
    b.plugin(hana.plugins.file_writer.FileWriter(deploy_path='test/out'))

    b.build()

def test_simple_hash():
    def plugin(files, hana):
        for _, hfile in files:
            hfile.sha1sum()

    b = hana.Hana()

    b.plugin(hana.plugins.file_loader.FileLoader(source_path='test/simple'))
    b.plugin(hana.plugins.file_writer.FileWriter(deploy_path='test/out'))
    b.plugin(plugin)

    b.build()


def test_plugins():
    plugin_executed = {}

    def plugin(files, hana):
        plugin_executed['executed'] = True

    b = hana.Hana()
    b.plugin(plugin)
    b.build()

    assert(plugin_executed)

