def test_story_data_types(live_story):
    """
    Test types of fields of a Story object
    """
    assert isinstance(live_story.rank, int)
    assert isinstance(live_story.story_id, int)
    assert isinstance(live_story.title, str)
    assert isinstance(live_story.link, str)
    assert isinstance(live_story.domain, str)
    assert isinstance(live_story.points, int)
    assert isinstance(live_story.submitter, str)
    assert isinstance(live_story.published_time, str)
    assert isinstance(live_story.submitter_profile, str)
    assert isinstance(live_story.num_comments, int)
    assert isinstance(live_story.comments_link, str)
    assert isinstance(live_story.is_self, bool)


def test_story_submitter(live_story):
    """
    Tests the author name
    """
    assert bool(live_story.submitter)
