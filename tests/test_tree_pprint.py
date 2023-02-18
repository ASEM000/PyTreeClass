from __future__ import annotations

from collections import namedtuple

import jax.tree_util as jtu
from jax import numpy as jnp

import pytreeclass as pytc
from pytreeclass import tree_diagram, tree_mermaid, tree_repr, tree_str, tree_summary


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


r1 = Repr1()
mask = jtu.tree_map(pytc.is_nondiff, r1)
r1f = r1.at[mask].apply(pytc.freeze)


def test_repr():

    assert (
        tree_repr(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b='string', \n  c=1.0, \n  d='aaaaa', \n  e=[10, 10, 10, 10, 10], \n  f={1, 2, 3}, \n  g={\n    a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n    b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n    c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n  }, \n  h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )

    assert (
        tree_repr(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=#1, \n  b=#'string', \n  c=1.0, \n  d=#'aaaaa', \n  e=[#10, #10, #10, #10, #10], \n  f=#{1, 2, 3}, \n  g={\n    a:#'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n    b:#'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n    c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n  }, \n  h=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  i=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0), \n  j=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n)"
    )


def test_str():

    assert (
        tree_str(r1)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=1, \n  b=string, \n  c=1.0, \n  d=aaaaa, \n  e=[10, 10, 10, 10, 10], \n  f={1, 2, 3}, \n  g={\n    a:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, \n    b:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, \n    c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n  }, \n  h=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )

    assert (
        tree_str(r1f)
        # trunk-ignore(flake8/E501)
        == "Repr1(\n  a=#1, \n  b=#string, \n  c=1.0, \n  d=#aaaaa, \n  e=[#10, #10, #10, #10, #10], \n  f=#{1, 2, 3}, \n  g={\n    a:#'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n    b:#'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n    c:\n      [[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]\n  }, \n  h=\n    [[1.]\n     [1.]\n     [1.]\n     [1.]\n     [1.]], \n  i=[[1. 1. 1. 1. 1. 1.]], \n  j=\n    [[[[1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]\n       [1. 1. 1. 1. 1.]]]]\n)"
    )


def test_tree_summary():

    assert (
        tree_summary(r1, depth=0)
        # trunk-ignore(flake8/E501)
        == "┌────┬─────┬─────────────┬──────────────┐\n│Name│Type │Count(Frozen)│Size(Frozen)  │\n├────┼─────┼─────────────┼──────────────┤\n│Σ   │Repr1│68(0)        │939.00B(0.00B)│\n└────┴─────┴─────────────┴──────────────┘"
    )

    assert (
        tree_summary(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────────────┬──────────────┐\n│Name│Type        │Count(Frozen)│Size(Frozen)  │\n├────┼────────────┼─────────────┼──────────────┤\n│a   │int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│b   │str         │1(0)         │55.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│c   │float       │1(0)         │24.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│d   │str         │1(0)         │54.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e   │list        │5(0)         │140.00B(0.00B)│\n├────┼────────────┼─────────────┼──────────────┤\n│f   │set         │1(0)         │216.00B(0.00B)│\n├────┼────────────┼─────────────┼──────────────┤\n│g   │dict        │27(0)        │298.00B(0.00B)│\n├────┼────────────┼─────────────┼──────────────┤\n│h   │f32[5,1]    │5(0)         │20.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│i   │f32[1,6]    │6(0)         │24.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│j   │f32[1,1,4,5]│20(0)        │80.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│Σ   │Repr1       │68(0)        │939.00B(0.00B)│\n└────┴────────────┴─────────────┴──────────────┘"
    )

    assert (
        tree_summary(r1, depth=2)
        == tree_summary(r1)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────────────┬──────────────┐\n│Name│Type        │Count(Frozen)│Size(Frozen)  │\n├────┼────────────┼─────────────┼──────────────┤\n│a   │int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│b   │str         │1(0)         │55.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│c   │float       │1(0)         │24.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│d   │str         │1(0)         │54.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e[0]│int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e[1]│int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e[2]│int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e[3]│int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│e[4]│int         │1(0)         │28.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│f   │set         │1(0)         │216.00B(0.00B)│\n├────┼────────────┼─────────────┼──────────────┤\n│g.a │str         │1(0)         │99.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│g.b │str         │1(0)         │99.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│g.c │f32[5,5]    │25(0)        │100.00B(0.00B)│\n├────┼────────────┼─────────────┼──────────────┤\n│h   │f32[5,1]    │5(0)         │20.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│i   │f32[1,6]    │6(0)         │24.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│j   │f32[1,1,4,5]│20(0)        │80.00B(0.00B) │\n├────┼────────────┼─────────────┼──────────────┤\n│Σ   │Repr1       │68(0)        │939.00B(0.00B)│\n└────┴────────────┴─────────────┴──────────────┘"
    )

    assert (
        tree_summary(r1f, depth=0)
        # trunk-ignore(flake8/E501)
        == "┌────┬─────┬─────────────┬────────────────┐\n│Name│Type │Count(Frozen)│Size(Frozen)    │\n├────┼─────┼─────────────┼────────────────┤\n│Σ   │Repr1│68(11)       │939.00B(691.00B)│\n└────┴─────┴─────────────┴────────────────┘"
    )

    assert (
        tree_summary(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────────────┬────────────────┐\n│Name│Type        │Count(Frozen)│Size(Frozen)    │\n├────┼────────────┼─────────────┼────────────────┤\n│a   │int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│b   │str         │1(1)         │55.00B(55.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│c   │float       │1(0)         │24.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│d   │str         │1(1)         │54.00B(54.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e   │list        │5(5)         │140.00B(140.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│f   │set         │1(1)         │216.00B(216.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│g   │dict        │27(2)        │298.00B(198.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│h   │f32[5,1]    │5(0)         │20.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│i   │f32[1,6]    │6(0)         │24.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│j   │f32[1,1,4,5]│20(0)        │80.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│Σ   │Repr1       │68(11)       │939.00B(691.00B)│\n└────┴────────────┴─────────────┴────────────────┘"
    )

    assert (
        tree_summary(r1f, depth=2)
        == tree_summary(r1f)
        # trunk-ignore(flake8/E501)
        == "┌────┬────────────┬─────────────┬────────────────┐\n│Name│Type        │Count(Frozen)│Size(Frozen)    │\n├────┼────────────┼─────────────┼────────────────┤\n│a   │int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│b   │str         │1(1)         │55.00B(55.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│c   │float       │1(0)         │24.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│d   │str         │1(1)         │54.00B(54.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e[0]│int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e[1]│int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e[2]│int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e[3]│int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│e[4]│int         │1(1)         │28.00B(28.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│f   │set         │1(1)         │216.00B(216.00B)│\n├────┼────────────┼─────────────┼────────────────┤\n│g.a │str         │1(1)         │99.00B(99.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│g.b │str         │1(1)         │99.00B(99.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│g.c │f32[5,5]    │25(0)        │100.00B(0.00B)  │\n├────┼────────────┼─────────────┼────────────────┤\n│h   │f32[5,1]    │5(0)         │20.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│i   │f32[1,6]    │6(0)         │24.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│j   │f32[1,1,4,5]│20(0)        │80.00B(0.00B)   │\n├────┼────────────┼─────────────┼────────────────┤\n│Σ   │Repr1       │68(11)       │939.00B(691.00B)│\n└────┴────────────┴─────────────┴────────────────┘"
    )


def test_tree_diagram():
    assert tree_diagram(r1, depth=0) == tree_diagram(r1f, depth=0) == "Repr1"

    assert (
        tree_diagram(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├── 'a':int=1\n    ├── 'b':str='string'\n    ├── 'c':float=1.0\n    ├── 'd':str='aaaaa'\n    ├── 'e':list=[10, 10, 10, 10, 10]\n    ├── 'f':set={1, 2, 3}\n    ├── 'g':dict={\n            a:'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n            b:'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n            c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n        }\n    ├── 'h':Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├── 'i':Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └── 'j':Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)"
    )

    assert (
        tree_diagram(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == "Repr1\n    ├#─ 'a':FrozenWrapper=1\n    ├#─ 'b':FrozenWrapper='string'\n    ├── 'c':float=1.0\n    ├#─ 'd':FrozenWrapper='aaaaa'\n    ├── 'e':list=[#10, #10, #10, #10, #10]\n    ├#─ 'f':FrozenWrapper={1, 2, 3}\n    ├── 'g':dict={\n            a:#'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', \n            b:#'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', \n            c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n        }\n    ├── 'h':Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    ├── 'i':Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n    └── 'j':Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)"
    )


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
        == "Test\n    ├── 'leaf_0':int=1\n    └── 'leaf_1':int=2"
    )
    assert (
        tree_summary(t)
        == tree_summary(t, depth=4)
        # trunk-ignore(flake8/E501)
        == "┌──────┬────┬─────────────┬─────────────┐\n│Name  │Type│Count(Frozen)│Size(Frozen) │\n├──────┼────┼─────────────┼─────────────┤\n│leaf_0│int │1(0)         │28.00B(0.00B)│\n├──────┼────┼─────────────┼─────────────┤\n│leaf_1│int │1(0)         │28.00B(0.00B)│\n├──────┼────┼─────────────┼─────────────┤\n│Σ     │Test│2(0)         │56.00B(0.00B)│\n└──────┴────┴─────────────┴─────────────┘"
    )

    assert tree_repr(Test) == repr(Test)
    assert tree_str(Test) == str(Test)


def test_tree_mermaid():
    assert (
        tree_mermaid(r1, depth=1)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"1 leaf<br>28.00B"|id10494519610961320729("<b>\'a\'</b>:int=1")\n    id15696277213149321320--->|"1 leaf<br>55.00B"|id6255200438522428121("<b>\'b\'</b>:str=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id11886647103852464460("<b>\'c\'</b>:float=1.0")\n    id15696277213149321320--->|"1 leaf<br>54.00B"|id12045685314397939980("<b>\'d\'</b>:str=\'aaaaa\'")\n    id15696277213149321320--->|"5 leaf<br>140.00B"|id12849812219546513022("<b>\'e\'</b>:list=[10, 10, 10, 10, 10]")\n    id15696277213149321320--->|"1 leaf<br>216.00B"|id13688920499336522395("<b>\'f\'</b>:set={1, 2, 3}")\n    id15696277213149321320--->|"27 leaf<br>298.00B"|id13847958709881997915("<b>\'g\'</b>:dict={\n    a:\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\', \n    b:\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\', \n    c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n}")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id14652085615030570957("<b>\'h\'</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id4682191244783855647("<b>\'i\'</b>:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id4205845433746830897("<b>\'j\'</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")'
    )
    assert (
        tree_mermaid(r1, depth=2)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320--->|"1 leaf<br>28.00B"|id10494519610961320729("<b>\'a\'</b>:int=1")\n    id15696277213149321320--->|"1 leaf<br>55.00B"|id6255200438522428121("<b>\'b\'</b>:str=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id11886647103852464460("<b>\'c\'</b>:float=1.0")\n    id15696277213149321320--->|"1 leaf<br>54.00B"|id12045685314397939980("<b>\'d\'</b>:str=\'aaaaa\'")\n    id15696277213149321320--->id5799912992642773938("<b>\'e\'</b>:list")\n    id5799912992642773938--->|"1 leaf<br>28.00B"|id16668247476351813566("<b>[0]</b>:int=10")\n    id15696277213149321320--->id1560593820203881330("<b>\'e\'</b>:list")\n    id1560593820203881330--->|"1 leaf<br>28.00B"|id7138933422235525757("<b>[1]</b>:int=10")\n    id15696277213149321320--->id12922615683341740371("<b>\'e\'</b>:list")\n    id12922615683341740371--->|"1 leaf<br>28.00B"|id2555295008850196259("<b>[2]</b>:int=10")\n    id15696277213149321320--->id13959455095614061014("<b>\'e\'</b>:list")\n    id13959455095614061014--->|"1 leaf<br>28.00B"|id6774266340834374003("<b>[3]</b>:int=10")\n    id15696277213149321320--->id14763582000762634056("<b>\'e\'</b>:list")\n    id14763582000762634056--->|"1 leaf<br>28.00B"|id16186910192800708861("<b>[4]</b>:int=10")\n    id15696277213149321320--->|"1 leaf<br>216.00B"|id13688920499336522395("<b>\'f\'</b>:set={1, 2, 3}")\n    id15696277213149321320--->id10592630500687500829("<b>\'g\'</b>:dict")\n    id10592630500687500829--->|"1 leaf<br>99.00B"|id7829607701212726634("<b>\'a\'</b>:str=\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\'")\n    id15696277213149321320--->id6353311328248608221("<b>\'g\'</b>:dict")\n    id6353311328248608221--->|"1 leaf<br>99.00B"|id9701008432171133616("<b>\'b\'</b>:str=\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\'")\n    id15696277213149321320--->id11984757993578644560("<b>\'g\'</b>:dict")\n    id11984757993578644560--->|"25 leaf<br>100.00B"|id8854506843490797092("<b>\'c\'</b>:Array=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id14652085615030570957("<b>\'h\'</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id4682191244783855647("<b>\'i\'</b>:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id4205845433746830897("<b>\'j\'</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")'
    )
    assert (
        tree_mermaid(r1f, depth=1)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(28.00B)"|id10494519610961320729("<b>\'a\'</b>:FrozenWrapper=1")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(55.00B)"|id6255200438522428121("<b>\'b\'</b>:FrozenWrapper=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id11886647103852464460("<b>\'c\'</b>:float=1.0")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(54.00B)"|id12045685314397939980("<b>\'d\'</b>:FrozenWrapper=\'aaaaa\'")\n    id15696277213149321320--->|"0(5) leaf<br>0.00B(140.00B)"|id12849812219546513022("<b>\'e\'</b>:list=[#10, #10, #10, #10, #10]")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(216.00B)"|id13688920499336522395("<b>\'f\'</b>:FrozenWrapper={1, 2, 3}")\n    id15696277213149321320--->|"25(2) leaf<br>100.00B(198.00B)"|id13847958709881997915("<b>\'g\'</b>:dict={\n    a:#\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\', \n    b:#\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\', \n    c:f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)\n}")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id14652085615030570957("<b>\'h\'</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id4682191244783855647("<b>\'i\'</b>:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id4205845433746830897("<b>\'j\'</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")'
    )
    assert (
        tree_mermaid(r1f, depth=2)
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Repr1</b>)\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(28.00B)"|id10494519610961320729("<b>\'a\'</b>:FrozenWrapper=1")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(55.00B)"|id6255200438522428121("<b>\'b\'</b>:FrozenWrapper=\'string\'")\n    id15696277213149321320--->|"1 leaf<br>24.00B"|id11886647103852464460("<b>\'c\'</b>:float=1.0")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(54.00B)"|id12045685314397939980("<b>\'d\'</b>:FrozenWrapper=\'aaaaa\'")\n    id15696277213149321320-..-id5799912992642773938("<b>\'e\'</b>:list")\n    id5799912992642773938-..-|"0(1) leaf<br>0.00B(28.00B)"|id16668247476351813566("<b>[0]</b>:FrozenWrapper=10")\n    id15696277213149321320-..-id1560593820203881330("<b>\'e\'</b>:list")\n    id1560593820203881330-..-|"0(1) leaf<br>0.00B(28.00B)"|id7138933422235525757("<b>[1]</b>:FrozenWrapper=10")\n    id15696277213149321320-..-id12922615683341740371("<b>\'e\'</b>:list")\n    id12922615683341740371-..-|"0(1) leaf<br>0.00B(28.00B)"|id2555295008850196259("<b>[2]</b>:FrozenWrapper=10")\n    id15696277213149321320-..-id13959455095614061014("<b>\'e\'</b>:list")\n    id13959455095614061014-..-|"0(1) leaf<br>0.00B(28.00B)"|id6774266340834374003("<b>[3]</b>:FrozenWrapper=10")\n    id15696277213149321320-..-id14763582000762634056("<b>\'e\'</b>:list")\n    id14763582000762634056-..-|"0(1) leaf<br>0.00B(28.00B)"|id16186910192800708861("<b>[4]</b>:FrozenWrapper=10")\n    id15696277213149321320-..-|"0(1) leaf<br>0.00B(216.00B)"|id13688920499336522395("<b>\'f\'</b>:FrozenWrapper={1, 2, 3}")\n    id15696277213149321320-..-id10592630500687500829("<b>\'g\'</b>:dict")\n    id10592630500687500829-..-|"0(1) leaf<br>0.00B(99.00B)"|id7829607701212726634("<b>\'a\'</b>:FrozenWrapper=\'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\'")\n    id15696277213149321320-..-id6353311328248608221("<b>\'g\'</b>:dict")\n    id6353311328248608221-..-|"0(1) leaf<br>0.00B(99.00B)"|id9701008432171133616("<b>\'b\'</b>:FrozenWrapper=\'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\'")\n    id15696277213149321320--->id11984757993578644560("<b>\'g\'</b>:dict")\n    id11984757993578644560--->|"25 leaf<br>100.00B"|id8854506843490797092("<b>\'c\'</b>:Array=f32[5,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"5 leaf<br>20.00B"|id14652085615030570957("<b>\'h\'</b>:Array=f32[5,1] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"6 leaf<br>24.00B"|id4682191244783855647("<b>\'i\'</b>:Array=f32[1,6] ∈[1.0,1.0] μ(σ)=1.0(0.0)")\n    id15696277213149321320--->|"20 leaf<br>80.00B"|id4205845433746830897("<b>\'j\'</b>:Array=f32[1,1,4,5] ∈[1.0,1.0] μ(σ)=1.0(0.0)")'
    )


def test_field_no_repr():
    @pytc.treeclass
    class Test:
        a: int = pytc.field(repr=False)
        b: int = pytc.field(repr=False)
        c: tuple = (1, 2, 3)
        d: namedtuple = namedtuple("Test", ["a", "b", "c"])(1, 2, 3)

    assert (
        tree_repr(Test(1, 2))
        == tree_str(Test(1, 2))
        == "Test(c=(1, 2, 3), d=namedtuple(a=1, b=2, c=3))"
    )
    assert (
        tree_diagram(Test(1, 2))
        # trunk-ignore(flake8/E501)
        == "Test\n    ├── 'c':tuple\n    │   ├── [0]:int=1\n    │   ├── [1]:int=2\n    │   └── [2]:int=3\n    └── 'd':Test=namedtuple(a=1, b=2, c=3)"
    )
    assert (
        tree_summary(Test(1, 2))
        # trunk-ignore(flake8/E501)
        == "┌────┬────┬─────────────┬──────────────┐\n│Name│Type│Count(Frozen)│Size(Frozen)  │\n├────┼────┼─────────────┼──────────────┤\n│c[0]│int │1(0)         │28.00B(0.00B) │\n├────┼────┼─────────────┼──────────────┤\n│c[1]│int │1(0)         │28.00B(0.00B) │\n├────┼────┼─────────────┼──────────────┤\n│c[2]│int │1(0)         │28.00B(0.00B) │\n├────┼────┼─────────────┼──────────────┤\n│d   │Test│1(0)         │64.00B(0.00B) │\n├────┼────┼─────────────┼──────────────┤\n│Σ   │Test│6(0)         │204.00B(0.00B)│\n└────┴────┴─────────────┴──────────────┘"
    )

    assert (
        tree_mermaid(Test(1, 2))
        # trunk-ignore(flake8/E501)
        == 'flowchart LR\n    id15696277213149321320(<b>Test</b>)\n    id15696277213149321320--->id12446973225081843704("<b>\'c\'</b>:tuple")\n    id12446973225081843704--->|"1 leaf<br>28.00B"|id9772267725759667989("<b>[0]</b>:int=1")\n    id15696277213149321320--->id12408280303145007954("<b>\'c\'</b>:tuple")\n    id12408280303145007954--->|"1 leaf<br>28.00B"|id7897116322308127883("<b>[1]</b>:int=2")\n    id15696277213149321320--->id8168961130706115346("<b>\'c\'</b>:tuple")\n    id8168961130706115346--->|"1 leaf<br>28.00B"|id2766159651176208202("<b>[2]</b>:int=3")\n    id15696277213149321320--->|"1 leaf<br>64.00B"|id4205845433746830897("<b>\'d\'</b>:Test=namedtuple(a=1, b=2, c=3)")'
    )
