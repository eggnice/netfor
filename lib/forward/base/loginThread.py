#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>


def loginThread(instance):
    if not instance.isLogin:
        result = instance.login()
        if not result['status']:
            print '[Login Error]: %s :%s' % (instance.ip, result['errLog'])
