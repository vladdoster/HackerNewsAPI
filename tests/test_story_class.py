import httpretty
import pytest

from hn import HN, Story
from hn import constants

from .test_utils import get_content


@pytest.fixture()
def story():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'item?id=6115341'),
                           body=get_content('6115341.html'))
    s = Story.fromid(6115341)
    yield s
    httpretty.HTTPretty.disable()


def test_story_data_types(story):
    """
    Test types of fields of a Story object
    """
    assert isinstance(story.rank, int)
    assert isinstance(story.story_id, int)
    assert isinstance(story.title, str)
    assert isinstance(story.link, str)
    assert isinstance(story.domain, str)
    assert isinstance(story.points, int)
    assert isinstance(story.submitter, str)
    assert isinstance(story.published_time, str)
    assert isinstance(story.submitter_profile, str)
    assert isinstance(story.num_comments, int)
    assert isinstance(story.comments_link, str)
    assert isinstance(story.is_self, bool)


def test_story_submitter(story):
    """
    Tests the author name
    """
    assert story.submitter == 'karangoeluw'
