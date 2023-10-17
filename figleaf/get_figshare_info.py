"""
A script to grab category or author information from figshare records.
Prints the output to the terminal.
The results should be manually entered into "researcher_metadata_figshare.xlsx" (for now).

Get info for one or more categories like so:
python get_figshare_info.py -f categories -i Neurosciences not elsewhere classified, "Structural biology (incl. macromolecular modelling)"
(Double quotes may not be necessary with some shells. I'm using zsh.)

Get info for one or more authors like so: 
python get_figshare_info.py -f authors -i Virginia Scarlett, Ana Van Gulick -t 12345678910abcdefghijklm

To access figshare's records for the stage environment, include the -s flag and use your stage account token.
python get_figshare_info.py -s -f authors -i Virginia Scarlett, Ana Van Gulick -t 12345678910abcdefghijklm

Note that the same entity will have different IDs for the stage and production environments.
So, for example:
python get_figshare_info.py -f authors -i Virginia Scarlett -t <my production token> 
will yield different results from:
python get_figshare_info.py -f authors -i Virginia Scarlett -t <my stage token> -s
"""

import requests
import argparse
import json

def build_url(stage, field):
    u = ''
    if stage:
        u = 'https://api.figsh.com/v2/'
    else:
        u = 'https://api.figshare.com/v2/'
    if field == 'authors':
        u += 'account/authors/search?limit=1000'
    elif field == 'categories':
        u += 'categories'
    return(u)

def http_request(field, final_url, token = None):
    """ Do a GET or POST request to get all info for user requested item(s) """
    if field == 'authors':
        response = requests.post(final_url, headers = {'Authorization': 'token {}'.format(token)})
        response.raise_for_status()
    elif field == 'categories':
        response = requests.get(final_url)
        response.raise_for_status()
    return(response.json()) # a list of dicts

def filter_response(res, field):
    """ Filter http response for items of interest """
    final = []
    searchkey = 'full_name' if field == 'authors' else 'title'
    for d in res:
        if d[searchkey] in my_items:
            final.append(d)
    return(final)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
parser.add_argument('-i', 
                    '--items', 
                    required = True, 
                    help = 'Comma-separated list of author OR category names. Spaces are allowed.',
                    type=str,
                    nargs='+'
                    )
parser.add_argument('-f', 
                    '--field', 
                    required = True, 
                    help = 'What are you searching for? Choose one: authors or categories.',
                    choices = ['authors', 'categories']
                    )
parser.add_argument('-s', 
                    '--stage', 
                    help = 'If -s is included, script will grab info from the stage environment, not the production environment.',
                    action='store_true' # The store_true option automatically creates a default value of False.
                    )
parser.add_argument('-t', 
                    '--token', 
                    required = False, 
                    help = 'Personal token, most easily obtained through the figshare website. Required to get author info.'
                    )

if __name__ == "__main__":
    args = parser.parse_args()

    my_items = [e.strip() for e in " ".join(args.items).split(',')]
    url = build_url(args.stage, args.field)
    data = http_request(args.field, url, token = args.token)
    print(
        json.dumps( filter_response(data, args.field), indent = 4 )
    )
