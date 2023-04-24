"""
This script extracts metadata from a csv, and creates a pydantic object with
those metadata as attributes. 
There are two phases here: first, we create the object that contains all the
researcher's metadata. Then, we nest that object inside a couple more objects
so that our JSON body matches the body we need to POST a request for a new DOI.

See this webpage for more info on creating DOIs: 
https://support.datacite.org/docs/api-create-dois
"""

from pandas import read_csv, isnull
#import pydantic
import datacite_models as models


class DataObj(models.BaseModel):
    type: str
    attributes: models.Model

class RequestBody(models.BaseModel):
    data: DataObj


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
data = read_csv('researcher_metadata.csv', dtype={'id':'Int32'}) # stop pandas from automatically converting int to float
records = data.to_dict(orient='records')
for d in records: # stupid pandas doesn't let me change NA to something else when I read in the data
    for k, v in d.items():
        if isnull(v):
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


# Next, identifiers. This field is mandatory, and must be a list.
# TODO: build out functionality to include RelatedIdentifiers
# The regular identifier object refers to the DOI. We can (and must) fill it with nonsense, since we don't have a DOI yet.
identifiers = [ models.Identifier(identifier = "0", identifierType = "DOI") ]

# Next, Creators.
creator_records = filter_records('Attr', 'creators')
creator_order = sorted(set( d['id'] for d in creator_records ))
creator_dicts = []
for i in creator_order:
    current_records = filter_records('id', i) # TODO: BUG. THIS FILTERS ALL RECORDS WITH id == i, not just creator records
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


publisher = filter_records('Attr', 'publisher')[0]['Attr_key']
pubYear = filter_records('Attr', 'publicationYear')[0]['Attr_key']

my_item = models.Model(
    types = resource_type_obj,
    identifiers = identifiers,
    creators = creator_objs,
    titles = title_objs,
    publisher = publisher,
    publicationYear = pubYear   
    )

# Now we have a handy python object. We can access attributes (e.g. my_item.titles) and add attributes fairly easily. 
# Pydantic has a lot of handy ways to manipulate these objects.
# Here, we want to remove the 'identifiers' attribute from the model, because 
# we don't have a DOI yet (we are trying to create one). 
# There's probably a more elegant solution than creating a dummy DOI and then excluding it, but this will suffice for now.
# See https://docs.pydantic.dev/usage/exporting_models/
my_data = DataObj(type = 'dois', attributes = my_item)
my_req = RequestBody(data = my_data)
exclude_keys = { 'data': { 'attributes': {'identifiers': True} } }

with open('researcher_metadata.json', 'w') as outF:
    outF.write(my_req.json(exclude=exclude_keys, indent=4))

