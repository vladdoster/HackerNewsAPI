import httpretty
import pytest

from hn import HN, Story
from hn import constants

from .test_utils import get_content


@pytest.fixture()
def leaders():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'leaders'),
                           body=get_content('leaders.html'))
    hn = HN()
    yield hn
    httpretty.HTTPretty.disable()


def test_get_leaders_with_no_parameter(leaders):
    result = [leader for leader in leaders.get_leaders()]
    assert len(result) == 10


def test_get_leaders_with_parameter(leaders):
    value = 50
    result = [leader for leader in leaders.get_leaders(value)]
    assert len(result) == value
