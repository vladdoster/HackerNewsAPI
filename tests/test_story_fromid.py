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


@pytest.fixture()
def story_new_format():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET,
                           '%s/%s' % (constants.BASE_URL,
                                      'item?id=6374031'),
                           body=get_content('6374031_new.html'))
    s = Story.fromid(6374031)
    yield s
    httpretty.HTTPretty.disable()


def test_fromid_new_html_format(story_new_format):
    """
    Tests that Story.fromid works with the current HN HTML structure
    where metadata is wrapped in a span.subline element.
    """
    assert story_new_format.title == 'Python API for Hacker News'
    assert story_new_format.is_self is False
    assert story_new_format.points == 53
    assert story_new_format.submitter != ''
    assert story_new_format.num_comments == 32
    assert story_new_format.domain == 'github.com/thekarangoel'
