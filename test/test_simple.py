import pytest
import hana

#TODO: test absolute paths
#TODO: test relative paths
def test_validation():
    with pytest.raises(hana.errors.HanaMissingSourceDirectoryError):
        b = hana.Hana(source=None)

    with pytest.raises(hana.errors.HanaMissingOutputDirectoryError):
        b = hana.Hana(source='test/simple', output=None)

def test_simple():
    b = hana.Hana(
        source='test/simple',
        output='test/out'
    )

    b.build(clean=True)

def test_plugins():
    plugin_executed = {}

    def plugin(files, hana):
        plugin_executed['executed'] = True

    b = hana.Hana(
        source='test/simple',
        output='test/out',
        plugins=[
            plugin
        ]
    )

    b.build(clean=True)

    assert(plugin_executed)

