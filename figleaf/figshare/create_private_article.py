import requests
import argparse
import json
import sys
import hashlib

CHUNK_SIZE = 10 * (1024 ** 2) # e.g. 10 * (1024 ** 2) = 10 Mb.
FILE_NAME = 'AA1121.json'

def check(response_to_check):
    if response_to_check.status_code != requests.codes.ok:
        print(f"Request failed with error code {response_to_check.status_code}")
        print(response_to_check.text) 
        sys.exit()

def initiate_new_upload(article_id, file_name):
    endpoint = '{}/{}/files'.format(base_url, article_id)
    md5, size = get_file_check_data(file_name)
    file_data = {'name': file_name, 'md5': md5, 'size': size}
    upload_response = requests.post(endpoint, headers=headers, data=json.dumps(file_data))
    check(upload_response)
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

def upload_parts(file_info):
    res = requests.get(file_info['location'], headers=headers)
    check(res)
    up_url, up_token = json.loads(res.content)['upload_url'], json.loads(res.content)['upload_token']
    uploader_service_response = requests.get(up_url, headers = {'Authorization': 'token {}'.format(up_token)} )
    check(uploader_service_response)
    with open(FILE_NAME, 'rb') as fin:
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
    check(part_res)

def complete_upload(article_id, file_id):
    requests.post('{}/{}/files/{}'.format(base_url, article_id, file_id))




parser = argparse.ArgumentParser(description='A script to create a new private figshare article, with metadata only. Research item will be uploaded later. Token required as a command line argument.')

parser.add_argument('-t', 
                    '--token', 
                    required = True, 
                    help = 'Personal token, most easily obtained through the figshare website.'
                    )

args = parser.parse_args()

# Note that researcher_metadata.json should be in the same directory as this script.
data = open("researcher_metadata.json", "rb").read()
base_url = "https://api.figsh.com/v2/account/articles"
headers = {'Authorization': 'token {}'.format(args.token)}
response = requests.post(base_url, headers=headers, data=data)
check(response)

# TODO: Ask the user if they want to proceed to upload a data file, and if so, name of file

file_info = initiate_new_upload(json.loads(response.content)['entity_id'], FILE_NAME)

# Until here we used the figshare API; following lines use the figshare upload service API.
upload_parts(file_info) # looks like e.g. {'location': 'https://api.figsh.com/v2/account/articles/8417838/files/830411224'}
# complete the upload
requests.post(file_info['location'], headers=headers)