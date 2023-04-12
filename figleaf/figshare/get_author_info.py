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
args = parser.parse_args()

full_names = [e.strip() for e in " ".join(args.authors).split(',')]

#This next line will need to be changed if we ever have more than 1000 users. Note limit=10000 fails.
url = 'https://api.figshare.com/v2/account/authors/search?limit=1000'
headers = {'Authorization': 'token {}'.format(args.token)}

response = requests.post(url, headers=headers)
response.raise_for_status()
#bug testing:
#response.status_code
#response.reason
data = response.json() # a list of dicts
final = []
for author in data:
    if author['full_name'] in full_names:
        final.append(author)

print(final)