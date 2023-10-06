This is how I created private_article_schema.json, a jsonschema
for POSTing new private articles to the figshare server. 

Hey ChatGPT, please create a JSON schema with the following properties:
title, which is mandatory and is a string.
description, which is optional and is a string. 
is_metadata_record, which is optional and is a boolean.
metadata_reason, which is optional and is a string.
tags, which is optional and is an array of strings.
keywords, which is optional and is an array of strings.
references, which is optional and is an array of strings, and each string in the array must start with "http://".
categories, which is optional and is an array of integers.
categories_by_source_id, which is optional and is an array of strings.
authors, which is optional and is an array of Authors.
Author, which is optional and has the following properties, which are all optional: id (integer), name (string), first_name (string), last_name (string), email (string), orcid_id (string). 
custom_fields, which is optional and is a JSON object.
defined_type, which is optional and is a string and is one of: figure, online resource, preprint, book, conference contribution, media, dataset, poster, journal contribution, presentation, thesis, software.
funding, which is optional and is a string.
group_id, which is optional and is an integer.