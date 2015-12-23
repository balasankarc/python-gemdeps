#!/usr/bin/env python

import argparse
import json
import os
import urllib2
import sys
import re
import copy

from jinja2 import Environment, FileSystemLoader

from gemfileparser import gemfileparser

gem_exceptions = {'rake': 'rake',
                  'rubyntlm': 'ruby-ntlm',
                  'rails': 'rails',
                  'asciidoctor': 'asciidoctor',
                  'unicorn': 'unicorn',
                  'capistrano': 'capistrano',
                  'cucumber': 'cucumber',
                  'rubyzip': 'ruby-zip',
                  'thin': 'thin',
                  'racc': 'racc',
                  'pry': 'pry',
                  'rexical': 'rexical',
                  'messagebus_ruby_api': 'ruby-messagebus-api',
                  'bundler': 'bundler',
                  'org-ruby': 'ruby-org',
                  'CFPropertyList': 'ruby-cfpropertylist',
                  'ruby-saml': 'ruby-saml',
                  'ruby_parser': 'ruby-parser',
                  'RedCloth': 'ruby-redcloth',
                  'gitlab_omniauth-ldap': 'ruby-omniauth-ldap',
                  "pyu-ruby-sasl": "ruby-sasl",
                  "gitlab-grit": "ruby-grit",
                  "ruby-fogbugz": "ruby-fogbugz",
                  "ruby-oembed": "ruby-oembed"}

skip_version_check = ['bootstrap-sass', 'messagebus_ruby_api']


class DetailedDependency(gemfileparser.GemfileParser.Dependency):
    '''Debian specific details of each gem'''

    def get_debian_name(self):
        if self.name in gem_exceptions:
            return gem_exceptions[self.name]
        else:
            hyphen_name = self.name.replace("_", "-")
            hyphen_name = hyphen_name.replace("--", "-")
            debian_name = "ruby-" + hyphen_name
            return debian_name

    def __init__(self, origdep=gemfileparser.GemfileParser.Dependency()):
        self.name = origdep.name
        self.requirement = origdep.requirement
        self.autorequire = origdep.autorequire
        self.source = origdep.source
        self.parent = origdep.parent
        self.group = origdep.group
        self.debian_name = self.get_debian_name()
        self.color = ''
        self.version = ''
        self.status = ''
        self.suite = ''
        self.satisfied = ''

    def is_in_unstable(self):
        rmadison_output = os.popen(
            'rmadison -s unstable -a amd64,all %s 2>&1' % self.debian_name)
        rmadison_output = rmadison_output.read()
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s unstable -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
        self.suite = "Unstable"
        self.status = "Packaged"
        try:
            self.version = rmadison_output.split("|")[1].strip()
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_in_experimental(self):
        rmadison_output = os.popen(
            'rmadison -s experimental -a amd64,all %s 2>&1' % self.debian_name)
        rmadison_output = rmadison_output.read()
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s experimental -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
        self.suite = "Experimental"
        self.status = "Packaged"
        try:
            self.version = rmadison_output.split("|")[1].strip()
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_in_new(self):
        rmadison_output = os.popen(
            'rmadison -s new -a amd64,all %s 2>&1' % self.debian_name)
        rmadison_output = rmadison_output.read()
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s new -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
        self.suite = "NEW"
        self.status = "NEW"
        try:
            self.version = rmadison_output.split("|")[1].strip()
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_itp(self):
        wnpp_output = os.popen('wnpp-check %s' % self.debian_name)
        wnpp_output = wnpp_output.read()
        count = 0
        if "curl:" in wnpp_output:
            while "curl:" in wnpp_output:
                count = count + 1
                wnpp_output = os.popen('wnpp-check %s' % self.debian_name)
                wnpp_output = wnpp_output.read()
        self.suite = "ITP"
        self.status = "ITP"
        self.version = "NA"
        if wnpp_output == "":
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def set_color(self):
        if self.suite == 'Unstable':
            self.color = 'green'
        elif self.suite == 'Experimental':
            self.color = 'yellow'
        elif self.suite == 'NEW':
            self.color = 'blue'
        elif self.suite == 'ITP':
            self.color = 'cyan'
        else:
            self.color = 'red'
        if not self.satisfied:
            if self.color not in ['red', 'cyan']:
                self.color = 'violet'

    def get_operator(self, requirement):
        ''' Splits the operator and version from a requirement string'''
        m = re.search("\d", requirement)
        pos = m.start()
        if pos == 0:
            return '=', requirement
        check = requirement[:pos].strip()
        ver = requirement[pos:]
        return check, ver

    def version_check(self):
        ''' Returns in debian_version satisfies gem_requirement'''
        gem_requirement, debian_version = self.requirement, self.version

        if self.name in skip_version_check:
            self.satisfied = True
            return

        if gem_requirement == '':
            self.satisfied = True
            return
        if debian_version == 'NA':
            self.satisfied = False
            return

        # Cleaning up version status in Debian
        if ":" in debian_version:
            pos = debian_version.index(":")
            debian_version = debian_version[pos + 1:]
        pos_rev = debian_version.index("-")
        debian_version = debian_version[:pos_rev]
        if '~' in debian_version:
            debian_version = debian_version[:debian_version.index('~')]
        elif '+' in debian_version:
            debian_version = debian_version[:debian_version.index('+')]

        # Cleaning up version requirement in gem
        requirement = gem_requirement.split(',')
        requirement = [x.strip() for x in requirement]

        # Perform comparison
        status = True
        for req in requirement:
            check, ver = self.get_operator(req)
            if check == '=':
                if debian_version == ver:
                    status = True
                else:
                    status = False
                    break
            elif check == '<=':
                if debian_version <= ver:
                    status = True
                else:
                    status = False
                    break
            elif check == '<':
                if debian_version < ver:
                    status = True
                else:
                    status = False
                    break
            elif check == '>':
                if debian_version > ver:
                    status = True
                else:
                    status = False
                    break
            elif check == '>=':
                if debian_version >= ver:
                    status = True
                else:
                    status = False
                    break
            elif check == '~>':
                n = min(debian_version.count('.'), ver.count('.'))
                dotcount = 0
                i = 0
                while dotcount < n and i < min(len(debian_version), len(ver)):
                    if debian_version[i] != ver[i]:
                        status = False
                        break
                    if debian_version[i] == '.':
                        dotcount += 1
                    i += 1
                if status is False:
                    break
        self.satisfied = status

    def debian_status(self):
        print "\t" + self.name
        self.is_in_unstable()
        if self.version == 'NA':
            self.is_in_experimental()
        if self.version == 'NA':
            self.is_in_new()
        if self.version == 'NA':
            self.is_itp()
        self.version_check()
        if not self.satisfied:
            tmp = copy.deepcopy(self)
            tmp.suite = ''
            tmp.satisfied = ''
            tmp.version = ''
            tmp.is_in_experimental()
            tmp.version_check()
            if tmp.satisfied:
                self.version = tmp.version
                self.suite = tmp.suite
                self.satisfied = tmp.satisfied
        self.set_color()


class Gemdeps:

    def __init__(self, appname):
        self.dep_list = []
        self.extended_dep_list = []
        self.appname = appname

    def dep_list_from_file(self, path):
        print "Fetching Dependencies"
        f = open(path)
        content = f.read()
        jsoncontent = json.loads(content)
        for item in jsoncontent:
            print "\t" + item['name']
            dep = gemfileparser.GemfileParser.Dependency()
            for key in item.keys():
                setattr(dep, key, item[key])
            self.dep_list.append(dep)

    def deb_status_list_from_file(self, path):
        f = open(path)
        content = f.read()
        jsoncontent = json.loads(content)
        for item in jsoncontent:
            print item['name']
            dep = DetailedDependency()
            for key in item.keys():
                setattr(dep, key, item[key])
            self.extended_dep_list.append(dep)

    def generate_html_csv(self):
        appname = self.appname
        packaged_count = 0
        unpackaged_count = 0
        itp_count = 0
        total = 0
        extended_dep_list = self.extended_dep_list
        for n in self.extended_dep_list:
            if n.status == 'Packaged' or n.status == 'NEW':
                packaged_count += 1
            elif n.status == 'ITP':
                itp_count += 1
            else:
                unpackaged_count += 1
        total = len(self.extended_dep_list)
        percent_complete = (packaged_count * 100) / total
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('main.html')
        render = template.render(locals())
        print "Generating HTML"
        with open(self.appname + ".html", "w") as file:
            file.write(render)

    def generate_pdf_dot(self, path=''):
        if not path:
            pdfout = open(self.appname + ".dot", "w")
            pdfout.write('digraph graphname {\n')
            for n in self.extended_dep_list:
                name = n.name.replace('-', '_').replace('.', '_')
                parent_name = n.parent.replace('-', '_').replace('.', '_')
                pdfout.write("\t" + name + "[color=" + n.color + "];\n")
                pdfout.write("\t" + parent_name + " -> " + name + " ;\n")
            pdfout.write('}')
            pdfout.close()
            os.popen('dot -Tps ' + self.appname +
                     '.dot -o ' + appname + '_dependency.pdf')
        else:
            os.popen('dot -Tps ' + path + ' -o ' + appname + '_dependency.pdf')

    def filetype(self, path):
        if path.lower().endswith('gemfile'):
            return 'gemfile'
        elif path.lower().endswith('gemspec'):
            return 'gemspec'
        else:
            print "Input filename should end with '.gemfile' or '.gemspec'"
            sys.exit(0)

    def get_deps(self, path):
        if not self.extended_dep_list:
            if not self.dep_list:
                if self.filetype(path) == 'gemfile':
                    print "Fetching Dependencies"
                    gemparser = gemfileparser.GemfileParser(path,
                                                            self.appname)
                    completedeps = gemparser.parse()
                    self.dep_list = completedeps['runtime']
                    counter = 0
                    while True:
                        currentgem = self.dep_list[counter].name
                        print "\t" + currentgem
                        if "rails-assets" not in currentgem:
                            urlfile = urllib2.urlopen(
                                'https://rubygems.org/api/v1/gems/%s.json'
                                % currentgem)
                            jsondata = json.loads(urlfile.read())
                            for dep in jsondata['dependencies']['runtime']:
                                if dep['name'] not in [x.name
                                                       for x in
                                                       self.dep_list]:
                                    n = gemparser.Dependency()
                                    n.name = dep['name']
                                    n.requirement = dep['requirements']
                                    n.parent = currentgem
                                    self.dep_list.append(n)
                            counter = counter + 1
                            if counter >= len(self.dep_list):
                                break
                        else:
                            counter = counter + 1
                            continue
                    deplistout = open(self.appname + '_deplist.json', 'w')
                    t = json.dumps([dep.__dict__ for dep in self.dep_list])
                    deplistout.write(str(t))
                    deplistout.close()
            print "\n\nDebian Status"
            for dep in self.dep_list:
                n = DetailedDependency(dep)
                n.debian_status()
                self.extended_dep_list.append(n)
            jsonout = open(self.appname + '_debian_status.json', 'w')
            t = json.dumps([dep.__dict__
                            for dep in self.extended_dep_list], indent=4)
            jsonout.write(str(t))
            jsonout.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get application dependency status')
    parser.add_argument(
        "--html", help="Use this option if you want HTML progressbar",
        action='store_true')
    parser.add_argument(
        "--pdf", help="Use this option if you want pdf dependency graph",
        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--deplistfile", dest="deplist",
                       help="Provide deplist.json as input\
                               (Skip fetching dependencies)")
    group.add_argument("--debstatusfile", dest="debian_status",
                       help="Provide debian_status.json as input \
                               (Skip checking Debian status)")
    group.add_argument("--dotfile", dest="dotfile",
                       help="Provide dot file to generate pdf")
    group.add_argument("--inputfile", dest="input_file",
                       help="Input path of gemfile or gemspec")
    parser.add_argument("appname", help="Name of the application")
    args = parser.parse_args()
    appname = args.appname
    gemdeps = Gemdeps(appname)
    if args.deplist:
        gemdeps.dep_list_from_file(args.deplist)
        path = ''
        gemdeps.get_deps(path)
    elif args.debian_status:
        gemdeps.deb_status_list_from_file(args.debian_status)
    elif args.input_file:
        path = os.path.abspath(args.input_file)
        gemdeps.get_deps(path)
    if args.html:
        gemdeps.generate_html_csv()
    if args.pdf:
        if args.dotfile:
            path = args.dotfile
        else:
            path = ''
        gemdeps.generate_pdf_dot(path)
