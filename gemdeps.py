from gemfileparser import GemfileParser
import json
import urllib2
import os


exceptions = {'rake': 'rake',
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


class DetailedDependency(GemfileParser.Dependency):
    '''Debian specific details of each gem'''

    def get_debian_name(self):
        if self.name in exceptions:
            return exceptions[self.gemname]
        else:
            hyphen_name = self.name.replace("_", "-")
            debian_name = "ruby-" + hyphen_name
            return debian_name

    def __init__(self, origdependency):
        self.name = origdependency.name
        self.reqtype = origdependency.reqtype
        self.requirement = origdependency.requirement
        self.autorequire = origdependency.autorequire
        self.source = origdependency.source
        self.parent = origdependency.parent
        self.debian_name = self.get_debian_name()
        self.color = ''
        self.version = ''
        self.status = ''

    def is_in_unstable(self):
        rmadison_output = os.popen(
            'rmadison -s unstable -a amd64,all %s 2>&1' % self.debian_name)
        rmadison_output = rmadison_output.read()
        # print "rmadison output is " + rmadison_output
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                # print "Retrying #", count
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s unstable -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
                # print "rmadison output is " + rmadison_output
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
        # print "rmadison output is " + rmadison_output
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                # print "Retrying #", count
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s experimental -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
                # print "rmadison output is " + rmadison_output
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
        # print "rmadison output is " + rmadison_output
        count = 0
        if "curl:" in rmadison_output:
            while "curl:" in rmadison_output:
                # print "Retrying #", count
                count = count + 1
                rmadison_output = os.popen(
                    'rmadison -s new -a amd64,all %s 2>&1'
                    % self.debian_name)
                rmadison_output = rmadison_output.read()
                # print "rmadison output is " + rmadison_output
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
                # print "Retrying #", count
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
            self.color = 'success'
        elif self.suite == 'Experimental':
            self.color = 'warning'
        elif self.suite == 'NEW':
            self.color = 'active'
        elif self.suite == 'ITP':
            self.color = 'itp'
        else:
            self.color = 'danger'

    def debian_status(self):
        # print "####"
        # print self.debian_name
        # print "Checking in unstable"
        self.is_in_unstable()
        if self.version == 'NA':
            # print "Checking in Experimental"
            self.is_in_experimental()
        if self.version == 'NA':
            # print "Checking in NEW"
            self.is_in_new()
        if self.version == 'NA':
            # print "Checking in ITP"
            self.is_itp()
        self.set_color()


if __name__ == '__main__':
    parser = GemfileParser('Gemfile')
    # print "Reading Gemfile"
    deps = parser.parse()
    # print "Read Gemfile"
    counter = 0
    # print "Reading from rubygems"
    while True:
        currentgem = deps[counter].name
        # print currentgem
        urlfile = urllib2.urlopen(
            'https://rubygems.org/api/v1/gems/%s.json' % currentgem)
        jsondata = json.loads(urlfile.read())
        for dep in jsondata['dependencies']['runtime']:
            if dep['name'] not in [x.name for x in deps]:
                n = parser.Dependency()
                n.name = dep['name']
                n.requirement = dep['requirements']
                n.parent = currentgem
                deps.append(n)
        counter = counter + 1
        if counter >= len(deps):
            break
    a = open('deplist.json', 'w')
    t = json.dumps([dep.__dict__ for dep in deps])
    a.write(str(t))
    a.close()
    extended_dep_list = []
    b = open("Gemfile.dot", "w")
    for dep in deps:
        n = DetailedDependency(dep)
        n.debian_status()
        extended_dep_list.append(n)
        b.write(n.name + "," + n.requirement + "," + n.version +
                "," + n.suite + "," + n.color + "," + n.status + "\n")
    b.close()
    a = open('extendedlist.json', 'w')
    t = json.dumps([dep.__dict__ for dep in extended_dep_list])
    a.write(str(t))
    a.close()
