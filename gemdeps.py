#!/usr/bin/env python

import argparse
import json
import os
import urllib2
import sys

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
                  "pyu-ruby-sasl": "ruby-sasl"}


class DetailedDependency(gemfileparser.GemfileParser.Dependency):
    '''Debian specific details of each gem'''

    def get_debian_name(self):
        if self.name in gem_exceptions:
            return gem_exceptions[self.name]
        else:
            hyphen_name = self.name.replace("_", "-")
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

    def debian_status(self):
        print "\t" + self.name
        self.is_in_unstable()
        if self.version == 'NA':
            self.is_in_experimental()
        if self.version == 'NA':
            self.is_in_new()
        if self.version == 'NA':
            self.is_itp()
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
            print "\t"+item['name']
            dep = gemfileparser.GemfileParser.Dependency()
            dep.name = item['name']
            dep.requirement = item['requirement']
            dep.group = item['group']
            dep.parent = item['parent']
            dep.autorequire = item['autorequire']
            dep.source = item['source']
            self.dep_list.append(dep)

    def deb_status_list_from_file(self, path):
        f = open(path)
        content = f.read()
        jsoncontent = json.loads(content)
        for item in jsoncontent:
            print item['name']
            dep = DetailedDependency()
            dep.name = item['name']
            dep.requirement = item['requirement']
            dep.group = item['group']
            dep.parent = item['parent']
            dep.autorequire = item['autorequire']
            dep.source = item['source']
            dep.debian_name = item['debian_name']
            dep.color = item['color']
            dep.version = item['version']
            dep.status = item['status']
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

    def generate_pdf_dot(self):
        pdfout = open(self.appname + ".dot", "w")
        pdfout.write('digraph graphname {\n')
        for n in self.extended_dep_list:
            name = n.name.replace('-', '_').replace('.', '_')
            parent_name = n.parent.replace('-', '_').replace('.', '_')
            pdfout.write("\t" + name + "[color=" + n.color + "];\n")
            pdfout.write("\t" + parent_name + " -> " + name + " ;\n")
        pdfout.write('}')
        pdfout.close()
        os.popen('dot -Tps ' + self.appname + '.dot dependency.pdf')

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
                        print "\t"+currentgem
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
                            for dep in self.extended_dep_list])
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
        gemdeps.generate_pdf_dot()
