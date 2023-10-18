"""
A script to create a private article from a file containing JSON-formatted metadata for that article.
Offers the user the option to upload one data file to that article. 
Articles are private before being made public. Run this script with -t and your stage token.
Currently the stage URL is hard-coded into the script, so doesn't work for production.
Write down the article ID that is printed to the terminal!
"""

import requests
import argparse
import json
import sys
import hashlib

CHUNK_SIZE = 10 * (1024 ** 2) # e.g. 10 * (1024 ** 2) = 10 Mb.
base_url = "https://api.figsh.com/v2/account/articles" #TODO: use --stage flag instead of hard-coding

def checkOK(response_to_check):
    if not response_to_check.ok:
        print(f"Request failed with error code {response_to_check.status_code}")
        print(response_to_check.text) 
        sys.exit()

def initiate_new_upload(url, headers, article_id, file_name):
    endpoint = '{}/{}/files'.format(url, article_id)
    md5, size = get_file_check_data(file_name)
    file_data = {'name': file_name, 'md5': md5, 'size': size}
    upload_response = requests.post(endpoint, headers=headers, data=json.dumps(file_data))
    checkOK(upload_response)
    return json.loads(upload_response.content) 

def get_file_check_data(file_name):
    with open(file_name, 'rb') as fin:
        md5 = hashlib.md5()
        size = 0
        data = fin.read(CHUNK_SIZE)
        while data:
            size += len(data)
            md5.update(data)
            data = fin.read(CHUNK_SIZE)
        return md5.hexdigest(), size

def upload_parts(headers, file_info, file_name):
    res = requests.get(file_info['location'], headers=headers)
    checkOK(res)
    up_url, up_token = json.loads(res.content)['upload_url'], json.loads(res.content)['upload_token']
    uploader_service_response = requests.get(up_url, headers = {'Authorization': 'token {}'.format(up_token)} )
    checkOK(uploader_service_response)
    with open(file_name, 'rb') as fin:
        for part in json.loads(uploader_service_response.content)['parts']:
            upload_part(file_info, fin, part, up_url)

def upload_part(file_info, stream, part, up_url):
    udata = file_info.copy()
    udata.update(part)
    udata['upload_url'] = up_url 
    part_url = '{upload_url}/{partNo}'.format(**udata)
    stream.seek(part['startOffset'])
    part_data = stream.read(part['endOffset'] - part['startOffset'] + 1)
    part_res = requests.put(part_url, data=part_data)
    checkOK(part_res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', 
                        '--token', 
                        required = True, 
                        help = 'Personal token, most easily obtained through the figshare website.'
                        )
    args = parser.parse_args()

    metadata_file = input("Please enter the name of the JSON-formatted metadata file: ")
    data = open(metadata_file, "rb").read()
    headers = {'Authorization': 'token {}'.format(args.token)}
    response = requests.post(base_url, headers=headers, data=data)
    checkOK(response)
    new_article_id = json.loads(response.content)['entity_id']
    print(f"New private article with ID {new_article_id} successfully created from {metadata_file}.")

    doi = input('Would you like to reserve a DOI for this article? (y/n): ')
    if doi.lower() == 'y':
        doi_res = requests.post(f"{base_url}/{args.article_id}/reserve_doi", headers=headers)
        checkOK(doi_res)
        print("DOI reserved successfully.")

    while True:
        proceed = input(f"Would you like to upload a file to the article you just created? (y/n): ")
        if proceed.lower() == "y":
            file_to_upload = input("Please enter the name of the file to upload: ")
            print("Uploading file ", file_to_upload, f"in {CHUNK_SIZE/(1024 ** 2)}Mb chunks")
            file_info = initiate_new_upload(base_url, headers, json.loads(response.content)['entity_id'], file_to_upload)
            # Until here we used the figshare API; the following lines use the figshare upload service API.
            upload_parts(headers, file_info, file_to_upload) # looks like e.g. {'location': 'https://api.figsh.com/v2/account/articles/8417838/files/830411224'}
            # complete the upload
            up_res = requests.post(file_info['location'], headers=headers)
            checkOK(up_res)
            print("Upload successful.")
        elif proceed.lower() == "n":
            break  # break out of the while loop
        else:
            print("Invalid input. Please enter 'y' to upload a file, or 'n' to cancel.")

    publish = input(f"Would you like to publish this article now? (y/n): ")
    if publish.lower() == 'y':
        pub_res = requests.post(f"{base_url}/{args.article_id}/publish", headers=headers)
        checkOK(pub_res)
        print("Article published successfully.")
