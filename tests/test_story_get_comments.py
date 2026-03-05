from random import randrange

import pytest

from hn import Story

from .test_utils import get_live_story_ids_with_comments

@pytest.fixture()
def story_comments():
    try:
        candidate_ids = get_live_story_ids_with_comments(limit=10,
                                                         min_comments=5)
    except RuntimeError:
        pytest.skip('No matching live stories found for comment tests')
    for story_id in candidate_ids:
        try:
            comments = Story.fromid(story_id).get_comments()
        except Exception:
            continue
        if comments:
            return comments
    pytest.skip('No story with comments found on live HN posts')


def test_get_comments_len(story_comments):
    """
    Tests whether or not len(get_comments) > 90 if there are multiple pages
    of comments.
    """
    assert len(story_comments) > 0


def test_comment_not_null(story_comments):
    """
    Tests for null comments.
    """
    comment = story_comments[randrange(0, len(story_comments))]
    assert bool(comment.body)
    assert bool(comment.body_html)


def test_get_nested_comments(story_comments):
    assert any(comment.level > 0 for comment in story_comments)
