import httpretty
import pytest

from hn import HN, Story
from hn import constants

from .test_utils import get_content


@pytest.fixture()
def story():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET,
                           'https://news.ycombinator.com/',
                           body=get_content('index.html'))
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'item?id=6115341'),
                           body=get_content('6115341.html'))
    hn = HN()
    s = Story.fromid(6115341)
    yield s
    httpretty.HTTPretty.disable()


def test_from_id_constructor(story):
    """
    Tests whether or not the constructor fromid works or not
    by testing the returned Story.
    """
    assert story.submitter == 'karangoeluw'
    assert story.title == 'Github: What does the "Gold Star" next to my repository (in Explore page) mean?'
    assert story.is_self is True


def test_comment_for_fromid(story):
    """
    Tests if the comment scraping works for fromid or not.
    """
    comments = story.get_comments()
    assert len(comments) == 3
    assert comments[0].comment_id == 6115436
    assert comments[2].level == 2
