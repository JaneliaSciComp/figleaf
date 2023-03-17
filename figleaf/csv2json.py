"""
This script is not finished.
Run AFTER create_models.py.
Plan is to extract metadata from a csv, turn those metadata into pydantic objects
for easy manipulation and thorough validation, and then ultimately convert them
into a json object, following the latest DataCite schema.


"""

import pandas as pd
import pydantic
#from typing import Any, Dict, Union
from jsonschema import Draft7Validator # A typing.Protocol class for v. 7 of the JSON Schema spec. 
#^Implements methods and subclasses for validating that the input JSON schema adheres to the v.7 spec.
import models


def create_creator(creator):
    # ^creator is a dictionary containing all provided metadata for one creator
    new_creator = models.Creator(name = creator['name'])
    if 'nameType' in creator:
        new_creator.nameType = models.NameType(creator['nameType'])
    if 'givenName' in creator:
        new_creator.givenName = creator['givenName']
    if 'familyName' in creator:
        new_creator.familyName = creator['familyName']
    if 'nameIdentifiers' in creator:
        if 'schemeURI' in creator: 
            new_creator.nameIdentifiers = models.NameIdentifiers( __root__ = [ 
                models.NameIdentifier(nameIdentifier = creator['nameIdentifiers'], nameIdentifierScheme = creator['nameIdentifierScheme'], schemeURI = creator['schemeURI']) 
                ] )
        else:
            new_creator.nameIdentifiers = models.NameIdentifiers( __root__ = [ 
                  models.NameIdentifier(nameIdentifier = creator['nameIdentifiers'], nameIdentifierScheme = creator['nameIdentifierScheme']) 
                ] )
    for k, v in creator.items():
        if k == 'Affiliations':
            affiliations = [ models.Affiliation(affiliation = a) for a in creator['Affiliations'] ]
            affiliations = models.Affiliations(__root__ = affiliations)
            new_creator.affiliations = affiliations
    if 'lang' in creator:
        new_creator.lang = creator['lang'] # untested
    return(new_creator)



# read in the metadata
data = pd.read_csv('test_spreadsheet.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')
# records looks like:
# [
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'name', 'Attr_value': 'Virginia Scarlett'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'nameType', 'Attr_value': 'Personal'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'nameIdentifiers', 'Attr_value': '0000-0002-4156-2849'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'nameIdentifierScheme', 'Attr_value': 'ORCID'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'schemeURI', 'Attr_value': 'https://orcid.org'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'Affiliations', 'Attr_value': 'University of California, Berkeley'}
# {'Attr': 'creators', 'id': 1, 'Attr_key': 'Affiliations', 'Attr_value': 'HHMI Janelia Research Campus'}
#   ... etc.
#   ]

# resource type. resourceType is mandatory, free text. resourceTypeGeneral is also mandatory, but controlled vocabulary.
rT = None
rTG = None
for record in records:
    if record['Attr_key'] == 'resourceType':
        rT = record['Attr_value']
    if record['Attr_key'] == 'resourceTypeGeneral':
        rTG = record['Attr_value']

resourceTypeObj = models.Types(resourceType = rT, resourceTypeGeneral = rTG)



creator_dicts = {} # will look like this:
# {
#    1: {'name': 'Virginia Scarlett', 'nameType': 'Personal', 'nameIdentifiers': '0000-0002-4156-2849', 'nameIdentifierScheme': 'ORCID', 'schemeURI': 'https://orcid.org', 'Affiliations': ['University of California, Berkeley', 'HHMI Janelia Research Campus']}, 
#    2: {'name': 'William Shakespeare', 'nameType': 'Personal'}
# }

for record in records:
    if record['Attr'] == 'creators':
        current_attr = record['Attr_key']
        creator_id = record['id']
        if creator_id not in creator_dicts:
            creator_dicts[creator_id] = {}
        if record['Attr_key'] == 'Affiliations':
            if 'Affiliations' in creator_dicts[creator_id]:
                creator_dicts[creator_id]['Affiliations'].append(record['Attr_value'])
            else:
                creator_dicts[creator_id]['Affiliations'] = [ record['Attr_value'] ]
        else:
            creator_dicts[creator_id][current_attr] = record['Attr_value']


# N.B.: Currently, if the same creator provides two nameIdentifiers, e.g. two ORCIDs, one will be overwritten.

# Create an instance of the Creator object for every creator.
creators_final = {}
for creator_id, creator_dict in creator_dicts.items(): 
    creators_final[creator_id] = create_creator(creator_dict)


title_objs = []
for record in records:
    if record['Attr'] == 'title':
        title_objs.append( models.Title(title = record['Attr_value']) )
    if record['Attr'] == 'titleType':
        title_objs.append( models.Title(title = record['Attr_value'], titleType = models.TitleType(record['Attr_key'])) )

# To do, at some point, maybe: ^^ add 'lang' to title(s), if provided






