import pytest
from hana.core import FileSet, File

def test_add():
    fm = FileSet()

    assert len(fm) == 0

    file_a = File(contents='test file a', count=1)
    fm.add('file_a', file_a)

    assert len(fm) == 1

def test_remove():
    fm = FileSet()

    assert len(fm) == 0

    file_a = File(contents='test file a', count=1)
    fm.add('file_a', file_a)

    assert len(fm) == 1

    fm.remove('file_a')

    assert len(fm) == 0

def test_rename():
    fm = FileSet()

    file_a = File(contents='test file a', count=1)
    fm.add('file_a', file_a)

    fm.rename('file_a', 'file_b')

    assert 'file_b' in fm
    assert 'file_a' not in fm

def test_getitem():
    fm = FileSet()
    file_a = File(contents='test file a', count=1)
    fm.add('file_a', file_a)

    fm['file_a'] == file_a


def test_subset_access():
    fm = FileSet()

    fm.add('file_a', File(contents='test file a', count=1))
    fm.add('file_b', File(contents='test file b', count=1))

    fm_sub = fm.filter(['*_a'])

    fm_sub['file_a']['count'] += 1

    assert fm['file_a']['count'] == 2
    assert fm['file_b']['count'] == 1


def test_subset_add():
    fm = FileSet()

    file_b = File(contents='test file b', count=1)
    file_c = File(contents='test file c', count=1)

    fm.add('file_a', File(contents='test file a', count=1))
    fm.add('file_b', file_b)

    fm_sub = fm.filter(['*_a'])

    fm_sub.add('file_c', file_c)

    assert 'file_b' not in fm_sub
    assert 'file_c' in fm_sub
    assert 'file_c' in fm

