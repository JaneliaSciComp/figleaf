"""
This script is not finished.
Run AFTER create_models.py.
Plan is to extract metadata from a csv and put that metadata 
into json format, following the latest DataCite schema.
"""

import pandas as pd
import pydantic
from typing import Any, Dict, Union
from jsonschema import Draft7Validator # A typing.Protocol class for v. 7 of the JSON Schema spec. 
#^Implements methods and subclasses for validating that the input JSON schema adheres to the v.7 spec.
import models

# read in the metadata
data = pd.read_csv('test_spreadsheet.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')

# Next, use pydantic to create an instance of the Creator object for every creator.
# Then we can easily validate the metadata before formatting it into json.
# (We'll also validate the json.)
# I will probably wrap this in a function or two once it's ready.
# I'm trying to build this in a modular way, so if we are starting with e.g. json 
# rather than csv, or we want to curate metadata at the level of the python objects,
# we can easily do that. 

# Put metadata from spreadsheet into a tidy dictionary
creators = {} # Will look like this:
# {
#    1: {'name': 'Virginia Scarlett', 'nameType': 'Personal', 'nameIdentifiers': '0000-0002-4156-2849', 'nameIdentifierScheme': 'ORCID', 'schemeURI': 'https://orcid.org', 'Affiliation': 'University of California, Berkeley', 'Affiliation1': 'HHMI Janelia Research Campus'}, 
#    2: {'name': 'William Shakespeare', 'nameType': 'Personal'}
# }
counter = 1
for record in records:
    if record['Attr'] == 'creators':
        current_attr = record['Attr_key']
        creator_id = record['id']
        if creator_id not in creators:
            creators[creator_id] = {}
        if current_attr in creators[creator_id]: # This will be True if a creator has multiple affiliations. 
            # In that case, 'Affiliation' may already be in the creator's dict.
            current_attr = current_attr + str(counter) # Add an arbitrary number to the key name to make it a unique string. 
            counter += 1
        creators[creator_id][current_attr] = record['Attr_value']

# Minor snag: Technically, the DataCite schema allows each creator/contributor to have multiple nameIdentifiers, but only one nameIdentifierScheme.
# So a person could technically have e.g. two ORCID ids, and this would not violate the DataCite schema.
# I think this is strange and should not be allowed! So I'm not allowing it. If the same creator provides two nameIdentifiers, one will be overwritten.
# Confusingly, then, I am stuck with DataCite's use of the plural "nameIdentifiers" for objects that will only ever contain one piece of data.


# Create another dictionary with one integer key per creator, but now the values are Creator objects instead of dicts.
creatorsfinal = {}
for creator_id, creator_dict in creators.items(): # Before we can create an instance of Creator, 
    # we need to create instances of nameType, nameIdentifiers, and Affiliations, if provided.
    creator = creators[creator_id] # e.g. creators[1] is the dict corresponding to Virginia Scarlett 

    # TO DO!!!: just build a new creator dict instead of deleting things from the old one?

    affiliations = []
    if 'nameType' in creator:
        creator['nameType'] = models.NameType(creator['nameType'])
    if 'nameIdentifiers' in creator:
        if 'schemeURI' in creator:
            creator['nameIdentifiers'] = models.NameIdentifiers( __root__ = [ 
                models.NameIdentifier(nameIdentifier = creator['nameIdentifiers'], nameIdentifierScheme = creator['nameIdentifierScheme'], schemeURI = creator['schemeURI']) 
                ] )
            del creator['schemeURI'] # delete because the nameIdentifiers obj holds this info now.
        else:
            creator['nameIdentifiers'] = models.NameIdentifiers( __root__ = [ 
                models.NameIdentifier(nameIdentifier = creator['nameIdentifiers'], nameIdentifierScheme = creator['nameIdentifierScheme']) 
                ] )
        del creator['nameIdentifierScheme'] # delete because the nameIdentifiers obj holds this info now.
    for k, v in creator.items():
        if 'ffiliation' in k:
            affiliations.append(v)
            del creator[k]

# RuntimeError: dictionary changed size during iteration

    if affiliations:
        affiliations = [ models.Affiliation(affiliation = a) for a in affiliations ]
        affiliations = models.Affiliations(__root__ = affiliations)
        creator['Affiliations'] = affiliations
    try:
        new_creator = models.Creator(**creator) # attempt to create an instance of class Creator
    except ValidationError as e:
         print(e)
    creatorsfinal[creator_id] = new_creator
    



# creatorsfinal looks like this:
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


