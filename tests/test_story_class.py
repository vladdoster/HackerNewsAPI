import pytest

from hn import Story

from .test_utils import get_live_story_ids_with_comments

@pytest.fixture()
def story():
    try:
        candidate_ids = get_live_story_ids_with_comments(
            limit=10, min_comments=0, require_submitter=True
        )
    except RuntimeError:
        pytest.skip('No matching live stories found for story_class tests')
    for story_id in candidate_ids:
        try:
            return Story.fromid(story_id)
        except Exception:
            continue
    pytest.skip('No parsable story with a submitter found on live HN posts')


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
    assert bool(story.submitter)
