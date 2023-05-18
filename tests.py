import pytest

import os
import ezid_client_tools as ect


EZID_USER = os.environ.get("EZID_USER")
EZID_PASSWD = os.environ.get("EZID_PASSWD")

if (EZID_USER is None) or (EZID_PASSWD is None):
    import settings

    EZID_USER = settings.EZID_USER
    EZID_PASSWD = settings.EZID_PASSWD

TEST_NAAN = "99999"
TEST_SHOULDER = "fk4"

# New shoulder

OC_NAAN = "28722"
OC_PREREG_SHOULDER = "r2"


def test_true():
    assert True


@pytest.mark.xfail()
def test_false():
    assert False


def test_console_client_view():
    cclient = ect.ConsoleClient()

    cclient.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
    cclient.args.server = "p"

    cclient.args.operation = ["view", "ark:/28722/k2154wc6r"]

    cclient.operation()
