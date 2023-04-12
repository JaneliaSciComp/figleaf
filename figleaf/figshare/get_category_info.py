"""
A script to grab category information from figshare records.
From a Mac (zsh shell), run like so:
python get_category_info.py -c Neurosciences not elsewhere classified, "Structural biology (incl. macromolecular modelling)"
(Double quotes may not be necessary with other shells, e.g. bash.)
Output looks like this:
[{'is_selectable': True, 'has_children': False, 'id': 24169, 'title': 'Structural biology (incl. macromolecular modelling)', 'parent_id': 24133, 'path': '/24130/24133/24169', 'source_id': '310112', 'taxonomy_id': 100}, {'is_selectable': True, 'has_children': False, 'id': 24748, 'title': 'Neurosciences not elsewhere classified', 'parent_id': 24724, 'path': '/24457/24724/24748', 'source_id': '320999', 'taxonomy_id': 100}]
"""

import requests
import argparse

parser = argparse.ArgumentParser(description='A script to grab category information from figshare records.')
parser.add_argument('-c', 
                    '--categories', 
                    required = True, 
                    help = 'Comma-separated list of category names. Spaces are allowed. If category contains parentheses and you are using the zsh shell (Mac OS), enclose it in double quotes.',
                    type=str,
                    nargs='+'
                    )
args = parser.parse_args()

my_categories = [e.strip() for e in " ".join(args.categories).split(',')]
#print(my_categories)
url = 'https://api.figshare.com/v2/categories'

response = requests.get(url)#
response.raise_for_status()
#bug testing:
#response.status_code
#response.reason
data = response.json() # a list of dicts
final = []
for category in data:
    if category['title'] in my_categories:
        final.append(category)

print(final)