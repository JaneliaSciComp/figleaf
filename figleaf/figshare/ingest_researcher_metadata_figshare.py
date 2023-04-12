"""
This script is untested.
Run AFTER creating figshare_models.
This script extracts metadata from a csv, and creates a pydantic object with
those metadata as attributes. For now, it requires that the pydantic object
adhere to the rather fragile schema grabbed from this url: https://docs.figshare.com/#private_article. 
"""

import pandas as pd
import pydantic
import figshare_models

def filter_records(column, match):
    """
    Filter rows collected from the spreadsheet where a certain column matches a certain number or word (match). 
    Return a list of dictionaries, or an empty list if no matches.
    If we know there should be only match, e.g. title, we can extract the 0th element from the resulting list.
    """
    return( [ d for d in records if d[column] == match ] )


def create_author(**kwargs):
    """
    From the create private article section of figshare API docs:
    Can contain the following fields: id, name, first_name, last_name, email, orcid_id. 
    If an id is supplied, it will take priority and everything else will be ignored. 
    No more than 10 authors. For adding more authors use the specific authors endpoint.
    """
    return (figshare_models.Author(**kwargs))


# read in the metadata
data = pd.read_csv('researcher_metadata_figshare.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')
for d in records: # stupid pandas doesn't let me change NA to something else when I read in the data
    for k, v in d.items():
        if pd.isnull(v):
            d[k] = None
# records looks like:
# [
#     {'Attr': 'authors', 'id': 1, 'Attr_key': 'full_name', 'Attr_value': 'Virginia Scarlett'}, 
#     {'Attr': 'authors', 'id': 1, 'Attr_key': 'figshare_id', 'Attr_value': '14526911'}, 
#     {'Attr': 'authors', 'id': 1, 'Attr_key': 'orcid_id', 'Attr_value': '0000-0002-4156-2849'}, 
#     {'Attr': 'authors', 'id': 1, 'Attr_key': 'url_name', 'Attr_value': 'Virginia_Scarlett'}, 
#     {'Attr': 'authors', 'id': 2, 'Attr_key': 'full_name', 'Attr_value': 'William Shakespeare'}, 
#     {'Attr': 'title', 'id': None, 'Attr_key': 'title', 'Attr_value': 'My cool dataset'}, 
#     ...
# ]

# First, title.
t = filter_records('Attr', 'title')[0]['Attr_value']
# Next, description.
d = filter_records('Attr', 'description')[0]['Attr_value']
# Next, keywords.
k_records = filter_records('Attr', 'keywords')
k = [ record['Attr_value'] for record in k_records ]
# Next, categories.
c_records = filter_records('Attr', 'categories')
c = [ str(record['Attr_value']) for record in c_records ]
# Next, authors.
a_records = filter_records('Attr', 'authors')
a_order = sorted(set( d['id'] for d in a_records ))
a_dicts = []
for i in a_order:
    current_records = filter_records('id', i)
    current_dict = {}
    for d in current_records:
        current_dict[d['Attr_key']] = d['Attr_value']
    a_dicts.append(current_dict)

a_objs = [ create_author(**d) for d in a_dicts ]
# Next, defined_type.
dt = filter_records('Attr', 'defined_type')[0]['Attr_value']

my_private_article = figshare_models.Model(
    title = t,
    description = d,
    keywords = k,
    categories = c,
    authors = a_objs,
    defined_type = dt   
    )

# Now we have a handy python object. We can access attributes like my_private_article.title, and add attributes fairly easily. 
# Pydantic has tons of ways to manipulate these objects, e.g. enforce a certain datetime encoding, export to dict e.g. my_item.dict(), and other useful stuff

#For now, let's just export directly to json and write to a file.

with open('researcher_metadata.json', 'w') as outF:
    outF.write(my_private_article.json(indent=4))


