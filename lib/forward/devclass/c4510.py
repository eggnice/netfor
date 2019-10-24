#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for c4510.
Author: Cheung kei-chuen
"""

from forward.devclass.baseCisco import BASECISCO


class C4510(BASECISCO):

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
