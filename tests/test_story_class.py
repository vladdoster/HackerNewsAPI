import pytest
import httpretty

from hn import HN, Story
from hn import constants

from .test_utils import get_content


class TestStory:

    def setup_method(self):
        httpretty.HTTPretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            '%s/%s' % (constants.BASE_URL, 'item?id=6115341'),
            body=get_content('6115341.html'),
        )
        # https://news.ycombinator.com/item?id=6115341
        self.story = Story.fromid(6115341)

    def teardown_method(self):
        httpretty.HTTPretty.disable()

    def test_story_data_types(self):
        """
        Test types of fields of a Story object
        """
        assert type(self.story.rank) == int
        assert type(self.story.story_id) == int
        assert type(self.story.title) == str
        assert type(self.story.link) == str
        assert type(self.story.domain) == str
        assert type(self.story.points) == int
        assert type(self.story.submitter) == str
        assert type(self.story.published_time) == str
        assert type(self.story.submitter_profile) == str
        assert type(self.story.num_comments) == int
        assert type(self.story.comments_link) == str
        assert type(self.story.is_self) == bool

    def test_story_submitter(self):
        """
        Tests the author name
        """
        assert self.story.submitter == 'karangoeluw'
