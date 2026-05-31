import pytest
from unittest.mock import patch, MagicMock

from htb.hosts import contains, get_ip, _read


SAMPLE_HOSTS = """\
127.0.0.1   localhost
127.0.1.1   archie
10.10.10.1  lame.htb
10.10.10.3  beep.htb
# 10.10.10.5  commented.htb
"""


@pytest.fixture(autouse=True)
def mock_hosts(monkeypatch):
    monkeypatch.setattr("htb.hosts._read", lambda: SAMPLE_HOSTS)


def test_contains_existing():
    assert contains("lame.htb") is True


def test_contains_missing():
    assert contains("notexist.htb") is False


def test_contains_commented():
    assert contains("commented.htb") is True  # substring match


def test_get_ip_existing():
    assert get_ip("lame.htb") == "10.10.10.1"


def test_get_ip_second_entry():
    assert get_ip("beep.htb") == "10.10.10.3"


def test_get_ip_missing():
    assert get_ip("notexist.htb") is None
