#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for ASR1006.
Author: Cheung Kei-chuen
"""

from forward.devclass.baseCisco import BASECISCO


class ASR1006(BASECISCO):

    def addUser(self, username, password):
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')

    def changePassword(self, username, password):
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='username {username} secret {password}\n')
