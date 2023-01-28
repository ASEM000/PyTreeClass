import copy
import dataclasses as dc

import jax.tree_util as jtu
import numpy.testing as npt
import pytest
from jax import numpy as jnp

import pytreeclass as pytc
from pytreeclass._src.tree_freeze import _set_dataclass_frozen


def test_field():

    with pytest.raises(ValueError):
        pytc.field(default=1, default_factory=lambda: 1)

    assert pytc.field(default=1).default == 1


def test_field_nondiff():
    @pytc.treeclass
    class Test:
        a: int = 1
        b: int = 2
        c: int = 3

    test = Test()

    @pytc.treeclass
    class Test:
        a: jnp.ndarray = jnp.array([1, 2, 3])
        b: jnp.ndarray = jnp.array([4, 5, 6])

    test = Test()

    @pytc.treeclass
    class Test:
        a: jnp.ndarray = pytc.field(nondiff=True, default=jnp.array([1, 2, 3]))
        b: jnp.ndarray = pytc.field(nondiff=True, default=jnp.array([4, 5, 6]))

    test = Test()

    assert jtu.tree_leaves(test) == []

    @pytc.treeclass
    class Test:
        a: jnp.ndarray = pytc.field(nondiff=True, default=jnp.array([1, 2, 3]))
        b: jnp.ndarray = jnp.array([4, 5, 6])

    test = Test()
    npt.assert_allclose(jtu.tree_leaves(test)[0], jnp.array([4, 5, 6]))


def test_hash():
    @pytc.treeclass
    class T:
        a: jnp.ndarray

    # with pytest.raises(TypeError):
    hash(T(jnp.array([1, 2, 3])))


def test_post_init():
    @pytc.treeclass
    class Test:
        a: int = 1

        def __post_init__(self):
            self.a = 2

    t = Test()

    assert t.a == 2


def test_subclassing():
    @pytc.treeclass
    class L0:
        a: int = 1
        b: int = 3
        c: int = 5

        def inc(self, x):
            return x

        def sub(self, x):
            return x - 10

    @pytc.treeclass
    class L1(L0):
        a: int = 2
        b: int = 4

        def inc(self, x):
            return x + 10

    l1 = L1()

    assert jtu.tree_leaves(l1) == [2, 4, 5]
    assert l1.inc(10) == 20
    assert l1.sub(10) == 0


def test_registering_state():
    @pytc.treeclass
    class L0:
        def __init__(self):
            self.a = 10
            self.b = 20

    t = L0()
    tt = copy.copy(t)

    assert tt.a == 10
    assert tt.b == 20


def test_copy():
    @pytc.treeclass
    class L0:
        a: int = 1
        b: int = 3
        c: int = 5

    t = L0()

    assert copy.copy(t).a == 1
    assert copy.copy(t).b == 3
    assert copy.copy(t).c == 5


def test_delattr():
    @pytc.treeclass
    class L0:
        a: int = 1
        b: int = 3
        c: int = 5

    t = L0()

    with pytest.raises(dc.FrozenInstanceError):
        del t.a

    @pytc.treeclass
    class L2:
        a: int = 1

        def delete(self, name):
            del self.a

    t = L2()
    t = _set_dataclass_frozen(t, False)
    t.delete("a")

    t = _set_dataclass_frozen(t, True)
    with pytest.raises(dc.FrozenInstanceError):
        t.delete("a")
