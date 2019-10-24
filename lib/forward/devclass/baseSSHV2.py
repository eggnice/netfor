#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

"""
-----Introduction-----
[Core][forward] Base device class for sshv2 method, by using paramiko module.
Author: Wangzhe, Cheung Kei-Chuen
"""

import re
import sys
from forward.base.sshv2 import sshv2
from forward.base.forwardError import ForwardError


class BASESSHV2(object):
    def __init__(self, ip, username, password, **kwargs):
        self.ip = ip
        self.username = username
        self.password = password

        self.port = kwargs['port'] if 'port' in kwargs else 22
        self.timeout = kwargs['timeout'] if 'timeout' in kwargs else 30
        self.privilegePw = kwargs['privilegePw'] if 'privilegePw' in kwargs else ''

        self.isLogin = False
        self.isEnable = False

        self.channel = ''
        self.shell = ''
        self.basePrompt = r'(>|#|\]|\$|\)) *$'
        self.prompt = ''
        self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'

        """
        - parameter ip: device's ip
        - parameter port : device's port
        - parameter timeout : device's timeout(Only for login,not for execute)
        - parameter channel: storage device connection channel session
        - parameter shell: paramiko shell, used to send(cmd) and recv(result)
        - parameter prompt: [ex][wangzhe@cloudlab100 ~]$
        - parameter njInfo : return interactive data's format
        """

    def __del__(self):
        self.logout()

    def login(self):
        result = {
            'status': False,
            'errLog': ''
        }
        # sshv2(ip,username,password,timeout,port=22)
        sshChannel = sshv2(self.ip, self.username, self.password, self.timeout, self.port)
        if sshChannel['status']:
            # Login succeed, init shell
            try:
                result['status'] = True
                self.channel = sshChannel['content']
                self.shell = self.channel.invoke_shell(width=10000, height=10000)
                tmpBuffer = ''
                while (
                    not re.search(self.basePrompt, tmpBuffer.split('\n')[-1])
                ) and (
                    not re.search('new +password', tmpBuffer.split('\n')[-1], flags=re.IGNORECASE)
                ):
                    tmpBuffer += self.shell.recv(1024)
                # if prompt is 'New Password' ,raise Error.
                if re.search('new +password', tmpBuffer.split('\n')[-1], flags=re.IGNORECASE):
                    raise ForwardError(
                        '[Login Error]: %s: Password expired, needed to be updated!' % self.ip
                    )
                self.shell.settimeout(self.timeout)
                self.isLogin = True
                self.getPrompt()
            except Exception as e:
                result['status'] = False
                result['errLog'] = str(e)
        else:
            # Login failed
            self.isLogin = False
            result['errLog'] = sshChannel['errLog']
        return result

    def logout(self):
        result = {
            'status': False,
            'errLog': ''
        }
        try:
            self.channel.close()
            self.isLogin = False
            result['status'] = True
        except Exception as e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def execute(self, cmd):
        result = {
            'status': True,
            'content': '',
            'errLog': ''
        }
        self.cleanBuffer()
        if self.isLogin:
            # check login status
            # [ex] when send('ls\r'),get 'ls\r\nroot base etc \r\n[wangzhe@cloudlab100 ~]$ '
            # [ex] data should be 'root base etc '
            self.shell.send(cmd + "\r")
            resultPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
            try:
                while not re.search(self.prompt, result['content'].split('\n')[-1]):
                    self.getMore(result['content'])
                    result['content'] += self.shell.recv(1024)
                # try to extract the return data
                tmp = re.search(resultPattern, result['content']).group(1)
                result['content'] = tmp
            except Exception as e:
                # pattern not match
                result['status'] = False
                result['content'] = result['content']
                result['errLog'] = str(e)
        else:
            # not login
            result['status'] = False
            result['errLog'] = '[Execute Error]: device not login'
        return result

    def getPrompt(self):
        if self.isLogin:
            # login status True
            result = ''
            self.cleanBuffer()
            self.shell.send('\n')
            # set recv timeout to self.timeout/10 fot temporary
            while not re.search(self.basePrompt, result):
                result += self.shell.recv(1024)
            if result:
                # recv() get something
                # select last line character,[ex]' >[localhost@labstill019~]$ '
                self.prompt = result.split('\n')[-1]
                # [ex]'>[localhost@labstill019~]$'
                # self.prompt=self.prompt.split()[0]
                # [ex]'[localhost@labstill019~]'
                # self.prompt=self.prompt[1:-1]
                # [ex]'\\[localhost\\@labstill019\\~\\]$'
                self.prompt = re.escape(self.prompt)
                return self.prompt
            else:
                # timeout,get nothing,raise error
                raise ForwardError('[Get Prompt Error]: %s: Timeout,can not get prompt.' % self.ip)
        else:
            # login status failed
            raise ForwardError('[Get Prompt Error]: %s: Not login yet.' % self.ip)

    def getMore(self, bufferData):
        # if check buffer data has 'more' flag, at last line.
        if re.search(self.moreFlag, bufferData.split('\n')[-1]):
            # can't used to \n and not use ' \r' ,because product enter character
            self.shell.send(' ')

    def cleanBuffer(self):
        if self.shell.recv_ready():
            self.shell.recv(4096)
        self.shell.send('\n')
        buff = ''
        # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
        while not re.search(self.basePrompt, buff.split('\n')[-1]):
            try:
                buff += self.shell.recv(1024)
            except:
                raise ForwardError('[Clean Buffer Error]: %s: Receive timeout [%s]' % (self.ip, buff))
