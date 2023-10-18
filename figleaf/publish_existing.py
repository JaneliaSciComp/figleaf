"""
A script to make a private article public, given an article id.
Article id can only be retrieved through the figshare API.
Run this script after create_and_publish.py (which prints the article_id to the terminal, btw).
Offers the user the option to reserve a DOI for the article and to
upload additional data files.
"""

import requests
import argparse
import create_and_publish

CHUNK_SIZE = 10 * (1024 ** 2) # e.g. 10 * (1024 ** 2) = 10 Mb.

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('-id',
                    '--article_id',
                    required = True,
                    help = 'Article ID, which was printed to the terminal at the time of creation.'
                    )
parser.add_argument('-t',
                    '--token',
                    required = True,
                    help = 'Personal token, most easily obtained through the figshare website.'
                    )
args = parser.parse_args()

headers = {'Authorization': 'token {}'.format(args.token)}
base_url = "https://api.figsh.com/v2/account/articles"

doi = input('Would you like to reserve a DOI for this article? (y/n): ')
if doi.lower() == 'y':
    doi_res = requests.post(f"https://api.figsh.com/v2/account/articles/{args.article_id}/reserve_doi", headers=headers)
    create_and_publish.checkOK(doi_res)
    print("DOI reserved successfully.")

while True:
    proceed = input("Would you like to upload an additional file to this article? (y/n): ")
    if proceed.lower() == "y":
        file_to_upload = input("Please enter the name of the file to upload: ")
        print("Uploading file ", file_to_upload, f"in {CHUNK_SIZE/(1024 ** 2)}Mb chunks")
        file_info = create_and_publish.initiate_new_upload(base_url, headers, args.article_id, file_to_upload)
        create_and_publish.upload_parts(headers, file_info, file_to_upload)
        up_res = requests.post(file_info['location'], headers=headers)
        create_and_publish.checkOK(up_res)
        print("Upload successful.")
    elif proceed.lower() == "n":
        break  # break out of the while loop
    else:
        print("Invalid input. Please enter 'y' to upload a file, or 'n' to cancel.")

publish = input(f"Would you like to publish this article now? (y/n): ")
if publish.lower() == 'y':
    pub_res = requests.post(f"https://api.figsh.com/v2/account/articles/{args.article_id}/publish", headers=headers)
    create_and_publish.checkOK(pub_res)
    print("Article published successfully.")