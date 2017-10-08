> Created by `luyidong <yidongsky@gmail.com>`

##### logMonitor

监控小程序
----------
基于应用稳定性的需求，并能及时发现问题，要求对应用程序的日志进行实时分析，当符合某个条件时就立刻报警。

目前主要针对日志中5XX 4XX进行收集，当该关键字出现时(状态值为1)，匹配到报警设定的阀值（最大阀值为1）时，发送报警给收件人。

##### 服务端
----------

主要功能:
1. 支持Ldap账号登录
2. 个人支持绑定微信，手机，邮件(默认)通知；
3. 报警匹配到个人和用户组；
4. 报警设置中，数据类型和节点名称支持正则表达式匹配多个服务节点名；
5. 节点详情页-节点详情页包含当前统计的状态值，IP，URL排序等；

### 客户端
----------

主要功能:
1. 客户端基于Inotify事件驱动的通知机制，当检测到文件修改写入时，检索日志中包含4xx 5xx的日志，上传到服务端；
2. 当没有文件更新时，自动释放资源，等待下一次事件触发启动。

项目部署
----------

Java环境:

`
salt -N '{项目组}' state.sls logmon.java
salt -N '{项目组}' cmd.run "chkconfig supervisord on; supervisord -c /etc/supervisord.conf"
`

PHP环境:
`
salt -N '{项目组}' state.sls logmon.php
salt -N '{项目组}' cmd.run "chkconfig supervisord on;supervisord -c /etc/supervisord.conf"
`

首页

!()[https://github.com/luyidong/logMonitor/blob/master/static/img/home.png "程序首页"]

详情页

!()[https://github.com/luyidong/logMonitor/blob/master/static/img/detail.png "详情页"]

报警列表

!()[https://github.com/luyidong/logMonitor/blob/master/static/img/alert-list.png "报警列表"]

微信,SMS通知

!()[https://github.com/luyidong/logMonitor/blob/master/static/img/detail.png "通知"]