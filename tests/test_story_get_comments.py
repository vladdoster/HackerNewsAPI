from random import randrange

import httpretty
import pytest

from hn import HN, Story
from hn import constants

from .test_utils import get_content


@pytest.fixture()
def story_comments():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET,
                           'https://news.ycombinator.com/',
                           body=get_content('index.html'))
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'item?id=7324236'),
        body=get_content('7324236.html'))
    httpretty.register_uri(httpretty.GET,
                           '%s/%s' % (constants.BASE_URL,
                                      'x?fnid=0MonpGsCkcGbA7rcbd2BAP'),
        body=get_content('7324236-2.html'))
    httpretty.register_uri(httpretty.GET,
                           '%s/%s' % (constants.BASE_URL,
                                      'x?fnid=jyhCSQtM6ymFazFplS4Gpf'),
        body=get_content('7324236-3.html'))
    httpretty.register_uri(httpretty.GET,
                           '%s/%s' % (constants.BASE_URL,
                                      'x?fnid=s3NA4qB6zMT3KHVk1x2MTG'),
        body=get_content('7324236-4.html'))
    httpretty.register_uri(httpretty.GET,
                           '%s/%s' % (constants.BASE_URL,
                                      'x?fnid=pFxm5XBkeLtmphVejNZWlo'),
        body=get_content('7324236-5.html'))

    story = Story.fromid(7324236)
    comments = story.get_comments()
    yield comments
    httpretty.HTTPretty.disable()


def test_get_comments_len(story_comments):
    """
    Tests whether or not len(get_comments) > 90 if there are multiple pages
    of comments.
    """
    assert len(story_comments) > 90


def test_comment_not_null(story_comments):
    """
    Tests for null comments.
    """
    comment = story_comments[randrange(0, len(story_comments))]
    assert bool(comment.body)
    assert bool(comment.body_html)


def test_get_nested_comments(story_comments):
    comment = story_comments[0].body
    assert comment.index("Healthcare.gov") == 0
