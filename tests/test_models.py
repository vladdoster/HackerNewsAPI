"""
Unit tests for Pydantic models (Story, Comment, User).
These tests validate the Pydantic model behavior without requiring HTTP mocking.
"""

import pytest
from pydantic import ValidationError

from hn import Story, Comment, User


class TestStoryModel:
    def test_story_creation(self):
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
        story = Story(
            rank=1,
            story_id=456,
            title="Test",
            link="https://example.com",
            domain="example.com",
            points=10,
            submitter="user",
            published_time="1 hour ago",
            submitter_profile="https://news.ycombinator.com/user?id=user",
            num_comments=5,
            comments_link="https://news.ycombinator.com/item?id=456",
            is_self=False,
        )
        assert repr(story) == "<Story: ID=456>"

    def test_story_validation_error_missing_field(self):
        with pytest.raises(ValidationError):
            Story(rank=1, story_id=123, title="Test")

    def test_story_self_post(self):
        story = Story(
            rank=1,
            story_id=789,
            title="Ask HN: Something",
            link="https://news.ycombinator.com/item?id=789",
            domain="https://news.ycombinator.com",
            points=50,
            submitter="askuser",
            published_time="3 hours ago",
            submitter_profile="https://news.ycombinator.com/user?id=askuser",
            num_comments=20,
            comments_link="https://news.ycombinator.com/item?id=789",
            is_self=True,
        )
        assert story.is_self is True


class TestCommentModel:
    def test_comment_creation(self):
        comment = Comment(
            comment_id=100,
            level=0,
            user="commenter",
            time_ago="1 hour ago",
            body="This is a comment",
            body_html="<p>This is a comment</p>",
        )
        assert comment.comment_id == 100
        assert comment.level == 0
        assert comment.user == "commenter"
        assert comment.time_ago == "1 hour ago"
        assert comment.body == "This is a comment"
        assert comment.body_html == "<p>This is a comment</p>"

    def test_comment_repr(self):
        comment = Comment(
            comment_id=200,
            level=1,
            user="user",
            time_ago="2 hours ago",
            body="body",
            body_html="<p>body</p>",
        )
        assert repr(comment) == "<Comment: ID=200>"

    def test_comment_validation_error(self):
        with pytest.raises(ValidationError):
            Comment(comment_id="not_an_int", level=0, user="u")

    def test_deleted_comment(self):
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
    def test_user_creation(self):
        user = User(
            username="testuser",
            date_created="2020-01-01",
            karma="1000",
            avg="10.5",
        )
        assert user.username == "testuser"
        assert user.date_created == "2020-01-01"
        assert user.karma == "1000"
        assert user.avg == "10.5"

    def test_user_repr(self):
        user = User(
            username="john",
            date_created="",
            karma="500",
            avg="8.2",
        )
        assert repr(user) == "john 500 8.2"

    def test_user_validation_error(self):
        with pytest.raises(ValidationError):
            User(username="test")
