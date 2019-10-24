#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for ne40ex16.
"""
import re
from forward.devclass.baseHuawei import BASEHUAWEI
from forward.base.sshv2 import sshv2


class NE40EX16(BASEHUAWEI):

    def _commit(self):
        saveCommand = "save"
        # exitCommand = "return"
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            if self.isConfigMode:
                self._exitConfigMode()
                # exit config mode
                self.shell.send('%s\n' % (saveCommand))
                # save setup to system
                while not re.search(self.prompt, data['content'].split('\n')[-1]):
                    data['content'] += self.shell.recv(1024)
                    if re.search(re.escape('Are you sure to continue?[Y/N]'), data['content'].split('\n')[-1]):
                        # interact,send y
                        self.shell.send("y\n")
                if re.search(re.escape('Save the configuration successfully'), data['content'], flags=re.IGNORECASE):
                    data['status'] = True
            else:
                raise IOError('Error: The current state is not configuration mode')
        except Exception, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def login(self, username, password):
        sshChannel = sshv2(self.ip, username, password, self.timeout, self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                self.njInfo['status'] = True
                self.channel = sshChannel['content']
                self.shell = self.channel.invoke_shell(width=1000, height=1000)
                tmpBuffer = ''
                while not re.search(self.basePrompt, tmpBuffer.split('\n')[-1]):
                    tmpBuffer += self.shell.recv(1024)
                    if re.search('\[Y/N\]:', tmpBuffer):
                        self.shell.send('N\n')
                self.shell.settimeout(self.timeout)
                self.getPrompt()
            except Exception as e:
                self.njInfo['status'] = False
                self.njInfo['errLog'] = str(e)
        else:
            # Login failed
            self.njInfo['errLog'] = sshChannel['errLog']
        return self.njInfo
