import pytest
from pydantic import ValidationError

from hn import Story, Comment, User


class TestStoryModel:
    """Tests for the Story Pydantic model."""

    def test_story_creation(self):
        """Test creating a Story with valid data."""
        story = Story(
            rank=1,
            story_id=123,
            title="Test Story",
            link="https://example.com",
            domain="example.com",
            points=100,
            submitter="testuser",
            published_time="2 hours ago",
            submitter_profile="https://news.ycombinator.com/user?id=testuser",
            num_comments=50,
            comments_link="https://news.ycombinator.com/item?id=123",
            is_self=False,
        )
        assert story.rank == 1
        assert story.story_id == 123
        assert story.title == "Test Story"
        assert story.link == "https://example.com"
        assert story.domain == "example.com"
        assert story.points == 100
        assert story.submitter == "testuser"
        assert story.published_time == "2 hours ago"
        assert story.num_comments == 50
        assert story.is_self is False

    def test_story_repr(self):
        """Test Story __repr__."""
        story = Story(
            rank=1, story_id=456, title="T", link="L", domain="D",
            points=0, submitter="U", published_time="P",
            submitter_profile="SP", num_comments=0,
            comments_link="CL", is_self=False,
        )
        assert repr(story) == '<Story: ID=456>'

    def test_story_validation_error(self):
        """Test that Story raises ValidationError for invalid data."""
        with pytest.raises(ValidationError):
            Story(
                rank="not_an_int",  # invalid
                story_id=123,
                title="Test",
                link="L",
                domain="D",
                points=0,
                submitter="U",
                published_time="P",
                submitter_profile="SP",
                num_comments=0,
                comments_link="CL",
                is_self=False,
            )

    def test_story_missing_field(self):
        """Test that Story raises ValidationError when a required field is missing."""
        with pytest.raises(ValidationError):
            Story(
                rank=1,
                # story_id missing
                title="Test",
                link="L",
                domain="D",
                points=0,
                submitter="U",
                published_time="P",
                submitter_profile="SP",
                num_comments=0,
                comments_link="CL",
                is_self=False,
            )

    def test_story_self_post(self):
        """Test creating a self-post Story."""
        story = Story(
            rank=1,
            story_id=789,
            title="Ask HN: Something",
            link="https://news.ycombinator.com/item?id=789",
            domain="https://news.ycombinator.com",
            points=10,
            submitter="askuser",
            published_time="1 hour ago",
            submitter_profile="https://news.ycombinator.com/user?id=askuser",
            num_comments=5,
            comments_link="https://news.ycombinator.com/item?id=789",
            is_self=True,
        )
        assert story.is_self is True


class TestCommentModel:
    """Tests for the Comment Pydantic model."""

    def test_comment_creation(self):
        """Test creating a Comment with valid data."""
        comment = Comment(
            comment_id=100,
            level=0,
            user="commenter",
            time_ago="3 hours ago",
            body="This is a test comment.",
            body_html="<p>This is a test comment.</p>",
        )
        assert comment.comment_id == 100
        assert comment.level == 0
        assert comment.user == "commenter"
        assert comment.time_ago == "3 hours ago"
        assert comment.body == "This is a test comment."
        assert comment.body_html == "<p>This is a test comment.</p>"

    def test_comment_repr(self):
        """Test Comment __repr__."""
        comment = Comment(
            comment_id=200, level=1, user="u",
            time_ago="1h", body="b", body_html="bh",
        )
        assert repr(comment) == '<Comment: ID=200>'

    def test_comment_validation_error(self):
        """Test that Comment raises ValidationError for invalid data."""
        with pytest.raises(ValidationError):
            Comment(
                comment_id="bad",  # invalid
                level=0,
                user="u",
                time_ago="t",
                body="b",
                body_html="bh",
            )

    def test_comment_deleted(self):
        """Test representing a deleted comment."""
        comment = Comment(
            comment_id=-1,
            level=0,
            user="",
            time_ago="",
            body="[deleted]",
            body_html="[deleted]",
        )
        assert comment.comment_id == -1
        assert comment.body == "[deleted]"


class TestUserModel:
    """Tests for the User Pydantic model."""

    def test_user_creation(self):
        """Test creating a User with valid data."""
        user = User(
            username="testuser",
            date_created="2010-01-01",
            karma="12345",
            avg="10.5",
        )
        assert user.username == "testuser"
        assert user.date_created == "2010-01-01"
        assert user.karma == "12345"
        assert user.avg == "10.5"

    def test_user_repr(self):
        """Test User __repr__."""
        user = User(
            username="alice",
            date_created="2020-01-01",
            karma="999",
            avg="8.0",
        )
        assert repr(user) == 'alice 999 8.0'

    def test_user_validation_error(self):
        """Test that User raises ValidationError when required fields are missing."""
        with pytest.raises(ValidationError):
            User(username="onlyuser")
