#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for n7018.
Author: Cheung Kei-chuen
"""
from forward.devclass.baseF5 import BASEF5


class F510000(BASEF5):

    def addUser(self, username, password):
        return BASEF5.addUser(self,
                              username=username,
                              password=password,
                              addCommand='user {username} password {password} role network-admin\n')

    def _commit(self):
        return BASEF5._commit(self,
                              saveCommand='copy running-config startup-config',
                              exitCommand='end')
