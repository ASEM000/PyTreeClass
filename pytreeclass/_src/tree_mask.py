# Copyright 2023 pytreeclass authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities to work with non-inexact type tree leaves across function transformations."""

from __future__ import annotations

import functools as ft
import hashlib
from typing import Any, Callable, Generic, NamedTuple, TypeVar, Union

from pytreeclass._src.backend import TreeUtil as tu
from pytreeclass._src.backend import numpy as np
from pytreeclass._src.tree_pprint import tree_repr, tree_str, tree_summary
from pytreeclass._src.tree_util import IsLeafType, is_tree_equal, tree_copy, tree_hash

T = TypeVar("T")
MaskType = Union[T, Callable[[Any], bool]]


class _FrozenError(NamedTuple):
    opname: str

    def __call__(self, *a, **k):
        raise NotImplementedError(
            f"Cannot apply `{self.opname}` operation to a frozen object "
            f"{', '.join(map(str, a))} "
            f"{', '.join(k + '=' + str(v) for k, v in k.items())}.\n"
            "Unfreeze the object first by unmasking the frozen mask:\n"
            "Example:\n"
            ">>> import jax\n"
            ">>> import pytreeclass as tc\n"
            ">>> tree = tc.tree_unmask(tree)"
        )


class _FrozenBase(Generic[T]):
    __slots__ = ["__wrapped__", "__weakref__"]
    __wrapped__: T

    def __init__(self, node: T) -> None:
        object.__setattr__(self, "__wrapped__", node)

    def __setattr__(self, _, __) -> None:
        raise AttributeError("Cannot assign to frozen instance.")

    def __delattr__(self, _: str) -> None:
        raise AttributeError("Cannot delete from frozen instance.")

    def __repr__(self) -> str:
        return "#" + tree_repr(self.__wrapped__)

    def __str__(self) -> str:
        return "#" + tree_str(self.__wrapped__)

    def __copy__(self) -> _FrozenBase[T]:
        return type(self)(tree_copy(self.__wrapped__))

    def __init_subclass__(klass, **k) -> None:
        # register subclass as an empty pytree node
        super().__init_subclass__(**k)

        tu.register_pytree_node(
            nodetype=klass,
            flatten_func=lambda tree: ((), tree),
            unflatten_func=lambda treedef, _: treedef,
        )

    # raise helpful error message when trying to interact with frozen object
    __add__ = __radd__ = __iadd__ = _FrozenError("+")
    __sub__ = __rsub__ = __isub__ = _FrozenError("-")
    __mul__ = __rmul__ = __imul__ = _FrozenError("*")
    __matmul__ = __rmatmul__ = __imatmul__ = _FrozenError("@")
    __truediv__ = __rtruediv__ = __itruediv__ = _FrozenError("/")
    __floordiv__ = __rfloordiv__ = __ifloordiv__ = _FrozenError("//")
    __mod__ = __rmod__ = __imod__ = _FrozenError("%")
    __pow__ = __rpow__ = __ipow__ = _FrozenError("**")
    __lshift__ = __rlshift__ = __ilshift__ = _FrozenError("<<")
    __rshift__ = __rrshift__ = __irshift__ = _FrozenError(">>")
    __and__ = __rand__ = __iand__ = _FrozenError("and")
    __xor__ = __rxor__ = __ixor__ = _FrozenError("")
    __or__ = __ror__ = __ior__ = _FrozenError("or")
    __neg__ = __pos__ = __abs__ = __invert__ = _FrozenError("unary operation")
    __call__ = _FrozenError("__call__")


@tree_summary.def_type(_FrozenBase)
def _(node) -> str:
    return f"#{tree_summary.type_dispatcher(node.__wrapped__)}"


class _FrozenHashable(_FrozenBase):
    def __hash__(self) -> int:
        return tree_hash(self.__wrapped__)

    def __eq__(self, rhs: Any) -> bool | np.ndarray:
        if not isinstance(rhs, _FrozenHashable):
            return False
        return is_tree_equal(self.__wrapped__, rhs.__wrapped__)


class _FrozenArray(_FrozenBase):
    def __hash__(self) -> int:
        bytes = np.array(self.__wrapped__).tobytes()
        return int(hashlib.sha256(bytes).hexdigest(), 16)

    def __eq__(self, other) -> bool:
        if not isinstance(other, _FrozenArray):
            return False

        lhs, rhs = self.__wrapped__, other.__wrapped__
        if lhs.shape != rhs.shape:
            return False
        if lhs.dtype != rhs.dtype:
            return False
        return np.all(lhs == rhs)


def freeze(value: T) -> _FrozenBase[T]:
    """Freeze a value to avoid updating it by through function transformations.

    Args:
        value: A value to freeze.

    Note:
        - :func:`.freeze` is idempotent, i.e. ``freeze(freeze(x)) == freeze(x)``.

    Example:
        >>> import jax
        >>> import pytreeclass as tc
        >>> import jax.tree_util as jtu
        >>> # Usage with `jax.tree_util.tree_leaves`
        >>> # no leaves for a wrapped value
        >>> jtu.tree_leaves(tc.freeze(2.))
        []

        >>> # retrieve the frozen wrapper value using `is_leaf=tc.is_frozen`
        >>> jtu.tree_leaves(tc.freeze(2.), is_leaf=tc.is_frozen)
        [#2.0]

        >>> # Usage with `jax.tree_util.tree_map`
        >>> a= [1,2,3]
        >>> a[1] = tc.freeze(a[1])
        >>> jtu.tree_map(lambda x:x+100, a)
        [101, #2, 103]
    """
    return freeze.type_dispatcher(value)


freeze.type_dispatcher = ft.singledispatch(lambda x: _FrozenHashable(x))
freeze.def_type = freeze.type_dispatcher.register


@freeze.def_type(np.ndarray)
def _(value: T) -> _FrozenArray[T]:
    return _FrozenArray(value)


@freeze.def_type(_FrozenBase)
def _(value: _FrozenBase[T]) -> _FrozenBase[T]:
    # idempotent freeze
    return value


def is_frozen(value: Any) -> bool:
    """Returns True if the value is a frozen wrapper."""
    return isinstance(value, _FrozenBase)


def unfreeze(value: T) -> T:
    """Unfreeze :func:`.freeze` value, otherwise return the value itself.

    Args:
        value: A value to unfreeze.

    Note:
        - use ``is_leaf=tc.is_frozen`` with ``tree_map`` to unfreeze a tree.**

    Example:
        >>> import pytreeclass as tc
        >>> import jax
        >>> frozen_value = tc.freeze(1)
        >>> tc.unfreeze(frozen_value)
        1
        >>> # usage with `jax.tree_map`
        >>> frozen_tree = jax.tree_map(tc.freeze, {"a": 1, "b": 2})
        >>> unfrozen_tree = jax.tree_map(tc.unfreeze, frozen_tree, is_leaf=tc.is_frozen)
        >>> unfrozen_tree
        {'a': 1, 'b': 2}
    """
    return unfreeze.type_dispatcher(value)


unfreeze.type_dispatcher = ft.singledispatch(lambda x: x)
unfreeze.def_type = unfreeze.type_dispatcher.register


@unfreeze.def_type(_FrozenBase)
def _(value: _FrozenBase[T]) -> T:
    return getattr(value, "__wrapped__")


def is_nondiff(value: Any) -> bool:
    """Returns True for non-inexact types, False otherwise.

    Args:
        value: A value to check.

    Note:
        - :func:`.is_nondiff` uses single dispatch to support custom types. To define
          a custom behavior for a certain type, use ``is_nondiff.def_type(type, func)``.

    Example:
        >>> import pytreeclass as tc
        >>> import jax.numpy as jnp
        >>> tc.is_nondiff(jnp.array(1))  # int array is non-diff type
        True
        >>> tc.is_nondiff(jnp.array(1.))  # float array is diff type
        False
        >>> tc.is_nondiff(1)  # int is non-diff type
        True
        >>> tc.is_nondiff(1.)  # float is diff type
        False

    Note:
        This function is meant to be used with ``jax.tree_map`` to
        create a mask for non-differentiable nodes in a tree, that can be used
        to freeze the non-differentiable nodes before passing the tree to a
        ``jax`` transformation.
    """
    return is_nondiff.type_dispatcher(value)


is_nondiff.type_dispatcher = ft.singledispatch(lambda x: True)
is_nondiff.def_type = is_nondiff.type_dispatcher.register


@is_nondiff.def_type(np.ndarray)
def _(value: np.ndarray) -> bool:
    # return True if the node is non-inexact type, otherwise False
    if np.issubdtype(value.dtype, np.inexact):
        return False
    return True


@is_nondiff.def_type(float)
@is_nondiff.def_type(complex)
def _(_: float | complex) -> bool:
    return False


def _tree_mask_map(
    tree: T,
    mask: MaskType,
    func: type | Callable[[Any], Any],
    *,
    is_leaf: IsLeafType = None,
):
    # apply func to leaves satisfying mask pytree/condtion
    _, lhsdef = tu.tree_flatten(tree, is_leaf=is_leaf)
    _, rhsdef = tu.tree_flatten(mask, is_leaf=is_leaf)

    if (lhsdef == rhsdef) and (type(mask) is type(tree)):
        return tu.tree_map(
            lambda x, y: func(x) if y else x,
            tree,
            mask,
            is_leaf=is_leaf,
        )

    if isinstance(mask, Callable):
        return tu.tree_map(
            lambda x: func(x) if mask(x) else x,
            tree,
            is_leaf=is_leaf,
        )

    raise ValueError(
        f"`mask` must be a callable that accepts a leaf and returns a boolean "
        f"or a tree with the same structure as tree with boolean values."
        f" Got {mask=} and {tree=}."
    )


def tree_mask(tree: T, mask: MaskType = is_nondiff, *, is_leaf: IsLeafType = None):
    """Mask leaves of a pytree based on ``mask`` boolean pytree or callable.

    Args:
        tree: A pytree of values.
        mask: A pytree of boolean values or a callable that accepts a leaf and
            returns a boolean. If a leaf is ``True`` either in the mask or the
            callable, the leaf is wrapped by with a wrapper that yields no
            leaves when ``tree_flatten`` is called on it, otherwise
            it is unchanged. defaults to :func:`.is_nondiff` which returns true for
            non-differentiable nodes.
        is_leaf: A callable that accepts a leaf and returns a boolean. If
            provided, it is used to determine if a value is a leaf. for example,
            ``is_leaf=lambda x: isinstance(x, list)`` will treat lists as leaves
            and will not recurse into them.

    Note:
        - Masked leaves are wrapped with a wrapper that yields no leaves when
          ``tree_flatten`` is called on it.
        - Masking is equivalent to applying :func:`.freeze` to the masked leaves.

            >>> import pytreeclass as tc
            >>> import jax
            >>> tree = [1, 2, {"a": 3, "b": 4.}]
            >>> # mask all non-differentiable nodes by default
            >>> def mask_if_nondiff(x):
            ...     return tc.freeze(x) if tc.is_nondiff(x) else x
            >>> masked_tree = jax.tree_map(mask_if_nondiff, tree)

        - Use masking on tree containing non-differentiable nodes before passing
          the tree to a ``jax`` transformation.

    Example:
        >>> import pytreeclass as tc
        >>> tree = [1, 2, {"a": 3, "b": 4.}]
        >>> # mask all non-differentiable nodes by default
        >>> masked_tree = tc.tree_mask(tree)
        >>> masked_tree
        [#1, #2, {'a': #3, 'b': 4.0}]
        >>> jax.tree_util.tree_leaves(masked_tree)
        [4.0]
        >>> tc.tree_unmask(masked_tree)
        [1, 2, {'a': 3, 'b': 4.0}]

    Example:
        >>> # pass non-differentiable values to `jax.grad`
        >>> import pytreeclass as tc
        >>> import jax
        >>> @jax.grad
        ... def square(tree):
        ...     tree = tc.tree_unmask(tree)
        ...     return tree[0]**2
        >>> tree = (1., 2)  # contains a non-differentiable node
        >>> square(tc.tree_mask(tree))
        (Array(2., dtype=float32, weak_type=True), #2)
    """
    return _tree_mask_map(tree, mask=mask, func=freeze, is_leaf=is_leaf)


def tree_unmask(tree: T, mask: MaskType = lambda _: True):
    """Undo the masking of tree leaves according to ``mask``. defaults to unmasking all leaves.

    Args:
        tree: A pytree of values.
        mask: A pytree of boolean values or a callable that accepts a leaf and
            returns a boolean. If a leaf is True either in the mask or the
            callable, the leaf is unfrozen, otherwise it is unchanged. defaults
            unmasking all nodes.

    Example:
        >>> import pytreeclass as tc
        >>> tree = [1, 2, {"a": 3, "b": 4.}]
        >>> # mask all non-differentiable nodes by default
        >>> masked_tree = tc.tree_mask(tree)
        >>> masked_tree
        [#1, #2, {'a': #3, 'b': 4.0}]
        >>> jax.tree_util.tree_leaves(masked_tree)
        [4.0]
        >>> tc.tree_unmask(masked_tree)
        [1, 2, {'a': 3, 'b': 4.0}]

    Example:
        >>> # pass non-differentiable values to `jax.grad`
        >>> import pytreeclass as tc
        >>> import jax
        >>> @jax.grad
        ... def square(tree):
        ...     tree = tc.tree_unmask(tree)
        ...     return tree[0]**2
        >>> tree = (1., 2)  # contains a non-differentiable node
        >>> square(tc.tree_mask(tree))
        (Array(2., dtype=float32, weak_type=True), #2)

    Note:
        - Unmasking is equivalent to applying :func:`.unfreeze` on the masked leaves.

            >>> import pytreeclass as tc
            >>> import jax
            >>> tree = [1, 2, {"a": 3, "b": 4.}]
            >>> # unmask all nodes
            >>> tree = jax.tree_map(tc.unfreeze, tree, is_leaf=tc.is_frozen)
    """
    return _tree_mask_map(tree, mask=mask, func=unfreeze, is_leaf=is_frozen)
