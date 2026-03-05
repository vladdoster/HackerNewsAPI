import httpretty
import pytest

from hn import HN, Story
from hn import constants

from .test_utils import get_content


@pytest.fixture()
def stories_data():
    httpretty.HTTPretty.enable()
    httpretty.reset()
    httpretty.register_uri(httpretty.GET,
                           'https://news.ycombinator.com/',
                           body=get_content('index.html'))
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'best'),
                           body=get_content('best.html'))
    httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                      'newest'),
                           body=get_content('newest.html'))

    hn = HN()
    top_stories = [story for story in hn.get_stories()]
    newest_stories = [story for story in hn.get_stories(story_type='newest')]
    best_stories = [story for story in hn.get_stories(story_type='best')]
    yield {
        'top': top_stories,
        'newest': newest_stories,
        'best': best_stories,
    }
    httpretty.HTTPretty.disable()


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
    assert len(stories_data['top']) == 30


def test_stories_dict_length_best(stories_data):
    """
    Checks if the dict returned by scraping the best page of HN is 30.
    """
    assert len(stories_data['best']) == 30


def test_stories_dict_length_top_newest(stories_data):
    """
    Checks if the dict returned by scraping the newest page of HN is 30.
    """
    assert len(stories_data['newest']) == 30
