#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for sshv2 method, by using paramiko module.
Author: Wangzhe
"""

import re
import sys
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.base.forwardError import ForwardError


class BASELINUX(BASESSHV2):
    def privilegeMode(self):
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        return result

    def addUser(self, username, password, **kwargs):
        # Extra parameters
        group = kwargs['group'] if 'group' in kwargs else username
        commandAdduser = 'adduser %s' % username if group == username else 'adduser --gid %s %s' % (group, username)
        commandPw = 'passwd %s\n' % username

        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # legal check
            if not group:
                raise ForwardError("[Add User Error]: %s: Group could NOT be blank." % self.ip)
            if not username or not password:
                raise ForwardError("[Add User Error]: %s: Username or Password could NOT be blank." % self.ip)

            if self.isLogin:
                # execute adduser
                addUserResult = self.execute(commandAdduser)
                if addUserResult['status']:
                    dirExtPattern = '(目录已经存在|home directory already exists)'

                    if not addUserResult['content']:
                        # success
                        pass
                    elif re.search(dirExtPattern, addUserResult['content']):
                        # success, but homedir already exist
                        pass
                    else:
                        # other errors
                        raise ForwardError("[Add User Error]: %s: %s" % (self.ip, addUserResult['content']))

                    # set passwd
                    self.shell.send(commandPw)
                    buff = ''
                    while not (re.search(self.basePrompt, buff) or re.search('New password:', buff)):
                        buff += self.shell.recv(256)
                    if re.search('New password:', buff):
                        self.shell.send(password + '\n')
                        buff = ''
                        while not (re.search(self.basePrompt, buff) or re.search('Retype new password:', buff)):
                            buff += self.shell.recv(256)
                        if re.search('Retype new password:', buff):
                            self.shell.send(password + '\n')
                            buff = ''
                            while not re.search(self.prompt, buff):
                                buff += self.shell.recv(256)
                            if re.search('updated successfully', buff):
                                result['status'] = True
                                return result

                    # error somewhere, raise
                    raise ForwardError("[Set Password Error]: %s: %s" % (self.ip, buff))
                else:
                    raise ForwardError("[Add User Error]: %s: %s" % (self.ip, addUserResult['errLog']))
            else:
                raise ForwardError("[Add User Error]: %s: Not login yet." % self.ip)
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def deleteUser(self, username):
        commandDelUser = 'userdel %s' % username

        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if not username:
                raise ForwardError("[Delete User Error]: %s: Username could NOT be blank." % self.ip)
            if self.isLogin:
                delUserResult = self.execute(commandDelUser)
                if delUserResult['status']:
                    if not delUserResult['content']:
                        # success
                        pass
                    else:
                        raise ForwardError("[Delete User Error]: %s: %s" % (self.ip, delUserResult['content']))
                    result['status'] = True
                    return result
                else:
                    raise ForwardError("[Delete User Error]: %s: %s" % (self.ip, delUserResult['errLog']))
            else:
                raise ForwardError("[Delete User Error]: %s: Not login yet." % self.ip)
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result
