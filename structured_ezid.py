from itertools import chain
from typing import Union, Optional, Dict, Any

import ezid_client_tools as ect
from ezid_client_tools.utils import ANVL


class EZIDIdentifier:
    pass


class DOIIdentifier:
    pass


class ARKIdentifier(EZIDIdentifier):
    def __init__(self, naan: str, shoulder: str, postfix: str, new_style: bool = False):
        self.naan = naan
        self.shoulder = shoulder
        self.postfix = postfix
        self.new_style = new_style

    def __repr__(self):
        """Return a string representation of the identifier."""
        label = "ark:" if self.new_style else "ark:/"
        return f"{label}{self.naan}/{self.shoulder}{self.postfix}"


class Client2(ect.Client):
    def create_identifier(
        self,
        id_: Union[str, ARKIdentifier],
        metadata: Optional[Dict[str, Any]] = None,
        update: bool = True,
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
            Whether to update the identifier if it already exists (default is True).
        """
        if isinstance(id_, ARKIdentifier):
            id_ = str(id_)
        self.args.operation = [f"""create{"!" if update else ""}""", id_]
        if metadata is not None:
            self.args.operation += list(chain(*metadata.items()))
        return self.operation()

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
        r = self.operation()
        return ANVL.parse_anvl_str(r.encode("utf-8"))
