# UmakaParser

This tool is to make a JSON file for [Umaka Viewer](https://umaka-viewer.dbcls.jp/).  
​  
First, you need to prepare a metadata file in the [SPARQL Builder Meatadata (SBM)](http://www.sparqlbuilder.org/doc/sbm_2015sep/) format.  
If you want to get such a metadata file, [TripleDataProfiler](https://bitbucket.org/yayamamo/tripledataprofiler/src/master/) can generate it for a SPARQL endpoint.  
​  
Then, if you have ontology files for the target endpoint or RDF dataset, you need to make asset files by this tool as follows.  
​  
`umakaparser --build-index [--dist <Path to put an asset file>] <ontology files in Turtle>`  
​  
If you have ontology files only in RDF/XML, this tool converts them into those in Turtle as follows.  
​  
`umakaparser --convert <files in RDF/XML>`  
​  
Finally, this tool generates a JSON file that can be accepted by [Umaka Viewer](https://umaka-viewer.dbcls.jp/) as follows.  
​  
`umakaparser --build [--a <Path to asset files>|--d <Path to put a generated JSON file>] <an SBM file>`  
​  
The JSON file structure is [here](https://github.com/dbcls/umakaparser/wiki/Data-specification).
