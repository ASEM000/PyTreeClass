from pytreeclass._src.tree_base import is_tree_equal, treeclass
from pytreeclass._src.tree_decorator import field
from pytreeclass._src.tree_freeze import freeze, is_frozen, is_nondiff, unfreeze
from pytreeclass._src.tree_operator import bcmap
from pytreeclass._src.tree_pprint import (
    tree_diagram,
    tree_mermaid,
    tree_repr,
    tree_str,
    tree_summary,
)

__all__ = (
    # general utils
    "treeclass",
    "field",
    "is_tree_equal",
    "bcmap",
    # pprint utils
    "tree_diagram",
    "tree_mermaid",
    "tree_repr",
    "tree_str",
    "tree_summary",
    # freeze/unfreeze utils
    "is_nondiff",
    "is_frozen",
    "freeze",
    "unfreeze",
)

__version__ = "0.2.0b"
