import re
from itertools import chain
from typing import Union, Optional, Dict, Any
import pathlib
from pathlib import PurePath as P

import ezid_client_tools as ect
from ezid_client_tools.utils import ANVL


class EZIDIdentifier:
    pass


class DOIIdentifier:
    pass


class ARKIdentifier(EZIDIdentifier):
    def __init__(
        self,
        naan: str = None,
        shoulder: str = None,
        postfix: str = None,
        new_form: bool = False,
        s: str = None,
        shoulder_size: int = 2,
    ):
        """
        Create an ARK identifier. Either pass in the components or pass in a string.
        """
        if s is not None:
            if s.startswith("ark:/"):
                self.new_form = False
                s = s[5:]
            elif s.startswith("ark:"):
                self.new_form = True
                s = s[4:]
            else:
                raise ValueError(f"String {s} does not start with ark: or ark:/")
            naan, s = s.split("/", maxsplit=1)
            shoulder, postfix = s[:shoulder_size], s[shoulder_size:]
        self.naan = naan
        self.shoulder = shoulder
        if postfix == ".":  # translate the root to an empty string
            postfix = ""
        self.postfix = postfix
        self.new_form = new_form

    def __eq__(self, __value: object) -> bool:
        return (
            self.naan == __value.naan
            and self.shoulder == __value.shoulder
            and self.postfix == __value.postfix
        )

    def __repr__(self):
        """Return a string representation of the identifier."""
        label = "ark:" if self.new_form else "ark:/"
        return f"{label}{self.naan}/{self.shoulder}{self.postfix}"

    @property
    def parent(self):
        p = P(self.postfix)
        return ARKIdentifier(self.naan, self.shoulder, str(p.parent))

    @property
    def parents(self):
        p = P(self.postfix)
        return [ARKIdentifier(self.naan, self.shoulder, str(x)) for x in p.parents]

    @property
    def parts(self):
        p = P(self.postfix)
        return p.parts

    @property
    def name(self):
        p = P(self.postfix)
        return p.name

    @property
    def stem(self):
        p = P(self.postfix)
        return p.stem

    @property
    def suffix(self):
        p = P(self.postfix)
        return p.suffix

    @property
    def suffixes(self):
        p = P(self.postfix)
        return p.suffixes

    @property
    def root(self):
        p = P(self.postfix)
        return ARKIdentifier(self.naan, self.shoulder, str(p.root))

    @property
    def is_valid(self):
        return oc_arks_filter(self.postfix)

    def is_relative_to(self, id2: Union[str, "ARKIdentifier"]):
        """
        Return True if the identifier is relative to the other identifier.
        id2: Union[str, ARKIdentifier],
        """
        if isinstance(id2, str):
            # if string, assume same naan and shoulder
            p = P(self.postfix)
            return p.is_relative_to(id2)
        elif isinstance(id2, ARKIdentifier):
            if self.naan != id2.naan or self.shoulder != id2.shoulder:
                return False
            p = P(self.postfix)
            return p.is_relative_to(id2.postfix)

    def joinpath(self, *args):
        """
        Return a new identifier with the given path appended.

        Parameters
        ----------
        *args : Path-like strings (for now)
        """
        p = P(self.postfix)
        return ARKIdentifier(self.naan, self.shoulder, str(p.joinpath(*args)))

    def __truediv__(self, *args):
        """
        Return a new identifier with the given path appended.

        Parameters
        ----------
        *args : Path-like strings (for now)
        """
        return self.joinpath(*args)


class Client2(ect.Client):
    def create_identifier(
        self,
        id_: Union[str, ARKIdentifier],
        metadata: Optional[Dict[str, Any]] = None,
        update: bool = False,
    ):
        """
        Create an identifier with the given metadata.

        Parameters
        ----------
        id_ : Union[str, ARKIdentifier]
            The identifier, which can be a string or an ARKIdentifier object.
        metadata : Optional[dict], optional
            A dictionary containing the metadata for the identifier (default is None).
        update : bool, optional
            Whether to update the identifier if it already exists (default is False).
        """
        if isinstance(id_, ARKIdentifier):
            id_ = str(id_)
        self.args.operation = [f"""create{"!" if update else ""}""", id_]
        if metadata is not None:
            self.args.operation += list(chain(*metadata.items()))
        (response, headers, status) = self.operation()
        return (response, headers, status)

    def view_identifier(
        self, id_: Union[str, ARKIdentifier], prefix_matching: bool = False
    ):
        """
        View an identifier's metadata.

        Parameters
        ----------
        id_ : Union[str, ARKIdentifier]
            The identifier, which can be a string or an ARKIdentifier object.
        prefix_matching : bool, optional
            Whether to enable prefix matching for the identifier (default is False).
        """
        if isinstance(id_, ARKIdentifier):
            id_ = str(id_)
        self.args.operation = [f"""view{"!" if prefix_matching else ""}""", id_]
        (response, headers, status) = self.operation()
        return (
            response,
            ANVL.parse_anvl_str(response.encode("utf-8")),
            headers,
            status,
        )

    def view_identifier_or_ancestor(
        self, id_: Union[str, ARKIdentifier], prefix_matching: bool = False
    ):
        """
        View an identifier's metadata or the metadata of its closest ancestor.
        Check whether there is metadata directly for id_.
        If not, then do prefix lookup for the parent -- maybe need to do a recursive look up the tree until we hit an actual ancestor.

        Parameters
        ----------
        id_ : Union[str, ARKIdentifier]
            The identifier, which can be a string or an ARKIdentifier object.
        prefix_matching : bool, optional
            Whether to enable prefix matching for the identifier (default is False).
        """
        try:
            return self.view_identifier(id_, prefix_matching=False)
        except ect.HTTPClientError as e:
            p = P(id_)


def oc_arks_filter(s):
    """
    regular expression that recognizes a limited set of paths
    Only lowercase letters, numbers, underscores are allowed in any given part, but there may one or more parts, separated by "/"
    In the  the leaf name, there may be periods -- but no period is allowed at the end
    stem can't be empty

    for example -- these are allowed:

    hello
    hello/there/dog
    hello/there/dog.py

    Not allowed:

    a/b/c.json.
    hello/there//dog

    """

    return re.match(r"^[a-z0-9_]+(?:/[a-z0-9_]+)*\.?[a-z0-9_]+$", s) is not None
