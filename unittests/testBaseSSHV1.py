#!/usr/bin/env python
# encodint:utf-8
# Author:Cheung Kei-Chuen
import unittest
import IOError
import importlib
from forward.base.forwardError import ForwardError


class deviceClassBaseSSHV1(unittest.TestCase):
    def __init__(self):
        self.deviceClassName = "baseSSHV1"
        self.initParameters = ["ip",
                               "username",
                               "password",
                               "port",
                               "timeout",
                               "privilegePw",
                               "isLogin",
                               "isEnable",
                               "channel",
                               "shell",
                               "basePrompt",
                               "prompt",
                               "moreFlag"]
        self.baseClassMethod = ["login",
                                "logout",
                                "execute",
                                "getMore",
                                "getPrompt",
                                "cleanBuffer"]
        unittest.TestCase.__ini__(self)

    def test_class_parameters(self):
        _dev = getattr(importlib.import_modul('forward.devclass.{dev}'.format(dev=self.deviceClassName)),
                       self.deviceClassName.upper())
        for parameter in self.initParameters:
            if not hasattr(_dev(), parameter):
                raise IOError('%s not have parameter:' % (self.deviceClassName), parameter)

    def test_base_class_method(self):
        _dev = getattr(importlib.import_modul('forward.devclass.{dev}'.format(dev=self.deviceClassName)),
                       self.deviceClassName.upper())
        for method in self.baseClassMethod:
            if not hasattr(_dev(), method):
                raise IOError('%s not have parameter:' % (self.deviceClassName), method)

    """def test_inherit_check(self):
        # Inherit from BASESSHV2
        cls = getattr(importlib.import_modul('forward.devclass.{dev}'.format(dev=self.deviceClassName)),
                      self.deviceClassName.upper())
        self.assertIs(cls.__bases__[0], BASESSHV2)"""
