#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for asa.
Author: Cheung Kei-chuen
"""

import re
from forward.devclass.baseCisco import BASECISCO
from forward.base.forwardError import ForwardError


class ASA(BASECISCO):

    def cleanBuffer(self):
        if self.shell.recv_ready():
                self.shell.recv(4096)
        self.shell.send('\r\n')
        buff = ''
        """ When after switching mode, the prompt will change,
        it should be based on basePromptto check and at last line"""
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                buff += self.shell.recv(1024)
            except:
                raise ForwardError('Receive timeout [%s]' % (buff))

    def addUser(self, username, password):
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')

    def changePassword(self, username, password):
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} password {password}\n')
