Hana
====

Yet another static site generator.

At the core, Hana is very simple and known only about reading files from the source directory and writing them to the output directory. Any processing that needs to happen is dependent on plugins. In this sense, Hana is template system agnostic, and can be used to process any files, even ebooks or pdfs (provided there are plugins).

Hana plugins consist of callables that accept two parameters: reference to files available for processing, and reference to Hana.

Hana can create files from a source other than filesystem, by using a custom loader. The loader must have a `get_files()` method, which returns all files that will be processed by Hana and its plugins.

