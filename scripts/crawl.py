import argparse
import itertools
import re
import sys
import time

import requests

LIST_RE = re.compile(r'<a rel:gtrack_id="post/title" .*? href="(.*?)" .*?>'
                     r'((the(se)? )?(top )?\d+ .*?)'
                     r'</a>', re.IGNORECASE)
PAGE_URL = 'http://www.buzzfeed.com/index/paging?r=1&p={}'

SHARE_SOURCES = ('facebook', 'twitter', 'email', ) # order of share numbers
SHARES_RE = re.compile(r'<div class="num">(.*?)</div>')
VIEWS_RE = re.compile(r'<span class="value" id="buzz_stats_impression_totals">(.*?)</span>')


class BuzzfeedList:
    def __init__(self, title, url):
        self.title = title
        self.url = url

        # first number in title:
        numbers = re.findall(r'\b\d+\b', title)
        self.n = int(numbers[0])

    def __repr__(self):
        return 'BuzzfeedList({}, {})'.format(repr(self.title), repr(self.url))


def parse_number(s):
    s = s.replace(',', '')
    if s.lower()[-1] == 'm':
        k = 1000000
        s = s[:-1]
    elif s.lower()[-1] == 'k':
        k = 1000
        s = s[:-1]
    else:
        k = 1
    return int(s) * k

def lists(lines):
    for line in lines:
        for match in LIST_RE.findall(line):
            yield BuzzfeedList(match[1], match[0])

def load_stats(article):
    article.views = article.facebook = article.twitter = article.emails = None

    url = 'http://www.buzzfeed.com' + article.url
    print(url, file=sys.stderr)
    lines = requests.get(url).text.splitlines()
    shares = []
    for line in lines:
        for match in VIEWS_RE.findall(line):
            article.views = parse_number(match)
        for match in SHARES_RE.findall(line):
            shares.append(parse_number(match))

    if article.views is None:
        print('no total views stat', file=sys.stderr)

    if len(shares) == len(SHARE_SOURCES):
        shares = dict(zip(SHARE_SOURCES, shares))
        article.facebook = shares['facebook']
        article.twitter = shares['twitter']
        article.emails = shares['email']
    else:
        print('expected {} share divs, but found {}'.format(len(SHARE_SOURCES), len(shares)), file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', type=int, default=1,
                        help='resume from a particular page')
    args = parser.parse_args()

    columns = ('title', 'url', 'n', 'views', 'facebook', 'twitter', 'emails')
    print('\t'.join(columns)) # column name header

    urls = set()
    for i in itertools.count(args.page):
        url = PAGE_URL.format(i)
        print(url, file=sys.stderr)
        lines = requests.get(url).text.splitlines()
        for l in lists(lines):
            if l.url in urls:
                print('duplicate url', l.url, file=sys.stderr)
            else:
                urls.add(l.url)

                time.sleep(0.5)
                load_stats(l)

                values = (getattr(l, k) for k in columns)
                print('\t'.join(str(x) if x is not None else '' for x in values))
        print(len(urls), 'lists', file=sys.stderr)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
