#!/usr/bin/env python

"""
Hacker News API
Unofficial Python API for Hacker News.

@author Karan Goel
@email karan@goel.im
"""

import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .utils import get_soup, get_item_soup
from .constants import BASE_URL


class Comment(BaseModel):
    """
    Represents a comment on a post on HN
    """
    model_config = ConfigDict(from_attributes=True)

    comment_id: int  # the comment's item id
    level: int  # comment's nesting level
    user: str  # user's name who submitted the post
    time_ago: str  # time when it was submitted
    body: str  # text representation of comment (unformatted)
    body_html: str  # html of comment, may not be valid

    def __repr__(self):
        return '<Comment: ID={0}>'.format(self.comment_id)


class User(BaseModel):
    """
    Represents a User on HN
    """
    model_config = ConfigDict(from_attributes=True)

    username: str
    date_created: str
    karma: str
    avg: str

    def __repr__(self):
        return '{0} {1} {2}'.format(self.username, self.karma, self.avg)


class Story(BaseModel):
    """
    Story class represents one single story on HN
    """
    model_config = ConfigDict(from_attributes=True)

    rank: int  # the rank of story on the page
    story_id: int  # the story's id
    title: str  # the title of the story
    link: str  # the url it points to (None for self posts)
    domain: str  # the domain of the link (None for self posts)
    points: int  # the points/karma on the story
    submitter: str  # the user who submitted the story
    published_time: str  # publish time of story
    submitter_profile: str  # link to submitter profile
    num_comments: int  # the number of comments it has
    comments_link: str  # the link to the comments page
    is_self: bool  # True if a self post

    def __repr__(self):
        return '<Story: ID={0}>'.format(self.story_id)

    def _get_next_page(self, soup, current_page):
        """
        Get the relative url of the next page (The "More" link at
        the bottom of the page)
        """

        # Get the table with all the comments:
        if current_page == 1:
            table = soup.find_all('table')[3]
        elif current_page > 1:
            table = soup.find_all('table')[2]

        # the last row of the table contains the relative url of the next page
        anchor = table.find_all('tr')[-1].find('a')
        if anchor and anchor.text == 'More':
            return anchor.get('href').lstrip(BASE_URL)
        else:
            return None

    def _build_comments(self, soup):
        """
        For the story, builds and returns a list of Comment objects.
        """

        comments = []
        current_page = 1

        while True:
            # Get the table holding all comments:
            if current_page == 1:
                table = soup.find_all('table')[3]
            elif current_page > 1:
                table = soup.find_all('table')[2]
            # get all rows (each comment is duplicated twice)
            rows = table.find_all('tr')
            # last row is more, second last is spacing
            rows = rows[:len(rows) - 2]
            # now we have unique comments only
            rows = [row for i, row in enumerate(rows) if (i % 2 == 0)]

            if len(rows) > 1:
                for row in rows:

                    # skip an empty td
                    if not row.find_all('td'):
                        continue

                    # Builds a flat list of comments

                    # level of comment, starting with 0
                    level = int(row.find_all('td')[1].find('img').get(
                        'width')) // 40

                    spans = row.find_all('td')[3].find_all('span')
                    # span[0] = submitter details
                    # [<a href="user?id=jonknee">jonknee</a>, ' 1 hour ago  | ', <a href="item?id=6910978">link</a>]
                    # span[1] = actual comment

                    if str(spans[0]) != '<span class="comhead"></span>':
                        # user who submitted the comment
                        user = spans[0].contents[0].string
                        # relative time of comment
                        time_ago = spans[0].contents[1].string.strip(
                        ).rstrip(' |')
                        try:
                            comment_id = int(re.match(r'item\?id=(.*)',
                                                      spans[0].contents[
                                                          2].get(
                                                          'href')).groups()[0])
                        except AttributeError:
                            comment_id = int(re.match(r'%s/item\?id=(.*)' %
                                                      BASE_URL,
                                                      spans[0].contents[
                                                          2].get(
                                                          'href')).groups()[0])

                        # text representation of comment (unformatted)
                        body = spans[1].text

                        if body[-2:] == '--':
                            body = body[:-5]

                        # html of comment, may not be valid
                        try:
                            pat = re.compile(
                                r'<span class="comment"><font color=".*">(.*)</font></span>')
                            body_html = re.match(pat, str(spans[1]).replace(
                                '\n', '')).groups()[0]
                        except AttributeError:
                            pat = re.compile(
                                r'<span class="comment"><font color=".*">(.*)</font></p><p><font size="1">')
                            body_html = re.match(pat, str(spans[1]).replace(
                                '\n', '')).groups()[0]

                    else:
                        # comment deleted
                        user = ''
                        time_ago = ''
                        comment_id = -1
                        body = '[deleted]'
                        body_html = '[deleted]'

                    comment = Comment(comment_id=comment_id, level=level,
                                      user=user, time_ago=time_ago,
                                      body=body, body_html=body_html)
                    comments.append(comment)

            # Move on to the next page of comments, or exit the loop if there
            # is no next page.
            next_page_url = self._get_next_page(soup, current_page)
            if not next_page_url:
                break

            soup = get_soup(page=next_page_url)
            current_page += 1

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
        title_row = info_rows[0].find_all('td')[1]
        title = title_row.find('a').text
        try:
            domain = title_row.find('span').string[2:-2]
            # domain found
            is_self = False
            link = title_row.find('a').get('href')
        except AttributeError:
            # self post
            domain = BASE_URL
            is_self = True
            link = '%s/item?id=%s' % (BASE_URL, item_id)

        # points, user, time, comments
        meta_row = info_rows[1].find_all('td')[1].contents
        # [<span id="score_7024626">789 points</span>, ' by ', <a href="user?id=endianswap">endianswap</a>,
        # ' 8 hours ago  | ', <a href="item?id=7024626">238 comments</a>]

        points = int(re.match(r'^(\d+)\spoint.*', meta_row[0].text).groups()[0])
        submitter = meta_row[2].text
        submitter_profile = '%s/%s' % (BASE_URL, meta_row[2].get('href'))
        published_time = ' '.join(meta_row[3].strip().split()[:3])
        comments_link = '%s/item?id=%s' % (BASE_URL, item_id)
        try:
            num_comments = int(re.match(r'(\d+)\s.*', meta_row[
                4].text).groups()[0])
        except AttributeError:
            num_comments = 0
        story = Story(rank=rank, story_id=story_id, title=title, link=link,
                      domain=domain, points=points, submitter=submitter,
                      published_time=published_time,
                      submitter_profile=submitter_profile,
                      num_comments=num_comments, comments_link=comments_link,
                      is_self=is_self)
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
        # get all rows but last 2
        rows = table.find_all('tr')[:-2]
        # remove the spacing rows
        # indices of spacing tr's
        spacing = range(2, len(rows), 3)
        rows = [row for (i, row) in enumerate(rows) if (i not in spacing)]
        # rank, title, domain
        info = [row for (i, row) in enumerate(rows) if (i % 2 == 0)]
        # points, submitter, comments
        detail = [row for (i, row) in enumerate(rows) if (i % 2 != 0)]

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
            # split in 3 cells
            info_cells = info.find_all('td')

            rank = int(info_cells[0].string[:-1])
            title = '%s' % info_cells[2].find('a').string
            link = info_cells[2].find('a').get('href')

            # by default all stories are linking posts
            is_self = False

            # the link doesn't contain "http" meaning an internal link
            if link.find('item?id=') == -1:
                # slice " (abc.com) "
                domain = info_cells[2].find('span').string[2:-2]
            else:
                link = '%s/%s' % (BASE_URL, link)
                domain = BASE_URL
                is_self = True
            #-- Get the info about a story --#

            #-- Get the detail about a story --#
            # split in 2 cells, we need only second
            detail_cell = detail.find_all('td')[1]
            # list of details we need, 5 count
            detail_concern = detail_cell.contents

            num_comments = -1

            if re.match(r'^(\d+)\spoint.*', detail_concern[0].string) is not \
                    None:
                # can be a link or self post
                points = int(re.match(r'^(\d+)\spoint.*', detail_concern[
                    0].string).groups()[0])
                submitter = '%s' % detail_concern[2].string
                submitter_profile = '%s/%s' % (BASE_URL, detail_concern[
                    2].get('href'))
                published_time = ' '.join(detail_concern[3].strip().split()[
                                          :3])
                comment_tag = detail_concern[4]
                story_id = int(re.match(r'.*=(\d+)', comment_tag.get(
                    'href')).groups()[0])
                comments_link = '%s/item?id=%d' % (BASE_URL, story_id)
                comment_count = re.match(r'(\d+)\s.*', comment_tag.string)
                try:
                    # regex matched, cast to int
                    num_comments = int(comment_count.groups()[0])
                except AttributeError:
                    # did not match, assign 0
                    num_comments = 0
            else:
                # this is a job post
                points = 0
                submitter = ''
                submitter_profile = ''
                published_time = '%s' % detail_concern[0]
                comment_tag = ''
                try:
                    story_id = int(re.match(r'.*=(\d+)', link).groups()[0])
                except AttributeError:
                    # job listing that points to external link
                    story_id = -1
                comments_link = ''
                comment_count = -1
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
        listleaders = leaders_table.find_all('tr')[2:]
        listleaders.pop(10)  # Removing because empty in the Leaders page
        for i, leader in enumerate(listleaders):
            if i == limit:
                return
            if not leader.text == '':
                item = leader.find_all('td')
                yield User(username=item[1].text, date_created='',
                           karma=item[2].text, avg=item[3].text)
