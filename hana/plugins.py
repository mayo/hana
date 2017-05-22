
# Metadata plugin

def metadata(metadata):
    def set_metadata(files, hana):
        for f in files.itervalues():
            f.metadata.update(metadata)

    return set_metadata

#Front matter plugin

import frontmatter

def front_matter(files, hana):
    for f in files.itervalues():
        metadata, f.contents = frontmatter.parse(f.contents)
        f.metadata.update(metadata)

#Ignore files plugin

import pathspec

def ignore(patterns):
    spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def remove_files(files, hana):
        matches = spec.match_files(files.iterkeys())

        for f in matches:
            del files[f]

    return remove_files

