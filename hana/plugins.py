from errors import HanaPluginError

#TODO: clean up prints. use logging

# FileLoader plugin

from hana.core import MetaFile

class FileLoader():
    def __init__(self, source_path):
        self._source_path = source_path

        if not os.path.isdir(self._source_path):
            raise SourceDirectoryError()

    def __call__(self, file_gen, hana):

        for path, dirs, sfiles in os.walk(self._source_path):
            for f in sfiles:
                source = os.path.join(path, f)
                filepath = os.path.relpath(source, self._source_path)

                files = list(file_gen)
                if filepath in files:
                    raise FileExistsError("File {} already exists".format(filepath))
                hana.files[filepath] = MetaFile(source, _source_file=source)

    class FileLoaderError(HanaPluginError): pass
    class FileExistsError(FileLoaderError): pass
    class SourceDirectoryError(FileLoaderError): pass


# Metadata plugin

#TODO: this should probably become the set_metadata plugin from build.py. This should be handled from initial configuration
def metadata(metadata):
    print 'loading metadata'
    def metadata_plugin(file_gen, hana):
        hana.metadata.update(metadata)

    return metadata_plugin

#Front matter plugin

import frontmatter

def front_matter(file_gen, hana):

    for filename, f in file_gen:
        if f.is_binary:
            continue

        # This will strip empty front matter statement
        metadata, hana.files[filename]['contents'] = frontmatter.parse(f['contents'])

        if metadata:
            hana.files[filename].update(metadata)

#Ignore files plugin

import pathspec

def ignore(patterns):
    spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def ignore_plugin(file_gen, hana):
        #matches = spec.match_files(files.iterkeys())
        matches = spec.match_files(( f[0] for f, _ in file_gen ))

        for f in matches:
            del hana.files[f]

    return ignore_plugin


#########
#more custom modules here
#########

#TODO: minify plugin
#TODO: combine js/css in single file plugin. webpack plugin?

# Add static assets to hana files

import shutil

def asset(assets):

    def asset_plugin(file_gen, hana):
        for asset in assets:
            src = asset.get('src')
            dst = asset.get('dst')

            if not src or not dst:
                raise InvalidAssetDefinition(asset)

            create_dest = asset.get('createDest', True)

            #TODO: get cwd from hana
            src = os.path.join(src)
            dst = os.path.join(hana.output, dst)

            if create_dest:
                def makedirs(path, dir):
                    if not dir:
                        return

                    if os.path.isdir(os.path.join(path, dir)):
                        return

                    makedirs(*os.path.split(path))

                    if os.path.isdir(path) or path == '':
                        dirpath = os.path.join(path, dir)
                        os.mkdir(dirpath)
                        return

                makedirs(*os.path.split(os.path.dirname(dst)))

            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

    return asset_plugin

class InvalidAssetDefinitionError(HanaPluginError): pass

# Drafts

def drafts(file_gen, hana):
    for f, _ in file_gen:
        if 'draft' in f:
            del hana.files[f]


# Markdown

import markdown
import os
import re

class Markdown():

    def __init__(self, config={}):
        #TODO: support file extension pattern

        self.output_extension = config.get('extension', '.html')

        extensions = ['markdown.extensions.smarty']

        extension_configs = {
            'markdown.extensions.smarty': {
                'substitutions': {
                    'left-single-quote': '&sbquo;', # sb is not a typo!
                    'right-single-quote': '&lsquo;',
                    'left-double-quote': '&bdquo;',
                    'right-double-quote': '&ldquo;'
                }
            }
        }

        self.md = markdown.Markdown(
                extensions=extensions,
                extension_configs=extension_configs,
                output_format='html5'
        )


    def __call__(self, file_gen, hana):
        md_re = re.compile(r'\.(md|markdown)$')

        for filename, f in file_gen:
            if not md_re.search(filename):
                continue

            del hana.files[filename]

            file_basename, _ = os.path.splitext(filename)
            filename = "{:s}{:s}".format(file_basename, self.output_extension)

            hana.files[filename] = f

            f['contents'] = self.md.convert(f['contents'])


# Titles

import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

#TODO: fix
def title(remove=False):
    md_re = re.compile(r'\.(md|markdown)$')
    html_re = re.compile(r'\.(html|htm)$')

    md_pattern = re.compile(r'^\s*#\s*([^n]+?) *#* *(?:\n+|$)')

    def title_plugin(file_gen, hana):
        for filename, f in file_gen:
            if 'title' in f:
                continue

            title = None

            if re.search(r'\.(md|markdown)$', filename):
                match = md_pattern.match(f['contents'])

            if re.search(r'\.(html|htm)$', filename):
                h1_tags = SoupStrainer('h1')
                soup = BeautifulSoup(f['contents'], 'html.parser', parse_only=p_tags)

                title = h1.string.strip()

            if not title:
                continue

            f['title'] = title

            if remove:
                #TODO: remove title from contents
                pass

    return title_plugin


# Excerpt

from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import pathspec

def excerpt(file_gen, hana):
    match = pathspec.PathSpec.from_lines('gitwildmatch', ['*.htm', '*.html']).match_file

    for filename, f in file_gen:
        if not match(filename):
            continue

        if f.get('excerpt'):
            continue

        p_tags = SoupStrainer('p')
        soup = BeautifulSoup(f['contents'], 'html.parser', parse_only=p_tags)

        p = soup.p

        while p and p.img:
            p = p.next_sibling

        f['excerpt'] = p


# Branch

import pathspec

class Branch():

    def __init__(self, qualifier):
        if isinstance(qualifier, str):
            qualifier = [qualifier]

        if callable(filter):
            #TODO
            pass

        self.match = pathspec.PathSpec.from_lines('gitwildmatch', qualifier).match_file

        self.plugins = []

    def __call__(self, file_gen, hana):
        #TODO
        pass


# Jinja

from jinja2 import Environment, FileSystemLoader
from jinja2.ext import Extension

class JinjaTemplate():
    def __init__(self, config={}):

        #TODO: make sure required stuff is in config

        tplPath = config['directory']
        print "TPL PATH: %s" % tplPath

        extensions = [
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
        ]

        self.env = Environment(loader=FileSystemLoader(tplPath),
                extensions=extensions)

        self.env.trim_blocks = True
        self.env.lstrip_blocks = True

        #try:
        #    from typogrify.templatetags import jinja_filters
        #except ImportError:
        #    jinja_filters = False

        #if jinja_filters:
        #    jinja_filters.register(self.env)

    def __call__(self, file_gen, hana):
        for filename, f in file_gen:
            #TODO: process only files matching pattern, if given
            #TODO: process only if template is defined or there is a default defined

            if 'template' in f:

                c = self.render(f, hana)
                f['contents'] = unicode(c)

    def render(self, node, hana):
        tpl = node.get('template')
        template = None

        if tpl == True:
            #TODO: this doesn't give great feedback if there is an error in the template. The error wil be tracable to the template that got extended. Ideally we should identify where the string we are using as template came from
            template = self.env.from_string(node['contents'])
        else:
            template = self.env.get_template(tpl)

        return template.render(site=hana.metadata, page=node)


# Collections

import pathspec

#TODO: define article previous/next links
class Collections():
    KEY = 'collection'

    def __init__(self, config={}):
        #TODO: validate config input. can't start with _
        self.config = config

        # Initialize empty collections
        self.collections = {}
        self.patterns = {}

        for c_name, c_def in self.config.iteritems():
            if 'pattern' in c_def:
                pats = c_def['pattern']

                if isinstance(pats, str):
                    pats = [pats]

                self.patterns[c_name] = pathspec.PathSpec.from_lines('gitwildmatch', pats)

    def __call__(self, file_gen, hana):

        for filename, f in file_gen:
            print f
            #TODO: this should probably be taken care of globally
            #TODO: metafile experiment
            f['path'] = filename

            # If file has collections defined
            if Collections.KEY in f:
                # Use set to enforce uniqueness
                file_collections = set(f.get(Collections.KEY))

                # Enumerate collections and keep track of files
                for col in file_collections:
                    if col not in self.collections:
                        self.collections[col] = {}

                    self.collections[col][filename] = f

            # Collections definition
            for c_name, c_pat in self.patterns.iteritems():
                if c_pat.match_file(filename):
                    if c_name not in self.collections:
                        self.collections[c_name] = {}

                    # Synthetize the metadata, as we don't want it to update from other plugins
                    self.collections[c_name][filename] = dict(f)


        hana.metadata['collections'] = {}
        for key, collection in self.collections.iteritems():
            collection = collection.itervalues()

            # Sort
            if key in self.config and 'sortBy' in self.config[key]:
                sort_key = self.config[key].get('sortBy')
                collection = sorted(collection, key=lambda f_meta: f_meta[sort_key])

            # Reverse
            if key in self.config and self.config[key].get('reverse', False):
                collection = reversed(collection)

            # Synthetize a list, as Jinja doesn't seem to be dealing well with iterator here
            # Set prev/next links for primary collection
            coll = []

            # Set prev/next links for collection
            for idx, post in enumerate(collection):
                coll.append(post)

                if idx < 1:
                    continue

                next_item = { 'path': post['path'], 'title': post['title'] }
                prev_item = { 'path': coll[idx-1]['path'], 'title': coll[idx-1]['title'] }

                # set it within collection
                coll[idx-1]['next'] = next_item
                coll[idx]['previous'] = prev_item

                # set the default collection as global prev/next
                if key in self.config and self.config[key].get('default', False):
                    hana.files[coll[idx-1]['path']]['next'] = next_item
                    hana.files[post['path']]['previous'] = prev_item


            hana.metadata['collections'][key] = coll


# Pretty url

import os

class PrettyUrl():

    def __init__(self, relative=True, index_file='index.html'):
        self.index_file = index_file

    def __call__(self, file_gen, hana):
        html_re = re.compile(r'\.(htm|html)$')

        for filename, f in file_gen:
            if not html_re.search(filename):
                continue

            if not f.get('permalink', True):
                continue

            del hana.files[filename]

            path, _ = os.path.splitext(filename)
            path = os.path.join(path, self.index_file)
            print path

            hana.files[path] = f
            f.permalink = True


# Beautify

from bs4 import BeautifulSoup
import re

#TODO: this screws with html introducing new white space/newlines.

def beautify(indent_size=4, indent_char=" "):
    html_re = re.compile(r'\.(htm|html)$')

    def beautify_plugin(file_gen, hana):
        for filename, f in file_gen:

            if not html_re.search(filename):
                continue

            #TODO temporary
            if not f['contents'][0:2] == '<!':
                continue

            soup = BeautifulSoup(f['contents'], 'html.parser')
            f['contents'] = soup.prettify(formatter="minimal")

    return beautify_plugin

