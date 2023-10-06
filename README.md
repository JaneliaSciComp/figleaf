# figleaf
Here are some simple scripts for interacting with the figshare APIs. Right now, the goal is to be able to create many figshare articles automatically in batches. Currently, all it can do is create a new article and upload data to that article, in a one-by-one, interactive way. I also started working on creating DOIs with metadata through the DataCite API, but that effort has been shelved for the moment.

The basic approach is as follows: I'm ingesting the researcher's metadata from an excel spreadsheet, then converting that to a JSON document. I asked ChatGPT to create a JSONSchema for fisghare's new article uploads. Then I'm using [datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/) and [Pydantic](https://docs.pydantic.dev/latest/) to validate that the researcher's metadata is compliant with that schema. Then I POST the validated JSON document to figshare's server, and then I upload the data file(s).

Currently, I'm only supporting a handful of metadata fields right now. 


Here's a graphical summary of the workflow:
<img
  src="READMEimg.png"
  style="display: inline-block; margin: 0 auto; max-width: 250px">


___

#### Workflow #1: Create figshare articles in batches
First, I create Python classes from a figshare JSON schema based on this page in figshare's API docs, [here](https://docs.figshare.com/#private_article_create):

`datamodel-codegen --input example_from_docs.json --input-file-type json --force-optional --output figshare_models.py`

Since figshare doesn't provide a schema, I don't know which metadata fields are mandatory or optional. So I'm just making everything optional. 

Next, we need to include categories and keywords in our metadata, and we have to use figshare's numerical codes for the categories and keywords we want. (This is all required by figshare.) I do this with my script `get_figshare_info.py`. For usage instructions, run that script with the `-h` flag.

Next, I have the researcher's metadata in a **very** carefully formatted excel sheet, which I export to csv, and convert to JSON with `ingest_researcher_metadata.py`. 

Next, `create_private_article.py` POSTs a private article with metadata to figshare's database. 

Finally, `upload.py` PUTs a file on figshare associated with that article. 


___
#### Workflow #2: Create DOIs directly through DataCite
Not yet up and running.

