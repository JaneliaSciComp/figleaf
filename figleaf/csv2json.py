"""
This script is not finished.
Run AFTER create_models.py.
Plan is to extract metadata from a csv, turn those metadata into pydantic objects
for easy manipulation and thorough validation, and then ultimately convert them
into a json object, following the latest DataCite schema.


"""

import pandas as pd
import pydantic
import models
#from typing import Any, Dict, Union
#from jsonschema import Draft7Validator # A typing.Protocol class for v. 7 of the JSON Schema spec. 
#^Implements methods and subclasses for validating that the input JSON schema adheres to the v.7 spec.

def filter_records(column, match):
    """
    Filter rows collected from the spreadsheet where a certain column matches a certain number or word (match). 
    Return a list of dictionaries, or an empty list if no matches.
    If we know there should be only match, e.g. title, we can extract the 0th element from the resulting list.
    """
    return( [ d for d in records if d[column] == match ] )


def create_creator(**kwargs):
    # N.B.: This code will break if the same creator provides two nameIdentifiers, e.g. two ORCIDs. 
    # This is such an unlikely scenario that I'm not adding code to accommodate it.
    if 'nameIdentifiers' in kwargs:
        if 'schemeURI' in kwargs: 
            kwargs['nameIdentifiers'] = models.NameIdentifiers( __root__ = [ 
                models.NameIdentifier(nameIdentifier = kwargs['nameIdentifiers'], nameIdentifierScheme = kwargs['nameIdentifierScheme'], schemeURI = kwargs['schemeURI']) 
                ] )
        else:
            kwargs['nameIdentifiers'] = models.NameIdentifiers( __root__ = [ 
                  models.NameIdentifier(nameIdentifier = kwargs['nameIdentifiers'], nameIdentifierScheme = kwargs['nameIdentifierScheme']) 
                ] )
    if 'affiliations' in kwargs:
            kwargs['affiliations'] = list(kwargs['affiliations']) if not isinstance(kwargs['affiliations'], list) else kwargs['affiliations']
            affiliations = [ models.Affiliation(affiliation = a) for a in kwargs['affiliations'] ]
            kwargs['affiliations'] = models.Affiliations(__root__ = affiliations)
    return(models.Creator(**kwargs))


# read in the metadata
data = pd.read_csv('test_spreadsheet.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')
for d in records: # stupid pandas doesn't let me change NA to something else when I read in the data
    for k, v in d.items():
        if pd.isnull(v):
            d[k] = None
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

# First, resource type. resourceType is mandatory, free text. resourceTypeGeneral is also mandatory, but controlled vocabulary.
rT = filter_records('Attr_key', 'resourceType')[0]['Attr_value']
rTG = filter_records('Attr_key', 'resourceTypeGeneral')[0]['Attr_value']
resource_type_obj = models.Types(resourceType = rT, resourceTypeGeneral = rTG)


# Next, identifier. This field is mandatory, but we can (and must) fill it with nonsense, since we don't have a DOI yet.
identifier_obj = models.Identifier(identifier = "0", identifierType = "DOI") 

# Next, Creators.
creator_records = filter_records('Attr', 'creators')
creator_order = sorted(set( d['id'] for d in creator_records ))
creator_dicts = []
for i in creator_order:
    current_records = filter_records('id', i)
    creator_dict = {}
    for d in current_records:
        if d['Attr_key'] in creator_dict: # e.g. affiliations
            if not isinstance(creator_dict[d['Attr_key']], list):
                creator_dict[d['Attr_key']] = [ creator_dict[d['Attr_key']] ]
            creator_dict[d['Attr_key']].append(d['Attr_value'])
        else:
            creator_dict[d['Attr_key']] = d['Attr_value']
    creator_dicts.append(creator_dict)

creator_objs = [ create_creator(**d) for d in creator_dicts ]


# Next, title(s)
# There should be one and only one title
title_objs = [ models.Title(title = filter_records('Attr', 'title')[0]['Attr_value']) ]
for d in filter_records('Attr', 'titleType'):
    title_objs.append( models.Title(title = d['Attr_value'], titleType = models.TitleType(d['Attr_key'])) )


publisher = filter_records('Attr', 'publisher')[0]['Attr_value']
pubYear = filter_records('Attr', 'publicationYear')[0]['Attr_value']

my_item = models.Model(
    types = resource_type_obj,
    identifiers = identifier_obj,
    creators = creator_objs,
    titles = title_objs,
    publisher = publisher,
    publicationYear = pubYear   
    )

# TODO: Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "pydantic/main.py", line 341, in pydantic.main.BaseModel.__init__
# pydantic.error_wrappers.ValidationError: 1 validation error for Model
# identifiers
#   value is not a valid list (type=type_error.list)



