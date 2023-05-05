# figleaf
Here are some simple scripts for interacting with the figshare and DataCite APIs. For now, the goal is to be able to create many figshare articles automatically in batches. Maybe someday I'll work on fancier things, like faster file uploads to figshare. At the same time, I'm also working on creating DOIs with metadata through the DataCite API. That way, we can get DOIs for (typically large) datasets that we are hosting on our own websites.

The basic approach is similar for the two workflows. I'm using [datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/) and [Pydantic](https://docs.pydantic.dev/latest/) to create python classes from the JSON schemas provided by figshare and DataCite. Then I wrangle the researcher's metadata into those python classes, and export those metadata to a JSON file I can POST to the server.

Currently, both workflows are very much under construction. I'm only supporting a handful of metadata fields right now.


___

#### Workflow #1: Create figshare articles in batches
First, I create Python classes from a suitable JSON object I found in figshare's API docs, [here](https://docs.figshare.com/#private_article_create):

`datamodel-codegen --input example_from_docs.json --input-file-type json --force-optional --output figshare_models.py`

Since figshare doesn't provide a schema, I don't know which metadata fields are mandatory or optional. So I'm just making everything optional. 

Next, in order to include categories and keywords in our metadata, (which I think are mandatory?) we need to query the server and get figshare's numerical codes for the categories and keywords we want. I do this with my script `get_figshare_info.py`. For usage instructions, run that script with the `-h` flag.

Next, I have the researcher's metadata in a **very** carefully formatted excel sheet, which I export to csv, and convert to JSON with `ingest_researcher_metadata.py`. 

Next, `create_private_article.py` POSTs a private article with metadata to figshare's database. 

Finally, `upload.py` PUTs a file on figshare associated with that article. 


___
#### Workflow #2: Create DOIs directly through DataCite
Not yet up and running.


___

Here's a graphical summary of the overall workflow:
<img
  src="figleaf_plan.png"
  style="display: inline-block; margin: 0 auto; max-width: 250px">
