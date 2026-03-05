import pytest

from hn import Story


@pytest.fixture(scope="module")
def story():
    return Story.fromid(6115341)


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
    assert story.submitter == '_hoa8'
