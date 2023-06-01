import datetime
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
TEST_ID = "isamplestest"
TEST_PROJECT_ID = "prefixmatch"

OC_NAAN = "28722"
OC_PREREG_SHOULDER = "r2"


def test_divide_by_zero():
    """
    This test should fail -- it's here to teach Raymond about pytest.raises
    """
    with pytest.raises(ZeroDivisionError):
        1 / 0


class TestARKIndentifier:
    def test_ark_identifier(self):
        ark = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, TEST_ID)
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == False
        assert ark.__repr__() == f"ark:/{TEST_NAAN}/{TEST_SHOULDER}{TEST_ID}"

    def test_ark_identifier_new_form(self):
        ark = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, TEST_ID, new_form=True)
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == True
        assert ark.__repr__() == f"ark:{TEST_NAAN}/{TEST_SHOULDER}{TEST_ID}"

    def test_ark_identifier_from_string(self):
        ark = sezid.ARKIdentifier(
            s=f"ark:/{TEST_NAAN}/{TEST_SHOULDER}{TEST_ID}", shoulder_size=3
        )
        assert ark.naan == TEST_NAAN
        assert ark.shoulder == TEST_SHOULDER
        assert ark.postfix == TEST_ID
        assert ark.new_form == False
        assert ark.__repr__() == f"ark:/{TEST_NAAN}/{TEST_SHOULDER}{TEST_ID}"


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
        client = ect.Client()
        client.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
        client.args.server = "p"
        return client

    def test_client_login(self, client):
        client.args.server = "s"
        client.args.operation = ["login"]
        response = client.operation()
        assert isinstance(response, str)

    def test_client_view(self, client):
        client.args.server = "p"

        client.args.operation = ["view", "ark:/28722/k2154wc6r"]
        r = ANVL.parse_anvl_str(client.operation()[0].encode("utf-8"))
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


class TestClient2:
    @pytest.fixture
    def client2(self):
        client = sezid.Client2()
        client.args.credentials = f"{EZID_USER}:{EZID_PASSWD}"
        client.args.server = "s"
        return client

    def test_percent_encoded_prefix(self, client2):
        postfix = "#"
        ark_ = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, postfix)
        (response, headers, status) = client2.create_identifier(ark_, update=True)
        assert response == f"success: ark:/{TEST_NAAN}/{TEST_SHOULDER}%2523"
        assert status == 201

    def test_invalid_posfix(self, client2):
        postfix = "我"
        ark_ = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, postfix)
        with pytest.raises(ect.HTTPClientError) as e:
            (response, headers, status) = client2.create_identifier(ark_, update=True)
            assert status == 400

    def test_client_create_ok(self, client2):
        dt = datetime.datetime.utcnow()

        metadata_ = {
            "profile": "erc",
            "erc.who": "Raymond Yee",
            "erc.what": "container for testing iSample-Open Context interactions with the EZID service",
            "erc.when": dt.replace(microsecond=0).isoformat(),
        }

        postfix = TEST_ID
        ark_ = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, postfix)

        (response, headers, status) = client2.create_identifier(
            ark_, metadata_, update=True
        )
        # TO DO: any way to get status of 200
        # EZID returns a 201 HTTP status code if the identifier was created
        # or a 200 HTTP status code if the identifier already existed and was successfully updated.

        assert status == 201

    def test_client_create_error(self, client2):
        """A call to update this identifier is expected to fail because of the _bad_field metadata field"""
        dt = datetime.datetime.utcnow()

        metadata_ = {
            "profile": "erc",
            "erc.who": "Raymond Yee",
            "erc.what": "container for testing iSample-Open Context interactions with the EZID service",
            "erc.when": dt.replace(microsecond=0).isoformat(),
            "_bad_field": "xxxx",
        }

        postfix = TEST_ID
        ark_ = sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, postfix)

        with pytest.raises(ect.HTTPClientError) as e:
            r = client2.create_identifier(ark_, metadata_, update=True)
            assert e.value.status == 400

    def test_setup_prefixmatch(self, client2):
        """
        create a set of identifiers to test prefix matching -- maybe this should be a fixture
        """
        arks_to_create = (
            sezid.ARKIdentifier(TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}"),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}"
            ),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}/a"
            ),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}/a/b"
            ),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}/a/c"
            ),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}/a/c1"
            ),
            sezid.ARKIdentifier(
                TEST_NAAN, TEST_SHOULDER, f"{TEST_ID}/{TEST_PROJECT_ID}/a/c1/d"
            ),
        )

        for ark_ in arks_to_create:
            dt = datetime.datetime.utcnow()

            metadata_ = {
                "profile": "erc",
                "erc.who": "Raymond Yee",
                "erc.what": ark_.postfix,
                "erc.when": dt.replace(microsecond=0).isoformat(),
            }

            try:
                (response, headers, status) = client2.create_identifier(
                    ark_, metadata_, update=True
                )
            except ect.ClientError as e:
                if isinstance(e, ect.HTTPClientError):
                    print(e.status, str(e))
                else:
                    print(e, type(e))
            else:
                print(response, status)

            ark0 = sezid.ARKIdentifier(
                s="ark:/99999/fk4isamplestest/prefixmatch", shoulder_size=3
            )

            TEST_ID_MAPPING = [
                ("a/c1/d", "a/c1/d"),
                ("a/c/e", "a/c"),
                ("a/c1/e", "a/c1"),
                ("a/c12/d/e", "a"),
            ]

            for k, v in TEST_ID_MAPPING:
                r = client2.view_identifier_or_ancestor(
                    ark0 / k, prefix_matching=True, shoulder_size=3
                )
                print(k, v, r[0])
                assert ark0 / v == r[0]


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
