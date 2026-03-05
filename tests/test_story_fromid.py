from hn import constants


def test_from_id_constructor(live_story):
    """
    Tests whether or not the constructor fromid works or not
    by testing the returned Story.
    """
    assert live_story.story_id > 0
    assert bool(live_story.submitter)
    assert bool(live_story.title)
    assert live_story.comments_link == f'{constants.BASE_URL}/item?id={live_story.story_id}'


def test_comment_for_fromid(live_story):
    """
    Tests if the comment scraping works for fromid or not.
    """
    comments = live_story.get_comments()
    assert len(comments) > 0
    assert comments[0].comment_id != 0
    assert comments[0].level >= 0


def test_from_id_new_html(live_story):
    """
    Tests fromid with the current HN HTML structure.
    """
    assert bool(live_story.title)
    assert bool(live_story.submitter)
    assert live_story.points >= 0
    assert isinstance(live_story.is_self, bool)
    assert live_story.num_comments >= 0
    assert bool(live_story.domain)
