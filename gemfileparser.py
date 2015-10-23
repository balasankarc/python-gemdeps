#!/usr/bin/env python

import csv
import StringIO
import re


class GemfileParser:

    class Dependency:

        def __init__(self):
            self.name = ''
            self.reqtype = ''
            self.requirement = ''
            self.autorequire = ''
            self.source = ''
            self.parent = ''

        def __str__(self):
            return self.name

    gemname_regex = re.compile(r"(?P<gemname>[a-zA-Z _-]+)")
    req_regex = re.compile(r"(?P<reqs>([>|<|=|~>|\d]+[ ]*[0-9\.\w]+[ ,]*)+)")
    source_regex = re.compile(r"source:[ ]?(?P<source>[a-zA-Z:\/\.-]+)")
    autoreq_regex = re.compile(r"require:[ ]?(?P<autoreq>[a-zA-Z:\/\.-]+)")

    def __init__(self, filepath):
        self.gemfile = open(filepath)
        self.dependencies = []
        self.contents = self.gemfile.readlines()
        if filepath.endswith('gemspec'):
            self.gemspec = True
        else:
            self.gemspec = False

    def parse(self):

        dependencies = []
        for line in self.contents:
            line = line.strip()
            if line.startswith('source') or line.startswith('#'):
                continue
            elif line.startswith('gem'):
                line = line[3:]
                linefile = StringIO.StringIO(line)
                for i in csv.reader(linefile, delimiter=','):
                    m = []
                    for k in i:
                        l = k.replace("'", "").replace('"', "").strip()
                        if "#" in l:
                            l = l[:l.index("#")]
                        m.append(l)
                    dep = self.Dependency()
                    for k in m:
                        match = self.source_regex.match(k)
                        if match:
                            dep.source = match.group('source')
                            continue
                        match = self.autoreq_regex.match(k)
                        if match:
                            dep.autorequire = match.group('autoreq')
                            continue
                        match = self.gemname_regex.match(k)
                        if match:
                            dep.name = match.group('gemname')
                            continue
                        match = self.req_regex.match(k)
                        if match:
                            if dep.requirement == '':
                                dep.requirement = match.group('reqs')
                            else:
                                dep.requirement += ' ' + match.group('reqs')
                            continue
                    dep.parent = 'diaspora'
                    dependencies.append(dep)
        return dependencies

if __name__ == "__main__":
    n = GemfileParser('Gemfile')
    n.parse()
