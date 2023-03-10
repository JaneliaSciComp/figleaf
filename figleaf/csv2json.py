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
    affiliations = []
    for k, v in creator.items():
        if 'ffiliation' in k:
            affiliations.append(v)
    if affiliations:
        affiliations = [ models.Affiliation(affiliation = a) for a in affiliations ]
        affiliations = models.Affiliations(__root__ = affiliations)
        new_creator.affiliations = affiliations
    if 'lang' in creator:
        new_creator.lang = creator['lang']
    return(new_creator)



# read in the metadata
data = pd.read_csv('test_spreadsheet.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')

# Put creator metadata from spreadsheet into a tidy dictionary

# First, work on the creator field
creator_dicts = {} # will look like this:
# {
#    1: {'name': 'Virginia Scarlett', 'nameType': 'Personal', 'nameIdentifiers': '0000-0002-4156-2849', 'nameIdentifierScheme': 'ORCID', 'schemeURI': 'https://orcid.org', 'Affiliation': 'University of California, Berkeley', 'Affiliation1': 'HHMI Janelia Research Campus'}, 
#    2: {'name': 'William Shakespeare', 'nameType': 'Personal'}
# }
counter = 1
for record in records:
    if record['Attr'] == 'creators':
        current_attr = record['Attr_key']
        creator_id = record['id']
        if creator_id not in creator_dicts:
            creator_dicts[creator_id] = {}
        if current_attr in creator_dicts[creator_id]: # This will be True if a creator has multiple affiliations. 
            # In that case, 'Affiliation' may already be in the creator's dict.
            current_attr = current_attr + str(counter) # Add an arbitrary number to the key name to make it a unique string. 
            counter += 1
        creator_dicts[creator_id][current_attr] = record['Attr_value']

# Minor snag: Technically, the DataCite schema allows each creator/contributor to have multiple nameIdentifiers, but only one nameIdentifierScheme.
# So a person could technically have e.g. two ORCID ids, and this would not violate the DataCite schema.
# I think this is strange and should not be allowed! So I'm not allowing it. If the same creator provides two nameIdentifiers, one will be overwritten.
# Confusingly, then, I am stuck with DataCite's use of the plural "nameIdentifiers" for objects that will only ever contain one piece of data.

# Create an instance of the Creator object for every creator.
creators_final = {}
for creator_id, creator_dict in creator_dicts.items(): 
    creators_final[creator_id] = create_creator(creator_dict)

# creators_final looks like this:
# {
#   1: Creator(
#       name='Virginia Scarlett', 
#       nameType=<NameType.Personal: 'Personal'>, 
#       givenName=None, 
#       familyName=None, 
#       nameIdentifiers=NameIdentifiers(__root__=[NameIdentifier(nameIdentifier='0000-0002-4156-2849', nameIdentifierScheme='ORCID', schemeURI=AnyUrl('https://orcid.org', scheme='https', host='orcid.org', tld='org', host_type='domain'))]), 
#   affiliations=None, lang=None
#       ), 
#   2: Creator(
#   name='William Shakespeare', 
#   nameType=<NameType.Personal: 'Personal'>, 
#   givenName=None, 
#   familyName=None, 
#   nameIdentifiers=None, 
#   affiliations=None, 
#   lang=None)
#}


# To do next: publisher and publication year
# Title(s?)
# Eventually: relatedIdentifiers



