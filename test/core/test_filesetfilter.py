import pytest
from hana.core import File, FileSet, FileSetFilter
from hana.metadata import MD

@pytest.mark.parametrize('patterns', [
    ['*'],
    ['blog/**', '*'],
    ['*', 'blog/**', '*'],
])
def test_pattern(patterns):

    fsf = FileSetFilter(FileSet())
    fsf.patterns(*patterns)

    assert fsf._patterns == set(patterns)

def test_patterns():
    patterns = ['*', 'blog/**', '*']

    fsf = FileSetFilter(FileSet())
    fsf.patterns(patterns[1])
    fsf.patterns(*patterns[1:])

    assert fsf._patterns == set(patterns)

@pytest.mark.parametrize('limit', [0, 1, 2, 3, 4])
def test_limit(limit):

    fs = FileSet()
    fs.add('a', File())
    fs.add('b', File())
    fs.add('c', File())

    fsf = FileSetFilter(fs)

    res = list(fsf.limit(limit))

    #Limit of 0 is no limit
    if limit >= 1 and limit <= len(fs):
        assert len(res) == limit

    else:
        assert len(res) == len(fs)

def test_pattern_limit():

    fs = FileSet()
    fs.add('file_a', File())
    fs.add('test_b', File())
    fs.add('test_c', File())

    fsf = FileSetFilter(fs)

    res = dict(fsf.patterns('test_*').limit(1))

    assert len(res) == 1

    filename = list(res.keys())[0]

    assert filename.startswith('test_')


def test_metadata_top():

    fs = FileSet()
    fs.add('file_a', File())
    fs.add('file_b', File(title='x'))
    fs.add('file_c', File(title='y', nested={'key': 'value'}))

    fsf = FileSetFilter(fs)

    res = dict(fsf.metadata(MD['nested']['key'] == 'value'))

    assert len(res) == 1

    filename = list(res.keys())[0]

    assert filename.startswith('file_c')


def test_metadata_nested():

    fs = FileSet()
    fs.add('file_a', File())
    fs.add('file_b', File(title='x'))
    fs.add('file_c', File(title='y', nested={'key': 'value'}))

    fsf = FileSetFilter(fs)


    res = dict(fsf.metadata(MD['title'] == 'x'))

    assert len(res) == 1

    filename = list(res.keys())[0]

    assert filename.startswith('file_b')



def test_metadata_limit():

    fs = FileSet()
    fs.add('file_a', File())
    fs.add('file_b', File(title='x'))
    fs.add('file_c', File(title='x'))

    fsf = FileSetFilter(fs)

    res = dict(fsf.metadata(MD('title') == 'x').limit(1))

    assert len(res) == 1

#def test_order():
#    assert 0
#
#
#def test_order_limit():
#    assert 0
#
#
#def test_metadata_order():
#    assert 0
#
#
#def test_metadata_order_limit():
#    assert 0


