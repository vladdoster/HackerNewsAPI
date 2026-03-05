from random import randrange

import pytest


@pytest.fixture()
def story_comments(live_story_with_many_comments):
    return live_story_with_many_comments.get_comments()


def test_get_comments_len(story_comments):
    """
    Tests whether or not len(get_comments) > 90 if there are multiple pages
    of comments.
    """
    assert len(story_comments) > 30


def test_comment_not_null(story_comments):
    """
    Tests for null comments.
    """
    comment = story_comments[randrange(0, len(story_comments))]
    if comment.comment_id == -1:
        assert comment.body == '[deleted]'
    else:
        assert comment.body is not None
        assert comment.body_html is not None


def test_get_nested_comments(story_comments):
    assert any(comment.level > 0 for comment in story_comments)
