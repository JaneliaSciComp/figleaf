A nascent effort to develop some simple scripts for interacting with the figshare and/or DataCite APIs. 

I am looking to https://github.com/dandi/dandi-schema for design inspiration. 

I have two different workflows: one for minting DataCite DOIs, and one for creating figshare articles.

My first goal is to create figshare articles through the API. 
To do this, I start with an example JSON object from the figshare docs (they do not provide a schema), which I convert to python classes using datamodel-code-generator and Pydantic. 
Next, the researcher inputs their metadata into an excel spreadsheet, and exports to csv.  
Then, I wrangle those metadata into a dictionary, and ultimately into instances of those python classes.
Here, I can easily pause and manipulate those objects, to add or delete fields, for example.
I then export the researcher metadata to a .JSON file, which will be the body of my POST request to create a new article.

Current status: Am able to create a private figshare article with this workflow. Next, need to work on data upload to figshare. Still working on minting DOIs directly through DataCite.

Here is a graphical overview:

<img
  src="figleaf_plan.png"
  style="display: inline-block; margin: 0 auto; max-width: 250px">
