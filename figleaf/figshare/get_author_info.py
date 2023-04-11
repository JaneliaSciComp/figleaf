import requests
import argparse

parser = argparse.ArgumentParser(description='A script to grab author information from figshare records.')
parser.add_argument('-t', 
                    '--token', 
                    required = True, 
                    help = 'Personal token, most easily obtained through the figshare website.',
                    )
args = parser.parse_args()

url = 'https://api.figshare.com/v2/account/authors/search?limit=10000'
headers = {
     'Authorization': 'token {}'.format(args.token)
     }

response = requests.post(url, headers=headers)
response.raise_for_status()

#TODO: filter json author list to contain only the authors you want