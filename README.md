# Forward
[![Build Status](http://192.168.182.52:8080/jenkins/job/Forward/job/forward.4.test.after/badge/icon)](http://192.168.182.52:8080/jenkins/job/Forward/job/forward.4.test.after/)
## 介绍
#### &ensp;&ensp;Forward是一个python模块，提供与目标设备之间的通道封装，基于指令行(Command Lines)的方式实现多数功能的封装，供开发者快速简便调用，屏蔽不同设备上指令差异。
#### &ensp;&ensp;建议使用Forward用于多种(厂家、型号)网络设备的自动化管理场景，可以快速构建出运维场景脚本。
## 安装
### 1. 构建虚拟环境(可选)
#### &ensp;&ensp;开发者用户推荐，使用pyenv和virtualenv构建纯净的python环境，推荐python版本2.7.10
```Bash
pyenv virtualenv 2.7.10 forward
pyenv activate forward
```
### 2. 拉取当前版本
```Bash
git clone http://192.168.182.51/promise/forward.git
cd forward
```
### 3. 安装依赖包
```Bash
pip install -r requirements.txt
```
### 4. 安装Forward
```Bash
python setup.py install
```
## 快速入门
#### &ensp;&ensp;下方代码段展示了一个简易的forward场景实现，批量连接到两台设备(思科Nexus7018)，执行指令并获取结果。
```Python
from forward import Forward

new = Forward()
new.addTargets(['192.168.113.99-192.168.113.100'],'n7018','username','password')
instances = new.getInstances()

lab99 = instances['192.168.113.99']
lab100 = instances['192.168.113.100']

result99 = lab99.execute('show version')
result100 = lab100.execute('show version')

if result99['status']:
    print '[%s] OS version info: %s' % ('lab99', result99['content'])
if result100['status']:
    print '[%s] OS version info: %s' % ('lab100', result100['content'])
```

## 版本更新记录
### V3.0.4
#### 1.修复bug:
#### >telnet与sshv1分支系列设备不能成功初始化的问题已经修复。
#### >cisco系列设备的二次认证问题已经修复。

### V3.0.3
#### 1.新增类库: 目前所有1.0版本中的类库已经重构完毕，可以使用，但未经过测试。
#### >根级基础类：baseTELNET,baseSSHV1
#### >厂家级基础类：baseJuniper,baseBear,baseDepp,baseF5,baseFortinet,baseRaisecom,baseZte
#### >华为类：s3300,e1000e
#### >Juniper类：mx960,srx3400
#### >启明星辰类：usg1000
#### 2.修复继承关系:
#### >f510000,fg1240,fg3040,fg3950,m6000,r3048g,s5800,sr7750,zx5952：这些类库目前正确地继承了厂家基础类。

### V3.0.2
#### 1.新增类库:
#### >华为类：e8000e,s9306,s9312,e8160e,ne40ex3,ne40ex16,s5328,s5352,s8512
#### >思科类：adx03100,asa,asr1006,f1000,f510000
#### >linux类：bclinux7
#### >其他类：sr7750,zx5952,fg1240,fg3040,fg3950,m6000,r3048g,s5800,vlb

### V3.0.1
#### 1.新增类库:
#### >厂家级基础类：baseHuawei
#### >华为类：s9303
#### 2.修正bug: n7018类现在可以被正确的调用了。

### V3.0.0
#### 1.版本重构，欢迎体验精简的Forward3.0，参考快速入门。
#### 2.当前支持的类库:
#### >根级基础类：basesshv2
#### >厂家级基础类：basecisco,baselinux
#### >思科类：c2960,c4510,c6506,c6509,n5548,n5596,n7010,n7018,n7710,n7718
#### 3.添加预登陆模式: 默认所有类实例将会在用户调用getInstances方法时批量登陆，如果你不需要预先登陆所有机器，可以指定preLogin属性，例如：Forward.getInstances(preLogin=False)，然后在单独的实例中调用login()方法进行登陆。
