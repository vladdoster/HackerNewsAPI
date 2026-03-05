import pytest
from pydantic import ValidationError

from hn import Story


def test_story_model_validates_input_types():
    with pytest.raises(ValidationError):
        Story(
            rank="not-an-int",
            story_id=1,
            title="title",
            link="https://example.com",
            domain="example.com",
            points=10,
            submitter="alice",
            published_time="1 hour ago",
            submitter_profile="https://news.ycombinator.com/user?id=alice",
            num_comments=5,
            comments_link="https://news.ycombinator.com/item?id=1",
            is_self=False,
        )
