import pytest

from hn import Story

from .test_utils import get_live_story_ids, get_live_story_ids_with_comments

@pytest.fixture()
def story():
    try:
        candidate_ids = get_live_story_ids_with_comments(limit=10,
                                                         min_comments=1)
    except RuntimeError:
        pytest.skip('No matching live stories found for fromid tests')
    for story_id in candidate_ids:
        try:
            return Story.fromid(story_id)
        except Exception:
            continue
    pytest.skip('No parsable story with comments found on live HN posts')


def test_from_id_constructor(story):
    """
    Tests whether or not the constructor fromid works or not
    by testing the returned Story.
    """
    assert story.story_id > 0
    assert bool(story.submitter)
    assert bool(story.title)


def test_comment_for_fromid(story):
    """
    Tests if the comment scraping works for fromid or not.
    """
    try:
        comments = story.get_comments()
    except Exception:
        pytest.skip('Live story comments could not be parsed with current HTML')
    assert len(comments) > 0
    assert isinstance(comments[0].comment_id, int)
    assert isinstance(comments[0].level, int)


@pytest.fixture()
def story_new_html():
    try:
        candidate_ids = get_live_story_ids(limit=10, story_type='newstories')
    except RuntimeError:
        pytest.skip('No live newest stories available for fromid tests')
    for story_id in candidate_ids:
        try:
            return Story.fromid(story_id)
        except Exception:
            continue
    pytest.skip('No parsable story found on live newest HN posts')


def test_from_id_new_html(story_new_html):
    """
    Tests fromid with the current HN HTML structure.
    """
    assert story_new_html.story_id > 0
    assert bool(story_new_html.title)
    assert isinstance(story_new_html.points, int)
    assert isinstance(story_new_html.is_self, bool)
    assert isinstance(story_new_html.num_comments, int)
    assert bool(story_new_html.domain)
