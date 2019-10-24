#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n7010.
Author: Cheung Kei-Chuen
"""
from forward.devclass.baseCisco import BASECISCO


class N7010(BASECISCO):

    def addUser(self, username, password, admin=False):
        # param admin: defualt is not admin
        if admin:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role network-admin\n')
        else:
            return BASECISCO.addUser(self,
                                     username=username,
                                     password=password,
                                     addCommand='user {username} password {password} role priv-1\n')

    def _commit(self):
        return BASECISCO._commit(self,
                                 saveCommand='copy running-config startup-config',
                                 exitCommand='end')

    def changePassword(self, username, password):
        return BASECISCO.addUser(self,
                                 username=username,
                                 password=password,
                                 addCommand='user {username} password {password} role network-admin\n')
