"""Pytest configuration for the tests package."""

import requests
import pytest

from hn import Story

HN_API_BASE = 'https://hacker-news.firebaseio.com/v0'


def _get_json(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def _get_live_story_id(endpoint='topstories', min_descendants=1):
    story_ids = _get_json(f'{HN_API_BASE}/{endpoint}.json')
    for story_id in story_ids:
        item = _get_json(f'{HN_API_BASE}/item/{story_id}.json')
        if not item:
            continue
        if item.get('type') != 'story':
            continue
        if item.get('deleted') or item.get('dead'):
            continue
        if item.get('descendants', 0) < min_descendants:
            continue
        return story_id
    return None


@pytest.fixture()
def live_story():
    try:
        story_id = _get_live_story_id(endpoint='topstories', min_descendants=1)
    except requests.RequestException as exc:
        pytest.skip(f'Unable to fetch live Hacker News stories: {exc}')

    if not story_id:
        pytest.skip('No suitable live Hacker News story found')

    return Story.fromid(story_id)


@pytest.fixture()
def live_story_with_many_comments():
    try:
        story_id = _get_live_story_id(endpoint='beststories',
                                      min_descendants=120)
    except requests.RequestException as exc:
        pytest.skip(f'Unable to fetch live Hacker News stories: {exc}')

    if not story_id:
        pytest.skip('No suitable high-comment live story found')

    return Story.fromid(story_id)
