import pytest

from hn import HN, Story


@pytest.fixture(scope="module")
def story():
    return Story.fromid(6115341)


def test_from_id_constructor(story):
    """
    Tests whether or not the constructor fromid works or not
    by testing the returned Story.
    """
    assert story.submitter == '_hoa8'
    assert story.title == 'Github: What does the "Gold Star" next to my repository (in Explore page) mean?'
    assert story.is_self is True


def test_comment_for_fromid(story):
    """
    Tests if the comment scraping works for fromid or not.
    """
    comments = story.get_comments()
    assert len(comments) >= 1
    assert isinstance(comments[0].comment_id, int)


@pytest.fixture(scope="module")
def story_new_html():
    return Story.fromid(6374031)


def test_from_id_new_html(story_new_html):
    """
    Tests fromid with the current HN HTML structure.
    """
    assert story_new_html.title == 'Python API for Hacker News'
    assert story_new_html.submitter == '_hoa8'
    assert story_new_html.points >= 1
    assert story_new_html.is_self is False
    assert story_new_html.num_comments >= 1
    assert story_new_html.domain == 'github.com/thekarangoel'
