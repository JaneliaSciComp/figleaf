"""
A script to create a JSON schema from a given JSON object.
There's no need to create a JSONschema since we really just want
the python classes.

Note that for now, I am making all fields optional.
"""

import requests
import os

def get_figshare_article(): 
    sr = requests.get(
        "https://api.figshare.com/v2/articles/22154810"
    )
    sr.raise_for_status() # make sure the GET request worked
    return sr


r = get_figshare_article()

# Write the schema to a file; will overwrite any existing file with this name
fname = 'example_article.json'
open(fname , 'wb').write(r.content)

os.system('datamodel-codegen --force-optional --input {} --input-file-type json --output figshare_models.py'.format(fname))
