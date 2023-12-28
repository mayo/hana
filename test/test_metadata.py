import re
import pytest

from hana.metadata import MD


def test_md_init():

    mdk = MD("mykey")

    assert mdk.name == ("mykey",)

    mdk = MD(("mykey","two"))

    assert mdk.name == ("mykey", "two")

def test_md_implicit():

    assert MD.mykey.name == ("mykey",)

    mdk = MD.mykey == 5

    assert mdk.name == ("mykey",)
    assert mdk.value == 5

def test_key():
    mdk = MD['test']

    assert mdk.name == ('test',)

    mdk = MD['test']['this']

    assert mdk.name == ('test', 'this')

def test_md_eval_eq():
    mdk = MD.mykey == 5

    assert mdk.eval(5) == True
    assert mdk.eval(6) == False

def test_md_eval_in():

    mdk = MD.mykey.in_("asd")

    assert mdk.eval("d") == True
    assert mdk.eval("f") == False

    mdk = MD.mykey.in_([1,2,3])

    assert mdk.eval(1) == True
    assert mdk.eval(3) == True
    assert mdk.eval(5) == False

def test_md_eval_nin():

    mdk = MD.mykey.nin("asd")

    assert mdk.eval("d") == False
    assert mdk.eval("f") == True

    mdk = MD.mykey.nin([1,2,3])

    assert mdk.eval(3) == False
    assert mdk.eval(5) == True

def test_md_eval_startswith():

    mdk = MD.mykey.startswith("as")

    assert mdk.eval("asd") == True
    assert mdk.eval("fgh") == False

def test_md_eval_match():

    mdk = MD.mykey.match(r"a.+", re.I)

    assert mdk.eval("a") == False
    assert mdk.eval("as") == True
    assert mdk.eval("As") == True

    mdk = MD.mykey.match(r"[0-9]", re.I)

    assert mdk.eval("a") == False
    assert mdk.eval(1) == True

