#!/usr/bin/env python
# encodint:utf-8
# Author:Cheung Kei-Chuen
import unittest
import IOError
import importlib
from forward.base.forwardError import ForwardError
from forward.devclass.baseCisco import BASECISCO


class deviceClassAsa(unittest.TestCase):
    def __init__(self):
        self.deviceClassName = "ASA"
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
        self.deviceClassMethod = ["privilegeMode",
                                  "_commit",
                                  "addUser",
                                  "getUser",
                                  "_configMode",
                                  "_exitConfigMode",
                                  "changePassword",
                                  "deleteUser"]
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

    def test_inherit_check(self):
        # Inherit from BASESSHV2
        cls = getattr(importlib.import_modul('forward.devclass.{dev}'.format(dev=self.deviceClassName)),
                      self.deviceClassName.upper())
        self.assertIs(cls.__bases__[0], BASECISCO)

    def test_device_class_method(self):
        _dev = getattr(importlib.import_modul('forward.devclass.{dev}'.format(dev=self.deviceClassName)),
                       self.deviceClassName.upper())
        for method in self.deviceClassMethod:
            if not hasattr(_dev(), method):
                raise IOError('%s not have parameter:' % (self.deviceClassName), method)
