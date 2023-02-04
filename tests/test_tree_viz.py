from __future__ import annotations

import dataclasses as dc
import sys

import jax.tree_util as jtu
import pytest
from jax import numpy as jnp

import pytreeclass as pytc
from pytreeclass.tree_viz import (
    tree_diagram,
    tree_mermaid,
    tree_repr,
    tree_str,
    tree_summary,
)


@pytc.treeclass
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

    def __post_init__(self):
        self.h = jnp.ones((5, 1))
        self.i = jnp.ones((1, 6))
        self.j = jnp.ones((1, 1, 4, 5))

        self.e = [10] * 5
        self.f = {1, 2, 3}
        self.g = {"a": "a" * 50, "b": "b" * 50, "c": jnp.ones([5, 5])}


@pytc.treeclass
class Repr2:
    a: jnp.ndarray
    b: jnp.ndarray
    c: jnp.ndarray

    def __init__(self) -> None:
        self.a = jnp.ones((5, 1))
        self.b = jnp.ones((1, 1))
        self.c = jnp.ones((1, 1, 4, 5))


@pytc.treeclass
class Linear:
    weight: jnp.ndarray
    bias: jnp.ndarray
    notes: str = pytc.field(nondiff=True, default=("string"))

    def __init__(self, in_dim, out_dim):
        self.weight = jnp.ones((in_dim, out_dim))
        self.bias = jnp.ones((1, out_dim))


@pytc.treeclass
class Repr3:
    l1: Linear = dc.field(repr=False)

    def __init__(self, in_dim, out_dim):
        self.l1 = Linear(in_dim=in_dim, out_dim=128)
        self.l2 = Linear(in_dim=128, out_dim=128)
        self.l3 = Linear(in_dim=128, out_dim=out_dim)


r1 = Repr1()
r2 = Repr2()
r3 = Repr3(in_dim=128, out_dim=10)

mask = jtu.tree_map(pytc.is_nondiff, r1)
r1f = r1.at[mask].apply(pytc.tree_freeze)

mask = r2 == r2
r2f = r2.at[mask].apply(pytc.tree_freeze)


@pytc.treeclass
class Repr3:
    l1: Linear = dc.field(repr=False)

    def __init__(self, in_dim, out_dim):
        self.l1 = Linear(in_dim=in_dim, out_dim=128)
        self.l2 = Linear(in_dim=128, out_dim=128)
        self.l3 = Linear(in_dim=128, out_dim=out_dim)


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="requires python <3.11")
def test_tree_repr():
    assert (
        tree_repr(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b='string', \n  c=1.0, \n  d='aaaaa', \n  e=[10,10,10,10,10], \n  f={1,2,3}, \n  g={\n    a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',\n    b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',\n    c:\n    f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n  }, \n  h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )

    assert (
        tree_repr(r2)
        # trunk-ignore(flake8/E501)
        == "Repr2(\n  a=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  b=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  c=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )

    assert (
        tree_repr(r3)
        # trunk-ignore(flake8/E501)
        == "Repr3(\n  l2=Linear(\n    weight=f32[128,128] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n    bias=f32[1,128] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n    *notes='string'\n  ), \n  l3=Linear(\n    weight=f32[128,10] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n    bias=f32[1,10] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n    *notes='string'\n  )\n)"
    )

    assert (
        tree_repr(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  #a=1, \n  #b='string', \n  c=1.0, \n  #d='aaaaa', \n  e=[\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10)\n  ], \n  #f={1,2,3}, \n  g={\n    a:FrozenWrapper('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),\n    b:FrozenWrapper('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),\n    c:\n    f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n  }, \n  h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )

    assert (
        tree_repr(r2f)
        # trunk-ignore(flake8/E501)
        == "Repr2(\n  #a=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  #b=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  #c=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="requires python <3.11")
def test_tree_str():

    assert (
        tree_str(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b=string, \n  c=1.0, \n  d=aaaaa, \n  e=[10,10,10,10,10], \n  f={1,2,3}, \n  g=\n    {\n      a:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,\n      b:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb,\n      c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n    }, \n  h=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )
    assert (
        tree_str(r2)
        # trunk-ignore(flake8/E501)
        == "Repr2(\n  a=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  b=[[1.]], \n  c=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )
    assert (
        tree_str(r3)
        # trunk-ignore(flake8/E501)
        == "Repr3(\n  l2=Linear(\n    weight=\n      [[1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       ...\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]], \n    bias=\n      [[1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n        1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n        1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n        1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n        1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n        1. 1. 1. 1. 1. 1. 1. 1.]], \n    *notes=string\n  ), \n  l3=Linear(\n    weight=\n      [[1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       ...\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]\n       [1. 1. 1. ... 1. 1. 1.]], \n    bias=[[1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]], \n    *notes=string\n  )\n)"
    )

    assert (
        tree_str(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  #a=1, \n  #b=string, \n  c=1.0, \n  #d=aaaaa, \n  e=[\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10),\n    FrozenWrapper(10)\n  ], \n  #f={1,2,3}, \n  g=\n    {\n      a:FrozenWrapper('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),\n      b:FrozenWrapper('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'),\n      c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n    }, \n  h=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )

    assert (
        tree_str(r2f)
        # trunk-ignore(flake8/E501)
        == "Repr2(\n  #a=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  #b=[[1.]], \n  #c=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="requires python <3.11")
def test_tree_diagram():

    assert (
        tree_diagram(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├── a:int=1\n    ├── b:str='string'\n    ├── c:float=1.0\n    ├── d:str='aaaaa'\n    ├── e:list=[10,10,10,10,10]\n    ├── f:set={1,2,3}\n    ├── g:dict\n    │   ├-─ a:str='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'\n    │   ├-─ b:str='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'\n    │   └-─ c:Array=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   \n    ├── h:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├── i:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └── j:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   "
    )
    assert (
        tree_diagram(r2)
        # trunk-ignore(flake8/E501)
        == "Repr2\n    ├── a:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├── b:Array=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └── c:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   "
    )
    assert (
        tree_diagram(r3)
        # trunk-ignore(flake8/E501)
        == "Repr3\n    ├── l2:Linear\n    │   ├── weight:Array=f32[128,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    │   ├── bias:Array=f32[1,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    │   └*─ notes:str='string'  \n    └── l3:Linear\n        ├── weight:Array=f32[128,10] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n        ├── bias:Array=f32[1,10] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n        └*─ notes:str='string'      "
    )

    assert (
        tree_diagram(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├#─ a:int=1\n    ├#─ b:str='string'\n    ├── c:float=1.0\n    ├#─ d:str='aaaaa'\n    ├── e:list\n    │   ├── [0]:_FrozenWrapper=FrozenWrapper(10)\n    │   ├── [1]:_FrozenWrapper=FrozenWrapper(10)\n    │   ├── [2]:_FrozenWrapper=FrozenWrapper(10)\n    │   ├── [3]:_FrozenWrapper=FrozenWrapper(10)\n    │   └── [4]:_FrozenWrapper=FrozenWrapper(10)    \n    ├#─ f:set={1,2,3}\n    ├── g:dict\n    │   ├-─ a:_FrozenWrapper=FrozenWrapper('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')\n    │   ├-─ b:_FrozenWrapper=FrozenWrapper('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')\n    │   └-─ c:Array=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   \n    ├── h:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├── i:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └── j:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   "
    )
    assert (
        tree_diagram(r2f)
        # trunk-ignore(flake8/E501)
        == "Repr2\n    ├#─ a:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├#─ b:Array=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └#─ c:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)   "
    )


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="requires python <3.11")
def test_tree_summary():

    assert tree_summary(r1, depth=0) == (
        # trunk-ignore(flake8/E501)
        "┌────┬─────┬──────┬───────┬───────────────────────────────────────────────────────────┐\n│Name│Type │Leaf #│Size   │Config                                                     │\n├────┼─────┼──────┼───────┼───────────────────────────────────────────────────────────┤\n│    │Repr1│68    │939.00B│=Repr1(                                                    │\n│    │     │      │       │  a=1,                                                     │\n│    │     │      │       │  b='string',                                              │\n│    │     │      │       │  c=1.0,                                                   │\n│    │     │      │       │  d='aaaaa',                                               │\n│    │     │      │       │  e=[10,10,10,10,10],                                      │\n│    │     │      │       │  f={1,2,3},                                               │\n│    │     │      │       │  g={                                                      │\n│    │     │      │       │    a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',│\n│    │     │      │       │    b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',│\n│    │     │      │       │    c:                                                     │\n│    │     │      │       │    f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                      │\n│    │     │      │       │  },                                                       │\n│    │     │      │       │  h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0),                     │\n│    │     │      │       │  i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0),                     │\n│    │     │      │       │  j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                  │\n│    │     │      │       │)                                                          │\n└────┴─────┴──────┴───────┴───────────────────────────────────────────────────────────┘\nTotal leaf count:       68\nNon-frozen leaf count:  68\nFrozen leaf count:      0\n---------------------------------------------------------------------------------------\nTotal leaf size:        939.00B\nNon-frozen leaf size:   939.00B\nFrozen leaf size:       0.00B\n=======================================================================================\n"
    )

    assert tree_summary(r1, depth=1) == (
        # trunk-ignore(flake8/E501)
        "┌────┬─────┬──────┬───────┬────────────────────────────────────────────────────────┐\n│Name│Type │Leaf #│Size   │Config                                                  │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│a   │int  │1     │28.00B │a=1                                                     │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│b   │str  │1     │55.00B │b='string'                                              │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│c   │float│1     │24.00B │c=1.0                                                   │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│d   │str  │1     │54.00B │d='aaaaa'                                               │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│e   │list │5     │140.00B│e=[10,10,10,10,10]                                      │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│f   │set  │1     │216.00B│f={1,2,3}                                               │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│g   │dict │27    │298.00B│g={                                                     │\n│    │     │      │       │ a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',│\n│    │     │      │       │ b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',│\n│    │     │      │       │ c:                                                     │\n│    │     │      │       │ f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                      │\n│    │     │      │       │}                                                       │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│h   │Array│5     │20.00B │h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)                     │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│i   │Array│6     │24.00B │i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)                     │\n├────┼─────┼──────┼───────┼────────────────────────────────────────────────────────┤\n│j   │Array│20    │80.00B │j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                 │\n└────┴─────┴──────┴───────┴────────────────────────────────────────────────────────┘\nTotal leaf count:       68\nNon-frozen leaf count:  68\nFrozen leaf count:      0\n------------------------------------------------------------------------------------\nTotal leaf size:        939.00B\nNon-frozen leaf size:   939.00B\nFrozen leaf size:       0.00B\n====================================================================================\n"
    )

    assert tree_summary(r1, depth=2) == (
        # trunk-ignore(flake8/E501)
        "┌────┬─────┬──────┬───────┬─────────────────────────────────────────────────────────┐\n│Name│Type │Leaf #│Size   │Config                                                   │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│a   │int  │1     │28.00B │a=1                                                      │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│b   │str  │1     │55.00B │b='string'                                               │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│c   │float│1     │24.00B │c=1.0                                                    │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│d   │str  │1     │54.00B │d='aaaaa'                                                │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│e[0]│int  │1     │28.00B │e[0]=10                                                  │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│e[1]│int  │1     │28.00B │e[1]=10                                                  │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│e[2]│int  │1     │28.00B │e[2]=10                                                  │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│e[3]│int  │1     │28.00B │e[3]=10                                                  │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│e[4]│int  │1     │28.00B │e[4]=10                                                  │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│f   │set  │1     │216.00B│f={1,2,3}                                                │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│g[a]│str  │1     │99.00B │g[a]='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'│\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│g[b]│str  │1     │99.00B │g[b]='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'│\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│g[c]│Array│25    │100.00B│g[c]=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                   │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│h   │Array│5     │20.00B │h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)                      │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│i   │Array│6     │24.00B │i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)                      │\n├────┼─────┼──────┼───────┼─────────────────────────────────────────────────────────┤\n│j   │Array│20    │80.00B │j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                  │\n└────┴─────┴──────┴───────┴─────────────────────────────────────────────────────────┘\nTotal leaf count:       68\nNon-frozen leaf count:  68\nFrozen leaf count:      0\n-------------------------------------------------------------------------------------\nTotal leaf size:        939.00B\nNon-frozen leaf size:   939.00B\nFrozen leaf size:       0.00B\n=====================================================================================\n"
    )

    assert tree_summary(r2) == (
        # trunk-ignore(flake8/E501)
        "┌────┬─────┬──────┬──────┬───────────────────────────────────────┐\n│Name│Type │Leaf #│Size  │Config                                 │\n├────┼─────┼──────┼──────┼───────────────────────────────────────┤\n│a   │Array│5     │20.00B│a=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├────┼─────┼──────┼──────┼───────────────────────────────────────┤\n│b   │Array│1     │4.00B │b=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├────┼─────┼──────┼──────┼───────────────────────────────────────┤\n│c   │Array│20    │80.00B│c=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)│\n└────┴─────┴──────┴──────┴───────────────────────────────────────┘\nTotal leaf count:       26\nNon-frozen leaf count:  26\nFrozen leaf count:      0\n------------------------------------------------------------------\nTotal leaf size:        104.00B\nNon-frozen leaf size:   104.00B\nFrozen leaf size:       0.00B\n==================================================================\n"
    )

    assert tree_summary(r3) == (
        # trunk-ignore(flake8/E501)
        "┌─────────┬─────┬──────┬───────┬────────────────────────────────────────────┐\n│Name     │Type │Leaf #│Size   │Config                                      │\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l1.weight│Array│16,384│64.00KB│weight=f32[128,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)│\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l1.bias  │Array│128   │512.00B│bias=f32[1,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l2.weight│Array│16,384│64.00KB│weight=f32[128,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)│\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l2.bias  │Array│128   │512.00B│bias=f32[1,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l3.weight│Array│1,280 │5.00KB │weight=f32[128,10] ∈[1.0,1.0] μ(σ)=1.0(0.0) │\n├─────────┼─────┼──────┼───────┼────────────────────────────────────────────┤\n│l3.bias  │Array│10    │40.00B │bias=f32[1,10] ∈[1.0,1.0] μ(σ)=1.0(0.0)     │\n└─────────┴─────┴──────┴───────┴────────────────────────────────────────────┘\nTotal leaf count:       34,314\nNon-frozen leaf count:  34,314\nFrozen leaf count:      0\n-----------------------------------------------------------------------------\nTotal leaf size:        134.04KB\nNon-frozen leaf size:   134.04KB\nFrozen leaf size:       0.00B\n=============================================================================\n"
    )

    assert tree_summary(r1f) == (
        # trunk-ignore(flake8/E501)
        "┌────┬──────────────────────┬──────┬───────┬────────────────────────────────────────────────────────────────────────┐\n│Name│Type                  │Leaf #│Size   │Config                                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│a   │int(Frozen)           │1     │28.00B │a=1                                                                     │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│b   │str(Frozen)           │1     │55.00B │b='string'                                                              │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│c   │float                 │1     │24.00B │c=1.0                                                                   │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│d   │str(Frozen)           │1     │54.00B │d='aaaaa'                                                               │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│e[0]│_FrozenWrapper(Frozen)│1     │48.00B │e[0]=FrozenWrapper(10)                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│e[1]│_FrozenWrapper(Frozen)│1     │48.00B │e[1]=FrozenWrapper(10)                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│e[2]│_FrozenWrapper(Frozen)│1     │48.00B │e[2]=FrozenWrapper(10)                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│e[3]│_FrozenWrapper(Frozen)│1     │48.00B │e[3]=FrozenWrapper(10)                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│e[4]│_FrozenWrapper(Frozen)│1     │48.00B │e[4]=FrozenWrapper(10)                                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│f   │set(Frozen)           │1     │216.00B│f={1,2,3}                                                               │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│g[a]│_FrozenWrapper(Frozen)│1     │48.00B │g[a]=FrozenWrapper('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')│\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│g[b]│_FrozenWrapper(Frozen)│1     │48.00B │g[b]=FrozenWrapper('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')│\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│g[c]│Array                 │25    │100.00B│g[c]=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                                  │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│h   │Array                 │5     │20.00B │h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)                                     │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│i   │Array                 │6     │24.00B │i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)                                     │\n├────┼──────────────────────┼──────┼───────┼────────────────────────────────────────────────────────────────────────┤\n│j   │Array                 │20    │80.00B │j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)                                 │\n└────┴──────────────────────┴──────┴───────┴────────────────────────────────────────────────────────────────────────┘\nTotal leaf count:       68\nNon-frozen leaf count:  57\nFrozen leaf count:      11\n---------------------------------------------------------------------------------------------------------------------\nTotal leaf size:        937.00B\nNon-frozen leaf size:   248.00B\nFrozen leaf size:       689.00B\n=====================================================================================================================\n"
    )

    assert tree_summary(r2f) == (
        # trunk-ignore(flake8/E501)
        "┌────┬─────────────┬──────┬──────┬───────────────────────────────────────┐\n│Name│Type         │Leaf #│Size  │Config                                 │\n├────┼─────────────┼──────┼──────┼───────────────────────────────────────┤\n│a   │Array(Frozen)│5     │20.00B│a=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├────┼─────────────┼──────┼──────┼───────────────────────────────────────┤\n│b   │Array(Frozen)│1     │4.00B │b=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)    │\n├────┼─────────────┼──────┼──────┼───────────────────────────────────────┤\n│c   │Array(Frozen)│20    │80.00B│c=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)│\n└────┴─────────────┴──────┴──────┴───────────────────────────────────────┘\nTotal leaf count:       26\nNon-frozen leaf count:  0\nFrozen leaf count:      26\n--------------------------------------------------------------------------\nTotal leaf size:        104.00B\nNon-frozen leaf size:   0.00B\nFrozen leaf size:       104.00B\n==========================================================================\n"
    )


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="requires python <3.11")
def test_tree_mermaid():
    assert (
        tree_mermaid(r1)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320 ---- |"1 leaf<br>28.00B"| id159132120600507116["<b>a</b>:int=1"]\n    id15696277213149321320 ---- |"1 leaf<br>55.00B"| id10009280772564895168["<b>b</b>:str=\'string\'"]\n    id15696277213149321320 ---- |"1 leaf<br>24.00B"| id7572222925824649475["<b>c</b>:float=1.0"]\n    id15696277213149321320 ---- |"1 leaf<br>54.00B"| id10865740276892226484["<b>d</b>:str=\'aaaaa\'"]\n    id15696277213149321320 ---- |"5 leaves<br>140.00B"| id2269144855147062920["<b>e</b>:list=[10,10,10,10,10]"]\n    id15696277213149321320 ---- |"1 leaf<br>216.00B"| id18278831082116368843["<b>f</b>:set={1,2,3}"]\n    id15696277213149321320 ---- |"27 leaves<br>298.00B"| id9682235660371205279["<b>g</b>:dict={\n    a:\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\',\n    b:\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\',\n    c:\n    f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n}"]\n    id15696277213149321320 ---- |"5 leaves<br>20.00B"| id12975753011438782288["<b>h</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id15696277213149321320 ---- |"6 leaves<br>24.00B"| id10538695164698536595["<b>i</b>:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id15696277213149321320 ---- |"20 leaves<br>80.00B"| id1942099742953373031["<b>j</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]'
    )
    assert (
        tree_mermaid(r2)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr2</b>)\n    id15696277213149321320 ---- |"5 leaves<br>20.00B"| id159132120600507116["<b>a</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id15696277213149321320 ---- |"1 leaf<br>4.00B"| id10009280772564895168["<b>b</b>:Array=f32[1,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id15696277213149321320 ---- |"20 leaves<br>80.00B"| id7572222925824649475["<b>c</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]'
    )
    assert (
        tree_mermaid(r3)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr3</b>)\n    id15696277213149321320 ---> |"16,512 leaves<br>64.50KB"| id159132120600507116("<b>l2</b>:Linear")\n    id159132120600507116 ---- |"16,384 leaves<br>64.00KB"| id7500441386962467209["<b>weight</b>:Array=f32[128,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id159132120600507116 ---- |"128 leaves<br>512.00B"| id10793958738030044218["<b>bias</b>:Array=f32[1,128] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id159132120600507116 ---- |"1 leaf<br>55.00B"| id16245750007010064142["<b>notes</b>:str=\'string\'"]\n    id15696277213149321320 ---> |"1,290 leaves<br>5.04KB"| id10009280772564895168("<b>l3</b>:Linear")\n    id10009280772564895168 ---- |"1,280 leaves<br>5.00KB"| id11951215191344350637["<b>weight</b>:Array=f32[128,10] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id10009280772564895168 ---- |"10 leaves<br>40.00B"| id1196345851686744158["<b>bias</b>:Array=f32[1,10] ∈[1.0,1.0] μ(σ)=1.0(0.0)"]\n    id10009280772564895168 ---- |"1 leaf<br>55.00B"| id6648137120666764082["<b>notes</b>:str=\'string\'"]'
    )

    # assert tree_mermaid(r1f)
