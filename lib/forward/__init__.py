#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2017, Azrael <azrael-ex@139.com>

import threading
import importlib
import forward.release
from forward.base.forwardError import ForwardError
from forward.base.loginThread import loginThread
from forward.base.paraCheck import paraCheck
from forward.base.deviceListSplit import DEVICELIST

__version__ = forward.release.__version__
__author__ = forward.release.__author__


class Forward(object):
    """docstring for Forward"""
    def __init__(self, targets=None):
        # target: [[ip,model,user,pw,{port},{timeout}],...]
        super(Forward, self).__init__()
        self.instances = {}
        if (targets is None):
            self.targets = []
        elif paraCheck(targets):
            self.targets = targets
        else:
            raise ForwardError('[Forward Init Failed]: parameters type error')

    def addTargets(self, iplist, model, username, password, **kwargs):
        # iplist,model,username,password,port=??,timeout=??
        ipAdds = DEVICELIST(iplist).getIpList()
        targetList = []

        for ip in ipAdds:
            if paraCheck([[ip, model, username, password, kwargs]]):
                targetList.append([ip, model, username, password, kwargs])
            else:
                print "[Add Targets Error]: %s parameters type error, please check." % ip

        self.targets.extend(targetList)

    def getInstances(self, preLogin=True):
        # thread init
        threads = []

        # init instances
        if preLogin:
            for target in self.targets:
                model = target[1]
                className = model.upper()
                self.instances[target[0]] = getattr(
                    importlib.import_module('forward.devclass.%s' % (model)),
                    className
                )(target[0], target[2], target[3], **target[4])

                threadNode = threading.Thread(target=loginThread, args=(self.instances[target[0]],))
                threadNode.start()
                threads.append(threadNode)
        else:
            for target in self.targets:
                model = target[1]
                className = model.upper()
                self.instances[target[0]] = getattr(
                    importlib.import_module('forward.devclass.%s' % (model)),
                    className
                )(target[0], target[2], target[3], **target[4])

        # pre login thread join
        if preLogin:
            for t in threads:
                t.join()

        return self.instances
