#!/usr/bin/evn python
# coding:utf-8
import sys
import re
import os
import time
from forward.base.sshv1 import sshv1
from forward.base.forwardError import ForwardError
import pexpect


class BASESSHV1(object):
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

    def login(self):
        result = {
            'status': False,
            'errLog': ''
        }
        sshChannel = sshv1(ip=self.ip,
                           username=self.username,
                           password=self.password,
                           port=self.port,
                           timeout=self.timeout)
        if sshChannel['status']:
            result['status'] = True
            self.channel = sshChannel['content']
            self.getPrompt()
            self.cleanBuffer()
            self.isLogin = True
        else:
            self.isLogin = False
            result['errLog'] = sshChannel['errLog']
        return result

    def __del__(self):
        self.logout()

    def logout(self):
        result = {
            'status': False,
            'errLog': ''
        }
        try:
            self.channel.close()
            self.isLogin = False
            result['status'] = True
        except Exception, e:
            result['status'] = False
            result['errLog'] = str(e)
        return result

    def enable(self, password):
        pass

    def execute(self, cmd):
        self.cleanBuffer()
        # dataPattern = re.escape(cmd)+'.*\r\n([\s\S]*)\r\n'+self.prompt
        dataPattern = '[\r\n]+([\s\S]*)[\r\n]+'
        # SSHV1 pexpect not have self.prompt end
        data = {'status': False,
                'content': '',
                'errLog': ''}
        if self.isLogin:
            self.channel.send(cmd + '\n')
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt, pexpect.TIMEOUT], timeout=self.timeout)
            result = ''
            if i == 0:
                result = self.channel.before
                # get result
                result += self.getMore()
                # get more result
            elif i == 2:
                data['errLog'] = 'Error: receive timeout '
            else:
                result = self.channel.before
            data['content'] += result
            data["status"] = True
            try:
                tmp = re.search(dataPattern, data['content']).group(1)
                data['content'] = tmp
            except Exception, e:
                data['status'] = False
                data['errLog'] = data['errLog'] + "not fond host prompt:Error(%s)" % str(e)
        else:
            data['status'] = False
            data['errLog'] = 'ERROR:device not login'
        return data

    def getMore(self):
        result = ''
        while True:
            self.channel.send(' ')
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt, pexpect.TIMEOUT], timeout=self.timeout)
            if i == 0:
                result += self.channel.before
                # After the encounter `moreFlag`, need to get the message
            elif i == 1:
                result += self.channel.before
                # After the encounter prompt, need to get the result
                break
            else:
                break
        return result

    def getPrompt(self):
        if self.isLogin:
            self.channel.send('\n')
            self.channel.expect([r"%s" % self.basePrompt, pexpect.TIMEOUT], timeout=self.timeout)
            self.prompt = self.channel.before.split('\n')[-1] + "(>|#|\$|\]|\)) *$"
        else:
            raise ForwardError('[Get Prompt Error]: %s: Not login yet.' % self.ip)
        return self.prompt

    def cleanBuffer(self):
        self.channel.send('\n')
        try:
            return self.channel.expect(self.prompt, timeout=self.timeout)
        except pexpect.TIMEOUT:
            return ''
