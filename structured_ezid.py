from itertools import chain
from typing import Union, Optional

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
        label = "ark:" if self.new_style else "ark:/"
        return f"{label}{self.naan}/{self.shoulder}{self.postfix}"


class Client2(ect.Client):
    def create_identifier(
        self,
        id_: Union[str, ARKIdentifier],
        metadata: Optional[dict] = None,
        update: bool = True,
    ):
        self.args.operation = [f"""create{"!" if update else ""}""", id_]
        if metadata is not None:
            self.args.operation += list(chain(*metadata.items()))
        return self.operation()

    def view_identifier(
        self, id_: Union[str, ARKIdentifier], prefix_matching: bool = False
    ):
        self.args.operation = [f"""view{"!" if prefix_matching else ""}""", id_]
        r = self.operation()
        return ANVL.parse_anvl_str(r.encode("utf-8"))
