"""
A script to create Pydantic models from a JSON schema.
You probably only need to run this once.

The actual DataCite metadata schema is not written in JSON; it's written in XML.
There is no community standard for a JSON "translation" of the DataCite metadata schema.
However, some person made a translation and many people on github seem to use it.

Here, we first check that the json datacite schema on github is a valid json schema. 
Then, we write that schema to a file.
Then, we use the data-model-code-generator tool to create pydantic models,
that is, python classes we can easily manipulate, from the file we just created.
The tool makes some minor decisions for us, but that's okay.
The pydantic models are saved in a file called models.py.
"""

from jsonschema import Draft7Validator # A typing.Protocol class for v. 7 of the JSON Schema spec. 
#^Implements methods and subclasses for validating that the input JSON schema adheres to the v.7 spec.
import requests
import os



#Functions modified from https://github.com/dandi/dandi-schema/blob/master/dandischema/datacite.py
def get_datacite_schema(): #fetch the schema from github
    sr = requests.get(
        "https://raw.githubusercontent.com/datacite/schema/"
        "732cc7ef29f4cad4d6adfac83544133cd57a2e5e/"
        "source/json/kernel-4.3/datacite_4.3_schema.json"
    )
    sr.raise_for_status() # make sure the GET request worked
    return sr

def validate_datacite(sr):
    schema = sr.json()
    # Validate that the schema from that github webpage is still valid
    Draft7Validator.check_schema(schema) 
    # ^ Raises jsonschema.exceptions.SchemaError if the schema is invalid



r = get_datacite_schema()
validate_datacite(r)

# Write the schema to a file; will overwrite any existing file with this name
fname = 'datacite_4.3_schema.json'
open(fname , 'wb').write(r.content)

#Create pydantic models from the validated datacite schema
os.system('datamodel-codegen  --input {} --input-file-type jsonschema --output models.py'.format(fname))

