from __future__ import annotations

import dataclasses as dc
from typing import Any, Iterable

import jax.tree_util as jtu
import numpy as np

from pytreeclass._src.tree_operator import _hash_node

PyTree = Any

_PARAMS = "__dataclass_params__"


def _set_dataclass_frozen(tree: PyTree, frozen: bool):
    def freeze_step(tree: PyTree, frozen: bool) -> PyTree:
        if not dc.is_dataclass(tree):
            return tree

        params = getattr(tree, _PARAMS)

        if params.frozen is not frozen:
            params.frozen = frozen  # params is an instance variable

        # traverse the tree
        for field in dc.fields(tree):
            if not hasattr(tree, field.name):
                continue
            # some field value might not be set yet
            child = freeze_step(getattr(tree, field.name), frozen=frozen)
            tree.__dict__[field.name] = child

        return tree

    return freeze_step((tree), frozen=frozen)


class _NonDiffField(dc.Field):
    """A field that is not differentiable"""

    pass


class _HashableWrapper:
    def __init__(self, wrapped) -> None:
        self.__wrapped__ = wrapped

    def __eq__(self, rhs: Any) -> bool:
        if not isinstance(rhs, _HashableWrapper):
            return False
        return _hash_node(self.__wrapped__) == _hash_node(rhs.__wrapped__)

    def __hash__(self):
        return _hash_node(self.__wrapped__)


@jtu.register_pytree_node_class
class FrozenWrapper:
    "Wrapper for frozen tree leaf"
    # in essence this is a wrapper for a tree leaf to make it appear as a leaf to jax.tree_util
    # but it is not editable (i.e. it is frozen)
    def __init__(self, wrapped: Any):
        # disable composition of Wrappers
        self.__wrapped__ = wrapped.__wrapped__ if is_frozen(wrapped) else wrapped
        self.__class__.__name__ = f"Frozen{self.__wrapped__.__class__.__name__}"

    def __setattr__(self, key: str, value: Any) -> None:
        if "__wrapped__" in self.__dict__:
            raise ValueError("FrozenWrapper only allows `__wrapped__` to be set once`")
        return super().__setattr__(key, value)

    def __getattr__(self, k):
        if k == "__wrapped__":
            return getattr(self, k)
        return getattr(self.__wrapped__, k)

    def tree_flatten(self):
        # Wrapping the metadata to ensure its hashability and equality
        # https://github.com/google/jax/issues/13027
        return (None,), _HashableWrapper(self.__wrapped__)

    @classmethod
    def tree_unflatten(cls, treedef, leaves):
        self = object.__new__(cls)
        self.__dict__.update(__wrapped__=_unwrap(treedef))
        self.__class__.__name__ = f"Frozen{self.__wrapped__.__class__.__name__}"
        return self

    def __repr__(self):
        return f"#({self.__wrapped__!r})"

    def __eq__(self, rhs: Any) -> bool:
        if not isinstance(rhs, FrozenWrapper):
            return False
        return self.__wrapped__ == rhs.__wrapped__

    def __hash__(self):
        return hash(self.__wrapped__)


def _unwrap(node: FrozenWrapper) -> PyTree:
    """Unwrap a tree"""
    return node.__wrapped__


def is_frozen(tree: PyTree) -> bool:
    """Check if a tree is wrapped by a wrapper"""
    return isinstance(tree, FrozenWrapper)


def tree_freeze(x: PyTree) -> PyTree:
    """Freeze tree leaf"""

    def map_func(node: Any):
        if is_frozen(node):
            return node
        return FrozenWrapper(node)

    return jtu.tree_map(map_func, x)


def tree_unfreeze(x: PyTree) -> PyTree:
    """Unfreeze tree leaf"""
    # this is a bit tricky as we are using `is_leaf` to stop
    # traversing the tree when we hit a `FrozenWrapper`
    # the problem here is that, unlike `tree_freeze` this function
    # can not be used inside a `jtu.tree_map` **without** specifying
    # `is_leaf` as it will traverse the whole tree and miss the wrapper mark
    def map_func(node: Any):
        if isinstance(node, FrozenWrapper):
            return _unwrap(node)
        return node

    return jtu.tree_map(map_func, x, is_leaf=is_frozen)


def is_nondiff(item: Any) -> bool:
    """Check if a node is non-differentiable."""

    def _is_nondiff_item(node: Any):
        if hasattr(node, "dtype") and np.issubdtype(node.dtype, np.inexact):
            return False
        if isinstance(node, (float, complex)):
            return False
        return True

    if isinstance(item, Iterable):
        # if an iterable has at least one non-differentiable item
        # then the whole iterable is non-differentiable
        return any([_is_nondiff_item(item) for item in jtu.tree_leaves(item)])

    return _is_nondiff_item(item)
