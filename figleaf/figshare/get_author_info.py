"""
A script to grab author information from figshare records.
Run like so:
python get_author_info.py -a Virginia Scarlett, Ana Van Gulick -t 12345678910abcdefghijklm
To get ids, etc. for stage account, run like so:
python get_author_info.py -s -a Virginia Scarlett, Ana Van Gulick -t 12345678910abcdefghijklm

# TODO: Combine this with get_category_info.py. Would like to have one script where I
# can grab author ids, category ids, group id, etc. just based on command line args.
"""

import requests
import argparse

parser = argparse.ArgumentParser(description='A script to grab author information from figshare records.')
parser.add_argument('-t', 
                    '--token', 
                    required = True, 
                    help = 'Personal token, most easily obtained through the figshare website.'
                    )
parser.add_argument('-a', 
                    '--authors', 
                    required = True, 
                    help = 'Comma-separated list of author FULL names. Spaces are allowed.',
                    type=str,
                    nargs='+'
                    )
parser.add_argument('-s', 
                    '--stage', 
                    help = 'If -s is included, script will grab info from the stage environment, not the production environment.',
                    action='store_true' # The store_true option automatically creates a default value of False.
                    )
args = parser.parse_args()

full_names = [e.strip() for e in " ".join(args.authors).split(',')]

#This next line will need to be changed if we ever have more than 1000 users. Note limit=10000 fails.
url = 'https://api.figshare.com/v2/account/authors/search?limit=1000'
if args.stage:
    url = 'https://api.figsh.com/v2/account/authors/search?limit=1000'
headers = {'Authorization': 'token {}'.format(args.token)}

# Get data for all authors
response = requests.post(url, headers=headers)
response.raise_for_status()
#bug testing:
#response.status_code
#response.reason
data = response.json() # a list of dicts

# Filter for authors of interest
final = []
for author in data:
    if author['full_name'] in full_names:
        final.append(author)

print(final)