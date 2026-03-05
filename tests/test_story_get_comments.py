import pytest

from hn import Story


@pytest.fixture(scope="module")
def story_comments():
    story = Story.fromid(7324236)
    return story.get_comments()


def test_get_comments_len(story_comments):
    """
    Tests whether or not get_comments returns at least one comment.
    """
    assert len(story_comments) >= 1


def test_comment_not_null(story_comments):
    """
    Tests for null comments.
    """
    comment = story_comments[0]
    assert bool(comment.body)
    assert bool(comment.body_html)
