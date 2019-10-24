#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

"""
-----Introduction-----
[Core][forward] Base device class for cisco basic device method, by using paramiko module.
Author: Cheung Kei-Chuen, Wangzhe
"""

import re
import sys
from forward.devclass.baseSSHV2 import BASESSHV2
from forward.base.forwardError import ForwardError


class BASEHUAWEI(BASESSHV2):
    def privilegeMode(self, secondPassword=''):
        self.privilegeModeCommand = 'super'
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        self.cleanBuffer()
        if self.isLogin and (len(secondPassword) > 0):
            # (login succeed status) and (secondPassword exist)
            self.cleanBuffer()
            self.shell.send('%s\n' % (self.privilegeModeCommand))
            enableResult = ''
            while True:
                """
                etc:
                [admin@NFJD-PSC-MGMT-COREVM60 ~]$ super
                [admin@NFJD-PSC-MGMT-COREVM60 ~]$

                or

                [admin@NFJD-PSC-MGMT-COREVM60 ~]$ super
                 Password:
                """
                """
                    fg3950: enable command result : 'enable\r\r\nUnknown action 0\r\n'
                """
                # need password
                passwordChar = """%s[\r\n]+ *[pP]assword""" % self.privilegeModeCommand
                promptChar = """{command}[\r\n]+[\s\S]*{basePrompt}""".format(
                    command=self.privilegeModeCommand,
                    basePrompt=self.basePrompt
                )

                # Second layers of judgment, Privileged command  char 'super/enable'  must be received.
                # otherwise recv continue... important!
                if re.search(passwordChar, enableResult):
                    # if received 'password'
                    break
                # no password
                elif re.search(promptChar, enableResult):
                    # if no password
                    break
                else:
                    # not finished,continue
                    enableResult += self.shell.recv(1024)

            if re.search('assword', enableResult):
                # need password
                self.shell.send("%s\n" % secondPassword)
                result = ''
                while not re.search(self.basePrompt, result) and (not re.search('assword|denied|Denied', result)):
                    result += self.shell.recv(1024)
                if re.search('assword|denied|Denied', result):
                    # When send the secondPassword, once again encountered a password hint password wrong.
                    result['status'] = False
                    result['errLog'] = '[Switch Mode Failed]: Password incorrect'
                elif re.search(self.basePrompt, result):
                    # Switch mode succeed
                    self.getPrompt()
                    result['status'] = True

            # Check the error information in advance
            elif re.search('\%|Invalid|\^', enableResult):
                # bad enable command
                result['status'] = False
                result['errLog'] = '[Switch Mode Failed]: Privileged mode command incorrect-A'
            elif re.search(self.basePrompt, enableResult):
                # Switch mode succeed, don't need password
                self.getPrompt()
                result['status'] = True
            else:
                result['stauts'] = False
                result['errLog'] = '[Switch Mode Failed]: Unknown device status'

        elif not self.isLogin:
            # login failed
            result['status'] = False
            result['errLog'] = '[Switch Mode Failed]: Not login yet'

        elif len(secondPassword) == 0:
            # secondPassword dosen't exist, do nothing
            pass

        return result

    def _commit(self, saveCommand='save', exitCommand='return'):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            if self.isConfigMode:
                self._exitConfigMode(exitCommand)
                # save setup to system
                self.shell.send('%s\n' % (saveCommand))
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                if re.search('(\[OK\])|(Copy complete)|(successfully)', result['content'], flags=re.IGNORECASE):
                    result['status'] = True
            else:
                raise ForwardError('[Commit Config Error]: The current state is not configuration mode')
        except ForwardError, e:
            result['errLog'] = str(e)
            result['status'] = False
        return result

    def addUser(self, username, password, userLevel=1):
        # user leve default 1
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            checkPermission = self._configMode(cmd='sys\naaa')
            # swith to config terminal mode.
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.shell.send('local-user {username} password cipher {password}\n'.format(username=username,
                                                                                            password=password))
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and\
                       (re.search('local-user .* password cipher[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                self.shell.send('local-user {username} privilege level  {userLevel}\n'.format(username=username,
                                                                                              userLevel=userLevel))
                data['content'] = ''
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and\
                       (re.search('local-user .* privilege level[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                self.shell.send("local-user {username} service-type terminal ssh\n".format(username=username))
                data['content'] = ''
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and \
                       (re.search('local-user .* service-type terminal ssh[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                self.shell.send("quit\n")
                data['content'] = ''
                while True:
                    if (re.search(self.basePrompt, data['content'].split('\n')[-1])) and \
                       (re.search('quit.*[\s\S]+%s' % self.basePrompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                self.getPrompt()
                self.shell.send("ssh user {username} authentication-type password\n".format(username=username))
                data['content'] = ''
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and \
                       (re.search('ssh user .* authentication-type password[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                self.shell.send("ssh user {username} service-type all\n".format(username=username))
                data['content'] = ''
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and \
                       (re.search('ssh user .* service-type all[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['status'] = False
            data['errLog'] = str(e)
        return data

    def getUser(self, command="show running-config | in username"):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # [{"username":"zhang-qichuan","secret":5},{}....]
            userList = []
            # execute query command
            info = self.execute(command)
            if not info["status"]:
                raise ForwardError("Error:get user list failed: %s" % info["errLog"])
            # process result
            result = info["content"]
            for line in result.split('\n'):
                # Each line
                index = 0
                # ['username' , 'test-user' , 'secret', '5','$.........']
                segments = line.split()
                for segment in segments:
                    if index <= 1:
                        index += 1
                        # Check after second fields username my-username secret/password .....
                        continue
                    else:
                        if segment == "secret" or segment == "password":
                            # get secret level
                            userData = {"username": segments[1], "secret": segments[index + 1]}
                            userList.append(userData)
                            break
                    index += 1
            result["content"] = userList
            result["status"] = True
        except ForwardError, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def _configMode(self, cmd='sys'):
        # cmd = 'sys\naaa' if addUser
        self.isConfigMode = False
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        self.cleanBuffer()
        self.shell.send("%s\n" % (cmd))
        while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
            result['content'] += self.shell.recv(1024)
        # release host prompt
        self.getPrompt()
        self.isConfigMode = True
        result['status'] = True
        return result

    def _exitConfigMode(self, cmd='return'):
        result = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        try:
            # Check current status
            if self.isConfigMode:
                self.shell.send("%s\n" % (cmd))
                while not re.search(self.basePrompt, result['content'].split('\n')[-1]):
                    result['content'] += self.shell.recv(1024)
                self.isConfigMode = False
                result["status"] = True
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            result["status"] = False
            result['errLog'] = str(e)
        # release host prompt
        self.getPrompt()
        return result

    def changePassword(self, username, password, userLevel=1):
        # user leve default 1
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            checkPermission = self._configMode()
            # swith to config terminal mode.
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.shell.send('local-user {username} password cipher {password}\n'.format(username=username,
                                                                                            password=password))
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and \
                       (re.search('local-user .* password cipher[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['status'] = False
            data['errLog'] = str(e)
        return data

    def deleteUser(self, username):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.cleanBuffer()
                self.shell.send('undo local-user {username}\n'.format(username=username))
                while True:
                    if (re.search(self.prompt, data['content'].split('\n')[-1])) and \
                       (re.search('undo local-user[\s\S]+%s' % self.prompt, data['content'])):
                        break
                    else:
                        data['content'] += self.shell.recv(1024)
                if re.search('error|invalid', data['content'], flags=re.IGNORECASE):
                    raise ForwardError(data['content'])
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['status'] = False
            data['errLog'] = str(e)
        return data
