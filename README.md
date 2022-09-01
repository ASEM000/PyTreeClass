<!-- <h1 align="center" style="font-family:Monospace" >Py🌲Class</h1> -->
<div align="center">
<img width="350px" src="assets/pytc%20logo.svg"></div>
<h2 align="center">Write pytorch-like layers with rich visualizations in JAX.</h2>

[**Installation**](#Installation)
|[**Description**](#Description)
|[**Quick Example**](#QuickExample)
|[**Filtering**](#Filtering)
|[**StatefulComputation**](#StatefulComputation)
|[**Applications**](#Applications)
|[**More**](#More)
|[**Acknowledgements**](#Acknowledgements)


![Tests](https://github.com/ASEM000/pytreeclass/actions/workflows/tests.yml/badge.svg)
![pyver](https://img.shields.io/badge/python-3.7%203.8%203.9%203.10-red)
![codestyle](https://img.shields.io/badge/codestyle-black-lightgrey)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1bkYr-5HidtRSXFFBlvYqFa5pc5fQK_7-?usp=sharing)
[![Downloads](https://pepy.tech/badge/pytreeclass)](https://pepy.tech/project/pytreeclass)
[![codecov](https://codecov.io/gh/ASEM000/pytreeclass/branch/main/graph/badge.svg?token=TZBRMO0UQH)](https://codecov.io/gh/ASEM000/pytreeclass)
[![Documentation Status](https://readthedocs.org/projects/pytreeclass/badge/?version=latest)](https://pytreeclass.readthedocs.io/en/latest/?badge=latest)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/ASEM000/pytreeclass)
<!-- [![Downloads](https://static.pepy.tech/personalized-badge/kernex?period=month&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/kernex) -->

## 🛠️ Installation<a id="Installation"></a>

```python
pip install pytreeclass
```
**Install development version**
```python
pip install git+https://github.com/ASEM000/PyTreeClass
```

## 📖 Description<a id="Description"></a>

PyTreeClass offers a JAX compatible `dataclass` like datastructure with the following functionalities

- 🏗️ [Create PyTorch like NN classes](#Pytorch)
- 🎨 [Visualize for pytrees decorated with `@pytc.treeclass`.](#Viz)
- ☝️ [Filtering by boolean masking similar to `jax.numpy.at` ](#Filtering)


## ⏩ Quick Example <a id="QuickExample">

### 🏗️ Create simple MLP <a id="Pytorch">


```python
import jax
from jax import numpy as jnp
import pytreeclass as pytc
import matplotlib.pyplot as plt

@pytc.treeclass
class Linear :
   # Any variable not wrapped with @pytc.treeclass
   # should be declared as a dataclass field here
   weight : jnp.ndarray
   bias   : jnp.ndarray

   def __init__(self,key,in_dim,out_dim):
       self.weight = jax.random.normal(key,shape=(in_dim, out_dim)) * jnp.sqrt(2/in_dim)
       self.bias = jnp.ones((1,out_dim))

   def __call__(self,x):
       return x @ self.weight + self.bias

@pytc.treeclass
class StackedLinear:

    def __init__(self,key,in_dim,out_dim,hidden_dim):
        keys= jax.random.split(key,3)

        # Declaring l1,l2,l3 as dataclass_fields is optional
        # as l1,l2,l3 are Linear class that is wrapped with @pytc.treeclass
        # To strictly include nodes defined in dataclass fields 
        # use `@pytc.treeclass(field_only=True)`
        self.l1 = Linear(key=keys[0],in_dim=in_dim,out_dim=hidden_dim)
        self.l2 = Linear(key=keys[1],in_dim=hidden_dim,out_dim=hidden_dim)
        self.l3 = Linear(key=keys[2],in_dim=hidden_dim,out_dim=out_dim)

    def __call__(self,x):
        x = self.l1(x)
        x = jax.nn.tanh(x)
        x = self.l2(x)
        x = jax.nn.tanh(x)
        x = self.l3(x)

        return x
        
model = StackedLinear(in_dim=1,out_dim=1,hidden_dim=10,key=jax.random.PRNGKey(0))

x = jnp.linspace(0,1,100)[:,None]
y = x**3 + jax.random.uniform(jax.random.PRNGKey(0),(100,1))*0.01
```

### 🎨 Visualize<a id="Viz">
<details>

<div align="center">
<table>
<tr>
 <td align = "center"> summary </td> <td align = "center">tree_box</td><td align = "center">tree_diagram</td>
</tr>
<tr>
 
<td>

```python
print(model.summary())
┌────┬──────┬───────┬───────┬─────────────────┐
│Name│Type  │Param #│Size   │Config           │
├────┼──────┼───────┼───────┼─────────────────┤
│l1  │Linear│20(0)  │80.00B │weight=f32[1,10] │
│    │      │       │(0.00B)│bias=f32[1,10]   │
├────┼──────┼───────┼───────┼─────────────────┤
│l2  │Linear│110(0) │440.00B│weight=f32[10,10]│
│    │      │       │(0.00B)│bias=f32[1,10]   │
├────┼──────┼───────┼───────┼─────────────────┤
│l3  │Linear│11(0)  │44.00B │weight=f32[10,1] │
│    │      │       │(0.00B)│bias=f32[1,1]    │
└────┴──────┴───────┴───────┴─────────────────┘
Total count :	141(0)
Dynamic count :	141(0)
Frozen count :	0(0)
-----------------------------------------------
Total size :	564.00B(0.00B)
Dynamic size :	564.00B(0.00B)
Frozen size :	0.00B(0.00B)
===============================================
```

</td>

 <td>

using jax.eval_shape (no-flops operation)

_note_ : the created modules in `__init__` should be in the same order where they are called in `__call__`

```python
print(model.tree_box(array=x))
┌──────────────────────────────────────┐
│StackedLinear[Parent]                 │
├──────────────────────────────────────┤
│┌────────────┬────────┬──────────────┐│
││            │ Input  │ f32[100,1]   ││
││ Linear[l1] │────────┼──────────────┤│
││            │ Output │ f32[100,128] ││
│└────────────┴────────┴──────────────┘│
│┌────────────┬────────┬──────────────┐│
││            │ Input  │ f32[100,128] ││
││ Linear[l2] │────────┼──────────────┤│
││            │ Output │ f32[100,128] ││
│└────────────┴────────┴──────────────┘│
│┌────────────┬────────┬──────────────┐│
││            │ Input  │ f32[100,128] ││
││ Linear[l3] │────────┼──────────────┤│
││            │ Output │ f32[100,1]   ││
│└────────────┴────────┴──────────────┘│
└──────────────────────────────────────┘
```
</td>
 
<td>

```python
print(model.tree_diagram())
StackedLinear
    ├── l1=Linear
    │   ├── weight=f32[1,10]
    │   └── bias=f32[1,10]
    ├── l2=Linear
    │   ├── weight=f32[10,10]
    │   └── bias=f32[1,10]
    └──l3=Linear
        ├── weight=f32[10,1]
        └── bias=f32[1,1]
```

 </td>

</tr>
 
<tr>
 
 </tr>
</table>

<table>
<tr><td align = "center" > mermaid.io (Native support in Github/Notion)</td></tr>
<tr>
 
<td>

```python
# generate mermaid diagrams
# print(pytc.tree_viz.tree_mermaid(model)) # generate core syntax
>>> pytc.tree_viz.save_viz(model,filename="test_mermaid",method="tree_mermaid_md")
# use `method="tree_mermaid_html"` to save as html
```

```mermaid

flowchart LR
    id15696277213149321320[StackedLinear]
    id15696277213149321320 --> id159132120600507116(l1\nLinear)
    id159132120600507116 --- id7500441386962467209["weight\nf32[1,10]"]
    id159132120600507116 --- id10793958738030044218["bias\nf32[1,10]"]
    id15696277213149321320 --> id10009280772564895168(l2\nLinear)
    id10009280772564895168 --- id11951215191344350637["weight\nf32[10,10]"]
    id10009280772564895168 --- id1196345851686744158["bias\nf32[1,10]"]
    id15696277213149321320 --> id7572222925824649475(l3\nLinear)
    id7572222925824649475 --- id4749243995442935477["weight\nf32[10,1]"]
    id7572222925824649475 --- id8042761346510512486["bias\nf32[1,1]"]
```
<div align="center",font-weight="bold">✨ Generate shareable vizualization links ✨</div>

```python
>>> pytc.tree_viz.tree_mermaid(model,link=True)
'Open URL in browser: https://pytreeclass.herokuapp.com/temp/?id=*********'
```


</td>

</tr>
 </table>

 </div>

</details>

### ✂️ Model surgery

<details>

```python
# freeze l1
model = model.at["l1"].freeze()

# Set negative_values in l2 to 0
filtered_l2 =  model.l2.at[model.l2<0].set(0) 
model = model.at["l2"].set( filtered_l2 )

# apply sin(x) to all values in l3
filtered_l3 = model.l3.at[...].apply(jnp.sin)
model  = model.at["l3"].set(filtered_l3)

# frozen nodes are marked with #
print(model.tree_diagram())
StackedLinear
    ├#─ l1=Linear
    │   ├#─ weight=f32[1,10]
    │   └#─ bias=f32[1,10]  
    ├── l2=Linear
    │   ├── weight=f32[10,10]
    │   └── bias=f32[1,10]  
    └── l3=Linear
        ├── weight=f32[10,1]
        └── bias=f32[1,1] 
```

</details>

## ☝️ Filtering with `.at[]` <a id="Filtering">
`PyTreeClass` offers four means of filtering: 
1. Filter by value
2. Filter by field name
3. Filter by field type
4. Filter by field metadata.

The following example demonstrates the usage the filtering.
Suppose you have the following (Multilayer perceptron) MLP class  
- **Note** in `StackedLinear` `l1` and `l2` has a description in `field` metadata.

<details> 

<summary>Model definition</summary>

```python
import jax
from jax import numpy as jnp
import pytreeclass as pytc
import matplotlib.pyplot as plt
from dataclasses import  field 

@pytc.treeclass
class Linear :
   weight : jnp.ndarray
   bias   : jnp.ndarray

   def __init__(self,key,in_dim,out_dim):
       self.weight = jax.random.normal(key,shape=(in_dim, out_dim)) * jnp.sqrt(2/in_dim)
       self.bias = jnp.ones((1,out_dim))

   def __call__(self,x):
       return x @ self.weight + self.bias

@pytc.treeclass
class StackedLinear:
    l1 : Linear = field(metadata={"description": "First layer"})
    l2 : Linear = field(metadata={"description": "Second layer"})

    def __init__(self,key,in_dim,out_dim,hidden_dim):
        keys= jax.random.split(key,3)

        self.l1 = Linear(key=keys[0],in_dim=in_dim,out_dim=hidden_dim)
        self.l2 = Linear(key=keys[2],in_dim=hidden_dim,out_dim=out_dim)

    def __call__(self,x):
        x = self.l1(x)
        x = jax.nn.tanh(x)
        x = self.l2(x)

        return x
        
model = StackedLinear(in_dim=1,out_dim=1,hidden_dim=5,key=jax.random.PRNGKey(0))
```
</details>


* Raw model values before any filtering.
```python
>>> print(model)

StackedLinear(
  l1=Linear(
    weight=[[-1.6248673  -2.8383057   1.3969219   1.3169124  -0.40784812]],
    bias=[[1. 1. 1. 1. 1.]]),
  l2=Linear(
    weight=
      [[ 0.98507565]
       [ 0.99815285]
       [-1.0687716 ]
       [-0.19255024]
       [-1.2108876 ]],
    bias=[[1.]]))
```

#### Filter by value

* Get all negative values
```python
>>> print(model.at[model<0].get())

StackedLinear(
  l1=Linear(
    weight=[-1.6248673  -2.8383057  -0.40784812],
    bias=[]),
  l2=Linear(
    weight=[-1.0687716  -0.19255024 -1.2108876 ],
    bias=[]))
```

*  Set negative values to 0
```python
>>> print(model.at[model<0].set(0))

StackedLinear(
  l1=Linear(
    weight=[[0.        0.        1.3969219 1.3169124 0.       ]],
    bias=[[1. 1. 1. 1. 1.]]),
  l2=Linear(
    weight=
      [[0.98507565]
       [0.99815285]
       [0.        ]
       [0.        ]
       [0.        ]],
    bias=[[1.]]))
```

* Apply f(x)=x^2 to negative values
```python
>>> print(model.at[model<0].apply(lambda x:x**2))

StackedLinear(
  l1=Linear(
    weight=[[2.6401937  8.05598    1.3969219  1.3169124  0.16634008]],
    bias=[[1. 1. 1. 1. 1.]]),
  l2=Linear(
    weight=
      [[0.98507565]
       [0.99815285]
       [1.1422727 ]
       [0.03707559]
       [1.4662486 ]],
    bias=[[1.]]))
```
* Sum all negative values
```python
>>> print(model.at[model<0].reduce_sum())
-7.3432307
```

#### Filter by field name

* Get all fields named `l1`
```python
>>> print(model.at[model == "l1"].get())

StackedLinear(
  l1=Linear(
    weight=[-1.6248673  -2.8383057   1.3969219   1.3169124  -0.40784812],
    bias=[1. 1. 1. 1. 1.]),
  l2=Linear(weight=[],bias=[]))
```

#### Filter by field type
* Get all fields of `Linear` type
```python
>>> print(model.at[model == Linear].get())

StackedLinear(
  l1=Linear(
    weight=[-1.6248673  -2.8383057   1.3969219   1.3169124  -0.40784812],
    bias=[1. 1. 1. 1. 1.]),
  l2=Linear(
    weight=[ 0.98507565  0.99815285 -1.0687716  -0.19255024 -1.2108876 ],
    bias=[1.]))
```

#### Filter by field metadata
* Get all fields of with `{"description": "First layer"}` in their metadata
```python
>>> print(model.at[model == {"description": "First layer"}].get())

StackedLinear(
  l1=Linear(
    weight=[-1.6248673  -2.8383057   1.3969219   1.3169124  -0.40784812],
    bias=[1. 1. 1. 1. 1.]),
  l2=Linear(weight=[],bias=[]))
```

### 🤯 Application : Filtering PyTrees by boolean masking 

-  Manipulate certain modules attributes values.
-  Set certain modules (e.g. `Dropout`) to *eval* mode

<details>


* Model definition

```python
import jax
from jax import numpy as jnp
import jax.random as jr
import pytreeclass as pytc

@pytc.treeclass
class Linear :
   weight : jnp.ndarray
   bias   : jnp.ndarray

   def __init__(self,key,in_dim,out_dim):
       self.weight = jax.random.normal(key,shape=(in_dim, out_dim)) * jnp.sqrt(2/in_dim)
       self.bias = jnp.ones((1,out_dim))

   def __call__(self,x):
       return x @ self.weight + self.bias


@pytc.treeclass
class Dropout:
    p: float
    eval : bool | None

    def __init__(self, p: float = 0.5, eval: bool | None = None):
        """p : probability of an element to be zeroed out"""
        self.p = p
        self.eval = eval

    def __call__(self, x, *, key=jr.PRNGKey(0)):
        return ( 
            x if (self.eval is True) 
            else 
            jnp.where(jr.bernoulli(key, (1 - self.p), x.shape), x / (1 - self.p), 0)
        )

@pytc.treeclass
class LinearWithDropout:
    def __init__(self):
        self.l1 = Linear(key=jr.PRNGKey(0), in_dim=1, out_dim=5)
        self.d1 = Dropout(p = 1.) # zero out all elements 

    def __call__(self, x):
        x = self.l1(x)
        x = self.d1(x)
        return x
```


#### `Linear` module with full dropout
```python
>>> model = LinearWithDropout()
>>> print(model(jnp.ones((1,1))))

[[0. 0. 0. 0. 0.]]
```

#### Disable `Dropout`
* using boolean masking with `.at[].set()` to disable `Dropout`
```python
>>> mask = (model == "eval")
>>> model_no_dropout = model.at[mask].set(True, is_leaf = lambda x:x is None)
>>> print(model_no_dropout(jnp.ones((1,1))))

[[ 1.2656513  -0.8149204   0.61661845  2.7664368   1.3457328 ]]
```

#### Set `Linear` module bias to 0
* Combining _attribute name_ mask and _class type_ mask 
```python
>>> mask = (model == "bias") & (model == Linear) 
>>> model_no_linear_bias = model.at[mask ].set(0)
>>> print(model_no_linear_bias)

LinearWithDropout(
 l1=Linear(
   weight=[[ 0.26565132 -1.8149204  -0.38338155  1.7664368   0.34573284]],
   bias=[[0. 0. 0. 0. 0.]]),
 d1=Dropout(p=1.0,eval=None))
```

</details>


## 📝 Applications<a id="Applications"></a>
- [Physics informed neural network (PINN)](https://github.com/ASEM000/Physics-informed-neural-network-in-JAX) 


## 🔢 More<a id="More"></a>

<details><summary><mark>More compact boilerplate</mark></summary>

Standard definition of nodes in `__init__` and calling in `__call__`
```python
@pytc.treeclass
class StackedLinear:
    def __init__(self,key,in_dim,out_dim,hidden_dim):
        keys= jax.random.split(key,3)
        self.l1 = Linear(key=keys[0],in_dim=in_dim,out_dim=hidden_dim)
        self.l2 = Linear(key=keys[1],in_dim=hidden_dim,out_dim=hidden_dim)
        self.l3 = Linear(key=keys[2],in_dim=hidden_dim,out_dim=out_dim)

    def __call__(self,x):
        x = self.l1(x)
        x = jax.nn.tanh(x)
        x = self.l2(x)
        x = jax.nn.tanh(x)
        x = self.l3(x)
        return x
```
Using `param`:
- More compact definition with node definition at runtime call
- The Linear layers are defined on the first call and retrieved on the subsequent calls
- This pattern is useful if the module definition depends on runtime data.
```python
@pytc.treeclass
class StackedLinear:
    def __init__(self,key):
        self.keys = jax.random.split(key,3)

    def __call__(self,x):
        x = self.param(Linear(self.keys[0],x.shape[-1],10),name="l1")(x)
        x = jax.nn.tanh(x)
        x = self.param(Linear(self.keys[1],10,10),name="l2")(x)
        x = jax.nn.tanh(x)
        x = self.param(Linear(self.keys[2],10,x.shape[-1]),name="l3")(x)
        return x
```
</details>




## 📙 Acknowledgements<a id="Acknowledgements"></a>
- [Farid Talibli (for visualization link generation backend)](https://www.linkedin.com/in/frdt98)
- [Equinox](https://github.com/patrick-kidger/equinox)
- [Treex](https://github.com/cgarciae/treex)
- [tree-math](https://github.com/google/tree-math)
