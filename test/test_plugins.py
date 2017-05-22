import pytest
import hana
import hana.plugins

def test_front_matter():

    def plugin(files, hana):
        assert(files['index.html'].metadata == {'key': 'value'})
        assert(files['index.html'].contents == 'a')

    b = hana.Hana(
        source='test/simple',
        output='test/out',
        plugins=[
            hana.plugins.front_matter,
            plugin
        ]
    )

    b.build(clean=True)


def test_metadata():

    def plugin(files, hana):
        for f in files.itervalues():
            assert(f.metadata == {'foo': 'bar'})

    b = hana.Hana(
        source='test/simple',
        output='test/out',
        plugins=[
            hana.plugins.metadata({'foo': 'bar'}),
            plugin
        ]
    )

    b.build(clean=True)


def test_ignore():

    b = hana.Hana(
        source='test/simple',
        output='test/out',
        plugins=[
            hana.plugins.ignore(['ignoreme']),
        ]
    )

    b.build(clean=True)

    assert('ignoreme' not in b.files)



