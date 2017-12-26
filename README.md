Hana
====

[![Build Status](https://travis-ci.org/mayo/hana.svg?branch=master)](https://travis-ci.org/mayo/hana)

Yet another static site generator.

Hana is a simple pipeling that keeps track of files and writes them out to an output directory at the end. Any processing that needs to happen is implemented with plugins. Because of this, Hana is template system agnostic, and can be used to process any files,.

Hana plugins consist of callables that accept two parameters: reference to Hana itself, and files that need to be processed.

