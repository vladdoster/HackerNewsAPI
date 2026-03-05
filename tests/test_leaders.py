import pytest

from hn import HN


@pytest.fixture(scope="module")
def leaders():
    return HN()


def test_get_leaders_with_no_parameter(leaders):
    result = [leader for leader in leaders.get_leaders()]
    assert len(result) == 10


def test_get_leaders_with_parameter(leaders):
    value = 50
    result = [leader for leader in leaders.get_leaders(value)]
    assert len(result) == value
