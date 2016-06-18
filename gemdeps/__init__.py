#!/usr/bin/env python

import copy
import json
import os
from distutils.version import LooseVersion

from gemfileparser import GemfileParser

from .util import *

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen


class DetailedDependency(object):
    '''
    Class to hold complete information about a gem. It includes::
      * Rubygem specific information
      * Debian packaging information
      * Rquirement Satisfaction information
    '''

    def __init__(self, original_dep=GemfileParser.Dependency()):
        '''
        Initialize attributes.
        '''
        self.name = original_dep.name
        self.requirement = original_dep.requirement
        self.autorequire = original_dep.autorequire
        self.source = original_dep.source
        self.parent = original_dep.parent
        self.group = original_dep.group
        self.color = ''
        self.version = ''
        self.status = ''
        self.suite = ''
        self.satisfied = ''
        self.link = ''
        self.debian_name = self.get_debian_name()

    def get_debian_name(self):
        '''
        Returns debian specific name of the gem.
        According to Debian Ruby team convention the following format is
        followed:

        * If gem is used as a library, add the prefix 'ruby-'
        * Underscores are replaced with a single hyphen
        * Double hyphens are replaced with a single hyphen
        '''
        if self.name in GEM_EXCEPTIONS:
            return GEM_EXCEPTIONS[self.name]
        else:
            hyphen_name = self.name.replace("_", "-")
            hyphen_name = hyphen_name.replace("--", "-")
            debian_name = "ruby-" + hyphen_name
            return debian_name

    def is_in_unstable(self):
        '''
        Check if the dependency is satisfied in unstable.
        '''
        rmadison_output = os.popen(
            'rmadison -s unstable -a amd64,all %s 2>&1' % self.debian_name)
        rmadison_output = rmadison_output.read()
        count = 0
        if "curl:" in rmadison_output:
            # If curl returns an error, repeat the steps
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
            self.link = "https://tracker.debian.org/pkg/%s" % self.debian_name
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_in_experimental(self):
        '''
        Check if the dependency is satisfied in experimental.
        '''
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
            self.link = "https://tracker.debian.org/pkg/%s" % self.debian_name
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_in_new(self):
        '''
        Check if the package is still in the NEW queue.
        '''
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
            self.link = "https://ftp-master.debian.org/new/%s_%s.html" % (
                self.debian_name, self.version)
        except:
            self.version = "NA"
            self.suite = "Unpackaged"
            self.status = "Unpackaged"

    def is_itp(self):
        '''
        Check if the dependency has an open ITP against it.
        '''
        wnpp_output = os.popen('wnpp-check %s' % self.debian_name)
        wnpp_output = wnpp_output.read()
        count = 0
        if "curl:" in wnpp_output:
            while "curl:" in wnpp_output:
                count = count + 1
                wnpp_output = os.popen('wnpp-check %s' % self.debian_name)
                wnpp_output = wnpp_output.read()
        self.version = "NA"
        if wnpp_output == "":
            self.suite = "Unpackaged"
            self.status = "Unpackaged"
        else:
            pos1 = wnpp_output.index('#')
            pos2 = wnpp_output.index(')')
            if 'ITP' in wnpp_output:
                self.suite = "ITP"
                self.status = "ITP"
            elif 'RFP' in wnpp_output:
                self.suite = "RFP"
                self.status = "RFP"
            self.link = "https://bugs.debian.org/%s" % wnpp_output[
                pos1 + 1:pos2]

    def set_color(self):
        '''
        Set the color for progressbar based on packaging status, suite and
        satisfaction.
        '''
        if self.suite == 'Unstable':
            self.color = 'green'
        elif self.suite == 'Experimental':
            self.color = 'yellow'
        elif self.suite == 'NEW':
            self.color = 'blue'
        elif self.suite == 'ITP' or self.suite == 'RFP':
            self.color = 'cyan'
        else:
            self.color = 'red'
        if not self.satisfied:
            if self.color not in ['red', 'cyan']:
                # Package status has more priority than satisfaction
                self.color = 'violet'

    def version_check(self):
        '''
        Returns if debian_version satisfies gem_requirement.
        '''
        gem_requirement, debian_version = self.requirement, self.version

        if self.name in SKIP_VERSION_CHECK:
            self.satisfied = True
            return

        if gem_requirement == '' and self.status == 'Packaged':
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
            status = version_satisfy_requirement(req, debian_version)
            if status is False:
                break
        self.satisfied = status

    def debian_status(self, jsoncontent={}):
        '''
        Calls necessary functions to set the packaging status.
        '''
        if self.name in jsoncontent:
            self.version = jsoncontent[self.name]['version']
            self.suite = jsoncontent[self.name]['suite']
            self.link = jsoncontent[self.name]['link']
            if self.suite == 'Unpackaged':
                self.status = "Unpackaged"
            elif self.suite == 'ITP':
                self.status = "ITP"
            elif self.suite == 'RFP':
                self.status = "RFP"
            else:
                self.status = "Packaged"
        else:
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


class GemDeps(object):
    '''
    Main Class to generate dependency list of a Ruby (on Rails) app.
    '''

    def __init__(self, appname):
        '''
        Initialize necessary attributes.
        '''
        self.appname = appname
        self.original_list = []
        self.dependency_list = {}

    def process(self, path):
        '''
        Generates dependency list based on provided input file.

        **Algorithm**
         1. Start
         2. Get list of direct dependencies from Gemfile
         3. For each dependency in dependency_list, "dep"

            a. Find out packaging status of "dep"
            b. If "dep" is satisfied in Debian, continue to next "dep"
            c. Else

               i. Get the runtime dependencies of "dep" from Rubygems API
                  at https://rubygems.org/api/v1/dependencies.json
               ii. Add each runtime dependency to dependency_list
        '''
        self.parser = GemfileParser(path, appname=self.appname)
        # self.cached_info = self.get_cache_content()
        parsed = self.parser.parse_gemfile(path)
        self.original_list = parsed['runtime'] + parsed['production']
        self.original_list_name = [x.name for x in self.original_list]
        counter = 0
        while True:
            try:
                current_gem = DetailedDependency(self.original_list[counter])
                print("Current Gem: %s" % current_gem.name)
                if "rails-assets" in current_gem.name:
                    print("\tRails Assets Found. Skipping")
                    counter = counter + 1
                    continue
                current_gem.debian_status()
                self.dependency_list[current_gem.name] = current_gem
                if current_gem.satisfied:
                    print("%s is satisfied in %s" % (current_gem.name,
                                                     current_gem.suite))
                else:
                    gem_dependencies = self.get_dependencies(current_gem)
                    for dep in gem_dependencies:
                        dep.parent.append(current_gem.name)
                        if dep.name not in self.original_list_name:
                            self.original_list.append(dep)
                            self.original_list_name.append(dep.name)
                        else:
                            existing_position = self.original_list_name.\
                                index(dep.name)
                            requirement1 = self.original_list[
                                existing_position].requirement
                            requirement2 = dep.requirement
                            stricter_req = get_stricter(requirement1,
                                                        requirement2)
                            if stricter_req != requirement1:
                                self.original_list[existing_position]\
                                    .requirement = requirement2
                counter = counter + 1
                pass
            except IndexError:
                break

    def get_dependencies(self, gem):
        '''
        Return dependencies of a gem.
        '''
        print("Getting Dependencies of %s" % gem.name)
        api_url = 'https://rubygems.org/api/v1/dependencies.json'
        parameters = 'gems=%s' % gem.name
        fetch_url = api_url + '?' + parameters
        a = urlopen(url=fetch_url)
        serialized = json.loads(a.read().decode('utf-8'))
        latest_gem = self.smallest_satisfiable(serialized, gem)
        dependency_list = []
        for dependency in latest_gem['dependencies']:
            n = GemfileParser.Dependency()
            n.name = dependency[0]
            n.requirement = dependency[1]
            dependency_list.append(n)
        return dependency_list

    def smallest_satisfiable(self, serialized, gem):
        '''
        Get smallest version of gem that satisfies the requirement.
        '''
        version_list = {}
        version_gem_list = []
        for gem_version in serialized:
            version_list[gem_version['number']] = gem_version
            version_gem_list.append(gem_version['number'])
        least = least_satisfiable_version(gem.requirement, version_gem_list)
        print("Gem name: %s, Requirement: %s, Selected Version: %s" %
              (gem.name, gem.requirement, least))
        return version_list[least]

    def write_output(self):
        '''
        Generate output in JSON format to generate statusbar.
        '''
        new_list = {}
        for dep in self.dependency_list:
            new_list[dep] = self.dependency_list[dep].__dict__
        with open(self.appname + "_debian_status.json", "w") as f:
            f.write(json.dumps(new_list, indent=4))

    def generate_dot(self):
        '''
        Generate output in dot format to generate graphs.
        '''
        dotf = open('%s.dot' % self.appname, 'w')
        dotf.write('digraph %s\n{\n' % self.appname)
        for dep in self.dependency_list:
            name = dep
            color = self.dependency_list[dep].color
            block = '"%s"[color=%s];\n' % (name, color)
            dotf.write(block)
            for parent in self.dependency_list[dep].parent:
                dotf.write('"%s"->"%s";\n' %
                           (parent, self.dependency_list[dep].name))
        dotf.write("}")
        dotf.close()
