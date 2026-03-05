from os import path

import requests

PRESETS_DIR = path.join(path.dirname(__file__), 'presets')
HN_API_BASE = 'https://hacker-news.firebaseio.com/v0'


def get_content(file):
    with open(path.join(PRESETS_DIR, file)) as f:
        return f.read()


def get_live_story_ids(limit=1, story_type='topstories'):
    response = requests.get(f'{HN_API_BASE}/{story_type}.json', timeout=10)
    response.raise_for_status()
    story_ids = response.json()[:limit]
    if not story_ids:
        raise RuntimeError(f'No live stories returned for "{story_type}"')
    return story_ids


def get_live_story_ids_with_comments(limit=1, min_comments=1, search_limit=50,
                                     story_type='topstories',
                                     require_submitter=False):
    story_ids = get_live_story_ids(limit=search_limit, story_type=story_type)
    matching_ids = []
    for story_id in story_ids:
        response = requests.get(f'{HN_API_BASE}/item/{story_id}.json',
                                timeout=10)
        response.raise_for_status()
        story_item = response.json() or {}
        if story_item.get('type') != 'story':
            continue
        if story_item.get('descendants', 0) < min_comments:
            continue
        if require_submitter and not story_item.get('by'):
            continue
        matching_ids.append(story_id)
        if len(matching_ids) == limit:
            return matching_ids
    raise RuntimeError('No matching live stories found')
