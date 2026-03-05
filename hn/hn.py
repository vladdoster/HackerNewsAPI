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
        anchor = table.find_all(['tr'])[-1].find('a')
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
            rows = table.find_all(['tr'])
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

                    comment_cell = row.find_all('td')[3]
                    header_span = comment_cell.find('span', class_='comhead')
                    comment_span = comment_cell.find(
                        'span', class_=re.compile(r'(commtext|comment)'))

                    if header_span and str(header_span) != '<span class="comhead"></span>':
                        user_link = header_span.find('a', class_='hnuser')
                        user = user_link.text if user_link else ''

                        age_span = header_span.find('span', class_='age')
                        if age_span and age_span.find('a'):
                            time_ago = age_span.find('a').text
                            comment_href = age_span.find('a').get('href')
                        else:
                            time_ago = ''
                            comment_href = ''
                            for anchor in header_span.find_all('a'):
                                href = anchor.get('href')
                                if href and 'item?id=' in href:
                                    comment_href = href
                                    break

                        match = re.match(r'.*item\?id=(\d+)', comment_href)
                        if match:
                            comment_id = int(match.groups()[0])
                        else:
                            togg_anchor = header_span.find(
                                'a', class_=re.compile(r'togg'))
                            togg_id = togg_anchor.get('id') if togg_anchor else ''
                            if togg_id and togg_id.isdigit():
                                comment_id = int(togg_id)
                            else:
                                continue

                        # text representation of comment (unformatted)
                        body = comment_span.text if comment_span else ''

                        if body[-2:] == '--':
                            body = body[:-5]

                        # html of comment, may not be valid
                        body_html = comment_span.decode_contents() if comment_span else ''

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
        # get all rows but last 2
        rows = table.find_all(['tr'])[:-2]
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
            if 'item?id=' not in link:
                # slice " (abc.com) "
                comhead = info_cells[2].find('span', class_='comhead')
                domain = comhead.string[2:-2] if comhead and comhead.string else ''
            else:
                link = f'{BASE_URL}/{link}'
                domain = BASE_URL
                is_self = True
            #-- Get the info about a story --#

            #-- Get the detail about a story --#
            story_id = None
            info_id = info.get('id')
            if info_id:
                try:
                    story_id = int(info_id)
                except (TypeError, ValueError):
                    story_id = None

            # split in 2 cells, we need only second
            detail_cell = detail.find_all('td')[1]
            # list of details we need, 5 count
            detail_concern = detail_cell.contents

            num_comments = -1

            subline = detail_cell.find('span', class_='subline')
            if subline:
                points_span = subline.find('span', class_='score')
                if points_span:
                    points = int(re.match(r'^(\d+)\spoint.*',
                                          points_span.text).groups()[0])
                else:
                    points = 0

                user_link = subline.find('a', class_='hnuser')
                if user_link:
                    submitter = user_link.text
                    submitter_profile = f'{BASE_URL}/{user_link.get("href")}'
                else:
                    submitter = ''
                    submitter_profile = ''

                age_span = subline.find('span', class_='age')
                published_time = age_span.find('a').text if age_span else ''

                if story_id is None and age_span and age_span.find('a'):
                    story_match = re.match(r'.*item\?id=(\d+)',
                                           age_span.find('a').get('href'))
                    if story_match:
                        story_id = int(story_match.groups()[0])

                comments_link = f'{BASE_URL}/item?id={story_id}' if story_id is not None else ''
                num_comments = 0
                for a_tag in subline.find_all('a'):
                    text = a_tag.text.replace('\xa0', ' ')
                    match = re.match(r'(\d+)\s.*comment', text)
                    if match:
                        num_comments = int(match.groups()[0])
                        comments_link = f'{BASE_URL}/{a_tag.get("href")}'
                        break
            elif re.match(r'^(\d+)\spoint.*', detail_concern[0].string) is not \
                    None:
                # can be a link or self post
                points = int(re.match(r'^(\d+)\spoint.*', detail_concern[
                    0].string).groups()[0])
                submitter = '%s' % detail_concern[2].string
                submitter_profile = f'{BASE_URL}/{detail_concern[2].get("href")}'
                published_time = ' '.join(detail_concern[3].strip().split()[
                                          :3])
                comment_tag = detail_concern[4]
                if story_id is None:
                    story_id = int(re.match(r'.*=(\d+)', comment_tag.get(
                        'href')).groups()[0])
                comments_link = f'{BASE_URL}/item?id={story_id}'
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
