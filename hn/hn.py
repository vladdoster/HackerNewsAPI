"""
Hacker News API
Unofficial Python API for Hacker News.

@author Karan Goel
@email karan@goel.im
"""

import re

from pydantic import BaseModel

from .utils import get_soup, get_item_soup
from .constants import BASE_URL


class Comment(BaseModel):
    """
    Represents a comment on a post on HN
    """
    comment_id: int
    level: int
    user: str
    time_ago: str
    body: str
    body_html: str

    def __repr__(self):
        return f'<Comment: ID={self.comment_id}>'


class User(BaseModel):
    """
    Represents a User on HN
    """
    username: str
    date_created: str
    karma: str
    avg: str

    def __repr__(self):
        return f'{self.username} {self.karma} {self.avg}'


class Story(BaseModel):
    """
    Story class represents one single story on HN
    """
    rank: int
    story_id: int
    title: str
    link: str
    domain: str
    points: int
    submitter: str
    published_time: str
    submitter_profile: str
    num_comments: int
    comments_link: str
    is_self: bool

    def __repr__(self):
        return f'<Story: ID={self.story_id}>'

    def _build_comments(self, soup):
        """
        For the story, builds and returns a list of Comment objects.
        """

        comments = []

        comment_tree = soup.find('table', class_='comment-tree')
        if not comment_tree:
            return comments

        for row in comment_tree.find_all('tr', class_='athing'):
            try:
                comment_id = int(row.get('id'))
            except (TypeError, ValueError):
                continue

            ind_td = row.find('td', class_='ind')
            try:
                level = int(ind_td.get('indent', 0))
            except (TypeError, ValueError):
                level = 0

            user_a = row.find('a', class_='hnuser')
            if user_a:
                user = user_a.text
                age_span = row.find('span', class_='age')
                time_ago = age_span.find('a').text if age_span else ''
                commtext = row.find(class_='commtext')
                if commtext:
                    body = commtext.text
                    body_html = str(commtext)
                else:
                    body = ''
                    body_html = ''
            else:
                # deleted comment
                user = ''
                time_ago = ''
                comment_id = -1
                body = '[deleted]'
                body_html = '[deleted]'

            comment = Comment(comment_id=comment_id, level=level,
                              user=user, time_ago=time_ago,
                              body=body, body_html=body_html)
            comments.append(comment)

        return comments

    @classmethod
    def fromid(cls, item_id):
        """
        Initializes an instance of Story for given item_id.
        It is assumed that the story referenced by item_id is valid
        and does not raise any HTTP errors.
        item_id is an int.
        """
        if not item_id:
            raise Exception('Need an item_id for a story')
        # get details about a particular story
        soup = get_item_soup(item_id)

        # this post has not been scraped, so we explicitly get all info
        story_id = item_id
        rank = -1

        # to extract meta information about the post
        info_table = soup.find_all('table')[2]
        # [0] = title, domain, [1] = points, user, time, comments
        info_rows = info_table.find_all('tr')

        # title, domain
        titleline = info_table.find('span', class_='titleline')
        if titleline:
            # New HN HTML structure
            title = titleline.find('a').text
            sitebit = titleline.find('span', class_='sitebit')
            if sitebit:
                domain = sitebit.text.strip().strip('()')
                is_self = False
                link = titleline.find('a').get('href')
            else:
                domain = BASE_URL
                is_self = True
                link = f'{BASE_URL}/item?id={item_id}'
        else:
            # Old HN HTML structure
            title_row = info_rows[0].find_all('td')[1]
            title = title_row.find('a').text
            try:
                domain = title_row.find('span').string[2:-2]
                is_self = False
                link = title_row.find('a').get('href')
            except AttributeError:
                domain = BASE_URL
                is_self = True
                link = f'{BASE_URL}/item?id={item_id}'

        # points, user, time, comments
        subline = info_table.find('span', class_='subline')
        if subline:
            # New HN HTML structure
            points_span = subline.find('span', class_='score')
            points = int(re.match(r'^(\d+)\spoint.*',
                                  points_span.text).groups()[0])

            user_link = subline.find('a', class_='hnuser')
            submitter = user_link.text
            submitter_profile = f'{BASE_URL}/{user_link.get("href")}'

            age_span = subline.find('span', class_='age')
            published_time = age_span.find('a').text if age_span else ''

            comments_link = f'{BASE_URL}/item?id={item_id}'
            num_comments = 0
            for a_tag in subline.find_all('a'):
                match = re.match(r'(\d+)\s.*comment',
                                 a_tag.text.replace('\xa0', ' '))
                if match:
                    num_comments = int(match.groups()[0])
                    break
        else:
            # Old HN HTML structure
            meta_row = info_rows[1].find_all('td')[1].contents
            points = int(re.match(r'^(\d+)\spoint.*',
                                  meta_row[0].text).groups()[0])
            submitter = meta_row[2].text
            submitter_profile = f'{BASE_URL}/{meta_row[2].get("href")}'
            published_time = ' '.join(meta_row[3].strip().split()[:3])
            comments_link = f'{BASE_URL}/item?id={item_id}'
            try:
                num_comments = int(re.match(r'(\d+)\s.*', meta_row[
                    4].text).groups()[0])
            except AttributeError:
                num_comments = 0
        story = Story(rank=rank, story_id=story_id, title=title, link=link,
                      domain=domain, points=points, submitter=submitter,
                      published_time=published_time,
                      submitter_profile=submitter_profile,
                      num_comments=num_comments,
                      comments_link=comments_link, is_self=is_self)
        return story

    def get_comments(self):
        """
        Returns a list of Comment(s) for the given story
        """
        soup = get_item_soup(self.story_id)
        return self._build_comments(soup)


class HN:
    """
    The class that parses the HN page, and builds up all stories
    """

    def __init__(self):
        self.more = ''

    def _get_zipped_rows(self, soup):
        """
        Returns all 'tr' tag rows as a list of tuples. Each tuple is for
        a single story.
        """
        # the table with all submissions
        table = soup.find_all('table')[2]
        all_rows = table.find_all(['tr'])
        # info rows: class includes 'athing'
        info = [r for r in all_rows if 'athing' in (r.get('class') or [])]
        # detail rows: td.subtext is present (or no class, follows an athing row)
        detail = [r for r in all_rows if r.find('td', class_='subtext')]

        # build a list of tuple for all post
        return zip(info, detail)

    def _build_story(self, all_rows):
        """
        Builds and returns a list of stories (dicts) from the passed source.
        """
        # list to hold all stories
        all_stories = []

        for (info, detail) in all_rows:

            #-- Get the info about a story --#
            info_cells = info.find_all('td')

            rank_span = info_cells[0].find('span', class_='rank')
            try:
                rank = int(rank_span.text.rstrip('.'))
            except (AttributeError, ValueError):
                rank = -1

            titleline = info_cells[2].find('span', class_='titleline')
            title = titleline.find('a').text
            link = titleline.find('a').get('href')

            # by default all stories are linking posts
            is_self = False

            if 'item?id=' not in link:
                sitebit = titleline.find('span', class_='sitebit')
                if sitebit:
                    sitestr = sitebit.find('span', class_='sitestr')
                    domain = sitestr.text if sitestr else ''
                else:
                    domain = ''
            else:
                link = f'{BASE_URL}/{link}'
                domain = BASE_URL
                is_self = True
            #-- Get the info about a story --#

            #-- Get the detail about a story --#
            detail_cell = detail.find('td', class_='subtext')
            subline = detail_cell.find('span', class_='subline') if detail_cell else None

            num_comments = 0

            if subline:
                # can be a link or self post
                score_span = subline.find('span', class_='score')
                if score_span:
                    points = int(re.match(r'^(\d+)\s', score_span.text).group(1))
                else:
                    points = 0

                user_a = subline.find('a', class_='hnuser')
                submitter = user_a.text if user_a else ''
                submitter_profile = f'{BASE_URL}/{user_a.get("href")}' if user_a else ''

                age_span = subline.find('span', class_='age')
                published_time = age_span.find('a').text if age_span else ''

                story_id = -1
                comments_link = ''
                for a_tag in subline.find_all('a'):
                    href = a_tag.get('href', '')
                    m = re.match(r'item\?id=(\d+)', href)
                    if m:
                        story_id = int(m.group(1))
                        comment_match = re.match(r'(\d+)\s', a_tag.text)
                        if comment_match:
                            num_comments = int(comment_match.group(1))
                            comments_link = f'{BASE_URL}/item?id={story_id}'
                if not comments_link and story_id != -1:
                    comments_link = f'{BASE_URL}/item?id={story_id}'
            else:
                # this is a job post
                points = 0
                submitter = ''
                submitter_profile = ''
                published_time = detail_cell.text.strip() if detail_cell else ''
                try:
                    story_id = int(re.match(r'.*=(\d+)', link).groups()[0])
                except AttributeError:
                    # job listing that points to external link
                    story_id = -1
                comments_link = ''
            #-- Get the detail about a story --#

            story = Story(rank=rank, story_id=story_id, title=title,
                          link=link, domain=domain, points=points,
                          submitter=submitter,
                          published_time=published_time,
                          submitter_profile=submitter_profile,
                          num_comments=num_comments,
                          comments_link=comments_link, is_self=is_self)

            all_stories.append(story)

        return all_stories

    def get_stories(self, story_type='', limit=30):
        """
        Yields a list of stories from the passed page
        of HN.
        'story_type' can be:
        \t'' = top stories (homepage) (default)
        \t'news2' = page 2 of top stories
        \t'newest' = most recent stories
        \t'best' = best stories

        'limit' is the number of stories required from the given page.
        Defaults to 30. Cannot be more than 30.
        """
        if limit is None or limit < 1 or limit > 30:
            # we need at least 30 items
            limit = 30

        stories_found = 0
        # while we still have more stories to find
        while stories_found < limit:
            # get current page soup
            soup = get_soup(page=story_type)
            all_rows = self._get_zipped_rows(soup)
            # get a list of stories on current page
            stories = self._build_story(all_rows)

            for story in stories:
                yield story
                stories_found += 1

                # if enough stories found, return
                if stories_found == limit:
                    return

    def get_leaders(self, limit=10):
        """ Return the leaders of Hacker News """
        if limit is None:
            limit = 10
        soup = get_soup('leaders')
        table = soup.find('table')
        leaders_table = table.find_all('table')[1]
        leader_rows = leaders_table.find_all('tr', class_='athing')
        for i, leader in enumerate(leader_rows):
            if i == limit:
                return
            item = leader.find_all('td')
            user_a = item[1].find('a', class_='hnuser') if len(item) > 1 else None
            username = user_a.text if user_a else item[1].text
            karma = item[2].text if len(item) > 2 else ''
            yield User(username=username, date_created='', karma=karma, avg='')
