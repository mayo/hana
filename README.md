Hana
====

[![Build Status](https://travis-ci.org/mayo/hana.svg?branch=master)](https://travis-ci.org/mayo/hana)

Yet another static site generator.

**WARNING**: *This is very much alpha version software. The Plugin API is relatively stable, but there are no guarantees. That being said, I welcome any help or contributions via pull requests.*

Hana is a simple pipeling tool that keeps track of files and writes them out to an output directory at the end. Any processing that needs to happen is implemented with plugins. Because of this, Hana is template system agnostic, and can be used to process any files,.

Hana plugins consist of callables that accept two parameters: reference to Hana itself, and files that need to be processed.

Hana is relatively simple pipeline processor – it executes steps (plugins) in a given order. Each step gets a list of files matchinggiven patterns and reference to the main pipeline. Plugins can be run multiple times, for different file patterns, etc. Hana itself has no knowledge of filesystem or files. Files are loaded using a plugin, as well as written out using a plugin. So is parsing of front matter, templating, or deploying to S3. File loader and writer come out of the box with Hana, but you aren't required to use them.

You can find the current list of plugins in [hana-plugins](http://github.com/mayo/hana-plugins). The basic stuff to [generate](http://oyam.ca) a static site is there, but couple of handy plugins are missing. I'm actively working and adding more.

Feel free to contact me with questions, tell me that I'm crazy for doing this, yell at me that the world doesn't need another static site generator. Or if you're interested and want to help out.


## Why not X

I've used Jekyll in the past, and it's a great system, but I have never liked the templating system it uses. I always ended up creating workarounds the templating more than actually doing anything with my site. I also dislike that the plugin execution order is controlled by the plugins, rather than the end user, and had issues with plugin execution order in past.

Hyde is pretty much dead at this point. Jinja2 is great templating language, but Hyde's plugin system was abysmal.

There are countless other static site generators, but I was never happy with the ones I found, and always had to change my workflow to make them work for me, rather than making the generators integrate in my workflow.

