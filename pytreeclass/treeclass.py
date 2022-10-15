from __future__ import annotations

# from dataclasses import dataclass, field
import dataclasses
import inspect
from types import MappingProxyType
from typing import Any

import jax
import jax.numpy as jnp
import jax.tree_util as jtu

from pytreeclass._src.tree_base import _treeBase
from pytreeclass._src.tree_indexer import _treeIndexer
from pytreeclass._src.tree_op import _treeOp
from pytreeclass._src.tree_pretty import _treePretty
from pytreeclass._src.tree_util import _mutable


class ImmutableInstanceError(Exception):
    pass


def field(
    *, nondiff: bool = False, frozen: bool = False, **kwargs
) -> dataclasses.Field:
    """Similar to dataclasses.field but with additional arguments
    Args:
        nondiff: if True, the field will not be differentiated
        frozen: if True, the field will be frozen
        name: name of the field. Will be inferred from the variable name if its assigned to a class attribute.
        type: type of the field. Will be inferred from the variable type if its assigned to a class attribute.
        **kwargs: additional arguments to pass to dataclasses.field
    """
    metadata = kwargs.pop("metadata", {})
    if nondiff is True:
        metadata["nondiff"] = metadata["static"] = True
    elif frozen is True:
        metadata["frozen"] = metadata["static"] = True

    return dataclasses.field(metadata=metadata, **kwargs)


def is_frozen_field(field_item: dataclasses.Field) -> bool:
    """check if field is frozen"""
    return isinstance(field_item, dataclasses.Field) and field_item.metadata.get(
        "frozen", False
    )


def is_nondiff_field(field_item: dataclasses.Field) -> bool:
    """check if field is strictly static"""
    return isinstance(field_item, dataclasses.Field) and field_item.metadata.get(
        "nondiff", False
    )


def fields(tree):
    if len(tree.__undeclared_fields__) == 0:
        return tree.__dataclass_fields__.values()
    return tuple({**tree.__dataclass_fields__, **tree.__undeclared_fields__}.values())


def treeclass(*args, **kwargs):
    def immutable_setter(tree, key: str, value: Any) -> None:

        if tree.__immutable_pytree__:
            msg = f"Cannot set {key}={value!r}. Use `.at['{key}'].set({value!r})` instead."
            raise ImmutableInstanceError(msg)

        object.__setattr__(tree, key, value)

        if (isinstance(value, _treeBase)) and (
            key not in [f.name for f in fields(tree)]
        ):
            # create field
            field_value = field()

            object.__setattr__(field_value, "name", key)
            object.__setattr__(field_value, "type", type(value))

            # register it to class
            new_fields = {**tree.__undeclared_fields__, **{key: field_value}}  # fmt: skip
            object.__setattr__(tree, "__undeclared_fields__", MappingProxyType(new_fields))  # fmt: skip

    def immutable_delattr(tree, key: str) -> None:
        if tree.__immutable_pytree__:
            raise ImmutableInstanceError(f"Cannot delete {key}.")
        object.__delattr__(tree, key)

    def class_wrapper(cls):

        if "__setattr__" in vars(cls):
            msg = f"Cannot use @treeclass on {cls.__name__} because it already has a __setattr__ method."
            raise AttributeError(msg)

        if "__delattr__" in vars(cls):
            msg = f"Cannot use @treeclass on {cls.__name__} because it already has a __delattr__ method."
            raise AttributeError(msg)

        dcls_keys = ("init", "repr", "eq", "order", "unsafe_hash", "frozen")
        dcls_vals = ("__init__" not in vars(cls), False, False, False, False, False)
        dcls = dataclasses.dataclass(**dict(zip(dcls_keys, dcls_vals)))(cls)

        attrs_keys = ("__setattr__", "__delattr__", "__immutable_pytree__", "__undeclared_fields__")  # fmt: skip
        attrs_vals = (immutable_setter, immutable_delattr, True, MappingProxyType({}))
        attrs = dict(zip(attrs_keys, attrs_vals))

        bases = (dcls, _treeBase, _treeIndexer, _treeOp, _treePretty)
        new_cls = type(cls.__name__, bases, attrs)

        # temporarily make the class mutable during class creation
        new_cls.__init__ = _mutable(new_cls.__init__)

        return jax.tree_util.register_pytree_node_class(new_cls)

    if len(args) == 1 and inspect.isclass(args[0]):
        # no args are passed to the decorator (i.e. @treeclass)
        return class_wrapper(args[0])

    raise TypeError(f"`treeclass` input must be of `class` type. Found {(*args, *kwargs)}.")  # fmt: skip


def is_treeclass(tree):
    """check if a class is treeclass"""
    return hasattr(tree, "__immutable_pytree__")


def is_treeclass_frozen(tree):
    """assert if a treeclass is frozen"""
    if is_treeclass(tree):
        field_items = fields(tree)
        if len(field_items) > 0:
            return all(is_frozen_field(f) for f in field_items)
    return False


def is_treeclass_nondiff(tree):
    """assert if a treeclass is static"""
    if is_treeclass(tree):
        field_items = fields(tree)
        if len(field_items) > 0:
            return all(is_nondiff_field(f) for f in field_items)
    return False


def is_treeclass_leaf_bool(node):
    """assert if treeclass leaf is boolean (for boolen indexing)"""
    if isinstance(node, jnp.ndarray):
        return node.dtype == "bool"
    return isinstance(node, bool)


def is_treeclass_leaf(tree):
    """assert if a node is treeclass leaf"""
    if is_treeclass(tree):

        return is_treeclass(tree) and not any(
            [is_treeclass(getattr(tree, fi.name)) for fi in fields(tree)]
        )
    return False


def is_treeclass_non_leaf(tree):
    return is_treeclass(tree) and not is_treeclass_leaf(tree)


def is_treeclass_equal(lhs, rhs):
    """Assert if two treeclasses are equal"""
    lhs_leaves, lhs_treedef = jtu.tree_flatten(lhs)
    rhs_leaves, rhs_treedef = jtu.tree_flatten(rhs)

    def is_node_equal(lhs_node, rhs_node):
        if isinstance(lhs_node, jnp.ndarray) and isinstance(rhs_node, jnp.ndarray):
            return jnp.array_equal(lhs_node, rhs_node)
        return lhs_node == rhs_node

    return (lhs_treedef == rhs_treedef) and all(
        [is_node_equal(lhs_leaves[i], rhs_leaves[i]) for i in range(len(lhs_leaves))]
    )
