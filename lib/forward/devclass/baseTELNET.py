#!/usr/bin/evn python
# coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments C6506.py
"""
import sys
import re
import os
from forward.base.telnet import telnet
from forward.base.forwardError import ForwardError


class BASETELNET(object):
    def __init__(self, ip, username, password, **kwargs):
        self.ip = ip
        self.username = username
        self.password = password

        self.port = kwargs['port'] if 'port' in kwargs else 23
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
        sshChannel = telnet(ip=self.ip,
                            username=self.username,
                            password=self.password,
                            port=self.port,
                            timeout=self.timeout)
        if sshChannel['status']:
            self.channel = sshChannel['content']
            self.getPrompt()
            result['status'] = True
            self.isLogin = True
        else:
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
            result['content'] = str(e)
        return result

    def execute(self, cmd):
        dataPattern = '[\r\n]+([\s\S]*)[\r\n]+' + self.prompt
        # Spaces will produce special characters and re.escape('show ver') --> show \\ ver
        data = {'status': False,
                'content': '',
                'errLog': ''}
        if self.isLogin:
            self.cleanBuffer()
            self.channel.write(cmd + "\n")
            i = self.channel.expect([r'%s' % self.moreFlag, r"%s" % self.prompt], timeout=self.timeout)
            result = i[-1]
            try:
                if i[0] == 0:
                    result += self.getMore()
                elif i[0] == -1:
                    raise ForwardError('Error: receive timeout ')
                data['content'] += result
                try:
                    tmp = re.search(dataPattern, data['content']).group(1)
                    data['content'] = tmp
                    data['status'] = True
                except Exception, e:
                    raise ForwardError('not found host prompt Errorr(%s)' % str(e))
            except Exception, e:
                data['status'] = False
                data['errLog'] = data['errLog'] + 'not found host prompt Errorr(%s)' % str(e)
        else:
            data['status'] = False
            data['content'] = 'ERROR:device not login'
        return data

    def getMore(self):
        result = ''
        while True:
            self.channel.send(' ')
            i = self.channel.expect([r'%s' % self.moreFlag, self.prompt], timeout=self.timeout)
            result += i[-1]
            if i[0] == 1:
                break
        return result

    def getPrompt(self):
        self.channel.send('\n')
        i = self.channel.expect([r"%s" % self.basePrompt], timeout=self.timeout)
        self.prompt = re.escape(i[-1].split('\n')[-1])
        return self.prompt

    def cleanBuffer(self):
        self.channel.send('\n')
        i = self.channel.expect([r"%s" % self.prompt], timeout=self.timeout)
        result = i[-1]
        return result
