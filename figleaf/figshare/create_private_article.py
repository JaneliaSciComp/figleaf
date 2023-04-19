import requests
import argparse

parser = argparse.ArgumentParser(description='A script to create a new private figshare article, with metadata only. Research item will be uploaded later. Token required as a command line argument.')

parser.add_argument('-t', 
                    '--token', 
                    required = True, 
                    help = 'Personal token, most easily obtained through the figshare website.'
                    )

args = parser.parse_args()

# Note that researcher_metadata.json should be in the same directory as this script.
data = open("researcher_metadata.json", "rb").read()
url = "https://api.figsh.com/v2/account/articles"
headers = {'Authorization': 'token {}'.format(args.token)}
response = requests.post(url, headers=headers, data=data)
if response.status_code == requests.codes.ok:
    print("Request was successful")
else:
    print(f"Request failed with error code {response.status_code}")
    print(response.text) # print the error message from the response
