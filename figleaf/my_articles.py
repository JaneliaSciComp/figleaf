''' my_articles.py
    Return my articles from FigShare
'''

import argparse
from operator import attrgetter
import os
import sys
import requests
import jrc_common.jrc_common as JRC

# Globals
MAX = {'doi': 3, 'title': 5, 'type': 4, 'size': 4, 'views': 5}
TOKEN = "FIGSHARE_JWT"

def terminate_program(msg=None):
    """ Log an optional error to output, close files, and exit
        Keyword arguments:
          err: error message
        Returns:
          None
    """
    if msg:
        LOGGER.critical(msg)
    sys.exit(-1 if msg else 0)


def call_responder(server, endpoint):
    """ Call a REST API
        Keyword arguments:
          server: server name
          endpoint: endpoint
        Returns:
          JSON
    """
    url = attrgetter(f"{server}.url")(REST) + endpoint
    try:
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + os.environ[TOKEN]}
        req = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as err:
        terminate_program(err)
    if req.status_code != 200:
        terminate_program(f"{url}\nStatus: {str(req.status_code)}")
    return req.json()


def humansize(num, suffix='B'):
    ''' Return a human-readable storage size
        Keyword arguments:
          num: size
          suffix: default suffix
        Returns:
          string
    '''
    for unit in ['', 'K', 'M', 'G', 'T']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"


def process_row(row):
    """ Log an optional error to output, close files, and exit
        Keyword arguments:
          row: article row
        Returns:
          List of title, type, published, DOI
    """
    if len(row['title']) > MAX['title']:
        MAX['title'] = len(row['title'])
    if len(row['defined_type_name']) > MAX['type']:
        MAX['type'] = len(row['defined_type_name'])
    doi = row['doi'] if 'doi' in row and row['doi'] else ''
    if len(doi) > MAX['doi']:
        MAX['doi'] = len(doi)
    size = views = 0
    if row['published_date']:
        # Get article details
        result = call_responder('figshare', f"articles/{row['id']}")
        if "files" in result:
            for file in result['files']:
                if "size" in file:
                    size += file['size']
        size = humansize(size)
        if len(size) > MAX['size']:
            MAX['size'] = len(size)
        # Views
        result = call_responder('figshare_stats', f"total/views/article/{row['id']}")
        if "totals" in result:
            views = result['totals']
        views = f"{views:,}"
        if len(views) > MAX['views']:
            MAX['views'] = len(views)
    if not size:
        size = "-"
    return [row['title'], row['defined_type_name'],
            'Yes' if row['published_date'] else 'No', doi, size, views]


def process_articles():
    """ Find and display articles for one user
        Keyword arguments:
          None
        Returns:
          None
    """
    page = 1
    article = []
    while True:
        result = call_responder('figshare', \
                                f"account/articles?page={page}&page_size=100")
        if not result:
            break
        for row in result:
            if ARG.PUBLISHED and ('published_date' not in row or not row['published_date']):
                continue
            article.append(process_row(row))
        page += 1
    print(f"{'Title':<{MAX['title']}}  {'Type':<{MAX['type']}}  " \
          + f"Published  {'DOI':<{MAX['doi']}}  {'Size':<{MAX['size']}}  {'Views':<{MAX['views']}}")
    print(f"{'-'*MAX['title']}  {'-'*MAX['type']}  {'-'*9}  {'-'*MAX['doi']}  {'-'*MAX['size']}  " \
          + f"{'-'*MAX['views']}")
    for row in article:
        print(f"{row[0]:<{MAX['title']}}  {row[1]:<{MAX['type']}}  " \
              + f"{row[2]:^9}  {row[3]:<{MAX['doi']}}  {row[4]:<{MAX['size']}}  " \
              + f"{row[5]:<{MAX['views']}}")

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Get my FigShare articles')
    PARSER.add_argument('--published', action='store_true', dest='PUBLISHED',
                        default=False, help='Show only published articles')
    PARSER.add_argument('--verbose', action='store_true', dest='VERBOSE',
                        default=False, help='Turn on verbose output')
    PARSER.add_argument('--debug', action='store_true', dest='DEBUG',
                        default=False, help='Turn on debug output')
    ARG = PARSER.parse_args()
    LOGGER = JRC.setup_logging(ARG)
    if TOKEN not in os.environ:
        terminate_program(f"Missing token - set in {TOKEN} environment variable")
    REST = JRC.get_config("rest_services")
    process_articles()
    terminate_program()
