import os
import pytest
import ezid_client_tools as ect
from ezid_client_tools.utils import ANVL
import structured_ezid as sezid


EZID_USER = os.environ.get("EZID_USER")
EZID_PASSWD = os.environ.get("EZID_PASSWD")

if (EZID_USER is None) or (EZID_PASSWD is None):
    import settings

    EZID_USER = settings.EZID_USER
    EZID_PASSWD = settings.EZID_PASSWD

TEST_NAAN = "99999"
TEST_SHOULDER = "fk4"
# an id for testing -- conceivably it can taken by someone else
TEST_ID = "00/a5"

OC_NAAN = "28722"
OC_PREREG_SHOULDER = "r2"


class TestARKIndentifier:
    def test_ark_identifier(self):
        ark = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, TEST_ID)
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == False
        assert ark.__repr__() == f"ark:/99999/fk400/a5"

    def test_ark_identifier_new_form(self):
        ark = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, TEST_ID, new_form=True)
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == True
        assert ark.__repr__() == f"ark:99999/fk400/a5"

    def test_ark_identifier_from_string(self):
        ark = sezid.ARKIdentifier(s=f"ark:/99999/fk400/a5", shoulder_size=3)
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == False
        assert ark.__repr__() == f"ark:/99999/fk400/a5"


class TestConsoleClient:
    @pytest.fixture
    def cclient(self):
        cclient = ect.ConsoleClient()
        cclient.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
        cclient.args.server = "p"
        return cclient

    def test_true(self):
        assert True

    @pytest.mark.xfail()
    def test_false(self):
        assert False

    def test_console_client_view(self, cclient):
        """
        making sure the console client can view an identifier
        """
        cclient.args.operation = ["view", "ark:/28722/k2154wc6r"]
        cclient.operation()


class TestClient:
    @pytest.fixture
    def client(self):
        client = ect.ConsoleClient()
        client.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
        client.args.server = "p"
        return client

    def test_client_view(self, client):
        client = ect.Client()

        client.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
        client.args.server = "p"

        client.args.operation = ["view", "ark:/28722/k2154wc6r"]
        r = ANVL.parse_anvl_str(client.operation().encode("utf-8"))
        assert type(r) == ect.utils.LastUpdatedOrderedDict
        assert set(r.keys()) == {
            "_created",
            "_export",
            "_owner",
            "_ownergroup",
            "_profile",
            "_status",
            "_target",
            "_updated",
            "erc.what",
            "erc.when",
            "erc.who",
            "success",
        }


class TestOcArksFilter:
    @pytest.mark.parametrize(
        "input_value, expected_result",
        [
            ("hello", True),
            ("HELLO", False),
            ("hello.123", True),
            ("hello/there/dog", True),
            ("hello/there/dog/", False),
            ("hello/there", True),
            ("hello//there", False),
            ("-", False),
            ("/", False),
            ("hello/there//dog", False),
            ("hello/there/.dog", False),
            ("hello/there/.dog/", False),
            ("hello/there/.dog/cat.jpg", False),
        ],
    )
    def test_oc_arks_filter(self, input_value, expected_result):
        assert sezid.oc_arks_filter(input_value) == expected_result
