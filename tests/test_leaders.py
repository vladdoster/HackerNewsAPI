import pytest
import httpretty

from hn import HN
from hn import constants

from .test_utils import get_content


class TestGetLeaders:

    def setup_method(self):
        self.hn = HN()
        httpretty.HTTPretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            '%s/%s' % (constants.BASE_URL, 'leaders'),
            body=get_content('leaders.html'),
        )

    def teardown_method(self):
        httpretty.HTTPretty.disable()

    def test_get_leaders_with_no_parameter(self):
        result = [leader for leader in self.hn.get_leaders()]
        assert len(result) == 10

    def test_get_leaders_with_parameter(self):
        value = 5
        result = [leader for leader in self.hn.get_leaders(value)]
        assert len(result) == value
