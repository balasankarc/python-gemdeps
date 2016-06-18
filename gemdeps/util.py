#!/usr/bin/env python

import re
from distutils.version import LooseVersion


GEM_EXCEPTIONS = {'rake': 'rake',
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
                  "ruby-oembed": "ruby-oembed",
                  "gollum-grit_adapter": "ruby-gollum-rugged-adapter",
                  "rails-assets-markdown-it--markdown-it-for-inline":
                      "ruby-rails-assets-markdown-it--markdown-it-for-inline",
                  "concurrent-ruby": "ruby-concurrent",
                  "ruby-beautify": "ruby-beautify",
                  "ruby-prof": "ruby-prof"}

SKIP_VERSION_CHECK = ['bootstrap-sass',
                      'messagebus_ruby_api',
                      'gitlab_omniauth-ldap']


def get_operator(requirement):
    '''
    Splits the operator and version from a requirement string.
    '''
    if requirement == '':
        return '>=', '0'
    m = re.search("\d", requirement)
    pos = m.start()
    if pos == 0:
        return '=', requirement
    check = requirement[:pos].strip()
    ver = requirement[pos:]
    return check, ver


def get_stricter(requirement1, requirement2):
    '''
    Returns the stricter requirement of the two.
    '''
    check1, ver1 = get_operator(requirement1)
    check2, ver2 = get_operator(requirement2)
    if check1 == '=':
        return requirement1
    elif check2 == '=':
        return requirement2
    elif check1 == '>' or check1 == '>=':
        if check2 == '>' or check2 == '>=':
            ver1 = LooseVersion(str(ver1))
            ver2 = LooseVersion(str(ver2))
            result = requirement1 if ver1 >= ver2 else requirement2
            return result
            # Return largest
        elif check2 == '<' or check2 == '<=':
            return requirement1
        elif check2 == '~>':
            ver1 = LooseVersion(str(ver1))
            ver2 = LooseVersion(str(ver2))
            if len(ver2.version) > 1:
                result = requirement2
            else:
                result = requirement1 if ver1 >= ver2 else requirement2
            return result
    elif check1 == '<' or check1 == '<=':
        if check2 == '<' or check2 == '<=':
            ver1 = LooseVersion(str(ver1))
            ver2 = LooseVersion(str(ver2))
            result = requirement1 if ver1 <= ver2 else requirement2
            return result
            # Return smallest
        elif check2 == '>' or check2 == '>=':
            return requirement2
        elif check2 == '~>':
            return requirement2
    elif check1 == '~>':
        if check2 == '~>':
            ver1 = LooseVersion(str(ver1))
            ver2 = LooseVersion(str(ver2))
            result = requirement1 if ver1 <= ver2 else requirement2
            return result
            # Return smallest
        elif check2 == '>' or check2 == '>=':
            ver1 = LooseVersion(str(ver1))
            ver2 = LooseVersion(str(ver2))
            if len(ver2.version) > 1:
                result = requirement2
            else:
                result = requirement1 if ver1 >= ver2 else requirement2
            return result
        elif check2 == '<' or check2 == '<=':
            return requirement1


def version_satisfy_requirement(requirement, input_version):
    '''
    Returns if input_version satisfies requirement.
    '''
    check, ver = get_operator(requirement)
    input_version = LooseVersion(str(input_version))
    ver = LooseVersion(str(ver))
    status = False
    if check == '=' and input_version == ver:
        status = True
    elif check == '<=' and input_version <= ver:
        status = True
    elif check == '<' and input_version < ver:
        status = True
    elif check == '>' and input_version > ver:
        status = True
    elif check == '>=' and input_version >= ver:
        status = True
    elif check == '~>':
        status = True
        input_version_int = input_version.version
        ver_int = ver.version
        n = min(len(input_version_int), len(ver_int)) - 1
        partcount = 0
        while partcount < n:
            if input_version_int[partcount] != ver_int[partcount]:
                status = False
                break
            partcount += 1
        if partcount < len(input_version_int):
            try:
                intdebver = input_version_int[partcount]
                intver = ver_int[partcount]
                if intdebver < intver:
                    status = False
            except:
                if input_version_int[partcount] < ver_int[partcount]:
                    status = False
        else:
            status = False
    return status


def least_satisfiable_version(requirement, version_list):
    '''
    Returns the smallest version that satisfies requirement.
    '''
    satisfied_list = []
    for version in version_list:
        if version_satisfy_requirement(requirement, version):
            satisfied_list.append(LooseVersion(str(version)))
    return str(min(satisfied_list))
