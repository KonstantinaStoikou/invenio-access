# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of CDS Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008 CERN.
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""External user authentication for CERN NICE/CRA Invenio."""

__revision__ = \
    "$Id$"

import httplib
import socket
import re

from invenio.external_authentication import ExternalAuth, \
        InvenioWebAccessExternalAuthError


# Tunable list of settings to be hidden
CFG_EXTERNAL_AUTH_HIDDEN_SETTINGS = ('auth', 'respccid', 'personid')
# Tunable list of groups to be hidden
CFG_EXTERNAL_AUTH_HIDDEN_GROUPS = (
    'All Exchange People',
    'CERN Users',
    'cern-computing-postmasters',
    'cern-nice2000-postmasters',
    'CMF FrontEnd Users',
    'CMF_NSC_259_NSU',
    'Domain Users',
    'GP Apply Favorites Redirection',
    'GP Apply NoAdmin',
    'info-terminalservices',
    'info-terminalservices-members',
    'IT Web IT',
    'NICE Deny Enforce Password-protected Screensaver',
    'NICE Enforce Password-protected Screensaver',
    'NICE LightWeight Authentication WS Users',
    'NICE MyDocuments Redirection (New)',
    'NICE Profile Redirection',
    'NICE Terminal Services Users',
    'NICE Users',
    'NICE VPN Users',
    )
CFG_EXTERNAL_AUTH_HIDDEN_GROUPS_RE = (
    re.compile(r'Users by Letter [A-Z]'),
    re.compile(r'building-[\d]+'),
    re.compile(r'Users by Home CERNHOME[A-Z]'),
    )

# Prefix name for Shibboleth variables
CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME = 'HTTP_ADFS_'
# Name of the variable containing groups
CFG_EXTERNAL_AUTH_SSO_GROUP_VARIABLE = CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME+'GROUP'
# Name of the variable containing login name
CFG_EXTERNAL_AUTH_SSO_LOGIN_VARIABLE = CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME+'LOGIN'
# Name of the variable containing email
CFG_EXTERNAL_AUTH_SSO_EMAIL_VARIABLE = CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME+'EMAIL'
# Name of the variable containing groups
CFG_EXTERNAL_AUTH_SSO_GROUP_VARIABLE = CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME+'GROUP'
# Separator character for group variable
CFG_EXTERNAL_AUTH_SSO_GROUPS_SEPARATOR = ';'

class ExternalAuthSSO(ExternalAuth):
    """
    External authentication example for a custom SSO-based
    authentication service.
    """


    def __init__(self, enforce_external_nicknames=False):
        """Initialize stuff here"""
        ExternalAuth.__init__(self, enforce_external_nicknames)


    def auth_user(self, username, password, req=None):
        """
        Check USERNAME and PASSWORD against the SSO system.
        Return None if authentication failed, or the email address of the
        person if the authentication was successful.  In order to do
        this you may perhaps have to keep a translation table between
        usernames and email addresses.
        If it is the first time the user logs in Invenio the nickname is
        stored alongside the email. If this nickname is unfortunatly already
        in use it is discarded. Otherwise it is ignored.
        Raise InvenioWebAccessExternalAuthError in case of external troubles.
        Note: for SSO the parameter are discarded and overloaded by Shibboleth
        variables
        """
        if req:
            req.add_common_vars()
            if req.subprocess_env.has_key(CFG_EXTERNAL_AUTH_SSO_EMAIL_VARIABLE):
                return req.subprocess_env[CFG_EXTERNAL_AUTH_SSO_EMAIL_VARIABLE]
        return None

    #def user_exists(self, email, req=None):
        #"""Checks against CERN NICE/CRA for existance of email.
        #@return True if the user exists, False otherwise
        #"""
        #users = self._try_twice(funct=AuthCernWrapper.list_users, \
                #params={"display_name":email})
        #return email.upper() in [user['email'].upper() for user in users]


    def fetch_user_groups_membership(self, email, password, req=None):
        """Fetch user groups membership from the SSO system.
        @return a dictionary of groupname, group description
        Note: for SSO the parameter are discarded and overloaded by Shibboleth
        variables
        """
        if req:
            req.add_common_vars()
            if req.subprocess_env.has_key(CFG_EXTERNAL_AUTH_SSO_GROUP_VARIABLE):
                groups = req.subprocess_env[CFG_EXTERNAL_AUTH_SSO_GROUP_VARIABLE].split(CFG_EXTERNAL_AUTH_SSO_GROUPS_SEPARATOR)
                # Filtering out uncomfortable groups
                groups = [group for group in groups if group not in CFG_EXTERNAL_AUTH_HIDDEN_GROUPS]
                for regexp in CFG_EXTERNAL_AUTH_HIDDEN_GROUPS_RE:
                    for group in groups:
                        if regexp.match(group):
                            groups.remove(group)
                return dict(map(lambda x: (x, '@' in x and x + ' (Mailing list)' \
                                or x + ' (Group)'), groups))
        return {}

    def fetch_user_nickname(self, username, password, req=None):
        """Given a username and a password, returns the right nickname belonging
        to that user (username could be an email).
        Note: for SSO the parameter are discarded and overloaded by Shibboleth
        variables
        """
        if req:
            req.add_common_vars()
            if req.subprocess_env.has_key(CFG_EXTERNAL_AUTH_SSO_LOGIN_VARIABLE):
                return req.subprocess_env[CFG_EXTERNAL_AUTH_SSO_LOGIN_VARIABLE]
        else:
            return None

    def _fetch_particular_preferences(self, req=None):
        """This hidden method is there to be overwritten in order to get some
        particular value from non standard variables.
        """
        if req:
            ret = {}
            req.add_common_vars()
            if req.subprocess_env.has_key('HTTP_SHIB_AUTHENTICATION_METHOD'):
                ret['authmethod'] = req.subprocess_env['HTTP_SHIB_AUTHENTICATION_METHOD']
            ret['external'] = '1'
            if req.subprocess_env.has_key('HTTP_ADFS_PERSONID'):
                if not int(req.subprocess_env['HTTP_ADFS_PERSONID']) == -1:
                    ret['external'] = '0'
            return ret
        return {}



    def fetch_user_preferences(self, username, password=None, req=None):
        """Fetch user preferences/settings from the SSO account.
        the external key will be '1' if the account is external to SSO,
        otherwise 0
        @return a dictionary.
        Note: for SSO the parameter are discarded and overloaded by Shibboleth
        variables
        """
        if req:
            req.add_common_vars()
            ret = {}
            prefs = self._fetch_particular_preferences(req)
            for key, value in req.subprocess_env.items():
                if key.startswith(CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME) and not key == CFG_EXTERNAL_AUTH_SSO_GROUP_VARIABLE:
                    prefs[key[len(CFG_EXTERNAL_AUTH_SSO_PREFIX_NAME):].lower()] = value
            for key, value in prefs.items():
                if key in CFG_EXTERNAL_AUTH_HIDDEN_SETTINGS:
                    ret['HIDDEN_' + key] = value
                else:
                    ret[key] = value
            return ret
        return {}

