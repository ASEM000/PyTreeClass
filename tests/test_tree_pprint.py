from __future__ import annotations

import functools as ft
import sys
from collections import namedtuple

# import jax
import jax.tree_util as jtu
import pytest
from jax import numpy as jnp

import pytreeclass as pytc
from pytreeclass import tree_diagram, tree_mermaid, tree_repr, tree_str, tree_summary

_msg = "Object sizes are changed for python 3.11 and above"


@ft.partial(pytc.treeclass, mask=True, index=True)
class Repr1:
    a: int = 1
    b: str = "string"
    c: float = 1.0
    d: tuple = "a" * 5
    e: list = None
    f: set = None
    g: dict = None
    h: jnp.ndarray = None
    i: jnp.ndarray = None
    j: jnp.ndarray = None
    k: tuple = pytc.field(repr=False, default=(1, 2, 3))
    l: namedtuple = namedtuple("a", ["b", "c"])(1, 2)
    m: jnp.array = jnp.ones((5, 5))
    n: jnp.array = jnp.array(True)
    o: jnp.array = jnp.array([1, 2.0], dtype=jnp.complex64)

    def __post_init__(self):
        self.h = jnp.ones((5, 1))
        self.i = jnp.ones((1, 6))
        self.j = jnp.ones((1, 1, 4, 5))

        self.e = [10] * 5
        self.f = {1, 2, 3}
        self.g = {"a": "a" * 50, "b": "b" * 50, "c": jnp.ones([5, 5])}


r1 = Repr1()
mask = jtu.tree_map(pytc.is_nondiff, r1)
r1f = r1.at[mask].apply(pytc.freeze)


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_repr():
    assert (
        tree_repr(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b='string', \n  c=1.0, \n  d='aaaaa', \n  e=[10, 10, 10, 10, 10], \n  f={1, 2, 3}, \n  g={\n    a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n    b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n    c:f32{5x5}∈[1.0,1.0]\n  }, \n  h=f32{5x1}∈[1.0,1.0], \n  i=f32{1x6}∈[1.0,1.0], \n  j=f32{1x1x4x5}∈[1.0,1.0], \n  l=namedtuple(b=1, c=2), \n  m=f32{5x5}∈[1.0,1.0], \n  n=bool{0}, \n  o=c64{2}\n)"
    )

    assert (
        tree_repr(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=#1, \n  b=#'string', \n  c=1.0, \n  d=#'aaaaa', \n  e=[#10, #10, #10, #10, #10], \n  f=#{1, 2, 3}, \n  g={\n    a:#'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n    b:#'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n    c:f32{5x5}∈[1.0,1.0]\n  }, \n  h=f32{5x1}∈[1.0,1.0], \n  i=f32{1x6}∈[1.0,1.0], \n  j=f32{1x1x4x5}∈[1.0,1.0], \n  l=namedtuple(b=#1, c=#2), \n  m=f32{5x5}∈[1.0,1.0], \n  n=#bool{0}, \n  o=c64{2}\n)"
    )


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_str():
    assert (
        tree_str(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b=string, \n  c=1.0, \n  d=aaaaa, \n  e=[10, 10, 10, 10, 10], \n  f={1, 2, 3}, \n  g={\n    a:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, \n    b:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, \n    c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n  }, \n  h=[[1.] [1.] [1.] [1.] [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=[[[[1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]]]], \n  l=namedtuple(b=1, c=2), \n  m=\n    [[1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]], \n  n=True, \n  o=[1.+0.j 2.+0.j]\n)"
    )

    assert (
        tree_str(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=#1, \n  b=#string, \n  c=1.0, \n  d=#aaaaa, \n  e=[#10, #10, #10, #10, #10], \n  f=#{1, 2, 3}, \n  g={\n    a:#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, \n    b:#bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, \n    c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n  }, \n  h=[[1.] [1.] [1.] [1.] [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=[[[[1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]   [1. 1. 1. 1. 1.]]]], \n  l=namedtuple(b=#1, c=#2), \n  m=\n    [[1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]\n     [1. 1. 1. 1. 1.]], \n  n=#True, \n  o=[1.+0.j 2.+0.j]\n)"
    )


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_tree_summary():
    assert (
        tree_summary(r1, depth=0)
        # trunk-ignore(flake8/E501)
        == "┌────┬─────┬─────┬──────┐\n│Name│Type │Count│Size  │\n├────┼─────┼─────┼──────┤\n│Σ   │Repr1│101  │1.17KB│\n└────┴─────┴─────┴──────┘"
    )

    assert (
        tree_summary(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────┬───────┐\n│Name│Type        │Count│Size   │\n├────┼────────────┼─────┼───────┤\n│a   │int         │1    │28.00B │\n├────┼────────────┼─────┼───────┤\n│b   │str         │1    │55.00B │\n├────┼────────────┼─────┼───────┤\n│c   │float       │1    │24.00B │\n├────┼────────────┼─────┼───────┤\n│d   │str         │1    │54.00B │\n├────┼────────────┼─────┼───────┤\n│e   │list        │5    │140.00B│\n├────┼────────────┼─────┼───────┤\n│f   │set         │1    │216.00B│\n├────┼────────────┼─────┼───────┤\n│g   │dict        │27   │298.00B│\n├────┼────────────┼─────┼───────┤\n│h   │f32{5x1}    │5    │20.00B │\n├────┼────────────┼─────┼───────┤\n│i   │f32{1x6}    │6    │24.00B │\n├────┼────────────┼─────┼───────┤\n│j   │f32{1x1x4x5}│20   │80.00B │\n├────┼────────────┼─────┼───────┤\n│l   │a           │2    │56.00B │\n├────┼────────────┼─────┼───────┤\n│m   │f32{5x5}    │25   │100.00B│\n├────┼────────────┼─────┼───────┤\n│n   │bool{0}     │1    │1.00B  │\n├────┼────────────┼─────┼───────┤\n│o   │c64{2}      │2    │16.00B │\n├────┼────────────┼─────┼───────┤\n│Σ   │Repr1       │101  │1.17KB │\n└────┴────────────┴─────┴───────┘"
    )

    assert (
        tree_summary(r1, depth=2)
        == tree_summary(r1)
        # trunk-ignore(flake8/E501)
        == "┌──────┬────────────┬─────┬───────┐\n│Name  │Type        │Count│Size   │\n├──────┼────────────┼─────┼───────┤\n│a     │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│b     │str         │1    │55.00B │\n├──────┼────────────┼─────┼───────┤\n│c     │float       │1    │24.00B │\n├──────┼────────────┼─────┼───────┤\n│d     │str         │1    │54.00B │\n├──────┼────────────┼─────┼───────┤\n│e[0]  │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│e[1]  │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│e[2]  │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│e[3]  │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│e[4]  │int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│f     │set         │1    │216.00B│\n├──────┼────────────┼─────┼───────┤\n│g['a']│str         │1    │99.00B │\n├──────┼────────────┼─────┼───────┤\n│g['b']│str         │1    │99.00B │\n├──────┼────────────┼─────┼───────┤\n│g['c']│f32{5x5}    │25   │100.00B│\n├──────┼────────────┼─────┼───────┤\n│h     │f32{5x1}    │5    │20.00B │\n├──────┼────────────┼─────┼───────┤\n│i     │f32{1x6}    │6    │24.00B │\n├──────┼────────────┼─────┼───────┤\n│j     │f32{1x1x4x5}│20   │80.00B │\n├──────┼────────────┼─────┼───────┤\n│l['b']│int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│l['c']│int         │1    │28.00B │\n├──────┼────────────┼─────┼───────┤\n│m     │f32{5x5}    │25   │100.00B│\n├──────┼────────────┼─────┼───────┤\n│n     │bool{0}     │1    │1.00B  │\n├──────┼────────────┼─────┼───────┤\n│o     │c64{2}      │2    │16.00B │\n├──────┼────────────┼─────┼───────┤\n│Σ     │Repr1       │101  │1.17KB │\n└──────┴────────────┴─────┴───────┘"
    )

    assert (
        tree_summary(r1f, depth=0)
        # trunk-ignore(flake8/E501)
        == "┌────┬─────┬─────────────┬───────────────┐\n│Name│Type │Count(Frozen)│Size(Frozen)   │\n├────┼─────┼─────────────┼───────────────┤\n│Σ   │Repr1│101(17)      │1.17KB(832.00B)│\n└────┴─────┴─────────────┴───────────────┘"
    )

    assert (
        tree_summary(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────────────┬────────────────┐\n│Name│Type        │Count(Frozen)│Size(Frozen)    │\n├────┼────────────┼─────────────┼────────────────┤\n│a   │int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│b   │str         │1(1)         │55.00B(55.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│c   │float       │1            │24.00B          │\n├────┼────────────┼─────────────┼────────────────┤\n│d   │str         │1(1)         │54.00B(54.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e   │list        │5(5)         │140.00B(140.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│f   │set         │1(1)         │216.00B(216.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│g   │dict        │27(2)        │298.00B(198.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│h   │f32{5x1}    │5            │20.00B          │\n├────┼────────────┼─────────────┼────────────────┤\n│i   │f32{1x6}    │6            │24.00B          │\n├────┼────────────┼─────────────┼────────────────┤\n│j   │f32{1x1x4x5}│20           │80.00B          │\n├────┼────────────┼─────────────┼────────────────┤\n│l   │a           │2(2)         │56.00B(56.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│m   │f32{5x5}    │25           │100.00B         │\n├────┼────────────┼─────────────┼────────────────┤\n│n   │bool{0}     │1(1)         │1.00B(1.00B)    │\n├────┼────────────┼─────────────┼────────────────┤\n│o   │c64{2}      │2            │16.00B          │\n├────┼────────────┼─────────────┼────────────────┤\n│Σ   │Repr1       │101(17)      │1.17KB(832.00B) │\n└────┴────────────┴─────────────┴────────────────┘"
    )

    assert (
        tree_summary(r1f, depth=2)
        == tree_summary(r1f)
        # trunk-ignore(flake8/E501)
        == "┌──────┬────────────┬─────────────┬────────────────┐\n│Name  │Type        │Count(Frozen)│Size(Frozen)    │\n├──────┼────────────┼─────────────┼────────────────┤\n│a     │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│b     │str         │1(1)         │55.00B(55.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│c     │float       │1            │24.00B          │\n├──────┼────────────┼─────────────┼────────────────┤\n│d     │str         │1(1)         │54.00B(54.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│e[0]  │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│e[1]  │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│e[2]  │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│e[3]  │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│e[4]  │int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│f     │set         │1(1)         │216.00B(216.00B)│\n├──────┼────────────┼─────────────┼────────────────┤\n│g['a']│str         │1(1)         │99.00B(99.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│g['b']│str         │1(1)         │99.00B(99.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│g['c']│f32{5x5}    │25           │100.00B         │\n├──────┼────────────┼─────────────┼────────────────┤\n│h     │f32{5x1}    │5            │20.00B          │\n├──────┼────────────┼─────────────┼────────────────┤\n│i     │f32{1x6}    │6            │24.00B          │\n├──────┼────────────┼─────────────┼────────────────┤\n│j     │f32{1x1x4x5}│20           │80.00B          │\n├──────┼────────────┼─────────────┼────────────────┤\n│l['b']│int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│l['c']│int         │1(1)         │28.00B(28.00B)  │\n├──────┼────────────┼─────────────┼────────────────┤\n│m     │f32{5x5}    │25           │100.00B         │\n├──────┼────────────┼─────────────┼────────────────┤\n│n     │bool{0}     │1(1)         │1.00B(1.00B)    │\n├──────┼────────────┼─────────────┼────────────────┤\n│o     │c64{2}      │2            │16.00B          │\n├──────┼────────────┼─────────────┼────────────────┤\n│Σ     │Repr1       │101(17)      │1.17KB(832.00B) │\n└──────┴────────────┴─────────────┴────────────────┘"
    )


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_tree_diagram():
    assert tree_diagram(r1, depth=0) == tree_diagram(r1f, depth=0) == "Repr1"

    assert (
        tree_diagram(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├── a=1\n    ├── b='string'\n    ├── c=1.0\n    ├── d='aaaaa'\n    ├── e=[10, 10, 10, 10, 10]\n    ├── f={1, 2, 3}\n    ├── g={\n            a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n            b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n            c:f32{5x5}∈[1.0,1.0]\n        }\n    ├── h=f32{5x1}∈[1.0,1.0]\n    ├── i=f32{1x6}∈[1.0,1.0]\n    ├── j=f32{1x1x4x5}∈[1.0,1.0]\n    ├── l=namedtuple(b=1, c=2)\n    ├── m=f32{5x5}∈[1.0,1.0]\n    ├── n=bool{0}\n    └── o=c64{2}"
    )

    assert (
        tree_diagram(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├── a=#1\n    ├── b=#'string'\n    ├── c=1.0\n    ├── d=#'aaaaa'\n    ├── e=[#10, #10, #10, #10, #10]\n    ├── f=#{1, 2, 3}\n    ├── g={\n            a:#'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n            b:#'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n            c:f32{5x5}∈[1.0,1.0]\n        }\n    ├── h=f32{5x1}∈[1.0,1.0]\n    ├── i=f32{1x6}∈[1.0,1.0]\n    ├── j=f32{1x1x4x5}∈[1.0,1.0]\n    ├── l=namedtuple(b=#1, c=#2)\n    ├── m=f32{5x5}∈[1.0,1.0]\n    ├── n=#bool{0}\n    └── o=c64{2}"
    )


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_custom_jax_class():
    @jtu.register_pytree_node_class
    class Test:
        def __init__(self):
            self.a = 1
            self.b = 2

        def tree_flatten(self):
            return (self.a, self.b), None

        @classmethod
        def tree_unflatten(cls, _, children):
            return cls(*children)

    t = Test()

    assert tree_repr(t) == "Test(leaf_0=1, leaf_1=2)"
    assert tree_str(t) == "Test(leaf_0=1, leaf_1=2)"
    assert (
        tree_diagram(t)
        == tree_diagram(t, depth=3)
        == "Test\n    ├── leaf_0=1\n    └── leaf_1=2"
    )
    assert (
        tree_summary(t)
        == tree_summary(t, depth=4)
        # trunk-ignore(flake8/E501)
        == "┌──────┬────┬─────┬──────┐\n│Name  │Type│Count│Size  │\n├──────┼────┼─────┼──────┤\n│leaf_0│int │1    │28.00B│\n├──────┼────┼─────┼──────┤\n│leaf_1│int │1    │28.00B│\n├──────┼────┼─────┼──────┤\n│Σ     │Test│2    │56.00B│\n└──────┴────┴─────┴──────┘"
    )

    assert tree_repr(Test) == repr(Test)
    assert tree_str(Test) == str(Test)


@pytest.mark.xfail(sys.version_info >= (3, 11), reason=_msg)
def test_tree_mermaid():
    assert (
        tree_mermaid(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"1 leaf<br>28.00B"|id4205845433746830897("<b>a</b>:int=1")\n    id15696277213149321320--->|"1 leaf<br>55.00B"|id4682191244783855647("<b>b</b>:str=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id14652085615030570957("<b>c</b>:float=1.0")\n    id15696277213149321320--->|"1 leaf<br>54.00B"|id13847958709881997915("<b>d</b>:str=\'aaaaa\'")\n    id15696277213149321320--->|"5 leaf<br>140.00B"|id13688920499336522395("<b>e</b>:list=[10, 10, 10, 10, 10]")\n    id15696277213149321320--->|"1 leaf<br>216.00B"|id12849812219546513022("<b>f</b>:set={1, 2, 3}")\n    id15696277213149321320--->|"27 leaf<br>298.00B"|id12045685314397939980("<b>g</b>:dict={\n    a:\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\', \n    b:\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\', \n    c:f32{5x5}∈[1.0,1.0]\n}")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id11886647103852464460("<b>h</b>:Array=f32{5x1}∈[1.0,1.0]")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id6255200438522428121("<b>i</b>:Array=f32{1x6}∈[1.0,1.0]")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id10494519610961320729("<b>j</b>:Array=f32{1x1x4x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"2 leaf<br>56.00B"|id8653553293540427044("<b>l</b>:a=namedtuple(b=1, c=2)")\n    id15696277213149321320--->|"25 leaf<br>100.00B"|id15738275504112119619("<b>m</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"1 leaf<br>1.00B"|id14934148598963546577("<b>n</b>:Array=bool{0}")\n    id15696277213149321320--->|"2 leaf<br>16.00B"|id13897309186691225934("<b>o</b>:Array=c64{2}")'
    )
    assert (
        tree_mermaid(r1, depth=2)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"1 leaf<br>28.00B"|id4205845433746830897("<b>a</b>:int=1")\n    id15696277213149321320--->|"1 leaf<br>55.00B"|id4682191244783855647("<b>b</b>:str=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id14652085615030570957("<b>c</b>:float=1.0")\n    id15696277213149321320--->|"1 leaf<br>54.00B"|id13847958709881997915("<b>d</b>:str=\'aaaaa\'")\n    id15696277213149321320--->id14638725082963138220("<b>e</b>:list")\n    id14638725082963138220--->|"1 leaf<br>28.00B"|id14592014235850192347("<b>[0]</b>:int=10")\n    id15696277213149321320--->id3276703219825279179("<b>e</b>:list")\n    id3276703219825279179--->|"1 leaf<br>28.00B"|id17843434834412067271("<b>[1]</b>:int=10")\n    id15696277213149321320--->id6638221190537326664("<b>e</b>:list")\n    id6638221190537326664--->|"1 leaf<br>28.00B"|id13190411717613956610("<b>[2]</b>:int=10")\n    id15696277213149321320--->id1435736902404385494("<b>e</b>:list")\n    id1435736902404385494--->|"1 leaf<br>28.00B"|id4211819650461554669("<b>[3]</b>:int=10")\n    id15696277213149321320--->id14251034310783900771("<b>e</b>:list")\n    id14251034310783900771--->|"1 leaf<br>28.00B"|id2605315370674698135("<b>[4]</b>:int=10")\n    id15696277213149321320--->|"1 leaf<br>216.00B"|id12849812219546513022("<b>f</b>:set={1, 2, 3}")\n    id15696277213149321320--->id15082591947165260818("<b>g</b>:dict")\n    id15082591947165260818--->|"1 leaf<br>99.00B"|id11078324222165094821("<b>[\'a\']</b>:str=\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\'")\n    id15696277213149321320--->id2207384860718056384("<b>g</b>:dict")\n    id2207384860718056384--->|"1 leaf<br>99.00B"|id10417323950676019168("<b>[\'b\']</b>:str=\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\'")\n    id15696277213149321320--->id6644435165639260262("<b>g</b>:dict")\n    id6644435165639260262--->|"25 leaf<br>100.00B"|id3969574453593360740("<b>[\'c\']</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id11886647103852464460("<b>h</b>:Array=f32{5x1}∈[1.0,1.0]")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id6255200438522428121("<b>i</b>:Array=f32{1x6}∈[1.0,1.0]")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id10494519610961320729("<b>j</b>:Array=f32{1x1x4x5}∈[1.0,1.0]")\n    id15696277213149321320--->id5884435832896721572("<b>l</b>:a")\n    id5884435832896721572--->|"1 leaf<br>28.00B"|id15460503754714421713("<b>[\'b\']</b>:int=1")\n    id15696277213149321320--->id5080308927748148530("<b>l</b>:a")\n    id5080308927748148530--->|"1 leaf<br>28.00B"|id11761671376559489106("<b>[\'c\']</b>:int=2")\n    id15696277213149321320--->|"25 leaf<br>100.00B"|id15738275504112119619("<b>m</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"1 leaf<br>1.00B"|id14934148598963546577("<b>n</b>:Array=bool{0}")\n    id15696277213149321320--->|"2 leaf<br>16.00B"|id13897309186691225934("<b>o</b>:Array=c64{2}")'
    )
    assert (
        tree_mermaid(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(28.00B)"|id4205845433746830897("<b>a</b>:FrozenWrapper=#1")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(55.00B)"|id4682191244783855647("<b>b</b>:FrozenWrapper=#\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id14652085615030570957("<b>c</b>:float=1.0")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(54.00B)"|id13847958709881997915("<b>d</b>:FrozenWrapper=#\'aaaaa\'")\n    id15696277213149321320--->|"0(5) leaf<br>0.00B(140.00B)"|id13688920499336522395("<b>e</b>:list=[#10, #10, #10, #10, #10]")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(216.00B)"|id12849812219546513022("<b>f</b>:FrozenWrapper=#{1, 2, 3}")\n    id15696277213149321320--->|"25(2) leaf<br>100.00B(198.00B)"|id12045685314397939980("<b>g</b>:dict={\n    a:#\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\', \n    b:#\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\', \n    c:f32{5x5}∈[1.0,1.0]\n}")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id11886647103852464460("<b>h</b>:Array=f32{5x1}∈[1.0,1.0]")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id6255200438522428121("<b>i</b>:Array=f32{1x6}∈[1.0,1.0]")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id10494519610961320729("<b>j</b>:Array=f32{1x1x4x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"0(2) leaf<br>0.00B(56.00B)"|id8653553293540427044("<b>l</b>:a=namedtuple(b=#1, c=#2)")\n    id15696277213149321320--->|"25 leaf<br>100.00B"|id15738275504112119619("<b>m</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(1.00B)"|id14934148598963546577("<b>n</b>:FrozenWrapper=#bool{0}")\n    id15696277213149321320--->|"2 leaf<br>16.00B"|id13897309186691225934("<b>o</b>:Array=c64{2}")'
    )
    assert (
        tree_mermaid(r1f, depth=2)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(28.00B)"|id4205845433746830897("<b>a</b>:FrozenWrapper=#1")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(55.00B)"|id4682191244783855647("<b>b</b>:FrozenWrapper=#\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id14652085615030570957("<b>c</b>:float=1.0")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(54.00B)"|id13847958709881997915("<b>d</b>:FrozenWrapper=#\'aaaaa\'")\n    id15696277213149321320--->id14638725082963138220("<b>e</b>:list")\n    id14638725082963138220--->|"0(1) leaf<br>0.00B(28.00B)"|id14592014235850192347("<b>[0]</b>:FrozenWrapper=#10")\n    id15696277213149321320--->id3276703219825279179("<b>e</b>:list")\n    id3276703219825279179--->|"0(1) leaf<br>0.00B(28.00B)"|id17843434834412067271("<b>[1]</b>:FrozenWrapper=#10")\n    id15696277213149321320--->id6638221190537326664("<b>e</b>:list")\n    id6638221190537326664--->|"0(1) leaf<br>0.00B(28.00B)"|id13190411717613956610("<b>[2]</b>:FrozenWrapper=#10")\n    id15696277213149321320--->id1435736902404385494("<b>e</b>:list")\n    id1435736902404385494--->|"0(1) leaf<br>0.00B(28.00B)"|id4211819650461554669("<b>[3]</b>:FrozenWrapper=#10")\n    id15696277213149321320--->id14251034310783900771("<b>e</b>:list")\n    id14251034310783900771--->|"0(1) leaf<br>0.00B(28.00B)"|id2605315370674698135("<b>[4]</b>:FrozenWrapper=#10")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(216.00B)"|id12849812219546513022("<b>f</b>:FrozenWrapper=#{1, 2, 3}")\n    id15696277213149321320--->id15082591947165260818("<b>g</b>:dict")\n    id15082591947165260818--->|"0(1) leaf<br>0.00B(99.00B)"|id11078324222165094821("<b>[\'a\']</b>:FrozenWrapper=#\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\'")\n    id15696277213149321320--->id2207384860718056384("<b>g</b>:dict")\n    id2207384860718056384--->|"0(1) leaf<br>0.00B(99.00B)"|id10417323950676019168("<b>[\'b\']</b>:FrozenWrapper=#\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\'")\n    id15696277213149321320--->id6644435165639260262("<b>g</b>:dict")\n    id6644435165639260262--->|"25 leaf<br>100.00B"|id3969574453593360740("<b>[\'c\']</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id11886647103852464460("<b>h</b>:Array=f32{5x1}∈[1.0,1.0]")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id6255200438522428121("<b>i</b>:Array=f32{1x6}∈[1.0,1.0]")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id10494519610961320729("<b>j</b>:Array=f32{1x1x4x5}∈[1.0,1.0]")\n    id15696277213149321320--->id5884435832896721572("<b>l</b>:a")\n    id5884435832896721572--->|"0(1) leaf<br>0.00B(28.00B)"|id15460503754714421713("<b>[\'b\']</b>:FrozenWrapper=#1")\n    id15696277213149321320--->id5080308927748148530("<b>l</b>:a")\n    id5080308927748148530--->|"0(1) leaf<br>0.00B(28.00B)"|id11761671376559489106("<b>[\'c\']</b>:FrozenWrapper=#2")\n    id15696277213149321320--->|"25 leaf<br>100.00B"|id15738275504112119619("<b>m</b>:Array=f32{5x5}∈[1.0,1.0]")\n    id15696277213149321320--->|"0(1) leaf<br>0.00B(1.00B)"|id14934148598963546577("<b>n</b>:FrozenWrapper=#bool{0}")\n    id15696277213149321320--->|"2 leaf<br>16.00B"|id13897309186691225934("<b>o</b>:Array=c64{2}")'
    )


def test_misc():
    x = (1, 2, 3)
    assert tree_repr(x) == tree_str(x) == "(1, 2, 3)"

    def example(a: int, b=1, *c, d, e=2, **f):
        pass

    assert tree_repr(example) == tree_str(example) == "example(a, b, *c, d, e, **f)"

    # example = jax.jit(example)
    # assert (
    #     tree_repr(example) == tree_str(example) == "jit(example(a, b, *c, d, e, **f))"
    # )

    assert tree_repr(jnp.ones([1, 2], dtype=jnp.uint16)) == "ui16{1x2}∈[1,1]"
