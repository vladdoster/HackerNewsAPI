import pytest
import httpretty

from hn import HN, Story, Comment, User
from hn import constants
from tests.conftest import get_content


@pytest.fixture(autouse=True)
def enable_httpretty():
    httpretty.HTTPretty.enable()
    httpretty.HTTPretty.reset()
    yield
    httpretty.HTTPretty.disable()
    httpretty.HTTPretty.reset()


class TestStoryFromId:

    @pytest.fixture(autouse=True)
    def setup_story(self):
        httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                         'item?id=6115341'),
                               body=get_content('6115341.html'))
        self.story = Story.fromid(6115341)

    def test_story_data_types(self):
        """Test types of fields of a Story object"""
        assert isinstance(self.story.rank, int)
        assert isinstance(self.story.story_id, int)
        assert isinstance(self.story.title, str)
        assert isinstance(self.story.link, str)
        assert isinstance(self.story.domain, str)
        assert isinstance(self.story.points, int)
        assert isinstance(self.story.submitter, str)
        assert isinstance(self.story.published_time, str)
        assert isinstance(self.story.submitter_profile, str)
        assert isinstance(self.story.num_comments, int)
        assert isinstance(self.story.comments_link, str)
        assert isinstance(self.story.is_self, bool)

    def test_story_submitter(self):
        """Tests the author name"""
        assert self.story.submitter == 'karangoeluw'

    def test_from_id_constructor(self):
        """Tests whether the constructor fromid works"""
        assert self.story.submitter == 'karangoeluw'
        assert self.story.title == 'Github: What does the "Gold Star" next to my repository (in Explore page) mean?'
        assert self.story.is_self is True

    def test_comment_for_fromid(self):
        """Tests if the comment scraping works for fromid"""
        comments = self.story.get_comments()
        assert len(comments) == 3
        assert comments[0].comment_id == 6115436
        assert comments[2].level == 2


class TestStoriesDict:

    @pytest.fixture(autouse=True)
    def setup_stories(self):
        httpretty.register_uri(httpretty.GET,
                               'https://news.ycombinator.com/',
                               body=get_content('index.html'))
        httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                         'best'),
                               body=get_content('best.html'))
        httpretty.register_uri(httpretty.GET, '%s/%s' % (constants.BASE_URL,
                                                         'newest'),
                               body=get_content('newest.html'))

        self.hn = HN()
        self.top_stories = list(self.hn.get_stories())
        self.newest_stories = list(self.hn.get_stories(story_type='newest'))
        self.best_stories = list(self.hn.get_stories(story_type='best'))

    def _check_story_types(self, stories):
        for story in stories:
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

    def test_stories_dict_structure_top(self):
        """Checks data type of each field of each story from front page."""
        self._check_story_types(self.top_stories)

    def test_stories_dict_structure_newest(self):
        """Checks data type of each field of each story from newest page"""
        self._check_story_types(self.newest_stories)

    def test_stories_dict_structure_best(self):
        """Checks data type of each field of each story from best page"""
        self._check_story_types(self.best_stories)

    def test_stories_dict_length_top(self):
        """Checks if the stories from the front page is 30."""
        assert len(self.top_stories) == 30

    def test_stories_dict_length_best(self):
        """Checks if the stories from the best page is 30."""
        assert len(self.best_stories) == 30

    def test_stories_dict_length_newest(self):
        """Checks if the stories from the newest page is 30."""
        assert len(self.newest_stories) == 30


class TestStoryGetComments:

    @pytest.fixture(autouse=True)
    def setup_comments(self):
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
        self.comments = story.get_comments()

    def test_get_comments_len(self):
        """Tests whether len(get_comments) > 90 for multi-page comments."""
        assert len(self.comments) > 90

    def test_comment_not_null(self):
        """Tests for null comments."""
        comment = self.comments[0]
        assert bool(comment.body)
        assert bool(comment.body_html)

    def test_get_nested_comments(self):
        comment = self.comments[0].body
        assert comment.index("Healthcare.gov") == 0
