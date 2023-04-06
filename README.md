A nascent effort to develop some simple scripts for interacting with the figshare and/or DataCite APIs. 

I am looking to https://github.com/dandi/dandi-schema for design inspiration. 

My first goal is a workflow for programmatic creation of figshare articles.
I'm starting by creating Python classes (Pydantic models) for storing and manipulating
DataCite or figshare JSON objects. Then I'm populating those class instances/JSON objects
with researcher metadata.

Here is the plan:

<img
  src="figleaf_plan.png"
  style="display: inline-block; margin: 0 auto; max-width: 250px">
