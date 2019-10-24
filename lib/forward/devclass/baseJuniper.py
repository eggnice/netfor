#!/usr/bin/evn python
# coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments mx960.py
"""
import sys
import re
import os
from forward.devclass.baseTELNET import BASETELNET
from forward.base.forwardError import ForwardError


class BASEJUNIPER(BASETELNET):

    def _recv(self, _prompt):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        try:
            if i[0] == -1:
                raise ForwardError('Error: receive timeout')
            data['status'] = True
            data['content'] = i[-1]
        except ForwardError, e:
            data['errLog'] = str(e)
        return data

    def _configMode(self):
        # private method
        self.isConfigMode = False
        data = {"status": False,
                "content": "",
                "errLog": ""}
        self.cleanBuffer()
        self.channel.write("configure\n")
        data = self._recv(self.basePrompt)
        if data['status']:
            self.isConfigMode = True
        self.getPrompt()
        return data

    def _exitConfigMode(self):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # Check current status
            if self.isConfigMode:
                self.channel.write("exit\n")
                data = self._recv(self.basePrompt)
                if data['status']:
                    self.isConfigMode = False
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
        self.getPrompt()
        return data

    def _commit(self):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if self.isConfigMode:
                self.channel.write('commit\n')
                result = self._recv(self.prompt)
                if re.search('succeeds', result['content'], flags=re.IGNORECASE):
                    data['status'] = True
                else:
                    data['content'] = result['content']
            else:
                raise ForwardError('Error: The current state is not configuration mode')
        except ForwardError, e:
                data['errLog'] = str(e)
                data['status'] = False
        return data

    def addUser(self, username, password, admin=False):
        if admin:
            command = "set system login user {username} class read-only\n".format(username=username)
        else:
            command = "set system login user {username} class  ABC\n".format(username=username)
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            checkPermission = self._configMode()   # swith to config terminal mode.
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # adduser
                self.channel.write(command)
                # recv result
                data = self._recv(self.prompt)
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                # execute useradd command
                self.channel.write('set system login user {username} \
                                   authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                # repassword
                if i[0] == 0:
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # set password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def deleteUser(self, username):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username:
                raise ForwardError('Please specify a username')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # delete user
                self.channel.write('delete system login user {username}\n'.format(username=username))
                i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                else:
                    data = self._commit()
                    # exit config terminal mode.
                    self._exitConfigMode()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password):
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if not username or not password:
                # Specify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # check terminal status
            if self.isConfigMode:
                # execute useradd command
                self.channel.write('set system login user {username} \
                                    authentication plain-text-password\n'.format(username=username))
                i = self.channel.expect([r"New password:", r"%s" % self.prompt], timeout=self.timeout)
                result = i[-1]
                if re.search('error|invalid', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # Enter password
                self.channel.write("{password}\n".format(password=password))
                # check password
                i = self.channel.expect([r"Retype new password:", r"%s" % self.prompt], timeout=self.timeout)
                if i[0] == 0:
                    # repassword
                    self.channel.write("{password}\n".format(password=password))
                    # check password
                    i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
                    if i[0] == 0:
                        result = i[-1]
                        if re.search('error|invalid', result, flags=re.IGNORECASE):
                            raise ForwardError(result)
                        else:
                            # change password is successed.
                            data = self._commit()
                            # exit config terminal mode.
                            self._exitConfigMode()
                    elif i[0] == -1:
                        raise ForwardError('Error: receive timeout')
                elif i[0] == 1:
                    # password wrong
                    raise ForwardError(i[-1])
                elif i[0] == -1:
                    # timeout
                    raise ForwardError('Error: receive timeout')
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
                data['errLog'] = str(e)
                data['status'] = False
        return data

    # def bindBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.bindBandwidth()
    #     return njInfo
    #
    # def deleteBindIPAndBandwidth(self, ip='', bandwidth=''):
    #     njInfo = {"status": False,
    #               "content": "",
    #               "errLog": ""}
    #     mx960Bandwidth = Bandwidth(ip=ip, bandwidth=bandwidth, shell=self)
    #     njInfo = mx960Bandwidth.deleteBindIPAndBandwidth()
    #     return njInfo
