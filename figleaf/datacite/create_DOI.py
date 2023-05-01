"""
This script is unfinished. Need to troubleshoot. Will (eventually) create a DOI through the DataCite REST API.
"""

import requests
import argparse

parser = argparse.ArgumentParser(description='A script to create a new DOI record.')

parser.add_argument('-t', 
                    '--token', 
                    required = True, 
                    help = 'Must be of the format Account.Repository:Password. E.g. ABCD.EFGHIJ:kLM012N3op4Qr'
                    )
parser.add_argument('-s', 
                    '--stage', 
                    help = 'If -s is included, script will work on the stage/test environment, not the production environment. Stage credentials required.',
                    action='store_true' # The store_true option automatically creates a default value of False.
                    )

args = parser.parse_args()

# Example from docs:
# curl -X PUT 
# -H "Content-Type:application/xml;charset=UTF-8" 
# -i 
# --user USERNAME:PASSWORD  
# -d @10.5072/0000-03VC.xml https://mds.test.datacite.org/metadata/10.5072/0000-03VC


# Note that researcher_metadata.json should be in the same directory as this script.
data = open("researcher_metadata.json", "rb").read()
url = 'https://api.datacite.org/dois' if not args.stage else "https://api.test.datacite.org/dois"
headers = {'Content-Type': 'application/vnd.api+json'}
#auth = args.token.split(':') 
response = requests.post(url, headers=headers, auth=args.token, data=data)
if response.status_code == requests.codes.ok:
    print("Request was successful")
else:
    print(f"Request failed with error code {response.status_code}")
    print(response.text) # print the error message from the response