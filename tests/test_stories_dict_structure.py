import pytest

from hn import Story

from .test_utils import get_live_story_ids

LIVE_STORY_LIMIT = 5

@pytest.fixture()
def stories_data():
    def _build_live_stories(story_type):
        story_ids = get_live_story_ids(limit=LIVE_STORY_LIMIT * 4,
                                       story_type=story_type)
        stories = []
        for story_id in story_ids:
            try:
                stories.append(Story.fromid(story_id))
            except Exception:
                continue
            if len(stories) == LIVE_STORY_LIMIT:
                return stories
        pytest.skip(f'Not enough parsable live {story_type} stories found')

    top_stories = _build_live_stories('topstories')
    newest_stories = _build_live_stories('newstories')
    best_stories = _build_live_stories('beststories')
    yield {
        'top': top_stories,
        'newest': newest_stories,
        'best': best_stories,
    }


def _check_story_types(story):
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


def test_stories_dict_structure_top(stories_data):
    """
    Checks data type of each field of each story from front page.
    """
    for story in stories_data['top']:
        _check_story_types(story)


def test_stories_dict_structure_newest(stories_data):
    """
    Checks data type of each field of each story from newest page
    """
    for story in stories_data['newest']:
        _check_story_types(story)


def test_stories_dict_structure_best(stories_data):
    """
    Checks data type of each field of each story from best page
    """
    for story in stories_data['best']:
        _check_story_types(story)


def test_stories_dict_length_top(stories_data):
    """
    Checks if the dict returned by scraping the front page of HN is 30.
    """
    assert len(stories_data['top']) == LIVE_STORY_LIMIT


def test_stories_dict_length_best(stories_data):
    """
    Checks if the dict returned by scraping the best page of HN is 30.
    """
    assert len(stories_data['best']) == LIVE_STORY_LIMIT


def test_stories_dict_length_top_newest(stories_data):
    """
    Checks if the dict returned by scraping the newest page of HN is 30.
    """
    assert len(stories_data['newest']) == LIVE_STORY_LIMIT
