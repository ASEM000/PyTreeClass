# Copyright 2023 PyTreeClass authors
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

"""Constructor code generation from type annotations."""

from __future__ import annotations

import functools as ft
import sys
from collections.abc import Callable, MutableMapping, MutableSequence, MutableSet
from types import FunctionType, MappingProxyType
from typing import Any, Literal, NamedTuple, Sequence, TypeVar, get_args

T = TypeVar("T")
PyTree = Any
EllipsisType = type(Ellipsis)
ArgKindType = Literal["POS_ONLY", "POS_OR_KW", "KW_ONLY"]
ArgKind = get_args(ArgKindType)
NULL = type("NULL", (), {"__repr__": lambda _: "NULL"})()
MUTABLE_TYPES = (MutableSequence, MutableMapping, MutableSet)
# https://github.com/google/jax/issues/14295


class Field(NamedTuple):
    name: str | None = None
    type: type | None = None
    default: Any = NULL
    init: bool = True
    repr: bool = True
    kind: ArgKindType = "POS_OR_KW"
    metadata: dict[str, Any] | None = None
    callbacks: Sequence[Callable[[Any], Any]] = ()
    alias: str | None = None

    def __call__(self, value: Any):
        """Call the callbacks on `value`."""
        for callback in self.callbacks:
            try:
                value = callback(value)
            except Exception as e:
                cname = getattr(callback, "__name__", callback)
                raise type(e)(f"On applying {cname} for field=`{self.name}`:\n{e}")
        return value


def field(
    *,
    default: Any = NULL,
    init: bool = True,
    repr: bool = True,
    kind: ArgKindType = "POS_OR_KW",
    metadata: dict[str, Any] | None = None,  # type: ignore
    callbacks: Sequence[Any] = (),
    alias: str | None = None,
) -> Field:
    """Field placeholder for type hinted attributes.

    Args:
        default: The default value of the field.
        init: Whether the field is included in the object's __init__ function.
        repr: Whether the field is included in the object's __repr__ function.
        kind: Argument kind, one of 'POS_ONLY', 'KW_ONLY', or 'POS_OR_KW'.
        metadata: A mapping of user-defined data for the field.
        callbacks: A sequence of functions to called on `setattr` during
            initialization to modify the field value.
        alias: An a alias for the field name in the constructor.

    Example:
        >>> import pytreeclass as pytc
        >>> class IsInstance(pytc.TreeClass):
        ...    klass: type
        ...    def __call__(self, x):
        ...        assert isinstance(x, self.klass)
        ...        return x
        >>> class Range(pytc.TreeClass):
        ...    start: int|float = float("-inf")
        ...    stop: int|float = float("inf")
        ...    def __call__(self, x):
        ...        assert self.start <= x <= self.stop
        ...        return x
        >>> class Employee(pytc.TreeClass):
        ...    # assert employee `name` is str
        ...    name: str = pytc.field(callbacks=[IsInstance(str)])
        ...    # use callback compostion to assert employee `age` is int and positive
        ...    age: int = pytc.field(callbacks=[IsInstance(int), Range(1)])
        ...    # use `id` in the constructor for `_id` attribute
        ...    # this is useful for private attributes that are not supposed
        ...    # to be accessed directly and hide it from the repr
        ...    _id: int = pytc.field(alias="id", repr=False)
        >>> employee = Employee(name="Asem", age=10, id=1)
        >>> print(employee)  # _id is not shown
        Employee(name=Asem, age=10)
        >>> assert employee._id == 1  # this is the private attribute
    """
    if not isinstance(alias, (str, type(None))):
        raise TypeError(f"Non-string {alias=} argument provided to `field`")
    if not isinstance(metadata, (dict, type(None))):
        raise TypeError(f"Non-dict {metadata=} argument provided to `field`")
    if kind not in ArgKind:
        raise ValueError(f"{kind=} not in {ArgKind}")
    if not isinstance(callbacks, Sequence):
        raise TypeError(f"Non-sequence {callbacks=} argument provided to `field`")
    for callback in callbacks:
        if not isinstance(callback, Callable):  # type: ignore
            raise TypeError(f"Non-callable {callback=} provided to `field`")

    return Field(
        default=default,
        init=init,
        repr=repr,
        kind=kind,
        metadata=metadata,  # type: ignore
        callbacks=callbacks,
        alias=alias,
    )


@ft.lru_cache(maxsize=128)
def _build_field_map(klass: type) -> MappingProxyType[str, Field]:
    field_map: dict[str, Field] = dict()

    if klass is object:
        return MappingProxyType(field_map)

    for base in reversed(klass.__mro__[1:]):
        field_map.update(_build_field_map(base))

    # TODO: use inspect to get annotations, once min python version >3.9
    if "__annotations__" not in vars(klass):
        return MappingProxyType(field_map)

    for name in (annotation_map := vars(klass)["__annotations__"]):
        value = vars(klass).get(name, NULL)
        hint = annotation_map[name]

        if name == "self":
            # while `dataclasses` allows `self` as a field name, its confusing
            # and not recommended. so raise an error
            raise ValueError("Field name cannot be `self`.")

        if isinstance(value, Field):
            if isinstance(value.default, MUTABLE_TYPES):
                # example case: `x: Any = field(default=[1, 2, 3])`
                raise TypeError(f"Mutable {value.default=} is not allowed.")
            # case: `x: Any = field(default=1)`
            field_map[name] = value._replace(name=name, type=hint)
        else:
            if isinstance(value, MUTABLE_TYPES):
                # example case: `x: Any = [1, 2, 3]`
                raise TypeError(f"Mutable {value=} is not allowed")
            # case: `x: int = 1` or `x: Any`
            field_map[name] = Field(name=name, type=hint, default=value)
    return MappingProxyType(field_map)


def fields(x: Any) -> Sequence[Field]:
    """Returns a tuple of `Field` objects for the given instance or class.

    `Field` objects are generated from the class type hints and contains
    the information about the field information.if the user uses
    the `pytreeclass.field` to annotate.

    Note:
        - If the class is not annotated, an empty tuple is returned.
        - The `Field` generation is cached for class and its bases.
    """
    return tuple(_build_field_map(x if isinstance(x, type) else type(x)).values())


def _build_init_method(klass: type) -> FunctionType:
    # generate a code object for the __init__ method and compile it
    # for the given class and return the function object
    body = []
    hints = dict()
    head = ["self"]
    heads = dict(zip(ArgKind, ([], [], [])))
    has_post = "__post_init__" in vars(klass)

    for field in (field_map := _build_field_map(klass)).values():
        dref = "" if field.default is NULL else f"=field_map['{field.name}'].default"

        if field.init:
            alias = field.alias or field.name
            hints[field.name] = field.type
            body += [f"self.{field.name}={alias}"]
            heads[field.kind] += [f"{alias}{dref}"]
        else:
            body += [f"self.{field.name}{dref}"]

    hints["return"] = None
    # add the post init call if the class has it, otherwise add a pass
    # in case all fields are not initialized in the __init__ method
    body += ["self.__post_init__()"] if has_post else ["pass"]

    # organize the arguments order (POS_ONLY, POS_OR_KW, KW_ONLY)
    head += (heads["POS_ONLY"] + ["/"]) if heads["POS_ONLY"] else []
    head += heads["POS_OR_KW"]
    head += (["*"] + heads["KW_ONLY"]) if heads["KW_ONLY"] else []

    # generate the code for the __init__ method
    code = "def closure(field_map):\n"
    code += f"\tdef __init__({','.join(head)}):"
    code += f"\n\t\t{';'.join(body)}"
    code += f"\n\t__init__.__qualname__ = '{klass.__qualname__}.__init__'"
    code += "\n\treturn __init__"

    exec(code, vars(sys.modules[klass.__module__]), namespace := dict())
    setattr(init := namespace["closure"](field_map), "__annotations__", hints)
    return init
